from fastapi import APIRouter, Depends, HTTPException
from configurations import *
from schema import *
import models as Models
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from elasticsearch import exceptions as es_exceptions


router = APIRouter(tags=["Songs"])


@router.get("/songsES")
def elastic_query_songs():
    """
    Retrieve information about songs from Elasticsearch.

    Returns:
    - A generator yielding information about songs.
    """
    try:
        if not es.indices.exists(index="songs"):
            raise HTTPException(status_code=404, detail="Index not found")
        query = {
            "query": {"match_all": {}},
            "_source": ["title", "artist_name", "genre_name", "album_name", "id"],
        }

        result = es.search(index="songs", body=query, size=100, scroll="1m")
        hits = result.get("hits", {}).get("hits", [])
        scroll_id = result.get("_scroll_id")
        while hits:
            songs_info = [hit["_source"] for hit in hits]
            yield songs_info
            result = es.scroll(scroll_id=scroll_id, scroll="1m")
            hits = result.get("hits", {}).get("hits", [])

    except es_exceptions.ConnectionError as conn_err:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Elasticsearch connection error: {str(conn_err)}",
        )

    except es_exceptions.TransportError as trans_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Elasticsearch transport error: {str(trans_err)}",
        )

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/songRating")
async def rate_songs(rating: SongRating, current_user=Depends(active_user)):
    """
    Rate a song or update the existing rating.

    Parameters:
    - `rating`: SongRating schema containing song ID and rating.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful rating update or addition.
    """
    try:
        existing_rating = (
            session.query(Models.SongRating)
            .filter(
                Models.SongRating.user_id == current_user["user"].id,
                Models.SongRating.song_id == rating.id,
            )
            .first()
        )

        if existing_rating:
            existing_rating.rating = rating.rating
        else:
            new_rating = Models.SongRating(
                user_id=current_user["user"].id,
                song_id=rating.id,
                rating=rating.rating,
            )
            session.add(new_rating)

        session.commit()

        es.update(
            index="songs",
            id=rating.id,
            body={
                "doc": {
                    "total_ratings": session.query(
                        func.round(func.avg(Models.SongRating.rating), 2)
                    )
                    .filter(Models.SongRating.song_id == rating.id)
                    .scalar()
                }
            },
        )

        return {"detail": "Rating Updated" if existing_rating else "Rating Added"}

    except SQLAlchemyError as sql_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=sql_err
        )

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/share")
async def share_song(share_details: Share, current_user=Depends(active_user)):
    """
    Share a song with another user.

    Parameters:
    - `share_details`: Share schema containing song ID and recipient user ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful song sharing.
    """
    try:
        share_song = Models.SongShare(
            from_user_id=current_user["user"].id,
            to_user_id=share_details.to_user,
            song_id=share_details.song_id,
        )
        session.add(share_song)
        session.commit()
        return {"Song shared successfully"}
    except SQLAlchemyError as sql_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=sql_err
        )

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/song/{sId}")
async def about_song(sId: str):
    """
    Retrieve information about a specific song from Elasticsearch.

    Parameters:
    - `sId`: Song ID.

    Returns:
    - Information about the specified song.
    """
    try:
        if not es.indices.exists(index="songs"):
            raise HTTPException(status_code=404, detail="Index not found")
        query = {"query": {"term": {"_id": sId}}}
        response = es.search(index="songs", body=query)
        song_data = response["hits"]["hits"][0]["_source"]

        return song_data
    except es_exceptions.ConnectionError as conn_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Elasticsearch connection error: {str(conn_err)}",
        )

    except es_exceptions.TransportError as trans_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Elasticsearch transport error: {str(trans_err)}",
        )

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
