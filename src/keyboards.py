from src.static import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.db_classes import NotificationsDB

notifications_db = NotificationsDB()

# Main menu keyboard.
# 4 buttons in main menu. Each button is designed for the corresponding timetable (1-4 course)
def main_menu_keyboard():

    pravo_c1.btn = InlineKeyboardButton('Правоведение - 1⃣', callback_data=pravo_c1.shortname)
    pravo_c2.btn = InlineKeyboardButton('Правоведение - 2⃣', callback_data=pravo_c2.shortname)
    pravo_c3.btn = InlineKeyboardButton('Правоведение - 3⃣', callback_data=pravo_c3.shortname)
    pravo_c4.btn = InlineKeyboardButton('Правоведение - 4⃣', callback_data=pravo_c4.shortname)

    mag_c1.btn = InlineKeyboardButton('Магистратура - 1⃣', callback_data=mag_c1.shortname)
    mag_c2.btn = InlineKeyboardButton('Магистратура - 2⃣', callback_data=mag_c2.shortname)

    keyboard = [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [mag_c1.btn, mag_c2.btn]]

    return(InlineKeyboardMarkup(keyboard))



# Menu for specific timetable. One button returns to main menu, one refreshes date and time info.
def answer_keyboard(ttb, user_id):

    # Button to refresh current answer menu (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить страницу', callback_data='refresh')

    # For notify function. Adds info to DB.
    notifications_db.connect()
    if notifications_db.check_if_user_notified(ttb, user_id):
        notify_text = u'🔕 Не уведомлять'
    else:
        notify_text = u'🔔 Уведомлять'
    notifications_db.close()

    # Button to put user id into db in order to notify him when the timetable is updated.
    notify_button = InlineKeyboardButton(notify_text, callback_data='notify')

    # Sends user back to the main menu.
    back_button = InlineKeyboardButton('⬅️ Назад в меню', callback_data='main_menu')

    keyboard = [[refresh_button],
                [notify_button],
                  [back_button]]

    return(InlineKeyboardMarkup(keyboard))


# Keyboard for a notification. Only one button to delete message.
def notify_keyboard():

    del_notification_button = InlineKeyboardButton('Скрыть уведомление',  callback_data='delete_notification')

    keyboard = [[del_notification_button]]

    return(InlineKeyboardMarkup(keyboard))
