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

####################################################


# Checks ttb' update time.
def ttb_gettime(ttb):
    
    # Send HTTP response.
    response =  urllib.request.urlopen(ttb.url)
    
    # Get date and time from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])
    
    # Transfer date to datetime format.
    date = list(str(datetime.strptime(native_date, '%d %b %Y %H:%M:%S')))
    print(date)
    
    # Transfer to GMT+3. Prevent "010:00, 011:00" if hour is less than 10.
    hour = str(int(str(date[11]) + str(date[12])) + 3)
    
    if len(hour) == 1:
        hour = '0' + hour

    date[11] = hour[0]
    date[12] = hour[1]
    
    date = ''.join(date)
    
    return(date)



while True:
    
    for ttb in [pravo_c1, pravo_c2, pravo_c3, pravo_c4]:
        print(ttb.name, ttb_gettime(ttb))
        
    
    
    time.sleep(60)
