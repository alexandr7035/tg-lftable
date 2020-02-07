from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import src.db_classes
import src.static


notifications_db = src.db_classes.NotificationsDB()


def main_menu_keyboard():
    pravo_btn = InlineKeyboardButton('📕 Правоведение', callback_data='pravo_menu')
    ek_polit_btn = InlineKeyboardButton('📗 Эк. право и политология', callback_data='ek_polit_menu')
    mag_btn = InlineKeyboardButton('📒 Магистратура', callback_data='mag_menu')
    ekz_zachet_btn = InlineKeyboardButton('☠️ Зачеты и экзамены', callback_data='ekz_zachet_menu')

    keyboard = [[pravo_btn], [ek_polit_btn], [mag_btn], [ekz_zachet_btn]]

    return(InlineKeyboardMarkup(keyboard))

def pravo_keyboard():
    pravo_c1_btn = InlineKeyboardButton('Правоведение - 1⃣', callback_data=src.static.pravo_c1.shortname)
    pravo_c2_btn = InlineKeyboardButton('Правоведение - 2⃣', callback_data=src.static.pravo_c2.shortname)
    pravo_c3_btn = InlineKeyboardButton('Правоведение - 3⃣', callback_data=src.static.pravo_c3.shortname)
    pravo_c4_btn = InlineKeyboardButton('Правоведение - 4⃣', callback_data=src.static.pravo_c4.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[pravo_c1_btn, pravo_c2_btn],
                [pravo_c3_btn, pravo_c4_btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def ek_polit_keyboard():
    ek_polit_c1_btn = InlineKeyboardButton('Эк. и полит. - 1⃣', callback_data=src.static.ek_polit_c1.shortname)
    ek_polit_c2_btn = InlineKeyboardButton('Эк. и полит. - 2⃣', callback_data=src.static.ek_polit_c2.shortname)
    ek_polit_c3_btn = InlineKeyboardButton('Эк. и полит. - 3⃣', callback_data=src.static.ek_polit_c3.shortname)
    ek_polit_c4_btn = InlineKeyboardButton('Эк. и полит. - 4⃣', callback_data=src.static.ek_polit_c4.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[ek_polit_c1_btn, ek_polit_c2_btn],
                [ek_polit_c3_btn, ek_polit_c4_btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def mag_keyboard():

    mag_c1_btn = InlineKeyboardButton('Магистратура - 1⃣', callback_data=src.static.mag_c1.shortname)
    mag_c2_btn = InlineKeyboardButton('Магистратура - 2⃣', callback_data=src.static.mag_c2.shortname)
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[mag_c1_btn, mag_c2_btn],
                [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def ekz_zachet_keyboard():
    zachet_btn = InlineKeyboardButton('💀 Зачеты', callback_data='zachet_menu')
    ekz_btn = InlineKeyboardButton('☠️ Экзамены', callback_data='ekz_menu')
    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='main_menu')

    keyboard = [[zachet_btn], [ekz_btn], [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def zachet_keyboard():
    zachet_c1_btn = InlineKeyboardButton('Зачеты - 1⃣', callback_data=src.static.zachet_c1.shortname)
    zachet_c2_btn = InlineKeyboardButton('Зачеты - 2️⃣', callback_data=src.static.zachet_c2.shortname)
    zachet_c3_btn = InlineKeyboardButton('Зачеты - 3️⃣', callback_data=src.static.zachet_c3.shortname)
    zachet_c4_btn = InlineKeyboardButton('Зачеты - 4️⃣', callback_data=src.static.zachet_c4.shortname)

    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='ekz_zachet_menu')

    keyboard = [[zachet_c1_btn, zachet_c2_btn], [zachet_c3_btn, zachet_c4_btn], [back_button]]

    return(InlineKeyboardMarkup(keyboard))

def ekz_keyboard():
    ekz_c1_btn = InlineKeyboardButton('Экзамены - 1⃣', callback_data=src.static.ekz_c1.shortname)
    ekz_c2_btn = InlineKeyboardButton('Экзамены - 2️⃣', callback_data=src.static.ekz_c2.shortname)
    ekz_c3_btn = InlineKeyboardButton('Экзамены - 3️⃣', callback_data=src.static.ekz_c3.shortname)
    ekz_c4_btn = InlineKeyboardButton('Экзамены - 4️⃣', callback_data=src.static.ekz_c4.shortname)

    back_button = InlineKeyboardButton('⬅️ Назад', callback_data='ekz_zachet_menu')

    keyboard = [[ekz_c1_btn, ekz_c2_btn], [ekz_c3_btn, ekz_c4_btn], [back_button]]

    return(InlineKeyboardMarkup(keyboard))

# Keyboard for specific timetable.
def answer_keyboard(ttb, user_id):

    # Button to refresh current timetable message (so you don't have to come back to main menu).
    refresh_button = InlineKeyboardButton('🔄 Обновить информацию', callback_data='refresh')

    # For notify function. Adds info to DB.
    notifications_db.connect()
    if notifications_db.check_if_user_notified(user_id, ttb.shortname):
        notify_text = u'🔕 Отключить уведомления'
    else:
        notify_text = u'🔔 Включить уведомления'
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

    back_button = InlineKeyboardButton('⬅️ Назад', callback_data=back_callback)

    keyboard = [[refresh_button],
                [notify_button],
                  [back_button]]

    return(InlineKeyboardMarkup(keyboard))


# Keyboard for a notification. Only one button to show menu again.
def notify_keyboard():

    # MESSAGE IF NOT DELETED FROM THE RELEASE v4.3
    # CALLBACK STRING SHOULD BE CHANGED LATER (saved for backward compatibility)
    show_menu_button = InlineKeyboardButton('📚 Показать меню',  callback_data='delete_notification')

    keyboard = [[show_menu_button]]

    return(InlineKeyboardMarkup(keyboard))
