# Version number
lftable_version = '2.0'

# Databases.
db_dir = 'db/'
users_db = db_dir + 'notify_users.db'
times_db = db_dir + 'times.db'

# Directory for the 'token.release' and 'token.dev' files
tokens_dir = 'tokens/'


# Interval for update checks (s).
check_updates_interval = 120

# Class for storing timetable's options.
class TTBS():
    pass

pravo_c1 = TTBS()
pravo_c2 = TTBS()
pravo_c3 = TTBS()
pravo_c4 = TTBS()

pravo_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_1_pravo.xls'
pravo_c1.name = 'Правоведение, 1-й курс'
pravo_c1.shortname = 'pravo_c1'

pravo_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_2_pravo.xls'
pravo_c2.name = 'Правоведение, 2-й курс'
pravo_c2.shortname = 'pravo_c2'

pravo_c3.url = 'https://law.bsu.by/pub/2/Raspisanie_3_pravo.xls'
pravo_c3.name = 'Правоведение, 3-й курс'
pravo_c3.shortname = 'pravo_c3'

pravo_c4.url = 'https://law.bsu.by/pub/2/Raspisanie_4_pravo.xls'
pravo_c4.name = 'Правоведение, 4-й курс'
pravo_c4.shortname = 'pravo_c4'
