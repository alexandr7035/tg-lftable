#!./lftable-venv/bin/python3
import telegram

import urllib.request
from datetime import datetime

import os
import time

# Use dev token
token_to_use = 'token.dev'
#token_to_use = 'token.release'

try:
    token_file = open('tokens/' + token_to_use) 
except Exception:
    print("No token file \'" + token_to_use + "\'. You should put it into 'tokens/' dir. Exit.")
    exit()


# Read token
token_str = token_file.readline()[:-1] 
token_file.close()

bot = telegram.Bot(token=token_str)

while True:
	
	
	
	time.sleep(60)
