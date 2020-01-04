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
    #items_changed = sum(1 for i in output_info if input_info[i-1] == output_info[i-1])
    items_changed = 0
    for song in output_info:
        i = song['id']
        if input_info[i-1] == output_info[i-1]:
            items_changed = items_changed + 1

    empty_title = sum(1 for song in output_info if song['title'] == 'None')
    empty_artist = sum(1 for song in output_info if song['artist'] == 'None')
    mix_type_count = sum(1 for song in output_info if song['mix'] != 'None')
    featured_count = sum(1 for song in output_info if song['featuring'] != 'None')
    extra_count = sum(1 for song in output_info if song['extra'] != 'None')

    print('------------------------------- SUMMARY -------------------------------')
    print('Items in folder:', file_count)
    print('Items before processing', items_before_processing)
    print('Items after processing:', items_after_processing)
    print('Items changed:', items_changed)
    print('Mix information retrieved:', mix_type_count)
    print('Featured artist information retrieved:', featured_count)
    print('Extra information retrieved:', extra_count)
    print('Number of items with empty title info:', empty_title)
    print('Number of items with empty artist info:', empty_artist)
    print('-----------------------------------------------------------------------')

def view_by_id():
    while True:
        try:
            x = int(input('input id number:' ))
            print(json.dumps(input_info[x-1], indent=2))
            print(json.dumps(output_info[x-1], indent=2))
        except:
            quit()

def view_by_extra():
    for song in output_info:
        if song['extra'] != 'None':
            print(song['extra'])
error_check()
view_by_extra()
view_by_id()
