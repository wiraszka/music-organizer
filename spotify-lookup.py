import os
import sys
import json
import pprint
import spotipy
import spotipy.util as util
from spotipy import oauth2
from bottle import route, run, request
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


txt = 'C:/Users/Adam/Desktop/Projects/music/songs.txt'

def sanity_check(txt):
# Open and read json file containing song info
    with open(txt, 'r') as j:
        contents = j.read()
        print(contents)
        return contents


# AUTHENTICATION USING OAUTH
# Client_key and Secret_key saved in config.py for security purposes
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

# Get access token
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)



def sp_search(txt,spotify):
# Isolate search_string from json file
    with open(txt, 'r') as j:
        all_songs = json.loads(j.read())
        for song in all_songs:
            search_str = song['artist'] + ' ' + song['title']
            print(search_str)
# Search for song (search_string) using spotify API
            result = spotify.search(search_str)
            pprint.pprint(result)
    return search_str

sanity_check(txt)
sp_search(txt,spotify)
