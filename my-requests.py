import requests
import os
import json

r = requests.get('https://www.wikipedia.org/')
print(r.text)
