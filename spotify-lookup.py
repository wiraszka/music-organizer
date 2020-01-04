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

def gen_search_str(song,try_number):
    print('Attempt',try_number)
    global search_str
    if try_number == 1:
        if song['mix'] != 'None':
            search_str = song['artist'] + ' ' + song['title'] + ' ' + song['mix']
            print(search_str)
            return search_str
        else:
            search_str = song['artist'] + ' ' + song['title']
            print(search_str)
            return search_str
    if try_number == 2:
        if song['mix'] != 'None':
            search_str = song['title'] + ' ' + song['mix']
            return search_str
        else:
            search_str = song['title']
            return search_str
    elif try_number == 3:
        search_str = song['artist']
        return search_str


# Initial sanity check
check_json(txt)
# Open and read json file containing song names
with open(txt, 'r') as j:
    all_songs = json.loads(j.read())
    for song in all_songs:
# Generate search string
        try_number = 1
        gen_search_str(song,try_number)
# Search for song (search string) using spotify API
        print('Searching for...', search_str)
        result = spotify.search(search_str)
        #pprint.pprint(result)
# Check if search unsuccessful
        while len(result['tracks']['items']) < 1:
            print('Search query failed for:', search_str)
# If unsuccessful, generate new search string and try again
            try_number = try_number + 1
            gen_search_str(song,try_number)
            print('New search string is:', search_str)
            result = spotify.search(search_str)
            if try_number == 3:
                pass
        if len(result['tracks']['items']) > 0:
            print('search successful')

# If successful, call album_cover_download function to dl album art
        try:
            album_cover = result['tracks']['items'][0]['album']['images'][0]['url']
            print('Image link is:', album_cover)
            dl_album_cover(album_cover)
        except:
            album_cover = ""
            print("Image indexing error for:", search_str)
            #pprint.pprint(result)
