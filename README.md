# spotitools

```text

  ┌─┐┌─┐┌─┐┌┬┐┬┌┬┐┌─┐┌─┐┬  ┌─┐
♪ └─┐├─┘│ │ │ │ │ │ ││ ││  └─┐ ♪
  └─┘┴  └─┘ ┴ ┴ ┴ └─┘└─┘┴─┘└─┘

```

A CLI to automate some tasks in Spotify. Currently, it can

- [x] Sort playlist by date.
- [x] **Extend playlist**: create a copy of a selected playlist, and keep track of its newly added tracks to update the playlist copy. The copy can be edited without restrictions.

It would be ideal to run this tool in a server 24/7, automatically sorting new entries in playlists and updating extended playlists. But this requires much more maintenance and increases the complexity to unwanted levels for the amount of use that it gets. For now, it is better to run it manually.

## Running

In its current state, the program needs the logging info of the user with access to the [Spotify API](https://developer.spotify.com/documentation/web-api/) as environment variables. It requires

- SPOTIFY_USERNAME
- SPOTIFY_REDIRECT_URI
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET

To run,

1. Create a .env file with the environment variables.

2. Activate the enviroment: `source venv/bin/activate && set -a; source .env; set +a`. This assumes the program is running in a python env.

3. Run `python main.py`, and hope for the best.
