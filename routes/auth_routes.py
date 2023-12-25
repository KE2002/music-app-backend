from fastapi import APIRouter, Depends, HTTPException, FastAPI
from jose import JWTError, jwt
from datetime import timedelta
from schema import *
from sqlalchemy.orm import Session
from configurations import *
import models as Models
from error_handler import *

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(user: User):
    """
    Endpoint for user login.

    Parameters:
    - `user`: The user credentials (username and password) for authentication.

    Returns:
    - A dictionary containing the access token, user ID, and username upon successful login.
    """
    user_found = (
        session.query(Models.User).filter(Models.User.username == user.username).first()
    )

    if user_found is None or not pwd_context.verify(
        user.password_hash, user_found.password_hash
    ):
        handle_unauth()

    access_token_expires = timedelta(minutes=30)
    access_token = access_token_generate({"sub": user_found.id}, access_token_expires)
    return {
        "access_token": access_token,
        "user_id": user_found.id,
        "user_name": user_found.username,
    }


@router.post("/signUp")
async def sign_up(user: User):
    """
    Endpoint for user registration.

    Parameters:
    - `user`: The user information (username and password) for registration.

    Returns:
    - A dictionary indicating successful user creation and the user ID.
    """
    user_found = (
        session.query(Models.User).filter(Models.User.username == user.username).all()
    )
    if user_found:
        handle_bad_request()

    new_user = Models.User(
        username=user.username, password_hash=pwd_context.hash(user.password_hash)
    )
    session.add(new_user)
    session.commit()
    session.close()
    return {
        "detail": "User Created",
        "userId": session.query(Models.User)
        .filter(Models.User.username == user.username)
        .first()
        .id,
    }
