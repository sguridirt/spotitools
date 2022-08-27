import os
import spotipy


def authorize_spotify():
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


def chunkated(l, size):
    """Create a generator with chunks of specified length for a given list.

    Args:
        l (list): the list to be split in chunks.
        size (int): the lenght of each chunk. The last chunk may have a different size.

    Returns:
        Iterator: the generator which contains every chunk of the split list.
    """

    return (l[i : i + size] for i in range(0, len(l), size))


def get_track_sorting_key(track):
    """Get the sorting key for a track.
    Tracks are sorted primarly by release date. In case of collisions, the
    relevant keys are the album name, the artist's name and the track name.

    Args:
        track (dict): the track, as per the Spotipy documentation.

    Returns:
        str:  the sorting key for the given track.
    """
    release_date = track["track"]["album"]["release_date"]
    artist_name = track["track"]["artists"][0]["name"]
    album_name = track["track"]["album"]["release_date"]
    track_name = track["track"]["name"]

    return f"{release_date} | {album_name} | {artist_name} | {track_name}"


def get_tracks(sp, playlist_id, fields):
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


def add_tracks(sp, username, playlist_id, tracks):
    """Add a list of tracks to a specified playlist. The user must have edit access to that playlist.

    Args:
        sp (spotipy.Spotify): spotipy.Spotify session.
        username (str): the username of the owner of the playlist to which the tracks will be added.
        playlist_id (str): the id of the playlist to which the tracks will be added.
        tracks (list[str]): the list of track ids that will be added to the playlist.
    """
    track_ids = [t["track"]["id"] for t in tracks]

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


def sort_playlist_by_release(sp, username, playlist_id, reverse=False, inplace=False):
    """Sort a playlist by release date of tracks, from old to new.

    Args:
        sp (spotipy.Spotify): spotipy.Spotify sessions.
        username (str): the username of the account which will have the sorted playlist.
        playlist_id (str): the id of the playlist to sort.
        reverse (bool, optional): option to sort the tracks from new to old. Defaults to False.
        inplace (bool, optional): option to sort the tracks and replace them in the original playlist. Defaults to False, which will create a copy of the original playlist.
    """
    tracks = get_tracks(
        sp,
        playlist_id,
        "items.track(id,name,album(name,release_date),artists(name))",
    )
    tracks = sorted(tracks, key=get_track_sorting_key, reverse=reverse)

    if inplace:
        delete_tracks(sp, playlist_id, tracks)
        add_tracks(sp, username, playlist_id, tracks)
    else:
        new_playlist = sp.user_playlist_create(
            username, "sorted playlist", public=False
        )
        add_tracks(sp, username, new_playlist["id"], tracks)


def run():
    token, username = authorize_spotify()
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sort_playlist_by_release(sp, username, "[some_playlist_id]", inplace=True)


if __name__ == "__main__":
    run()
