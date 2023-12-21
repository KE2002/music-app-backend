# Introduction

Basic music application to handle songs collection and playlist creation. users can rate a song, share a song to another user. Song recommendation based on user's playlist and full text search

#
#### Schema Diagram 
https://drawsql.app/teams/core_dumped-1/diagrams/music-app
#
## Endpoints

### <span style="font-family:consolas;"><span style="color:yellow">POST</span> /login</span>

    Endpoint for user login.
    Parameters:
    - `user`: The user credentials (username and password) for authentication.

    Returns:
    - A dictionary containing the access token, user ID, and username upon successful login.

#

### <span style="font-family:consolas;"><span style="color:yellow">POST</span> /signUp</span>

    Endpoint for user registration.

    Parameters:
    - user: The user information (username and password) for registration.

    Returns:
    - A dictionary indicating successful user creation and the user ID.


#

### <span style="font-family:consolas;"><span style="color:green">GET</span> /playlistSongs/<span style="color:orange">{pId}</span></span>

    Retrieve details of a playlist, including its songs.

    Parameters:
    - `pId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - Details of the playlist, including its songs.

#

### <span style="font-family:consolas;"><span style="color:green">GET</span> /displayUserPlaylistES</span>

    Display playlists using Elasticsearch for the current user.

    Parameters:
    - `current_user`: Dependency to get the current user.

    Returns:
    - A generator yielding playlist information from Elasticsearch.
    """

#

### <span style="font-family:consolas;"><span style="color:green">GET</span> /playlistSongsES/<span style="color:orange">{pId}</span></span>

    Display songs from a playlist using Elasticsearch.

    Parameters:
    - `pId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - Songs from the specified playlist.

#

### <span style="font-family:consolas;"><span style="color:yellow">POST</span> /createPlaylist</span>

    Create a new playlist for the current user.

    Parameters:
    - `plist`: Playlist name.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A success message indicating the playlist creation.

#

### <span style="font-family:consolas;"><span style="color:violet">PATCH</span> /addSongs/playlist</span>

    Add songs to a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `sId`: Song ID.

    Returns:
    - A message indicating successful addition of the song to the playlist.

#

### <span style="font-family:consolas;"><span style="font-family:consolas;"><span style="color:blue">PUT</span> /deleteSong/playlist</span>

    Remove a song from a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `sId`: Song ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful removal of the song from the playlist.

#

### <span style="font-family:consolas;"><span style="color:red">DELETE</span> /deletePlaylist/<span style="color:orange">{playlistId}</span></span>

    Delete a playlist.

    Parameters:
    - `playlistId`: Playlist ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful deletion of the playlist.

#

### <span style="font-family:consolas;"><span style="color:green">GET</span> /curatePlaylist</span>

    Curate a playlist based on specified criteria.

    Parameters:
    - `playlist_details`: Details for curating the playlist includes playlist name, genre_id, artist_id and album_id.

    - `current_user`: Dependency to get the current user.

    Returns:
    - List of songs curated based on the specified criteria.

#

### <span style="font-family:consolas;"><span style="color:green">GET</span> /songRecommendationES</span>

    Get song recommendations for the current user based on their playlists.

    Parameters:
    - `current_user`: Dependency to get the current user.

    Returns:
    - A list of recommended songs based on the user's playlists.

#

### <span style="font-family:consolas;"><span style="color:yellow">POST</span> /searchES</span>

    Search for songs in the Elasticsearch index.

    Parameters:
    - `input`: Search input containing the query string.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A list of search hits containing information about the matched songs.

#
### <span style="font-family:consolas;"><span style="color:green">GET</span> /songsES</span>

    Retrieve information about songs from Elasticsearch.

    Returns:
    - A generator yielding information about songs.

#
### <span style="font-family:consolas;"><span style="color:blue">PUT</span> /songRating</span>

    
    Rate a song or update the existing rating.

    Parameters:
    - `rating`: SongRating schema containing song ID and rating.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful rating update or addition.
    
#
### <span style="font-family:consolas;"> <span style="color:yellow">POST</span> /share</span>

    Share a song with another user.

    Parameters:
    - `share_details`: Share schema containing song ID and recipient user ID.
    - `current_user`: Dependency to get the current user.

    Returns:
    - A message indicating successful song sharing.

#
### <span style="font-family:consolas;"><span style="color:green">GET</span> /song/<span style="color:orange">{sId}</span></span>

    Retrieve information about a specific song from Elasticsearch.

    Parameters:
    - `sId`: Song ID.

    Returns:
    - Information about the specified song.
    
