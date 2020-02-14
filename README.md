# music-organizer

## Current functionalities

**1) song-reformat.py**
- input is a directory with music files
- scans files for mp3 audio format
- reformats song info and saves to list
- creates txt file with original media tags "original-info.txt" in json format
- reformats tags to include 'remixed by', 'featuring', 'mix'
- creates txt file with new media tags "songs.txt" in json format

**2) music-update-tags.py**
- takes song.txt and corresponding audio files as input
- searches spotify API for each song using reformatted song.txt info
- spotify API search queries must closely match song name on spotify so multiple search attempts with various combos of song info are used
- fuzzy match and compare duration between audio file and spotify API results
- if match above threshold, dl album cover and reformat tags on audio file
- each change is documented in manifest.txt as script progresses through audio files
