import os
import json
import re
from fuzzywuzzy import fuzz
from shutil import copy
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

path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/sample-music-test'
txt = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/songs.txt'
output_path = 'C:/Users/Adam/Desktop/Projects/music/music-organizer/songs'

# NEW FLOW:
# Input is all audio files in directory under variable = path
# Generate search string to send to Youtube and Spotify APIs from each audio filename
# Retrieve search info from both APIs
# Fuzzy match to find closest matches between API call results and original search string
# If no close match exists, generate new search string
# Check durations of chosen spotify hit and youtube hit to make sure they match audio file
### Give hits a score based on how close in duration to the audio file they are
# If not, check durations of all other results to see if they match
# If close enough match, download audio using youtube-dl
# Add ID3 tags to final audio track
# Save manifest and errors

def generate_search_str(song, try_number, current_match):
    print('Search attempt number', try_number)
    if try_number == 1:
        if song['mix'] != 'None':
            search_str = song['artist'] + ' - ' + song['title'] + ' ' + song['mix']
        else:
            search_str = song['artist'] + ' - ' + song['title']
    if try_number == 2:
        if song['mix'] != 'None':
            search_str = song['title'] + ' ' + song['mix']
        else:
            search_str = song['filename'].replace('.mp3', '')
    if try_number == 3:
        if song['mix'] != 'None':
            search_str = song['filename'].replace('.mp3', '')
        else:
            if len(current_match) > 0:
                search_str = current_match[0]['best_vid']
            else:
                search_str = song['filename'].replace('.mp3', '')
    if try_number > 3:
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
        print('Spotify search results:')
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
            print(tags['id'], '-', tags['artist'], '-', tags['track'], '- album:', tags['album'], '- duration:', tags['duration_s'])
            song_info.append(tags)
        spotify_summary = json.dumps(song_info, indent=2)
    #print(spotify_summary)
    return spotify_summary


def search_youtube(search_str):
# Youtube API Authentication and generate search request
    print('Searching Youtube for:', search_str)
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


def match_audio(song, search_str, spotify_summary, youtube_results, sp_success, current_match):
    match_result = []
# Match search string to Youtube results using fuzzy matching then duration similarity
    print('current match:', current_match)
    best_video = {
        'best_vid' : '',
        'best_url' : '',
        'fuzzy_score' : 0,
        'dur_score' : 0,
        'total_score' : 0
        }
    for item in youtube_results:
# Remove videos such as covers, live recordingss/performances unless explicitly asked for
        #print('Analyzing Youtube video:', item['vid_title'], item['duration'])
        if 'cover' not in search_str:
            if 'cover' in item['vid_title'].lower():
                #print('DISALLOWED')
                continue
        if 'live' not in search_str:
            if 'live' in item['vid_title'].lower():
                #print('DISALLOWED')
                continue
# Give result a score based on how close the video duration is to audio file
        track_duration = int(song['duration'])
        video_duration = int(item['duration'])
        diff = abs(track_duration - video_duration)
        dur_score = (100 - diff) * 0.35
        dur_score = round(dur_score, 2)
        if dur_score < 0:
            dur_score = 0
        #print(dur_score)
# Use fuzzy matching to find closest match between search string and remaining search results
        match_ratio = fuzz.ratio(item['vid_title'], search_str) * 0.65
        match_ratio = round(match_ratio, 2)
        #print('Match ratio:', match_ratio)
        total_score = dur_score + match_ratio
        print('Match score:', total_score)
# Save best match based on total score
        if total_score > best_video['total_score']:
            best_video['best_vid'] = item['vid_title']
            best_video['best_url'] = item['url']
            best_video['fuzzy_score'] = match_ratio
            best_video['dur_score'] = dur_score
            best_video['total_score'] = total_score
        print('current best match is:', best_video)
    if len(current_match) > 0:
        current_match = json.loads(current_match)
        if best_video['total_score'] > current_match[0]['total_score']:
            match_result.append(best_video)
        else:
            match_result.append(current_match[0])
    else:
        match_result.append(best_video)
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
    if len(current_match) > 0:
        #current_match = json.loads(current_match)
        if best_sp_result['total_score'] > current_match[1]['total_score']:
            match_result.append(best_sp_result)
        else:
            match_result.append(current_match[1])
    else:
        match_result.append(best_sp_result)

    if sp_success == False:
        print('No spotify results to fuzzy match.')
        match_result.append(current_match[1])

    match_result = json.dumps(match_result, indent=2)
    print(match_result)

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
        print('filename is:', audio_filename)
    return audio_filename


def dl_cover_art(index, spotify_summary):
# Download cover art
    if os.path.exists('img.png'):
        os.remove('img.png')
    image_file = 'img.png'.format(0)
    response = urllib.request.urlretrieve(spotify_summary[index]['album_art'], image_file)


def apply_ID3_tags(index, spotify_summary, audio_filename, output_filename):
# Rename audio file to 'temp.mp3' because file might have non-ascii characters (eyed3 cannot handle these)
    try:
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
        os.rename('temp.mp3', output_filename)
    except:
        print('Could not apply media tags to file')


# ------------------------------------------------------------------------------
#                             - STARTS HERE -
# ------------------------------------------------------------------------------

# Load txt file containing output from 'song-reformat.py'
with open(txt, 'r') as song_info:
    contents = json.loads(song_info.read())
    #print(contents[0])

errors = []
# Exclude audio files with no artist info (indicates song-reformat.py error)
for song in contents:
    print('='*80)
    print('Analyzing track', song['id'], ': ', song['artist'], song['title'])
    if song['duration'] > 1000:
        print('Song too long.')
        song['error_type'] = 'audio too long.'
        errors.append(song)
        continue
    if song['artist'] == 'None':
        print('Error - Song ID:', song['id'], 'Filename', song['file_name'])
        song['error_type'] = 'filename error'
        errors.append(song)
        continue
    if song['bitrate'] == 320000:
        print('Bitrate 320kbps detected')

# Initial paramters:
    vid_match = False
    sp_match = False
    current_match = []
    try_number = 1
    matched = False
    while matched == False:
        if try_number > 3:
            break
# Generate search string from audio file info
        search_str = generate_search_str(song, try_number, current_match)
# Search Spotify API to retrieve official song info
        spotify_summary = spotify_search(search_str)
        if type(spotify_summary) is None:
            sp_success = False
        else:
            sp_success = True
# Search Youtube API to retrieve download link
        youtube_results = search_youtube(search_str)
# Check search results for closest match in terms of name and duration
        match_result = match_audio(song, search_str, spotify_summary, youtube_results, sp_success, current_match)
        current_match = json.loads(match_result)
# Spotify fuzzy matching score above 80
        if current_match[1]['total_score'] >= 80:
            sp_match = True
            index = current_match[1]['index']
# Youtube fuzzy matching score above 80
        if current_match[0]['total_score'] >= 80:
            vid_match = True
            chosen_url = current_match[0]['best_url']
# Check if both Spotify and Youtube came back with good enough hit
        if sp_match == False or vid_match == False:
            print('Generating new search string.')
            try_number += 1
        elif sp_match == True and vid_match == True:
            matched = True
            print('Full match!')
# If youtube link found, download audio
    if vid_match == True:
        audio_filename = dl_song(chosen_url)
    else:
        audio_filename = song['file_name']
# If Spotify song info found, apply cover art and ID3 tags to audio file
    if sp_match == True:
        if vid_match == False:
            copy(song['file_path'], output_path)
            output_filename = song['file_name']
            print('Spotify results found but no Youtube result. Copying original mp3 file to output folder.')
        elif vid_match == True:
            spotify_summary = json.loads(spotify_summary)
            output_filename = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track'] + '.mp3'
            print('Spotify and Youtube results found. Downloading cover art and applying tags.')
        print('output file name:', output_filename)
        dl_cover_art(index, spotify_summary)
        apply_ID3_tags(index, spotify_summary, audio_filename, output_filename)

    else:
        print('Could not find audio tags or album art')
        song['error_type'] = 'Spotify search failed, no song info retrieved.'
        errors.append(song)

error_tracker = json.dumps(errors, indent=2)
with open("errors.txt", "w") as file:
    file.write(error_tracker)
