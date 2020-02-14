# Cleans up audio file names and tags
import os
import mutagen
import re
import json
from mutagen import MutagenError
from mutagen.mp3 import MP3

# Specify directory where audio files are located
#root = "C:/Users/Adam/Documents/Adams Music2"
original_info_txt = "C:/Users/Adam/Desktop/Projects/music/music-organizer/original-info.txt"
root = "C:/Users/Adam/Desktop/Projects/music/music-organizer/sample-music2"

def get_tags(filepath, filename):
# Retrieves relevant file tags for each song, then puts them in dict with the following keys:
    all_tags = []
    for song in os.listdir(root):
        if not song.endswith(".mp3"):
            print('Audio type error')
        else:
            filepath = root + "/" + song
            filename = song
            tags = {
                'id' : '',
                'file_path' : '',
                'file_name' : '',
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
            info = mutagen.File(filepath, easy=True)

            for key in tags.keys():
                if key in info.keys():
                    tags[key] = info.get(key)[0]
                if key not in info.keys():
                    tags[key] = 'None'
        # Get song duration and bitrate using MP3 module
            extra_info = MP3(filepath)
            tags['duration'] = extra_info.info.length
            tags['bitrate'] = extra_info.info.bitrate
            tags['file_path'] = filepath
            tags['file_name'] = filename
        # Create list containing all songs and tags
            all_tags.append(tags)
        # Add 'id' number
            count = 0
            for item in all_tags:
                count += 1
                item['id'] = count
# Create txt file with all original song info
    all_tags = json.dumps(all_tags, indent=2)
    with open('C:/Users/Adam/Desktop/Projects/music/music-organizer/original-info.txt','w') as original:
        original.write(all_tags)
    all_tags = json.loads(all_tags)
    return all_tags

def fix_brackets(all_tags):
# Converts all bracket types to () in title tag
    for tags in all_tags:
        print(tags)
        tags['title'] = tags['title'].replace('[', '(').replace(']', ')')
        tags['title'] = tags['title'].replace('{', '(').replace('}', ')')
        tags['title'] = tags['title'].replace('"', '')
        print('fixed brackets:', tags['title'])
    return all_tags


if os.path.exists(original_info_txt):
    with open(original_info_txt, 'r') as info:
        contents = json.loads(info.read())
else:
    print('info file does not exist')
    quit()

        all_tags = get_tags(filepath, filename)
        all_tags = fix_brackets(all_tags)

        #check_featured(all_tags)
        #splice_brackets(all_tags)
        #format_mix_and_featured(all_tags)
        #final_formatting(all_tags)
        #create_json(all_tags)
