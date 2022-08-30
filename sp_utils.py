import os
import spotipy

from utils import chunkated


def authorize_spotify(username=None):
    if not username:
        username = os.environ["SPOTIFY_USERNAME"]
    client_id = os.environ["SPOTIFY_CLIENT_ID"]
    client_secret = os.environ["SPOTIFY_CLIENT_SECRET"]
    redirect_uri = os.environ["SPOTIFY_REDIRECT_URI"]

    scopes = [
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-public",
        "playlist-modify-private",
        "user-library-read",
    ]
    token = spotipy.util.prompt_for_user_token(
        username=username,
        scope=" ".join(scopes),
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
    return token, username


def get_playlist_tracks(sp, playlist_id, fields):
    """Get the tracks from a playlist.

    Args:
        sp (spotipy.Spotify): the Spotify session.
        playlist_id (str): the playlist id to get the tracks from.
        fields (str): the data fields that will be fetched for each track.

    Returns:
        list[dict]: list of tracks with all their data fields.
    """
    all_tracks = []
    count = 0
    while True:
        tracks = sp.playlist_tracks(
            playlist_id=playlist_id, limit=100, offset=count, fields=f"{fields},total"
        )

        all_tracks.extend(tracks["items"])
        count += len(tracks["items"])

        total = tracks["total"]
        if count >= total:
            break

    return all_tracks


def add_tracks(sp, username, playlist_id, track_ids):
    """Add a list of tracks to a specified playlist. The user must have edit access to that playlist.

    Args:
        sp (spotipy.Spotify): spotipy.Spotify session.
        username (str): the username of the owner of the playlist to which the tracks will be added.
        playlist_id (str): the id of the playlist to which the tracks will be added.
        track_ids (list[str]): the list of track ids that will be added to the playlist.
    """

    CHUNK_SIZE = 100
    for ids_chunks in chunkated(track_ids, CHUNK_SIZE):
        sp.user_playlist_add_tracks(username, playlist_id, ids_chunks)


def delete_tracks(sp, playlist_id, tracks):
    """Remove tracks from a playlist. The user must have edit access to that playlist.

    Args:
        sp (spotipy.Spotify): spotipy.Spotify session.
        playlist_id (str): id of the playlist from which the tracks will be deleted.
        tracks (list[str]): list of track ids that will be deleted from the playlist.
    """
    track_ids = [*set([t["track"]["id"] for t in tracks])]

    CHUNK_SIZE = 100
    for ids_chunk in chunkated(track_ids, CHUNK_SIZE):
        sp.playlist_remove_all_occurrences_of_items(playlist_id, ids_chunk)
