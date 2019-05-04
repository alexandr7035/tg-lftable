from static import *
import random
from datetime import datetime
from backend import ttb_gettime

# Main menu text
def main_menu_message():
  
    text = '<b>LFTable v' + lftable_version + '</b>: быстрый доступ к расписанию занятий юридического факультета БГУ.\n\n'
    
    text += 'Источник: https://law.bsu.by\n'
    text += 'Информация об авторских правах юрфака: https://law.bsu.by/avtorskie-prava.html\n'
    
    # Use a string of 15 randomly mixed two space symbols to fix badrequest error.
    space = '\u0020'
    thin_space = '\u2009'
    
    for i in range(1,15):
        if random.randint(0,1) == 1:
            text += space
            #text += '1'
        else:
            #text += '0'
            text += thin_space
    # Newline symbol
    text += '\n'
    
    text += 'Выберите нужное расписание:'

    return(text)


def ttb_message(ttb):
    # Get the timetable's "mtime"
    ttb_datetime = ttb_gettime(ttb)
    
    # Change date to necessary format.
    update_time = ttb_datetime.strftime('%H:%M')
    update_date = ttb_datetime.strftime('%d.%m.%Y')
    
    
    # Form the message's text
    text = '<b>' + ttb.name + '</b>\n\n'
    
    text += 'Дата обновления: ' + update_date + '\n'
    text += 'Время обновления: '+ update_time + '\n\n'

    text += '<b>Скачать</b>: ' + ttb.url + "\n\n"
    
    # To fix badrequest error.
    text += '-------------------\n'
    text += 'Страница обновлена: ' + datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    # Return this text
    return(text)
