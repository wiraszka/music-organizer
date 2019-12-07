# Cleans up audio file names and tags
import os
import mutagen
import json
from mutagen import MutagenError
from mutagen.mp3 import MP3

# Specify directory where audio files are located
root = "C:/Users/Adam/Desktop/Projects/music/sample-music"
all_tags = []

def get_tags(filename, song):
# Retrieves relevant file tags, then puts them in list
    tags = {
        'artist' : '',
        'title' : '',
        'remixed_by' : '',
        'featuring' : '',
        'album' : '',
        'genre' : '',
        'bpm' : '',
        'duration' : '',
        'bitrate' : '',
        }
    info = mutagen.File(filename, easy=True)
    for key in tags.keys():
        if key in info.keys():
            tags[key] = info.get(key)[0]
        if key not in info.keys():
            tags[key] = "None"
# Get song duration and bitrate using MP3 module
    extra_info = MP3(filename)
    tags['duration'] = extra_info.info.length
    tags['bitrate'] = extra_info.info.bitrate

    all_tags.append(tags)
    return all_tags, tags

def format_file(all_tags):
    for tags in all_tags:
        if 'feat.' or 'feat' or 'ft' or 'ft.' in tags['title']:
            tags['title'] = tags['title'].replace(('feat.' or 'feat' or 'ft' or 'ft.'), 'Feat.')
        else:
            pass
        #print(tags)
    return all_tags

def create_json(all_tags):
    j = json.dumps(all_tags, indent=2)
    print(j)
    with open('C:/Users/Adam/Desktop/Projects/music/songs.txt','w') as songs:
        songs.write(j)
    return j



for song in os.listdir(root):
    if song.endswith((".mp3",".m4a",".flac",".alac")):
        try:
            filename = root + "/" + song
            get_tags(filename, song)
        except MutagenError:
            print("error")
#format_file(all_tags)
create_json(all_tags)
