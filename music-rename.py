import os
from tinytag import TinyTag, TinyTagException

tracks = []

root = "C:/Users/Adam/Desktop/Projects/music/music_sample"
for file in os.listdir(root):
    if file.endswith((".mp3",".m4a",".flac",".alac")):
        try:
            tag = TinyTag.get(root + "/" + file)
            info = tag.artist, tag.title, tag.genre, tag.duration
            tracks.append(info)
            if tag.artist is None:

        except TinyTagException:
            print("error")
print(tracks)
