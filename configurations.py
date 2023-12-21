from fastapi import FastAPI, status, HTTPException, Depends, UploadFile, File
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import DBSessionMiddleware
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from jose import JWTError, jwt
from elasticsearch import Elasticsearch
import models as Models
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(".env")
app = FastAPI()
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
engine = create_engine(os.environ["DATABASE_URI"])
session = Session(engine)
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URI"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ELASTICSEARCH_URL = "https://localhost:9200"

es = Elasticsearch(
    hosts=ELASTICSEARCH_URL,
    basic_auth=("elastic", "wPc_9KpUMnW0l=9wv-P8"),
    verify_certs=False,
)


def access_token_generate(usr: dict, expiry_time: timedelta):
    to_encode = usr.copy()
    if expiry_time:
        expire = datetime.utcnow() + expiry_time
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userUUID: str = payload.get("sub")
        if userUUID is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return userUUID


def active_user(current_user: str = Depends(verify_token)):
    return {
        "user": session.query(Models.User)
        .filter(Models.User.id == current_user)
        .first()
    }
