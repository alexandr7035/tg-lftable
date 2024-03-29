#!/usr/bin/env python3

import os
import sys
import time
import sqlite3
import argparse
import pytz
from datetime import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, JobQueue, Filters
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

        logger.info("-")
        logger.info("the program was STARTED now")

        # Import src/tokens.py
        # There should be 2 variables (token strings): 'develop' and 'release'
        try:
            import src.tokens
        except ImportError:
            print('No tokens file. Exit.')
            logger.critical("can't import 'tokens.py', exit.")
            sys.exit()

        # Change directory to the one in wich the script is located
        # This is necessary in order to correctly create 'db/' and 'log/' directories
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Objects to access the databases
        self.timesdb = src.db_classes.TimesDB()
        self.notificationsdb = src.db_classes.NotificationsDB()
        self.statisticsdb = src.db_classes.StatisticsDB()

        # Create necessary directories and files
        self.prepare_workspace()
        # Parse command-line arguments
        self.parse_arguments()


    # This method creates necessary directories and files
    def prepare_workspace(self):

        # Create directory for sqlite3 databases
        if not os.path.exists(src.static.db_dir):
            os.mkdir(src.static.db_dir)

        # Create databases. See db_classes.py
        if not os.path.isfile(src.static.timesdb_path):
            self.timesdb.connect()
            self.timesdb.construct()
            self.timesdb.close()

            logger.info("'" + src.static.timesdb_path + "' database was created")

        if not os.path.isfile(src.static.notificationsdb_path):
            self.notificationsdb.connect()
            self.notificationsdb.construct()
            self.notificationsdb.close()

            logger.info("'" + src.static.notificationsdb_path + "' database was created")

        if not os.path.isfile(src.static.statisticsdb_path):
            self.statisticsdb.connect()
            self.statisticsdb.construct()
            self.statisticsdb.close()

            logger.info("'" + src.static.statisticsdb_path + "' database was created")


    # Parse command-line arguments
    def parse_arguments(self):

        parser = argparse.ArgumentParser(description="tg-lftable: telegram bot which provides an easy way to get the law faculty's timetable (BSU).")

        # See src/logger.py (log_exceptions() function)
        parser.add_argument('--log-exceptions', action='store_true')
        # See src/test_notifications.py (test_notifications() function)
        parser.add_argument('--test-notifications', action='store_true')

        required_arg = parser.add_argument_group(title='required arguments')
        # Responsible for choosing a token (either 'develop' or 'release')
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

        # Get token depending on --mode parameter
        try:
            self.bot_token = getattr(src.tokens, self.args.mode)
        except AttributeError:
            logger.critical("no '" + self.args.mode + "' token string variable in tokens.py file, exit")
            print("no '" + self.args.mode + "' token string variable in tokens.py file, exit")

        # Log exceptions (see src/logger.py)
        if self.args.log_exceptions == True:
            log_exceptions()


    # Receives 'update.message.date' in pure form
    # Compares current time with request time 
    # True, if the differance is less than or equal to 'src.static.max_request_delay'
    # Used in command and message handlers 
    #+ to skip old requests if bot was down for some time to prevent spam
    # TRUE IF REQUEST IS LATE !!!
    def check_if_request_late(self, request_date):

        # Convert it to GMT+3
        old_tz = pytz.timezone('GMT')
        new_tz = pytz.timezone('Europe/Minsk')
        gmt3_request_date = old_tz.localize(request_date).astimezone(new_tz)
        
        # Get unix timestamp from gmt3_request_date)
        gmt3_request_unixtime = time.mktime(gmt3_request_date.timetuple())

        # Compare current time with request time 
        request_delay = time.time() - gmt3_request_unixtime

        if request_delay >= src.static.max_request_delay:
            return True
        else:
            return False


    # Sends main menu on '/start' command
    def handle_start_command(self, update, context):

        user_id = update.message.chat_id

        # Add a new user to statistics.db
        self.statisticsdb.connect()
        if user_id not in self.statisticsdb.get_unique_users():
            self.statisticsdb.add_unique_user(user_id)
            logger.info('add unique user ' + str(user_id))
        self.statisticsdb.close()

        # Skip late requests, see self.check_if_request_late metod
        if self.check_if_request_late(update.message.date):
            logger.info('skip old /start command from user ' + str(user_id))
        # Handle the request
        else:
            logger.info('user ' + str(user_id) + ' entered /start command')

            update.message.reply_text(src.messages.main_menu_message(),
                            reply_markup=src.keyboards.main_menu_keyboard(),
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            timeout=10)
    

    # '/stop' command
    def handle_stop_command(self, update, context):
        user_id = str(update.message.chat_id)

        # Check for late requests
        if self.check_if_request_late(update.message.date):
            logger.info('skip old /stop command from user ' + str(user_id))
        else:
            logger.info('user ' + str(user_id) + ' entered \'stop\' command, disable all notifications')
            self.notificationsdb.connect()
        
            # Disable all notifications for user
            for timetable in src.static.all_timetables:
                if self.notificationsdb.check_if_user_notified(user_id, timetable.shortname):
                    logger.info('stop command recived: disable \'' + timetable.shortname + '\' notifications for user ' + str(user_id))
                    self.notificationsdb.disable_notifications(user_id, timetable.shortname)

            self.notificationsdb.close()

            update.message.reply_text(src.messages.stop_message(),
                              parse_mode=ParseMode.HTML,
                              disable_web_page_preview=True,
                              timeout=10)


    # Handle any received text message EXCEPT telegram commands -
    # (except messages started with '/' like '/start').
    # Just send info message how to start the bot.
    def handle_text_commands(self, update, context):
        user_id = update.message.chat_id
        
        # Skip late requests, see self.check_if_request_late metod
        if self.check_if_request_late(update.message.date):
            logger.info('skip old command \'' + update.message.text + '\' from user ' + str(user_id))
            # EXIT
            return
        # Handle the request
        else: 
            logger.info('user ' + str(user_id) + ' entered \'' + update.message.text + '\' command')
            context.bot.send_message(chat_id=user_id,
                                 text=src.messages.no_such_command_message())


    # This method is called if ANY button is pressed
    def handle_button_click(self, update, context):
        query = update.callback_query

        # Each button has its own callback, see src/keyboards.py
        callback = query.data
        # User who pressed the button
        user_id = str(query.message.chat_id)

        # Message to edit
        message_id = query.message.message_id
        # Message text (for 'notify' and 'refresh' buttons to detect timetable name)
        message_text = query.message.text

        logger.debug('user ' + user_id + ' pressed button \'' + callback + '\'')

        # Main menu (for 'back' button)
        if callback == 'main_menu':
            context.bot.edit_message_text(chat_id=user_id,
                        message_id=message_id,
                        text=src.messages.main_menu_message(),
                        parse_mode=ParseMode.HTML,
                        reply_markup=src.keyboards.main_menu_keyboard(),
                        disable_web_page_preview=True,
                        timeout=10)

        # Menus for specializations
        elif callback in ['pravo_menu', 'ek_polit_menu', 'mag_menu', 'ekz_zachet_menu', 'zachet_menu', 'ekz_menu']:
            self.show_timetable_menu(context.bot, callback, user_id, message_id)

        # Messagess for certain timetables
        elif callback in ['pravo_c1', 'pravo_c2', 'pravo_c3', 'pravo_c4',
                          'ek_polit_c1', 'ek_polit_c2', 'ek_polit_c3', 'ek_polit_c4',
                          'zachet_c1', 'zachet_c2', 'zachet_c3', 'zachet_c4',
                          'ekz_c1', 'ekz_c2', 'ekz_c3', 'ekz_c4',
                          'mag_c1', 'refresh', 'notify']:
            self.show_timetable_message(context.bot, callback, user_id, message_id, message_text)

        # Since we cannot delete messages older than 48 hours,
        # the "Delete notification" button now just sends the main menu
        if callback == 'delete_notification':
            logger.info('user ' + str(user_id) + " used 'show_menu_button' from a notification (message: " + str(query.message.message_id) + ")")
            context.bot.send_message(chat_id=user_id,
                             text=src.messages.main_menu_message(),
                             reply_markup=src.keyboards.main_menu_keyboard(),
                             disable_web_page_preview=True,
                             parse_mode=ParseMode.HTML)


    # Menus for specializations or credits/exams
    def show_timetable_menu(self, bot, callback, user_id, message_id):
        if callback == 'pravo_menu':
            keyboard = src.keyboards.pravo_keyboard()
        elif callback == 'mag_menu':
            keyboard = src.keyboards.mag_keyboard()
        elif callback == 'ek_polit_menu':
            keyboard = src.keyboards.ek_polit_keyboard()
        
        # This menu has 2 submenus
        # Credit/exam timetables are separated and ech have its own menu
        elif callback == 'ekz_zachet_menu':
            keyboard = src.keyboards.ekz_zachet_keyboard()
        # The submenus
        elif callback == 'zachet_menu':
            keyboard = src.keyboards.zachet_keyboard()
        elif callback == 'ekz_menu':
            keyboard = src.keyboards.ekz_keyboard()

        bot.edit_message_text(chat_id=user_id,
                        message_id=message_id,
                        text=src.messages.main_menu_message(),
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard,
                        disable_web_page_preview=True,
                        timeout=10)

    
    # Message for certain timetable
    def show_timetable_message(self, bot, callback, user_id, message_id, message_text):

        # If 'refresh' or 'notify' button is pressed the only way to detect timetable (to show this message again)
        # is to parse message text
        if callback in ['refresh', 'notify']:
            # Detect the timetable checking first line of the timetable message
            for ttb in src.static.all_timetables:
                if message_text.split('\n')[0] == ttb.name:
                    timetable_to_show = ttb
        else:
            timetable_to_show = getattr(src.static, callback)

        # Handle notify button (write to db)
        # See src.db_classes.NotificationsDB() methods 
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
                        text=src.messages.timetable_message(timetable_to_show),
                        parse_mode=ParseMode.HTML,
                        reply_markup=src.keyboards.timetable_keyboard(timetable_to_show, user_id), timeout=10)


    # A timejob for notifications
    def notifications_timejob(self, context):

        # Connect to the times.db
        self.timesdb.connect()

        # See 'all_timetables' list in 'src/static.py'
        for checking_ttb in src.static.all_timetables:

            # Get ttb update time from law.bsu.by
            # Use different gettime functions for ussual and credit/exam timetables. See src.gettime.py
            if checking_ttb in src.static.credit_exam_timetables:
                data = src.gettime.credit_exam_gettime(checking_ttb)
                update_time = data['time'].strftime('%d.%m.%Y %H:%M:%S')
                timetable_url = data['url']
            else:
                update_time = src.gettime.ttb_gettime(checking_ttb).strftime('%d.%m.%Y %H:%M:%S')
                timetable_url = checking_ttb.url

            # Get old update time from db.
            old_update_time = self.timesdb.get_time(checking_ttb.shortname)

            # Convert string dates to datetime objects
            dt_update_time = datetime.strptime(update_time, '%d.%m.%Y %H:%M:%S')
            dt_old_update_time = datetime.strptime(old_update_time, '%d.%m.%Y %H:%M:%S')

            # Compare the two dates
            # If the timetable was updated, sends it to all users
            #+ from certain table in 'users.db'
            if dt_update_time > dt_old_update_time:

                logger.info("'" + checking_ttb.shortname + "' timetable was updated at " + update_time)
                
                # Get list of users who enabled notifications for this timetable
                self.notificationsdb.connect()
                users_to_notify = self.notificationsdb.get_notified_users(checking_ttb.shortname)
                self.notificationsdb.close()

                # Send a notification to each user.
                for user_id in users_to_notify:

                    try:
                        context.bot.send_message(chat_id=user_id,
                                         text=src.messages.notification_message(checking_ttb, dt_update_time, timetable_url),
                                         reply_markup=src.keyboards.notify_keyboard(),
                                         parse_mode=ParseMode.HTML)
                    # If user blocked this bot & etc...
                    except Exception as e:
                        logger.info("can't send '" + checking_ttb.shortname + "' notification to user " + user_id + ", skip")
                        continue

                    logger.info("'" + checking_ttb.shortname + "' notification was sent to user " + user_id)

                    # A delay to prevent any spam control exceptions
                    time.sleep(src.static.send_message_interval)

                # Write new update time to the database.
                self.timesdb.write_time(checking_ttb.shortname, update_time)

            # A delay to prevent any spam control exceptions
            time.sleep(src.static.site_requests_interval)

        # Close 'times.db' until next check.
        self.timesdb.close()


    # Method that runs the bot
    def start(self):
        
        # Sets times to the 'times.db' immediately after the run WITHOUT notifiying users
        # This is to prevent late notifications if the bot was down for a long time
        self.timesdb.connect()
        for timetable in src.static.all_timetables:
            # There is separate gettime function for credits and exams
            if timetable in src.static.credit_exam_timetables:
                update_time = src.gettime.credit_exam_gettime(timetable)['time'].strftime('%d.%m.%Y %H:%M:%S')
            # Function for usual timetables
            else:
                update_time = src.gettime.ttb_gettime(timetable).strftime('%d.%m.%Y %H:%M:%S')
            
            # Write time to the db
            self.timesdb.write_time(timetable.shortname, update_time)
        self.timesdb.close()
        

        # Start notifcations test immediatly after the run if '--test-notificztions' option is specified
        if self.args.test_notifications == True:
            src.test_notifications.test_notifications()

        self.updater = Updater(self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

         # Run timejob for notificatins
         # First run within 5 seconds after the start
        job = self.updater.job_queue

        job.run_repeating(self.notifications_timejob, interval = src.static.check_updates_interval, first=5)

        self.dispatcher.add_handler(CommandHandler('start', self.handle_start_command))
        self.dispatcher.add_handler(CommandHandler('stop', self.handle_stop_command))
        self.dispatcher.add_handler(CallbackQueryHandler(self.handle_button_click))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.handle_text_commands))

        # Checking for updates.
        self.updater.start_polling(clean=False)
        self.updater.idle()


if __name__ == "__main__":
    lftable = LFTableBot()
    lftable.start()
