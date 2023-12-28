
from configurations import *
from routes import (
    auth_routes,
    playlist_routes,
    populate_routes,
    recommendation_routes,
    search_routes,
    songs_routes

)

Models.Base.metadata.create_all(engine)

app.include_router(auth_routes.router)
app.include_router(songs_routes.router)
app.include_router(playlist_routes.router)
app.include_router(search_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(populate_routes.router)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
