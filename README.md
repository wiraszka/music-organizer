## music-organizer

# Current functionalities

**1) audio-file-fixer.py**
- input is a directory with music files
- scans files for proper music format (mp3)
- scans metadata of all music files and reformats them into specified fields
- creates txt file with original media tags "original-info.txt"
- reformats tags to include 'remixed by', 'featuring', 'mix'
- creates txt file with new media tags "songs.txt"

**2) spotify-lookup.py**
-



**3) error-checking.py**








# Functionalities to add:

**1) audio-file-fixer.py**
- fill in title and artist tags from filename if none present
- fix issue with 'None' (string) vs null
- handle foreign keyboard characters


**2) spotify-lookup.py**
- download album cover
- get bpm for songs (either through analyzing wave file or scraping info)
- get key for songs
- get genre for songs
- add search sequence to search multiple times with different combos of tags
-


**Other ideas**
- add shazam (waveform comparison) functionality if possible
- incorporate youtube API search into matching to make it more accurate and deal with lesser known songs
-
- suggest recommended songs based on songs already analyzed (maybe using AI, training a neural net)
-
