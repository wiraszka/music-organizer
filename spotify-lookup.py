import os
import sys
import json
import pprint
import requests
import urllib.request
import spotipy
import spotipy.util as util
from spotipy import oauth2
from json.decoder import JSONDecodeError
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET


txt = 'C:/Users/Adam/Desktop/Projects/music/songs.txt'

## AUTHENTICATION USING OAUTH
# Client_key and Secret_key saved in config.py for security purposes
token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)

# Get access token
cache_token = token.get_access_token()
spotify = spotipy.Spotify(cache_token)


def check_json(txt):
# Open txt file and check json containing song info
    with open(txt, 'r') as j:
        contents = j.read()
        if len(contents) < 1:
            print('txt file does not exist or in wrong directory')
        else:
            print(contents)
        return contents

def dl_album_cover(album_cover):
    filename = 'img{}.png'.format(i)
    print(filename)
    response = urllib.request.urlretrieve(album_cover, filename)
    if response.status_code == 200:
        try:
            album_dump = 'C:/Users/Adam/Desktop/Projects/music/album-dump/'
            with open(album_dump, 'wb') as f:
                f.write(response.content)
        except:
            print('Could not download image')
    else:
        print('Server error')
    return filename

def sp_search(txt):
# Open and read json file containing song names
    with open(txt, 'r') as j:
        all_songs = json.loads(j.read())
        for song in all_songs:
            search_str = song['artist'] + ' ' + song['title']
# Search for song (search_string) using spotify API
            print('Searching for...', search_str)
            result = spotify.search(search_str)
            #pprint.pprint(result)
# Check if search unsuccessful
            if len(result['tracks']['items']) < 1:
                print('Search query failed for:', search_str)
# If unsuccessful, create new search string and try again
                search_str = song['title']
                print('New search string is:', search_str)
                result = spotify.search(search_str)
            else:
                print('search successful')

# If successful, call album_cover_download function to dl album art
            try:
                album_cover = result['tracks']['items'][0]['album']['images'][0]['url']
                print('Image link is:', album_cover)
                dl_album_cover(album_cover)
            except:
                album_cover = ""
                print("image indexing error for:", search_str)
                #pprint.pprint(result)

    return search_str, album_cover


check_json(txt)
start(txt)
sp_search(txt)
