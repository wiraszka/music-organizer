# Cleans up audio file names and tags
import os
import mutagen
import re
import json
from mutagen import MutagenError
from mutagen.mp3 import MP3

# Specify directory where audio files are located
#root = "C:/Users/Adam/Documents/Adam's Music"
root = "C:/Users/Adam/Desktop/Projects/music/sample-music-test"
all_tags = []

def get_tags(filename, song):
# Retrieves relevant file tags for each song, then puts them in dict with the following keys:
    tags = {
        'artist' : '',
        'title' : '',
        'mix' : '',
        'featuring' : '',
        'album' : '',
        'genre' : '',
        'extra' : '',
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
    global old_tags
    old_tags = all_tags
    old_tags = json.dumps(old_tags, indent=2)
    with open('C:/Users/Adam/Desktop/Projects/music/original-info.txt','w') as original:
        original.write(old_tags)

    return all_tags, tags, old_tags


def fix_title(all_tags):
# If title tag contains 'artist' and 'title' info
# Or if all info in filename instead of tags
    return all_tags
    pass

def fix_brackets(all_tags):
# Converts all bracket types to () in title tag
    for tags in all_tags:
        tags['title'] = tags['title'].replace('[', '(').replace(']', ')')
        tags['title'] = tags['title'].replace('{', '(').replace('}', ')')
        tags['title'] = tags['title'].replace('"', '')
        print('fixed brackets:', tags['title'])
    return all_tags

def check_featured(all_tags):
# Sanity check
    for tags in all_tags:
        if '**' in tags['title']:
            print('Error - feauted artist identifier ** already present in:', tags['title'])
            continue
        else:
# Checks if a non-bracketed 'featured artist' identifier exists in title tag...
# If yes, adds (* prefix to identifier so it can be processed correctly later
            bracketed = False
            for b in ['(Featuring', '(featuring', '(Feat', '(feat', '(Ft', '(ft']:
                if b in tags['title']:
                    print('contains bracketed feat', tags['title'])
                    tags['title'] = tags['title'].replace(b, '(**Feat')
                    bracketed = True
                    break
            for c in ['featuring', 'feat', 'ft']:
                if c in tags['title'] and bracketed is False:
                    tags['title'] = tags['title'].replace(c, '(**Feat')
                else:
                    continue
            print('after formatting:', tags['title'])
    return all_tags


def splice_brackets(all_tags):
# Checks if song contains brackets, returns spliced title tag
    for tags in all_tags:
        if '(' not in tags['title']:
            print('no brackets found in:', tags['title'])
            continue
        else:
            print('() found in title tag, Sliced!')
            spliced = tags['title'].split('(')
            print(spliced)
            if len(spliced) == 1:
                tags['title'] = spliced
                print('Error')
            elif len(spliced) == 2:
                tags['title'] = spliced
                print('spliced once:', tags['title'])
            elif len(spliced) > 2:
                tags['title'] = spliced
                print('SPLICED 2 OR MORE TIMES!!!', tags['title'])
            else:
                print('something bad happened')
    return all_tags

def format_mix_and_featured(all_tags):
# Check if song title contains mix type information
    for tags in all_tags:
        print('checking song type:', tags['title'])
        for type in ['Remix', 'remix', 'Mix', 'mix', 'Edit', 'edit', 'Flip', 'flip']:
# Check if non-bracketed mix info exists in title tag, will only come up True if string, not a list

# ADD WAY TO FORMAT UNBRACKETED MIX INFO

            if type in tags['title']:
                print('Mix information found in title but no brackets')
                continue
# FORMAT MIX TYPE (Remix, Original Mix, Radio Edit, etc... )
            if len(tags['title']) > 1:
                for item in tags['title']:
                    for type in ['Remix', 'remix', 'Mix', 'mix', 'Edit', 'edit', 'Flip', 'flip']:
                        if type in item:
                            tags['mix'] = item.replace(')','').strip()
                            try:
                                tags['title'].remove(item).strip()
                            except:
                                continue
                            print('mix tag is now:', tags['mix'])
                            print('title tag is now:', tags['title'])
                        else:
                            continue
            else:
                continue
# FORMAT FEATURED ARTIST **
        try:
            for item in tags['title']:
                if not item.startswith('**'):
                    continue
# If featured artist exists, add info to 'featuring' tag and remove item from title tag
                else:
                    tags['featuring'] = item.replace('**Feat.', '').replace(')','').strip()
                    tags['title'].remove(item)
        except:
            print('title not list!!!')



def final_formatting(all_tags):
    for tags in all_tags:
# check number of items contained in title tag
        print('formatting title contents for:',tags['title'])
        if len(tags['title']) < 1:
            print('Error - song title field empty')
            break
# Check contents of title tag: string, one member list or multi-member list
        try:
            tags['title'].sort()
            count = 0
            for c in tags['title']:
                count = count + 1
# If title tag contains string, leave for now

        except:
            tags['title'] = tags['title'].strip()
            print('one string in title tag. unaffected.', tags['title'])

        if count == 1:
            print('found one item as type=list')
            tags['title'] = str(tags['title']).replace("[","").replace("]","").replace("'","").replace('"','').strip()

        elif count == 2:
            print('found two items in title tag. Starting formatting...')
            for item in tags['title']:
                if ')' in item:
                    tags['extra'] = item.replace(')','').strip()
                    tags['title'].remove(item)
                    tags['title'] = str(tags['title']).replace("[","").replace("]","").replace("'","").strip()
        else:
            continue

        print('FINAL TITLE:', tags['title'], 'FEATURING:', tags['featuring'], 'MIX TYPE:', tags['mix'], 'EXTRA INFO:', tags['extra'])


def create_json(all_tags):
    song_info = json.dumps(all_tags, indent=2)
    print(song_info)
    with open('C:/Users/Adam/Desktop/Projects/music/songs.txt','w') as songs:
        songs.write(song_info)
    return song_info


for song in os.listdir(root):
    if song.endswith((".mp3",".m4a",".flac",".alac")):
        try:
            filename = root + "/" + song
            get_tags(filename, song)
        except MutagenError:
            print("error")
            continue
fix_title(all_tags)
fix_brackets(all_tags)
check_featured(all_tags)
splice_brackets(all_tags)
format_mix_and_featured(all_tags)
final_formatting(all_tags)
create_json(all_tags)
error_check(all_tags, old_tags)
