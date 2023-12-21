from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete")
    song_ratings = relationship(
        "SongRating", back_populates="user", cascade="all, delete"
    )


class Artist(Base):
    __tablename__ = "artists"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    songs = relationship("Song", back_populates="artist", cascade="all, delete")
    albums = relationship("Album", back_populates="artist", cascade="all, delete")


class Genre(Base):
    __tablename__ = "genres"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    songs = relationship("Song", back_populates="genre", cascade="all, delete")


class Album(Base):
    __tablename__ = "albums"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    artist_id = Column(String, ForeignKey("artists.id", ondelete="CASCADE"))
    artist = relationship("Artist", back_populates="albums", cascade="all, delete")
    songs = relationship("Song", back_populates="album", cascade="all, delete")


class Song(Base):
    __tablename__ = "songs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    artist_id = Column(String, ForeignKey("artists.id", ondelete="CASCADE"))
    genre_id = Column(String, ForeignKey("genres.id", ondelete="CASCADE"))
    album_id = Column(String, ForeignKey("albums.id", ondelete="CASCADE"))
    artist = relationship("Artist", back_populates="songs")
    genre = relationship("Genre", back_populates="songs")
    album = relationship("Album", back_populates="songs")
    ratings = relationship("SongRating", back_populates="song")
    playlists = relationship("PlaylistSong", back_populates="song")


class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="playlists")
    songs = relationship(
        "PlaylistSong", back_populates="playlist", cascade="all, delete"
    )


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    song_id = Column(String, ForeignKey("songs.id", ondelete="CASCADE"))
    playlist_id = Column(String, ForeignKey("playlists.id", ondelete="CASCADE"))
    playlist = relationship("Playlist", back_populates="songs")
    song = relationship("Song", back_populates="playlists")


class SongRating(Base):
    __tablename__ = "song_ratings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    song_id = Column(String, ForeignKey("songs.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="song_ratings")
    song = relationship("Song", back_populates="ratings")
    rating = Column(Integer)


class SongShare(Base):
    __tablename__ = "song_shares"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    song_id = Column(String, ForeignKey("songs.id", ondelete="CASCADE"))
