#!./lftable-venv/bin/python3
import telegram

import urllib.request
from datetime import datetime

import os
import time

# See common_data.py to understant how it works.
from common_data import *

# Use dev token
token_to_use = 'token.dev'
#token_to_use = 'token.release'



# If there's no 'tokens' directory.
if not os.path.exists('tokens/'):
    print("You should create 'tokens/' dir and put 'token.dev' or 'token.release' file there. Exit")
    exit()

# If there is no token file.
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
