import os

from sp_utils import get_playlist_tracks, add_tracks


def save_tracks_on_file(filepath, track_ids):
    with open(filepath, "w+") as file:
        for track_id in track_ids:
            file.write(track_id + " \n")


def read_tracks_from_file(filepath):
    with open(filepath, "r") as f:
        for track_id in f:
            yield track_id.strip()


def extract_track_ids(tracks):
    for track in tracks:
        yield track["track"]["id"]


def extend_playlist(spotify, username, tracked_pl_id, new_pl_name):
    """Create a new playlist with songs from specified playlist. Save to db."""

    new_playlist = spotify.user_playlist_create(username, new_pl_name)
    tracks = get_playlist_tracks(
        spotify, tracked_pl_id, "items.track(id,name,duration_ms)"
    )
    add_tracks(
        sp=spotify,
        username=username,
        playlist_id=new_playlist["id"],
        track_ids=[t["track"]["id"] for t in tracks],
    )

    db_name = f'{new_playlist["id"]}'
    os.mkdir(f"db/{db_name}")

    save_tracks_on_file(
        filepath=f"db/{db_name}/tracks.txt",
        track_ids=extract_track_ids(
            get_playlist_tracks(spotify, tracked_pl_id, "items.track(id)")
        ),
    )


def update_extended_playlist(spotify, username, tracked_pl_id, extended_pl_id):
    """Track new songs from playlist and add them to extended playlist.

    Arguments:
        spotify {spotipy.Spotify} -- Spotify object in charge of making the calls.
        tracked_pl_id {string} -- Spotify playlist id to copy songs from
        extended_pl_id {string} -- Spotify playlist id to copy new songs to
    """
    reference_playlist = get_playlist_tracks(spotify, tracked_pl_id, "items.track.id")
    reference_playlist_ids = set(extract_track_ids(reference_playlist))

    updating_playlist = get_playlist_tracks(spotify, extended_pl_id, "items.track.id")
    updating_playlist_ids = set(extract_track_ids(updating_playlist))

    alltime_playlist_ids = set(read_tracks_from_file(f"db/{extended_pl_id}/tracks.txt"))

    deleted_tracks = alltime_playlist_ids - updating_playlist_ids
    new_track_ids = reference_playlist_ids - updating_playlist_ids - deleted_tracks

    if new_track_ids:
        add_tracks(spotify, username, extended_pl_id, list(new_track_ids))
        print("New tracks added to playlist!")
        print(new_track_ids, "\n")
        save_tracks_on_file(
            f"db/{extended_pl_id}/tracks.txt",
            (alltime_playlist_ids | updating_playlist_ids | new_track_ids),
        )
