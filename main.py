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
    return token


def sort_playlist():
    pass


def run():
    token = authorize_spotify()
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False

        sort_playlist()


if __name__ == "__main__":
    run()
