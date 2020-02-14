import os
import json
from itunesLibrary import library

path = ("C:/Users/Adam/Desktop/Projects/music/music-organizer/iTunes Music Library.xml")

# must first parse...
lib = library.parse(path)

print(len(lib))    # number of items stored

musicItems = set(lib.getPlaylist("Music").items)
library = []
for item in musicItems:
    song = {}
    song['track'] = item.title
    song['artist'] = item.artist
    #song['location'] = item.filename
    library.append(song)

with open('itunes_lib.txt', 'w') as itunes_lib:
    library = json.dumps(library, indent=2)
    itunes_lib.write(library)
#for playlist in lib.playlists:
    #print(playlist)
    #for item in playlist.items:
        #print(item)          # perform function on each item in the playlist

# get a single playlist
#playlist = lib.getPlaylist("3*")
#for item in playlist

# get a list of all of the David Bowie songs
#bowie_items = lib.getItemsForArtist("David Bowie")
