from sqlalchemy import func
from configurations import *
from typing import List
from schema import *
import models as Models
from fastapi import APIRouter, Depends, HTTPException
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


router = APIRouter(tags=["recommend"])


@router.get("/songRecommendationES")
def song_recommend(current_user=Depends(active_user)):
    """
    Get song recommendations for the current user based on their playlists.

    Parameters:
    - `current_user`: Dependency to get the current user.

    Returns:
    - A list of recommended songs based on the user's playlists.
    """
    try:
        if not es.indices.exists(index="playlist-info"):
            raise HTTPException(status_code=404, detail="Index not found")
        query = {
            "query": {"match": {"user": current_user["user"].id}},
            "_source": ["songs"],
        }

        result = es.search(index="playlist-info", body=query)
        hits = result.get("hits", {}).get("hits", [])

        all_songs = [hit["_source"]["songs"] for hit in hits]
        song_merge = []

        for i in all_songs:
            if i:
                for j in i:
                    song_merge.append({"_id": j})
        if len(song_merge) <= 3:
            random_songs = (
                session.query(Models.Song).order_by(func.random()).limit(10).all()
            )
            for item in random_songs:
                song_merge.append({"_id": item.id})
        # return song_merge
        english_stopwords = set(stopwords.words("english"))
        # print(list(english_stopwords))
        mlt_query = {
            "query": {
                "more_like_this": {
                    "fields": ["artist_name", "genre_name", "album_name"],
                    "like": song_merge,
                    "min_term_freq": 2,
                    "stop_words": list(english_stopwords),
                }
            },
            "aggs": {
                "details": {
                    "top_hits": {
                        "size": 5,
                        "_source": {
                            "includes": [
                                "title",
                                "song_id",
                                "genre_name",
                                "artist_name",
                                "album_name",
                            ]
                        },
                    }
                }
            },
            "_source": {
                "includes": ["_id", "title", "artist_name", "genre_name", "album_name"]
            },
            "explain": True,
        }

        result = es.search(index="songs", body=mlt_query, size=100)
        return result
        explanations = {}
        for hit in result.get("hits", {}).get("hits", []):
            # print(hit)
            doc_id = hit.get("_id")
            # print("doc")
            # print(doc_id)
            explanation = es.explain(index="songs", id=doc_id, body=mlt_query)
            explanations[doc_id] = explanation

        # result["_explanations"] = explanations
        return explanations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
