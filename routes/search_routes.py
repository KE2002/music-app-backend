from configurations import *
from typing import List
from schema import *
import models as Models
from fastapi import APIRouter, Depends, HTTPException, FastAPI

router = APIRouter(tags=["Search"])


@router.post("/searchES")
def search_index(input: Search, current_user=Depends(active_user)):
    """
    Search for songs in the Elasticsearch index.

    Parameters:
    - `input`: Search input containing the query string.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A list of search hits containing information about the matched songs.
    """
    try:
        if not es.indices.exists(index="songs"):
            raise HTTPException(status_code=404, detail="Index not found")
        query = {
            "query": {
                "multi_match": {
                    "query": input.input,
                    "fields": ["title", "artist_name", "genre_name", "album_name"],
                }
            },
            "explain": True,
        }
        result = es.search(index="songs", body=query, size=10)
        hits = result.get("hits", {}).get("hits", [])
        return hits

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
