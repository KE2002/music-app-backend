import io
from configurations import *
from typing import List
from schema import *
import models as Models
from fastapi import APIRouter
import pandas as pd
from sqlalchemy import func

router = APIRouter(tags=["Populate Database"])


@app.post("/populateDatabase")
async def populate_tables(file: UploadFile = File(...)):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    for row in range(len(df)):
        artist = (
            session.query(Models.Artist)
            .filter_by(name=df.iloc[row].to_dict()["artist"])
            .first()
        )
        if not artist:
            artist = Models.Artist(name=df.iloc[row].to_dict()["artist"])
            session.add(artist)
        genre = (
            session.query(Models.Genre)
            .filter_by(name=df.iloc[row].to_dict()["genre"])
            .first()
        )
        if not genre:
            genre = Models.Genre(name=df.iloc[row].to_dict()["genre"])
            session.add(genre)
        album = (
            session.query(Models.Album)
            .filter_by(title=df.iloc[row].to_dict()["album"])
            .first()
        )
        if not album:
            album = Models.Album(
                title=df.iloc[row].to_dict()["album"], artist_id=artist.id
            )
            session.add(album)
        session.commit()
        print(album.id)
        song = Models.Song(
            title=df.iloc[row].to_dict()["title"],
            artist_id=artist.id,
            genre_id=genre.id,
            album_id=album.id,
        )
        session.add(song)
    session.commit()
    return {"message": "Database populated successfully"}


@app.post("/populate_elastic", response_model=List[SongList])
async def populate_tables():
    if not es.indices.exists(index="songs"):
        es.indices.create(
            index="songs",
            body={
                "mappings": {
                    "properties": {
                        "_score": {"type": "float", "store": True},
                        "id": {"type": "keyword"},
                        "artist_id": {"type": "keyword"},
                        "genre_id": {"type": "keyword"},
                        "album_id": {"type": "keyword"},
                        "total_ratings": {"type": "float"},
                    }
                },
            },
        )

    songs_query = session.query(Models.Song).all()
    for item in songs_query:
        tot_rating = (
            session.query(func.round(func.avg(Models.SongRating.rating), 2))
            .filter(Models.SongRating.song_id == item.id)
            .scalar()
        )

        it = {
            "id": item.id,
            "title": item.title,
            "artist_name": item.artist.name,
            "artist_id": item.artist.id,
            "genre_name": item.genre.name,
            "genre_id": item.genre.id,
            "album_name": item.album.title,
            "album_id": item.album.id,
            "total_ratings": 0.00 if not tot_rating else tot_rating,
        }
        es.index(index="songs", body=it, id=item.id)
    if not es.indices.exists(index="playlist-info"):
        es.indices.create(index="playlist-info")
    return songs_query


@app.post("/playlistES", response_model=List[PlayListDetails])
async def display_all_playlist():
    all_playlist = session.query(Models.Playlist).all()
    # return all_playlist
    playlist_dicts = []

    for playlist in all_playlist:
        playlist_data = {
            "id": playlist.id,
            "name": playlist.name,
            "user": playlist.user.id,
            "songs": [],
        }
        playlist_data["songs"] = []
        if playlist.songs:
            for s in playlist.songs:
                playlist_data["songs"].append(
                    s.song.id,
                )

        playlist_dicts.append(playlist_data)
    for playlist_data in playlist_dicts:
        print(playlist_data)
        es.index(index="playlist-info", body=playlist_data, id=playlist_data["id"])
    return all_playlist


@app.delete("/deleteTable")
async def delete_table():
    delete_statement = delete(Models.PlaylistSong).where(True)
    session.execute(delete_statement)
    session.commit()
    session.close()
