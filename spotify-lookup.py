import os
import sys
import json
import spotipy
import spotipy.util as util
from spotipy import oauth2
from bottle import route, run, request
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

# Open json file containing song info
file = 'C:/Users/Adam/Desktop/Projects/music/songs.txt'
with open(file, 'r') as j:
    contents = j.read()
    print(contents)

# User_id and playlist_id:
# Client_key and Secret_key saved in config.py for security purposes
USER = 'spotify:user:wiraadam'
PLAY_LIST = 'spotify:playlist:03z1YorF0FYtEpdfGKJ54n'

#Authentication through OAuth
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

# Get access token
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)

results1 = spotify.user_playlist_tracks(USER, PLAY_LIST, limit=100, offset=0)
print(dir(spotipy.Spotify()))
