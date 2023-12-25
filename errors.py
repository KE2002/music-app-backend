from fastapi import HTTPException

def handle_error_500(message):
    return HTTPException(status_code=status_code, ) 