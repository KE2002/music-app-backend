from schema import *
import models as Models
from fastapi import APIRouter, Depends, HTTPException
from elasticsearch.exceptions import TransportError
from elasticsearch import exceptions as es_exceptions
from sqlalchemy.exc import SQLAlchemyError

from operations import *
from sqlalchemy.orm.exc import NoResultFound
from error_handler import *

router = APIRouter(tags=["Playlists"])


@router.get("/playlistSongs/{pId}", response_model=PlayListDetails)
async def display_songs_playlist(pId: str, current_user=Depends(active_user)):
    """
    Retrieve details of a playlist, including its songs.

    Parameters:
    - `pId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - Details of the playlist, including its songs.
    """
    try:
        list_songs = (
            session.query(Models.Playlist)
            .filter(
                Models.Playlist.id == pId,
                Models.Playlist.user_id == current_user["user"].id,
            )
            .one()
        )

        return list_songs

    except NoResultFound:
        handle_not_found()

    except Exception as e:
        handle_generic_error(e)


@router.get("/displayUserPlaylistES")
def display_playlist_elastic_search(current_user=Depends(active_user)):
    """
    Display playlists using Elasticsearch for the current user.

    Parameters:
    - `current_user`: Dependency to get the current user.

    Returns:
    - A generator yielding playlist information from Elasticsearch.
    """
    try:
        if not index_exists("playlist-info"):
            handle_not_found()
        query = {
            "query": {"match": {"user": current_user["user"].id}},
            "_source": ["name"],
        }
        result = index_search(index_name="playlist-info", query=query)
        hits = result.get("hits", {}).get("hits", [])
        return hits

    except HTTPException as e:
        handle_http_exception(e)

    except (Exception, es_exceptions.TransportError) as e:
        handle_generic_error(e)


@router.get("/playlistSongsES/{pId}")
def display_songs_from_playlist(pId: str, current_user=Depends(active_user)):
    """
    Display songs from a playlist using Elasticsearch.

    Parameters:
    - `pId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - Songs from the specified playlist.
    """
    try:
        if not index_exists(index_name="playlist-info"):
            handle_not_found()
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"user": current_user["user"].id}},
                        {"match": {"id": pId}},
                    ]
                }
            },
            "_source": ["songs"],
        }
        
        result = index_search(index_name="playlist-info", query=query, size=100)
        hits = result.get("hits", {}).get("hits", [])
        return hits
    except HTTPException as e:
        handle_http_exception(e)

    except (es_exceptions.TransportError, Exception) as e:
        handle_generic_error(e)


@router.post("/createPlaylist")
async def create_playlist(plist: CreatePlaylist, current_user=Depends(active_user)):
    """
    Create a new playlist for the current user.

    Parameters:
    - `plist`: Playlist name.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A success message indicating the playlist creation.
    """
    try:
        existing_playlist = (
            session.query(Models.Playlist)
            .filter(
                Models.Playlist.name == plist.name,
                Models.Playlist.user_id == current_user["user"].id,
            )
            .all()
        )
        if existing_playlist:
            handle_bad_request()

        new_playlist = Models.Playlist(name=plist.name, user_id=current_user["user"].id)

        session.add(new_playlist)
        session.commit()

        playlist_data = {
            "id": session.query(Models.Playlist)
            .filter(
                Models.Playlist.name == plist.name,
                Models.Playlist.user_id == current_user["user"].id,
            )
            .first()
            .id,
            "name": plist.name,
            "user": current_user["user"].id,
            "songs": [],
        }

        index_elastic(
            index_name="playlist-info", body=playlist_data, id=playlist_data["id"]
        )
        return {"Playlist Created"}

    except (SQLAlchemyError, es_exceptions.TransportError, Exception) as e:
        handle_generic_error(e)


@router.patch("/addSongs/playlist")
async def add_songs(playlistId: str, sId: str, current_user=Depends(active_user)):
    """
    Add songs to a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `sId`: Song ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful addition of the song to the playlist.
    """
    try:
        list_songs = (
            session.query(Models.PlaylistSong)
            .filter(Models.PlaylistSong.playlist_id == playlistId)
            .all()
        )
        if list_songs:
            is_present = any(item.song_id == sId for item in list_songs)
            if is_present:
                handle_bad_request()

        add_song_playlist = Models.PlaylistSong(song_id=sId, playlist_id=playlistId)
        session.add(add_song_playlist)
        session.commit()

        playlist_doc = get_doc(index_name="playlist-info", id=playlistId)
        songs = playlist_doc["_source"].get("songs", [])
        if sId not in songs:
            songs.append(sId)
            index_update(
                index_name="playlist-info", id=playlistId, body={"doc": {"songs": songs}}
            )

        return {"detail": "Song Added To Playlist"}

    except HTTPException as e:
        handle_http_exception(e)
    except (SQLAlchemyError, es_exceptions.TransportError, Exception) as e:
        handle_generic_error(e)


@router.put("/deleteSong/playlist")
async def remove_song(playlistId: str, sId: str, current_user=Depends(active_user)):
    """
    Remove a song from a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `sId`: Song ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful removal of the song from the playlist.
    """
    try:
        playlist_song = (
            session.query(Models.PlaylistSong)
            .filter(Models.PlaylistSong.song_id == sId)
            .first()
        )

        if playlist_song:
            session.delete(playlist_song)
            session.commit()
            playlist_doc = get_doc(index_name="playlist-info", id=playlistId)
            songs = playlist_doc["_source"].get("songs", [])

            if sId in songs:
                songs.remove(sId)
                index_update(
                    index_name="playlist-info", id=playlistId, body={"doc": {"songs": songs}}
                )

        else:
            handle_not_found()

        return {"detail": "Song Removed From Playlist"}

    except HTTPException as e:
        handle_http_exception(e)

    except (Exception, SQLAlchemyError, es_exceptions.TransportError) as e:
        handle_generic_error(e)


@router.delete("/deletePlaylist/{playlistId}")
async def delete_playlist(playlistId: str, current_user=Depends(active_user)):
    """
    Delete a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful deletion of the playlist.
    """
    try:
        playlist_hit = (
            session.query(Models.Playlist)
            .filter(
                Models.Playlist.id == playlistId,
                Models.Playlist.user_id == current_user["user"].id,
            )
            .first()
        )
        print(playlist_hit)
        if not playlist_hit:
            handle_forbidden()
        session.delete(playlist_hit)
        session.commit()
        index_dox_delete(index_name="playlist-info", id=playlistId)
        return {"detail": "Playlist deleted successfully"}

    except HTTPException as e:
        handle_http_exception(e)

    except (Exception, SQLAlchemyError, es_exceptions.ApiError) as e:
        handle_generic_error(e)


@app.get("/curatePlaylist")
async def curate_playlist(
    playlist_details: CuratePlaylist, current_user=Depends(active_user)
):
    """
    Curate a playlist based on specified criteria.

    Parameters:
    - `playlist_details`: Details for curating the playlist.
    - `current_user`: Dependency to get the current user.

    Returns:
    - List of songs curated based on the specified criteria.
    """
    should_conditions = []

    if playlist_details.artist_ids:
        should_conditions.extend(
            {"match": {"artist_id": artist_id}}
            for artist_id in playlist_details.artist_ids
        )

    if playlist_details.genre_ids:
        should_conditions.extend(
            {"match": {"genre_id": genre_id}} for genre_id in playlist_details.genre_ids
        )

    if playlist_details.album_ids:
        should_conditions.extend(
            {"match": {"album_id": album_id}} for album_id in playlist_details.album_ids
        )
    query = {"query": {"bool": {"should": should_conditions}}}
    # return query
    try:
        result = index_search(index_name="songs", query=query, size=20)
        hits = result.get("hits", {}).get("hits", [])
        # return hits
        song_list = [hit["_source"] for hit in hits]
        new_playlist = Models.Playlist(
            name=playlist_details.name, user_id=current_user["user"].id
        )
        session.add(new_playlist)
        session.commit()
        songs = []
        for song in song_list:
            songs.append(song["id"])
        playlist_data = {
            "id": session.query(Models.Playlist)
            .filter(
                Models.Playlist.name == playlist_details.name,
                Models.Playlist.user_id == current_user["user"].id,
            )
            .first()
            .id,
            "name": playlist_details.name,
            "user": current_user["user"].id,
            "songs": songs,
        }

        index_elastic(index_name="playlist-info", body=playlist_data, id=playlist_data["id"])
        return song_list
    except HTTPException as e:
        handle_http_exception(e)

    except (Exception, SQLAlchemyError, es_exceptions.ApiError) as e:
        handle_generic_error(e)
