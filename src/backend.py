from static import *
import os
import sqlite3

import urllib.request
from datetime import datetime

import pytz
import ssl
from logger import *

# The most important function of the program.
# Get and return timetable's mtime using urllib module.
def ttb_gettime(ttb):


    # THIS IS A HOTFIX TO PREVENT "CERTIFICATE_VERIFY_FAILED" ERROR!
    # DISABLE THIS LATER
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    response =  urllib.request.urlopen(ttb.url, timeout=25, context=ctx)

    # Get date from HTTP header.
    native_date = ' '.join(dict(response.headers)['Last-Modified'].rsplit()[1:-1])

    # Transfer date to normal format.
    gmt_date = datetime.strptime(native_date, '%d %b %Y %H:%M:%S')

    # Transfer date to our timezone (GMT+3).
    old_tz = pytz.timezone('Europe/London')
    new_tz = pytz.timezone('Europe/Minsk')

    date = old_tz.localize(gmt_date).astimezone(new_tz)

    return(date)


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

        update_time = ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')

        cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable.shortname,));

    conn.commit()
    conn.close()


# Collecting statistics.
# Writes uniq user ids to 'statistics.db'
def send_statistics(user_id):
    conn = sqlite3.connect(statistics_db)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM uniq_users')
    result = cursor.fetchall()

    # List of user_ids in the db
    uniq_users = []
    for i in result:
        uniq_users.append(i[0])

    # Add new user to the db
    if user_id not in uniq_users:
        cursor.execute('INSERT INTO uniq_users VALUES (?)', (user_id,))
        conn.commit()
        # Write to log
        logger.info("a new user "  + str(user_id) + " added to 'statistics.db'")

    conn.close()


# Checks if user is notified when timetable is updated.
# Used to set text on the "notify" button.
def check_user_notified(ttb, user_id):

    # Connect to users db.
    conn = sqlite3.connect(notifications_db)
    cursor = conn.cursor()

    cursor.execute('SELECT users FROM ' + ttb.shortname)
    result = cursor.fetchall()

    conn.close()

    # List for users notifed about current ttb updates.
    users_to_notify = []
    for i in result:
       users_to_notify.append(i[0])


    if str(user_id) in users_to_notify:
           return True
    else:
           return False
