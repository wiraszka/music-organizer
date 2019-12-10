# Cleans up audio file names and tags
import os
import json
import sys



#root = "C:/Users/Adam/Documents/Adam's Music"
root = "C:/Users/Adam/Desktop/Projects/music/sample-music-test"
input_txt = "C:/Users/Adam/Desktop/Projects/music/original-info.txt"
output_txt = "C:/Users/Adam/Desktop/Projects/music/songs.txt"

with open(input_txt,'r') as j:
    old_tags = j.read()
input_info = json.loads(old_tags)

with open(output_txt, 'r') as k:
    all_tags = k.read()
output_info = json.loads(all_tags)

def error_check():
    file_count = len(next(os.walk(root))[2])
    items_before_processing = sum(1 for song in input_info)
    items_after_processing = sum(1 for song in output_info)
    items_changed = sum(1 for i in range(0,(items_after_processing-1)) if input_info[i] == output_info[i])
    empty_title = sum(1 for song in output_info if song['title'] == 'None')
    empty_artist = sum(1 for song in output_info if song['artist'] == 'None')
    mix_type_count = sum(1 for song in output_info if song['mix'] != 'None')
    featured_count = sum(1 for song in output_info if song['featuring'] != 'None')

    print('--- SUMMARY ---')
    print('Items in folder:', file_count)
    print('Items before processing', items_before_processing)
    print('Items after processing:', items_after_processing)
    print('Items changed:', items_changed)
    print('Mix information retrieved:', mix_type_count)
    print('Featured artist information retrieved:', featured_count)
    print('Number of empty title tags:', empty_title)
    print('Number of empty artist tags:', empty_artist)


error_check()
