from static import *
import random

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
