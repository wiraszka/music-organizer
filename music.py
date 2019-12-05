import os
import time
from tinytag import TinyTag, TinyTagException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

tracks = []

root = "C:/Users/Adam/Desktop/Projects/music/music_sample"
for file in os.listdir(root):
    if file.endswith((".mp3",".m4a",".flac",".alac")):
        try:
            tag = TinyTag.get(root + "/" + file)
            info = tag.artist, tag.title, tag.genre, tag.duration
            tracks.append(info)
            if tag.artist is None:
                name = tag.title
                print(name, "--- FILENAME INCORRECT FORMAT ---")
                artist_id, song_id = name.split("-")
                artist_id = artist_id.strip()
                song_id = song_id.strip()
                print(artist_id)
                
        except TinyTagException:
            print("error")
print(tracks)

browser = webdriver.Chrome('C:/Users/Adam/Downloads/chromedriver_win32/chromedriver.exe')
browser.get('http://www.beatport.com')

search = browser.find_element_by_name('q')
search.send_keys("tchami")
search.send_keys(Keys.RETURN) # hit return after you enter search text
time.sleep(5) # sleep for 5 seconds so you can see the results
browser.quit()
