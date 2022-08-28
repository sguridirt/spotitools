import spotipy
import inquirer
from yaspin import yaspin

from sp_utils import authorize_spotify, get_playlist_tracks, add_tracks, delete_tracks


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


def sort_playlist_by_release(sp, username, playlist_id, reverse=False, inplace=False):
    """Sort a playlist by release date of tracks, from old to new.

    Args:
        sp (spotipy.Spotify): spotipy.Spotify sessions.
        username (str): the username of the account which will have the sorted playlist.
        playlist_id (str): the id of the playlist to sort.
        reverse (bool, optional): option to sort the tracks from new (top of playlist) to old. Defaults to False.
        inplace (bool, optional): option to sort the tracks and replace them in the original playlist. Defaults to False, which will create a copy of the original playlist.
    """
    original_playlist_name = sp.playlist(playlist_id, fields="name")
    tracks = get_playlist_tracks(
        sp,
        playlist_id,
        "items.track(id,name,album(name,release_date),artists(name))",
    )
    tracks = sorted(tracks, key=get_track_sorting_key, reverse=reverse)

    if inplace:
        delete_tracks(sp, playlist_id, tracks)
        add_tracks(sp, username, playlist_id, tracks)
        sp.playlist_change_details(
            playlist_id,
            name=f"{original_playlist_name['name']}",
            description="delicadamente ordenada por fecha «para más placer 🤌».",
        )
    else:
        new_playlist = sp.user_playlist_create(
            username, original_playlist_name["name"], public=False
        )
        add_tracks(sp, username, new_playlist["id"], tracks)
        sp.playlist_change_details(
            new_playlist["id"],
            description="delicadamente ordenada por fecha «para más placer 🤌».",
        )


# TODO: parse command 'extend'
# TODO: parse command 'sort'
# TODO: parse command 'help'


def ask_sort_info():
    """Ask user information and options to sort the playlist.

    Returns:
        dict[str]: dictionary with info and options.
    """
    questions = [
        inquirer.Text(name="plid", message="Enter the id of the playlist to sort"),
        inquirer.List(
            name="inplace",
            message="Do you want to do the sorting in place or create a sorted copy of the playlist?",
            choices=["Copy sort", "Sort in place"],
        ),
        inquirer.List(
            name="order",
            message="Oldest to newest or newest to oldest?",
            choices=[
                "Newest (top) to oldest (bottom)",
                "Oldest (top) to newest (bottom)",
            ],
        ),
        inquirer.Confirm(
            name="confirm_sort",
            message="Confirm? This action cannot be undone.",
            default=False,
        ),
    ]

    return inquirer.prompt(questions, theme=inquirer.themes.GreenPassion())


def run():
    print("\nSpotitools!\n")
    token, username = authorize_spotify()
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        options = ask_sort_info()
        with yaspin(text="Sorting your playlist..."):
            sort_playlist_by_release(
                sp,
                username,
                playlist_id=options["plid"],
                inplace=options["inplace"] == "Sort in place",
                reverse=options["order"] == "Newest (top) to oldest (bottom)",
            )
        print("Your playlist has been sorted!")
    else:
        pass


if __name__ == "__main__":
    run()
