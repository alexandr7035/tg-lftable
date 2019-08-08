#!/usr/bin/env python3

import os
import sys
import time
import sqlite3
import argparse
from datetime import datetime

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

# Import all local modules, see 'src/' directory
import src.db_classes
import src.gettime
import src.static
import src.messages
import src.keyboards
import src.test_notifications

# Logging to 'lftable.log'
# Add '--log-exceptions' option to script to log exceptions ('lftable-exceptions.log')
from src.logger import *


class LFTableBot():
    def __init__(self):

        # Start message
        logger.info("-")
        logger.info("the program was STARTED now")

        # Import src/tokens.py
        try:
            import src.tokens
        except ImportError:
            print('No tokens file. Exit.')
            logger.critical("can't import 'tokens.py', exit.")
            sys.exit()

        # Change directory to the one in wich the script is located
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()

        self.prepare_workspace()
        self.parse_arguments()

    # This method creates necessary directories and files
    def prepare_workspace(self):

        # Create directory for sqlite3 databases
        if not os.path.exists(src.static.db_dir):
            os.mkdir(db_dir)

        # Create databases. See db_classes.py
        if not os.path.isfile(src.static.times_db):
            self.timesdb.connect()
            self.timesdb.construct()
            self.timesdb.close()

            logger.info("'" + src.static.times_db + "' database was created")

        if not os.path.isfile(src.static.notifications_db):
            self.notificationsdb.connect()
            self.notificationsdb.construct()
            self.notificationsdb.close()

            logger.info("'" + src.static.notifications_db + "' database was created")

        if not os.path.isfile(src.static.statistics_db):
            self.statisticsdb.connect()
            self.statisticsdb.construct()
            self.statisticsdb.close()

            logger.info("'" + src.static.statistics_db + "' database was created")

    # Parse command-line arguments
    def parse_arguments(self):

        parser = argparse.ArgumentParser(description="tg-lftable: telegram bot which provides an easy way to get the law faculty's timetable (BSU).")

        parser.add_argument('--log-exceptions', action='store_true')
        parser.add_argument('--test-notifications', action='store_true')

        required_arg = parser.add_argument_group(title='required arguments')
        required_arg.add_argument('--mode',
                                  type=str,
                                  help='Either \'release\' or \'development\' string. The bot starts with the corresponding token',
                                  required=True)

        self.args = parser.parse_args()

        if self.args.mode == 'release':
            print("Started in 'release' mode")

        elif self.args.mode == 'develop':
            print("Started in 'develop' mode")

        else:
            print("Invalid mode specified. Use either 'release' or 'develop' string.' Exit.")
            sys.exit()

        # get token depending on --mode parameter
        try:
            self.bot_token = getattr(src.tokens, self.args.mode)
        except AttributeError:
            logger.critical("no '" + self.args.mode + "' token string variable in tokens.py file, exit")
            print("no '" + self.args.mode + "' token string variable in tokens.py file, exit")

        # Log exceptions
        if self.args.log_exceptions == True:
            log_exceptions()

    # Sends main menu on '/start' command
    def handle_start_command(self, bot, update):
        update.message.reply_text(src.messages.main_menu_message(),
                                  reply_markup=src.keyboards.main_menu_keyboard(),
                                  parse_mode=ParseMode.HTML,
                                  timeout=10)

    def handle_button_click(self, bot, update):
        query = update.callback_query

        # Each button has its own callback, see src/keyboards.py
        callback = query.data
        # User who pressed the button
        user_id = str(query.message.chat_id)

        # Message to edit
        message_id = query.message.message_id
        # Message text (for 'notify' and 'refresh' buttons to detect timetable name)
        message_text = query.message.text

        if callback == 'main_menu':
            bot.edit_message_text(chat_id=user_id,
                        message_id=message_id,
                        text=src.messages.main_menu_message(),
                        parse_mode=ParseMode.HTML,
                        reply_markup=src.keyboards.main_menu_keyboard(), timeout=10)

        elif callback in ['pravo_menu', 'ek_polit_menu', 'mag_menu']:
            self.show_timetable_menu(bot, callback, user_id, message_id)

        elif callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                          'ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4',
                        'mag_c1', 'mag_c2', 'refresh', 'notify']:
            self.show_timetable_message(bot, callback, user_id, message_id, message_text)

        if callback == 'delete_notification':
            # Deletes notification message if 'delete' button is pressed.
            bot.delete_message(user_id, message_id)
            # Write to log
            logger.info('user ' + str(user_id) + " deleted notification (message: " + str(query.message.message_id) + ")")


    def show_timetable_message(self, bot, callback, user_id, message_id, message_text):

        if callback in ['refresh', 'notify']:
            # Detect the timetable checking first line of the ttb message
            for ttb in src.static.all_timetables:
                if message_text.split('\n')[0] == ttb.name:
                    timetable_to_show = ttb
        else:
            timetable_to_show = getattr(src.static, callback)

        # Handle notify button
        if callback == 'notify':
            self.notificationsdb.connect()
            if not self.notificationsdb.check_if_user_notified(user_id, timetable_to_show.shortname):
                self.notificationsdb.enable_notifications(user_id, timetable_to_show.shortname)
                logger.info('user ' + user_id + " enabled notifications for the '" + timetable_to_show.shortname + "' timetable")
            else:
                self.notificationsdb.disable_notifications(user_id, timetable_to_show.shortname)
                logger.info('user ' + user_id + " disabled notifications for the '" + timetable_to_show.shortname + "' timetable")
            self.notificationsdb.close()

        bot.edit_message_text(chat_id=user_id,
                        message_id=message_id,
                        text=src.messages.ttb_message(timetable_to_show),
                        # Used for bold font
                        parse_mode=ParseMode.HTML,
                        reply_markup=src.keyboards.answer_keyboard(timetable_to_show, user_id), timeout=10)

    def show_timetable_menu(self, bot, callback, user_id, message_id):
        if callback == 'pravo_menu':
            keyboard = src.keyboards.pravo_keyboard()
        elif callback == 'mag_menu':
            keyboard = src.keyboards.mag_keyboard()
        elif callback == 'ek_polit_menu':
            keyboard = src.keyboards.ek_polit_keyboard()

        bot.edit_message_text(chat_id=user_id,
                        message_id=message_id,
                        text=src.messages.main_menu_message(),
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard, timeout=10)

    # A timejob for notifications
    def notifications_timejob(self, bot, job):

        # Connect to the times.db
        self.timesdb.connect()

        # See 'all_timetables' list in 'src/static.py'
        for checking_ttb in src.static.all_timetables:

            # Get ttb update time from law.bsu.by
            update_time = src.gettime.ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')

            # Get old update time from db.
            old_update_time = self.timesdb.get_time(checking_ttb.shortname)

            # Convert string dates to datetime objects
            dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
            dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')

            # Compare the two dates
            # If the timetable was updated, sends it to all users
            #+ from certain table in 'users.db'
            if dt_update_time > dt_old_update_time:

                # Write to log
                logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)

                self.notificationsdb.connect()
                users_to_notify = self.notificationsdb.get_notified_users(checking_ttb.shortname)
                self.notificationsdb.close()

                # Send a notification to each user.
                for user_id in users_to_notify:

                    try:
                        bot.send_message(chat_id=user_id,
                                         text=src.messages.notification_message(checking_ttb, dt_update_time),
                                         reply_markup=src.keyboards.notify_keyboard(),
                                         parse_mode=ParseMode.HTML)
                    except Exception as e:
                        print(e)
                        # Write to log
                        logger.info("can't send '" + checking_ttb.shortname + "' notification to user " + user_id + ", skip")
                        continue

                    # Write to log
                    logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + user_id)

                    # A delay to prevent any spam control exceptions
                    time.sleep(src.static.send_message_interval)

                # Write new update time to the database.
                self.timesdb.write_time(checking_ttb.shortname, update_time)

            # A delay to prevent any spam control exceptions
            time.sleep(src.static.send_message_interval)

        # Close 'times.db' until next check.
        self.timesdb.close()

    def start(self):
        # Sets times to the 'times.db' immediately after the run WITHOUT notifiying users
        # This is to prevent late notifications if the bot was down for a long time
        self.timesdb.connect()
        for timetable in src.static.all_timetables:
            update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
            self.timesdb.write_time(timetable.shortname, update_time)
        self.timesdb.close()

        if self.args.test_notifications == True:
            src.test_notifications.test_notifications()


        self.updater = Updater(self.bot_token)
        self.dispatcher = self.updater.dispatcher

         # Run timejob for notificatins
        job = self.updater.job_queue
        job.run_repeating(self.notifications_timejob, interval = src.static.check_updates_interval, first=0)

        self.dispatcher.add_handler(CommandHandler('start', self.handle_start_command))
        self.dispatcher.add_handler(CallbackQueryHandler(self.handle_button_click))

        # Checking for updates.
        self.updater.start_polling(clean=False)
        self.updater.idle()


if __name__ == "__main__":
    lftable = LFTableBot()
    lftable.start()
