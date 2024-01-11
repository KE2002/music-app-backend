from configurations import *
from schema import *

from fastapi import APIRouter, Depends, HTTPException
from error_handler import *
from operations import *

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
        if not index_exists(index_name="songs"):
            raise HTTPException(status_code=404, detail="Index not found")
        query = {
            "query": {
                "multi_match": {
                    "query": input.input,
                    "type": "best_fields",
                    "fields": ["title^4", "artist_name^3", "genre_name^2", "album_name"],
                    "fuzziness": "auto",
                    
                }
                
            },
            "explain": True,
        }
        result = index_search(index_name="songs", query=query, size=10)
        hits = result.get("hits", {}).get("hits", [])
        return hits

    except Exception as e:
        handle_generic_error(e)
