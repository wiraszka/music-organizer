import os
import json
import re
from fuzzywuzzy import fuzz
from shutil import copy
from itunesLibrary import library
import pafy
import youtube_dl
import ffmpeg
import html
import urllib.request
from urllib.request import urlopen
import eyed3
import spotipy
import spotipy.util as util
from spotipy import oauth2
from json.decoder import JSONDecodeError
from apiclient.discovery import build
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YOUTUBE_API_KEY

path = "C:/Users/Adam/Documents/Adams Music2"
#path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/sample-music2'
txt = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/songs.txt'
output_path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/songs'
library_xml = "C:/Users/Adam/Desktop/Projects/music/music-organizer/iTunes Music Library.xml"


def generate_search_str(song, try_number, current_match):
    print('Search attempt number', try_number)
    if try_number == 1:
        if song['mix'] != 'None':
            search_str = song['artist'] + ' - ' + song['title'] + ' ' + song['mix']
        else:
            search_str = song['artist'] + ' - ' + song['title']
    if try_number == 2:
        if song['mix'] != 'None':
            if 'remix' in song['mix'].lower():
                search_str = song['title'] + ' ' + song['mix']
            else:
                search_str = song['file_name'].replace('.mp3', '')
        else:
            search_str = song['file_name'].replace('.mp3', '')
    if try_number == 3:
        if song['mix'] != 'None':
            search_str = song['artist'] + ' - ' + song['title'] + ' ' + song['mix']
            search_str = search_str.lower()
        else:
            search_str = song['artist'] + ' - ' + song['title']
            search_str = search_str.lower()
    if try_number == 4:
        featuring = ['feat.', 'ft.', 'feat', 'ft']
        for f in featuring:
            if f in song['title'].lower():
                title = song['title'].split(f)
                song['title'] = title[0]
                search_str = song['artist'] + ' - ' + song['title']
                search_str = search_str.lower()
            else:
                search_str = song['artist'] + ' - ' + song['title'] + ' ' + song['mix']
                search_str = search_str.lower()
    if try_number > 4:
        quit()
    #print('Search string is:', search_str)
    return search_str



def spotify_search(search_query):
# Get access token for Spotipy API (from config.py)
    token = util.oauth2.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    cache_token = token.get_access_token()
    spotify = spotipy.Spotify(cache_token)

# Input song name and search spotify
    print('Searching for...', search_query)
    result = spotify.search(search_query, limit=10)
    spotify_summary = None
    #print(json.loads(result, indent=2)

# Check if search successful
    if len(result['tracks']['items']) < 1:
        print('Spotify search failed!')
        sp_success = False
    else:
        print('Spotify search successful.')
        sp_success = True

# If spotify search successful, return relevant song info for top-10 results in json format
    if sp_success == True:
        song_info = []
        count = 0
        #print('Spotify search results:')
        for song in result['tracks']['items']:
            count += 1
            tags = {}
            tags['id'] = count
            tags['artist'] = song['artists'][0]['name']
            tags['track'] = song['name']
            tags['album'] = song['album']['name']
            tags['album_artist'] = song['album']['artists'][0]['name']
            tags['album_type'] = song['album']['album_type']
            tags['album_art'] = song['album']['images'][0]['url']
            tags['year'] = song['album']['release_date'][:4]
            tags['track_number'] = song['track_number']
            tags['total_tracks'] = song['album']['total_tracks']
            tags['duration_s'] = int(song['duration_ms']) / 1000
            #print(tags['id'], '-', tags['artist'], '-', tags['track'], '- album:', tags['album'], '- duration:', tags['duration_s'])
            song_info.append(tags)
        spotify_summary = json.dumps(song_info, indent=2)
    #print(spotify_summary)
    return spotify_summary


def search_youtube(search_str):
# Youtube API Authentication and generate search request
    #print('Searching Youtube for:', search_str)
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=search_str, part='snippet', type='video', maxResults=10)
    results = request.execute()
# Return video title and url for each result
    youtube_results = []
    for item in results['items']:
        info = {}
        info['vid_title'] = html.unescape(item['snippet']['title'])
        info['url'] ='https://www.youtube.com/watch?v=' + item['id']['videoId']
        #print('Analyzing:', info['vid_title'], info['url'])
    #print(youtube_results)
# Get video durations and append to youtube_results
        video = pafy.new(info['url'])
        info['duration'] = video.length
        print('video title:', info['vid_title'], 'video duration:', info['duration'])
        youtube_results.append(info)
    return youtube_results


def match_audio(song, search_str, spotify_summary, sp_success, current_match):
    match_result = []
    #print('current match:', current_match)
# Match search string to Spotify results
    best_sp_result = {
        'best_spotify' : '',
        'fuzzy_score' : 0,
        'dur_score' : 0,
        'total_score' : 0
        }
    index = -1
    if sp_success == True:
        for item in json.loads(spotify_summary):
            #print(item)
            index += 1
            track_duration = int(song['duration'])
            spotify_duration = int(item['duration_s'])
            diff = abs(track_duration - spotify_duration)
            #print('spotify time difference is:', diff)
            dur_score = (100 - diff) * 0.35
            dur_score = round(dur_score, 2)
            #print('duration score:', dur_score)
            if dur_score < 0:
                dur_score = 0
    # Use fuzzy matching to find closest match between search string and remaining search results
            track_name = item['artist'] + ' - ' + item['track']
            match_ratio = fuzz.ratio(track_name, search_str) * 0.65
            match_ratio = round(match_ratio, 2)
            #print('Match ratio:', match_ratio)
            total_score = dur_score + match_ratio
            #print('Spotify match score:', total_score)

    # Save best match based on total score
            if total_score > best_sp_result['total_score']:
                best_sp_result['best_spotify'] = track_name
                best_sp_result['index'] = index
                best_sp_result['dur_score'] = dur_score
                best_sp_result['fuzzy_score'] = match_ratio
                best_sp_result['total_score'] = total_score
            #print('current best match is:', best_sp_result)
    if not current_match is None:
        #current_match = json.loads(current_match)
        if best_sp_result['total_score'] > current_match[0]['total_score']:
            match_result.insert(0, best_sp_result)
        else:
            match_result.append(current_match[0])
    else:
        match_result.append(best_sp_result)

    if sp_success == False:
        #print('No spotify results to fuzzy match.')
        match_result.append(current_match)

    match_result = json.dumps(match_result, indent=2)
    #print(match_result)

    return match_result


def dl_song(chosen_url):
# Youtube_dl parameters config
    download_options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

# Specify output directory for downloads
    if os.path.exists('songs'):
        os.chdir('songs')

# Download song from chosen Youtube url
    with youtube_dl.YoutubeDL(download_options) as dl:
        audio_filename = dl.prepare_filename(dl.extract_info(chosen_url))
        audio_filename = audio_filename.replace('.webm', '.mp3')
        #dl.download([chosen_url])
        #print('filename is:', audio_filename)
    return audio_filename


def dl_cover_art(index, spotify_summary):
# Download cover art
    os.chdir(path)
    if os.path.exists('img.png'):
        os.remove('img.png')
    image_file = 'img.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)
    audio_filename = song['file_name']
    return audio_filename

def apply_ID3_tags(index, spotify_summary, audio_filename, output_filename):
# Rename audio file to 'temp.mp3' because file might have non-ascii characters (eyed3 cannot handle these)
    #try:
    if os.path.exists('temp.mp3'):
        os.remove('temp.mp3')
    os.rename(audio_filename, 'temp.mp3')
    apply_tags = eyed3.load('temp.mp3')
    apply_tags.initTag()
    apply_tags.tag.images.set(3, open('img.png','rb').read(), 'image/png')
    apply_tags.tag.artist = spotify_summary[index]['artist']
    apply_tags.tag.title = spotify_summary[index]['track']
    apply_tags.tag.album = spotify_summary[index]['album']
    apply_tags.tag.album_artist = spotify_summary[index]['album_artist']
    apply_tags.tag.recording_date = spotify_summary[index]['year']
    apply_tags.tag.track_num = spotify_summary[index]['track_number']
    apply_tags.tag.save()
    print('Media tags and album art applied to audio file')
    forb_char = ['/', '?', ':', '*', '|', '>', '>', '"', '\\']
    for i in forb_char:
        if i in output_filename:
            output_filename = output_filename.replace(i, '').strip()
    os.rename('temp.mp3', output_filename)
    #except:
    #    print('Could not apply media tags to file')

def manifest_check(song, load_manifest):
# Check if manifest file exists
    check = False
    for man_item in load_manifest:
        if song['file_path'] == man_item['file_path']:
            print('Song already exists in manifest')
            check = True
    return check


# ------------------------------------------------------------------------------
#                             - STARTS HERE -
# ------------------------------------------------------------------------------

# Load txt file containing output from 'song-reformat.py'
with open(txt, 'r') as song_info:
    contents = json.loads(song_info.read())
    #print(contents[0])
os.chdir(path)
input1 = input('Load manifest? y / n')
if input1 == 'y':
    use_manifest = True
    if os.path.exists('manifest.txt'):
        with open('manifest.txt', 'r+') as manifest_txt:
            manifest_s = manifest_txt.read()
            if len(manifest_s) < 1:
                print('Manifest is blank.')
                manifest_txt.write('[]')
                use_manifest = False
            else:
                num_items = len(manifest_s)
                print('Manifest contains', num_items, 'items')
                load_manifest = json.loads(manifest_s)
    else:
        print('Manifest could not be found. Creating manifest txt file...')
        with open('manifest.txt', 'w') as manifest_txt:
            manifest_txt.write('[]')
        use_manifest = False
#            manifest_txt.close()

elif input1 == 'n':
    print('Manifest not being used')
    use_manifest = False
else:
    quit()

lib = library.parse(library_xml)

errors = []
# Exclude audio files that are too long (probably not songs), not formatted correctly or were already updated
for song in contents:
    print('='*80)
    print('Analyzing track', song['id'], ': ', song['artist'], song['title'])
    if use_manifest == True:
        check = manifest_check(song, load_manifest)
        if check == True:
            continue
    if song['duration'] > 1000:
        print('Song too long.')
        song['error_type'] = 'audio too long.'
        errors.append(song)
        continue
    if song['artist'] == 'None':
        print('Error - Song ID:', song['id'], 'Filename', song['file_name'])
        song['error_type'] = 'filename error, song reformat.py failed'
        errors.append(song)
        continue
    if type(song['title']) is list or type(song['artist']) is list:
        continue
        song['error_type'] = 'filename error, song reformat.py failed'
        errors.append(song)
    #if song['bitrate'] == 320000:
        #print('Bitrate 320kbps detected')

# Initial paramters:
    sp_match = False
    current_match = None
    try_number = 1
    while sp_match == False:
        if try_number > 4:
            break
# Generate search string from audio file info
        search_str = generate_search_str(song, try_number, current_match)
        if try_number == 1:
            original_id = search_str
# Search Spotify API to retrieve official song info
        spotify_summary = spotify_search(search_str)
        if not spotify_summary is None:
            sp_success = True
        else:
            sp_success = False

        #print('sp_success =', sp_success)
# Check search results for closest match in terms of name and duration
        match_result = match_audio(song, search_str, spotify_summary, sp_success, current_match)
        current_match = json.loads(match_result)
        #print(current_match)
# Spotify fuzzy matching score above 76
        if current_match[0]['total_score'] >= 76:
            index = current_match[0]['index']
            #print('matched!')
            sp_match = True

# Check if both Spotify came back with good enough hit
        if sp_match == False:
            #print('Generating new search string.')
            try_number += 1
# If Spotify song info found, apply cover art and ID3 tags to audio file
    if sp_match == True:
                        #copy(song['file_path'], output_path)
        spotify_summary = json.loads(spotify_summary)
        result_id = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track']
        output_filename = result_id + '.mp3'
        print('output file name:', output_filename)
        #print('Downloading cover art and applying tags.')
        final_match = fuzz.ratio(original_id, result_id)
        #print(original_id, result_id)
        if final_match < 60:
            #print('Aborted. Final output name differs from original file name')
            song['error_type'] = 'final output name differs greatly.'
            errors.append(song)
        else:
            #print('Passed final check with similarity score:', final_match)
            audio_filename = dl_cover_art(index, spotify_summary)
            apply_ID3_tags(index, spotify_summary, audio_filename, output_filename)

    else:
        print('Could not find audio tags or album art')
        song['error_type'] = 'Spotify Error - Spotify search or fuzzy matching failed.'
        errors.append(song)

    manifest_item = song

    if sp_match == True:
        manifest_item['output_filename'] = output_filename
        manifest_item['output_artist'] = spotify_summary[index]['artist']
        manifest_item['output_track'] = spotify_summary[index]['track']
        manifest_item['output_album'] = spotify_summary[index]['album']
        manifest_item['output_year'] = spotify_summary[index]['year']
        manifest_item['output_track_number'] = spotify_summary[index]['track_number']


    with open('manifest.txt', 'r+') as manifest:
        manifest_str = manifest.read()
        #print(manifest_str, type(manifest_str))
        #print('adding item to manifest')
        manifest_str = json.loads(manifest_str)
        #print(manifest_str, type(manifest_str))
        manifest_str = list(manifest_str)
        #print(manifest_str, type(manifest_str))
        manifest_str.append(manifest_item)
        #print(manifest_str, type(manifest_str))
        manifest_str = json.dumps(manifest_str, indent=2)
        manifest.seek(0)
        manifest.truncate()
        manifest.write(manifest_str)



error_tracker = json.dumps(errors, indent=2)
with open("errors.txt", "w") as errors:
    errors.write(error_tracker)
