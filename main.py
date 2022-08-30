import spotipy
import inquirer
from yaspin import yaspin

from playlist_sort import sort_playlist_by_release
from playlist_extend import extend_playlist, update_extended_playlist
from sp_utils import authorize_spotify


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

    return inquirer.prompt(questions)


def run():
    print()
    print("┌─┐┌─┐┌─┐┌┬┐┬┌┬┐┌─┐┌─┐┬  ┌─┐ ")
    print("└─┐├─┘│ │ │ │ │ │ ││ ││  └─┐ ")
    print("└─┘┴  └─┘ ┴ ┴ ┴ └─┘└─┘┴─┘└─┘•")
    print()

    print(
        "Spotitools needs your authorization to work with your library.\nTo authorize it, spotitools will ask your username and then direct you to the Spotify log in. Spotitools won't know your password."
    )

    username = inquirer.text("Enter your Spotify username: ")

    token, username = authorize_spotify(username)
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False

        action = inquirer.list_input(
            "What do you want to do?",
            choices=["Sort playlist", "Extend/Update extended playlist"],
        )
        if action == "Sort playlist":
            options = ask_sort_info()
            with yaspin(text="Sorting your playlist..."):
                sort_playlist_by_release(
                    sp,
                    username,
                    playlist_id=options["plid"],
                    inplace=options["inplace"] == "Sort in place",
                    reverse=options["order"] == "Newest (top) to oldest (bottom)",
                )
        elif action == "Extend/Update extended playlist":
            action = inquirer.list_input(
                "Do you want to extend a playlist or update an extended playlist?",
                choices=["Extend new playlist", "Update extended playlist"],
            )
            if action == "Extend new playlist":
                questions = [
                    inquirer.Text(
                        name="tracked_plid",
                        message="Enter the id of the playlist to track",
                    ),
                    inquirer.Text(
                        name="new_pl_name",
                        message="Enter the new playlist name",
                    ),
                ]
                options = inquirer.prompt(questions)
                with yaspin(text="Extending your playlist..."):
                    extend_playlist(
                        sp, username, options["tracked_plid"], options["new_pl_name"]
                    )
            elif action == "Update extended playlist":
                questions = [
                    inquirer.Text(
                        name="tracked_plid",
                        message="Please, enter the tracked playlist id",
                    ),
                    inquirer.Text(
                        name="plid",
                        message="Please, enter the id of the playlist to be updated",
                    ),
                ]
                options = inquirer.prompt(questions)
                with yaspin(text="Updating your playlist..."):
                    update_extended_playlist(
                        sp, username, options["tracked_plid"], options["plid"]
                    )

    print("Done! Thanks for using spotitools.\n")


if __name__ == "__main__":
    run()
