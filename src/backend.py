from src.static import *
import os
import sqlite3

import urllib.request
from datetime import datetime

import pytz
import ssl
from src.logger import *
import src.gettime

# Create necessary project dirs and files.
# (See 'static.py' for values of the variables)
def first_run_check():

    try:
        os.mkdir(db_dir)
        # Write to log
        logger.info("'" + db_dir + "' directory was created")
    except Exception:
        pass

    try:
        os.mkdir(tokens_dir)
        # Write to log
        logger.info("'" + tokens_dir + "' directory was created")
    except Exception:
        pass


    # Create database for users notified about timetables' updates.
    # 4 tables for each timetable, each with 'users' column
    if not os.path.exists(notifications_db):
        conn = sqlite3.connect(notifications_db)
        cursor = conn.cursor()

        # Write to log
        logger.info("'" + notifications_db + "' database was created")

        for timetable in all_timetables:
            cursor.execute('CREATE TABLE ' + timetable.shortname + ' (users)')

        conn.commit()
        conn.close()


    # Create database to store the last update time of each timetable
    # 1 table, 4 rows (1 for each timetable), 2 columns (ttb name and the time of last update)
    if not os.path.exists(times_db):

        conn = sqlite3.connect(times_db)
        cursor = conn.cursor()

        # Write to log
        logger.info("'" + times_db + "' database was created")

        cursor.execute('CREATE TABLE times (ttb, time)')
        conn.commit()

        for timetable in all_timetables:
            cursor.execute('INSERT INTO times VALUES ("' + timetable.shortname + '", "")')

        conn.commit()
        conn.close()


    # Database for statistics.
    if not os.path.exists(statistics_db):
        conn = sqlite3.connect(statistics_db)

        # Write to log
        logger.info("'" + statistics_db + "' database was created")

        cursor = conn.cursor()

        cursor.execute('CREATE TABLE uniq_users (users)')

        conn.commit()
        conn.close()



# Sets times to the 'times.db' immediately after the run WITHOUT notifiying users
# Prevents late notifications if the program was down for a long time.
def db_set_times_after_run():
    conn = sqlite3.connect(times_db)
    cursor = conn.cursor()

    for timetable in all_timetables:

        update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')

        cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable.shortname,));

    conn.commit()
    conn.close()
