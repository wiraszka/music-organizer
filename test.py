import os
import json


path = "C:/Users/Adam/Documents/Adams Music2"

os.chdir(path)

with open('manifest.txt', 'r+') as manifest:
    manifest = json.loads(manifest.read())

count = 0
errors = 0
for item in manifest:
    if 'output_filename' in item.keys():
        count += 1
        if item['mix'] != 'None':
            print(item['artist'], '-', item['title'], item['mix'],'  |||   ', item['output_artist'], '-', item['output_track'])
        else:
            print(item['artist'], '-', item['title'], '  |||   ', item['output_artist'], '-', item['output_track'])
    if 'error_type' in item.keys():
        errors += 1

print('Manifest items:', len(manifest))
print('Items with updated info:', count)
print('Number of errors:', errors)
