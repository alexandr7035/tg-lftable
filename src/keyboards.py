from src.static import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.db_classes import NotificationsDB

notifications_db = NotificationsDB()


def main_menu_keyboard():
    pravo_btn = InlineKeyboardButton('📌 Правоведение', callback_data='pravo_menu')
    ek_polit_btn = InlineKeyboardButton('📌 Эк. право и политология', callback_data='ek_polit_menu')
    mag_btn = InlineKeyboardButton('📌 Магистратура', callback_data='mag_menu')

    keyboard = [[pravo_btn], [ek_polit_btn], [mag_btn]]

    return(InlineKeyboardMarkup(keyboard))

def pravo_keyboard():
    pravo_c1.btn = InlineKeyboardButton('Правоведение - 1⃣', callback_data=pravo_c1.shortname)
    pravo_c2.btn = InlineKeyboardButton('Правоведение - 2⃣', callback_data=pravo_c2.shortname)
    pravo_c3.btn = InlineKeyboardButton('Правоведение - 3⃣', callback_data=pravo_c3.shortname)
    pravo_c4.btn = InlineKeyboardButton('Правоведение - 4⃣', callback_data=pravo_c4.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[pravo_c1.btn, pravo_c2.btn],
                [pravo_c3.btn, pravo_c4.btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def ek_polit_keyboard():
    ek_polit_c1.btn = InlineKeyboardButton('Эк. право и политология - 1⃣', callback_data=ek_polit_c1.shortname)
    ek_polit_c2.btn = InlineKeyboardButton('Эк. право и политология - 2⃣', callback_data=ek_polit_c2.shortname)
    ek_polit_c3.btn = InlineKeyboardButton('Эк. право и политология - 3⃣', callback_data=ek_polit_c3.shortname)
    ek_polit_c4.btn = InlineKeyboardButton('Эк. право и политология - 4⃣', callback_data=ek_polit_c4.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[ek_polit_c1.btn, ek_polit_c2.btn],
                [ek_polit_c3.btn, ek_polit_c4.btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def mag_keyboard():

    mag_c1.btn = InlineKeyboardButton('Магистратура - 1⃣', callback_data=mag_c1.shortname)
    mag_c2.btn = InlineKeyboardButton('Магистратура - 2⃣', callback_data=mag_c2.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[mag_c1.btn, mag_c2.btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))


# Menu for specific timetable. One button returns to main menu, one refreshes date and time info.
def answer_keyboard(ttb, user_id):

    # Button to refresh current answer menu (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить страницу', callback_data='refresh')

    # For notify function. Adds info to DB.
    notifications_db.connect()
    if notifications_db.check_if_user_notified(user_id, ttb.shortname):
        notify_text = u'🔕 Не уведомлять'
    else:
        notify_text = u'🔔 Уведомлять'
    notifications_db.close()

    # Button to put user id into db in order to notify him when the timetable is updated.
    notify_button = InlineKeyboardButton(notify_text, callback_data='notify')

    # Set back_callback to send user to previous menu 
    if ttb.shortname.startswith('pravo'):
        back_callback = 'pravo_menu'
    elif ttb.shortname.startswith('mag'):
        back_callback = 'mag_menu'
    elif ttb.shortname.startswith('ek_polit'):
        back_callback = 'ek_polit_menu'

    back_button = InlineKeyboardButton('⬅️ Назад в меню', callback_data=back_callback)

    keyboard = [[refresh_button],
                [notify_button],
                  [back_button]]

    return(InlineKeyboardMarkup(keyboard))


# Keyboard for a notification. Only one button to delete message.
def notify_keyboard():

    del_notification_button = InlineKeyboardButton('Скрыть уведомление',  callback_data='delete_notification')

    keyboard = [[del_notification_button]]

    return(InlineKeyboardMarkup(keyboard))
