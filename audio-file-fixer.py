# Cleans up audio file names and tags
import os
import mutagen
import re
import json
from mutagen import MutagenError
from mutagen.mp3 import MP3

# Specify directory where audio files are located
root = "C:/Users/Adam/Desktop/Projects/music/sample-music-test"
all_tags = []

def get_tags(filename, song):
# Retrieves relevant file tags for each song, then puts them in dict with the following keys:
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
# Create list containing all songs and tags
    all_tags.append(tags)
    return all_tags, tags

def format_title(all_tags):
# If title tag contains 'artist' and 'title' info
# Or if all info in filename instead of tags
    return all_tags
    pass

def format_bracket_contents(all_tags):
    for tags in all_tags:
# check number of items contained in title tag
        print('formatting brackets for:',tags['title'])
        if len(tags['title']) < 1:
            print('Error - song title field empty')
            break
        elif len(tags['title']) == 1:
            print('unaffected.')
            continue
        elif len(tags['title']) == 2:
            print('brackets found.')
# Check title field for featured artist, then do some formatting
            if not tags['title'][1].startswith('Feat' or 'feat' or 'Ft'):
                continue
            else:
                tags['title'][1] = tags['title'][1].replace(('Featuring' or 'Feat' or 'feat.' or 'feat' or 'ft.'), '')
                tags['featuring'] = tags['title'][1].replace(')','')
                if len(tags['title']) > 2:
                    print('noooooooooo, spliced too many things!', tags['title'])
                tags['title'] = tags['title'][0].rstrip()
                print('featured artist found!')
                print('new song title:',tags['title'])
                print('featuring:', tags['featuring'])
# If featuring artist exists, add info to 'featuring' tag


        elif len(tags['title']) > 2:
            continue


def extra():
    split = []
    print('blah')
    if len(split) > 1:
        tags['title'] = split[0].rstrip()
        print('song title is now:', tags['title'])
        if tags['title'][1].find('Remix'):
            print('Remix found in title')
            tags['remixed_by'] = split[1].replace(')','')
            print('remixed_by field is now:',tags['remixed_by'])
        else:
            print('final song name:', tags['title'])
            print('featuring...',tags['featuring'])
    else:
        pass


def check_brackets(all_tags):
# Converts all bracket types to () in title tag
    for tags in all_tags:
        tags['title'] = tags['title'].replace('[', '(').replace(']', ')')
        print(tags['title'])
# Formats 'featured artist' identifier if found in title tag
        for b in ['(Featuring', '(featuring', '(Feat', '(feat', '(Ft', '(ft']:
            if b in tags['title']:
                print('contains bracketed feat')
                break
            else:
                print('does not contain bracketed feat')
                for c in ['featuring', 'feat', 'ft']:
                    if c in tags['title']:
                        tags['title'] = tags['title'].replace(c, '(Feat')
                        print('replaced:', tags['title'])
                    else:
                        break
# Checks if song contains brackets, returns spliced title tag
        if '(' not in tags['title']:
            continue
        else:
            print('() found in title tag, Sliced!')
            spliced = tags['title'].split('(')
            print(spliced)
            if len(spliced) == 1:
                tags['title'] = spliced
                print('song not spliced')
            elif len(spliced) == 2:
                tags['title'] = spliced
                print('spliced once:', tags['title'])
            elif len(spliced) > 2:
                tags['title'] = spliced
                print('SPLICED 2 OR MORE TIMES!!!')
            else:
                print('something bad happened')
    print(all_tags)
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
format_title(all_tags)
check_brackets(all_tags)
format_bracket_contents(all_tags)
create_json(all_tags)
