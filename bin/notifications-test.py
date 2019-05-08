#!/usr/bin/env python3

# This script sets old times to the 'times.db' 
# in order to test notifications if any timetable was updated

import sys
# Add src/' directory with local modules to path
sys.path.append('../src')

import os


# The script should be run only from 'bin/' directory
if os.getcwd() != os.path.dirname(os.path.realpath(sys.argv[0])):
    print('Error. Go to the \'bin/\' directory and run the script there. Exit')
    sys.exit()
    
import sqlite3
# Database with upate times of each timetable
from static import times_db
# List of all timetables
from static import all_timetables

conn = sqlite3.connect("../" + times_db)
cursor = conn.cursor()

# Set wrong old times to the times db in order to check whether notifications work correctly
for ttb in all_timetables:
    cursor.execute("UPDATE times SET time = '01.01.2001 00:00:00' WHERE ttb = ?", (ttb.shortname,))

conn.commit()
conn.close()

