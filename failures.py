import os
import json
import shutil
from json.decoder import JSONDecodeError

music_path = "C:/Users/Adam/Documents/Adams Music2"
#path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/sample-music2'
dir_path = "C:/Users/Adam/Desktop/Projects/music/music-organizer"

os.chdir(music_path)
if not os.path.exists('Errors'):
    os.mkdir('Errors')
    os.chdir('Errors')

os.chdir(music_path)
with open('manifest.txt', 'r') as manifest:
    manifest = json.loads(manifest.read())
    #print(json.dumps(manifest, indent=2))


error_list = [item for item in manifest if 'output_track' not in item.keys()]
error_list = [item for item in error_list if 'file_name' in item.keys()]
error_manifest = []
error_info = {}

count_errors = len(error_list)
print('error count:', count_errors)

if not os.path.exists(dir_path):
    print('Path to original-info.txt does not exist, check path')
else:
    songs_txt = dir_path + '/original-info.txt'
    with open(songs_txt, 'r') as original_songs:
        original_songs = json.loads(original_songs.read())

    for error_song in error_list:
        for or_song in original_songs:
            if error_song['file_name'] == or_song['file_name']:
                error_song['original_filename'] = or_song['file_name']
                error_song['original_artist'] = or_song['artist']
                error_song['original_track'] = or_song['title']
        origin_path = error_song['file_path']
        destination_path = music_path + '/Errors'
        shutil.copy(origin_path, destination_path)
    error_list = json.dumps(error_list, indent=2)
    print(error_list)
