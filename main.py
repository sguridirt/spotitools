import spotipy
import inquirer
from yaspin import yaspin

from playlist_sort import sort_playlist_by_release
from sp_utils import authorize_spotify


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
