from fastapi import HTTPException, status
from elasticsearch import exceptions as es_exceptions
from sqlalchemy.exc import SQLAlchemyError


def handle_http_exception(e):
    raise e


def handle_generic_error(e):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
    )


def handle_not_found():
    raise HTTPException(status_code=404, detail="Not Found")


def handle_bad_request():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data Exists")


def handle_forbidden():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Allowed")


def handle_unauth():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
    )
