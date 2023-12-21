# build a schema using pydantic
from pydantic import BaseModel
from typing import Optional, List


class User(BaseModel):
    username: str
    password_hash: str

    class Config:
        orm_mode = True


class UserDetails(BaseModel):
    username: str
    id: str

    class Config:
        orm_mode = True


class Artist(BaseModel):
    name: str
    id: str

    class Config:
        orm_mode = True


class Genre(BaseModel):
    name: str
    id: str

    class Config:
        orm_mode = True


class Album(BaseModel):
    title: str
    id: str

    class Config:
        orm_mode = True


class Song(BaseModel):
    title: str
    artist_id: str
    genre_id: str
    album_id: str

    class Config:
        orm_mode = True


class Playlist(BaseModel):
    name: str
    id: str
    user: UserDetails

    class Config:
        orm_mode = True


class SongList(BaseModel):
    id: str
    title: str
    artist: Artist
    genre: Genre
    album: Album

    class Config:
        orm_mode = True


class PlaylistSong(BaseModel):
    song: SongList

    class Config:
        orm_mode = True


class SongRating(BaseModel):
    rating: int
    id: str

    class Config:
        orm_mode = True


class PlayListDetails(BaseModel):
    id: str
    name: str
    user: UserDetails
    songs: List[PlaylistSong]

    class Config:
        orm_mode = True


class CreatePlaylist(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CuratePlaylist(BaseModel):
    name: str
    genre_ids: Optional[List[str]] = None
    artist_ids: List[str]
    album_ids: Optional[List[str]] = None

    class Config:
        orm_mode = True


class Share(BaseModel):
    to_user: str
    song_id: str

    class Config:
        orm_mode = True
        
class Search(BaseModel):
    input: str