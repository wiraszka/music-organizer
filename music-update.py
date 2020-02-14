import os
import json
import re
from fuzzywuzzy import fuzz
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

# NEW FLOW:
# Search Youtube first using full filename
# 




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
        print('Spotify search failed')
        search_success = False
    else:
        print('Spotify search successful')
        search_success = True

# If spotify search successful, return relevant song info for top-10 results in json format
    if search_success == True:
        song_info = []
        count = 0
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
        video_id = item['id']['videoId']
        searchUrl = "https://www.googleapis.com/youtube/v3/videos?id="+video_id+"&key="+YOUTUBE_API_KEY+"&part=contentDetails"
        response = urllib.request.urlopen(searchUrl).read()
        data = json.loads(response)
        duration = data['items'][0]['contentDetails']['duration']
        duration = re.findall('\d+', duration)
        info['duration'] = int(duration[0]) * 60
        try:
            info['duration'] = info['duration'] + int(duration[1])
        except:
            pass
        #print(info['duration'])
        youtube_results.append(info)
    return youtube_results


def match_audio(search_str, youtube_results, song):
    matched = False
    vid_list = {
        'best_vid' : '',
        'best_url' : '',
        'highest_match' : 0
        }
    for item in youtube_results:
# Remove videos such as covers, live recordingss/performances unless explicitly asked for
        print('Analyzing:', item['vid_title'], item['duration'])
        if 'cover' not in search_str:
            if 'cover' in item['vid_title'].lower():
                print('DISALLOWED')
                continue
        if 'live' not in search_str:
            if 'live' in item['vid_title'].lower():
                print('DISALLOWED')
                continue
# Remove videos that don't match length of target song on spotify
        lower_limit = int(song['duration']) - 5
        upper_limit = int(song['duration']) + 5
        print(lower_limit, item['duration'], upper_limit)
        if not lower_limit < item['duration'] < upper_limit:
            print('Duration mismatch')
            continue


# Use fuzzy matching to find closest match between search string and remaining search results
        match_ratio = fuzz.ratio(item['vid_title'], search_str)
        print('Match ratio:', match_ratio)
        if match_ratio > vid_list['highest_match']:
            vid_list['best_vid'] = item['vid_title']
            vid_list['best_url'] = item['url']
            vid_list['highest_match'] = match_ratio
        #print('current best match is:', vid_list)
        if match_ratio > 85:
            matched = True
            chosen_url = item['url']
            chosen_video = item['vid_title']
    if matched == False:
        chosen_url = vid_list['best_url']
        chosen_video = vid_list['best_vid']
        print('Best match:', chosen_video)
    else:
        print('Matched!', chosen_video)

    return chosen_url


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
with open(txt, 'r') as song_info:
    contents = json.loads(song_info.read())
    #print(contents[0])

errors = []
# Check if song is 320kbps
for song in contents:
    if song['bitrate'] == 320000:
        print('Analyzing...', song['id'], 'song:', song['artist'], song['title'])
        print('Bitrate 320kbps detected')
        search_str = song['artist'] + ' ' + song['title']
    else:
        print('Analyzing...', song['id'], 'song:', song['artist'], song['title'])
        print('Bitrate not 320kbps')
        if song['artist'] == 'None':
            print('Error - Song ID:', song['id'], 'Filename', song['filename'])
            song['error_type'] = 'filename error'
            errors.append(song)
            continue
        if song['mix'] != 'None':
            print('song contains mix information')
            search_str = song['artist'] + ' ' + song['title'] + ' ' + song['mix']
        else:
            search_str = song['artist'] + ' ' + song['title']
# Search Spotify API for song
    spotify_summary = spotify_search(search_str)
    if type(spotify_summary) is None:
        search_success = False
        print('Spotify search unsuccessful.')
    else:
        search_success = True
        print('Spotify search successful.')
# Check if spotify result matches the audio file in terms of name and duration
    print(spotify_summary)
    print('-'*50)
    if search_success == True:
        duration_match = False
        index = 0
        matched = False
        count = 0
        for item in json.loads(spotify_summary):
            count += 1
            search_result = item['artist'] + ' ' + item['track']
            print(search_result)
            match_ratio = fuzz.ratio(search_result, search_str)
            print('Match ratio:', match_ratio)
            lower_limit = int(song['duration']) - 5
            upper_limit = int(song['duration']) + 5
            print(lower_limit, item['duration_s'], upper_limit)
            if not lower_limit < item['duration_s'] < upper_limit:
                print('Duration mismatch')
                duration_match = False
                continue
            else:
                print('Duration match')
                duration_match = True
# Choose closest match
            if match_ratio > 90:
                index = count - 1
                matched = True
                break
            elif match_ratio >= 75 and duration_match == True:
                index = count - 1
                matched = True
                break
        if matched == False:
            print('Spotify search error!')
            song['error_type'] = 'Spotify search result error'
            errors.append(song)

    print('Finding download link for:', search_str)
    youtube_results = search_youtube(search_str)
    chosen_url = match_audio(search_str, youtube_results, song)
    audio_filename = dl_song(chosen_url)
    if matched == True:
        spotify_summary = json.loads(spotify_summary)
        output_filename = spotify_summary[index]['artist'] + ' - ' + spotify_summary[index]['track'] + '.mp3'
        print('output file name:', output_filename)
        dl_cover_art(index, spotify_summary)
        apply_ID3_tags(index, spotify_summary, audio_filename, output_filename)
    else:
        print('Could not find audio tags or album art')

    error_tracker = json.dumps(errors, indent=2)
    with open("errors.txt", "w") as file:
        file.write(error_tracker)


# if no hit, search in other name formats (artist - title)
# if still no hit, search for song on youtube directly
# if spotify API returns info, save song info in json
# search for song using youtube's API
# fuzzy match and compare durations of youtube-video-results and spotify-result
# if match (within threshold), download song
# dl album cover and apply tags (from json)
# Blah
