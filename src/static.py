# Version number
lftable_version = '5.0.3'

# Python module with tokens
tokens_file = 'src/tokens.py'

# Logs
log_dir = 'log/'

# Databases.
db_dir = 'db/'
notificationsdb_path = db_dir + 'notifications.db'
timesdb_path = db_dir + 'times.db'
statisticsdb_path = db_dir + 'statistics.db'


# Intervals for update checks and notifications (s).
check_updates_interval = 120
send_message_interval = 0.05
site_requests_interval = 0.5
max_request_delay = 5

# Class for storing timetable's options.
class TTBS():
    pass

# All types of timetables
pravo_c1 = TTBS()
pravo_c2 = TTBS()
pravo_c3 = TTBS()
pravo_c4 = TTBS()
mag_c1 = TTBS()
mag_c2 = TTBS()
ek_polit_c1 = TTBS()
ek_polit_c2 = TTBS()
ek_polit_c3 = TTBS()
ek_polit_c4 = TTBS()


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

ek_polit_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_1_ek_polit.xls'
ek_polit_c1.name = 'Экономическое право и политология, 1-й курс'
ek_polit_c1.shortname = 'ek_polit_c1'

ek_polit_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_2_ek_polit.xls'
ek_polit_c2.name = 'Экономическое право и политология, 2-й курс'
ek_polit_c2.shortname = 'ek_polit_c2'

ek_polit_c3.url = 'https://law.bsu.by/pub/2/Raspisanie_3_ek_polit.xls'
ek_polit_c3.name = 'Экономическое право и политология, 3-й курс'
ek_polit_c3.shortname = 'ek_polit_c3'

ek_polit_c4.url = 'https://law.bsu.by/pub/2/Raspisanie_4_ek_polit.xls'
ek_polit_c4.name = 'Экономическое право и политология, 4-й курс'
ek_polit_c4.shortname = 'ek_polit_c4'

mag_c1.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_1_kurs_1s.xlsx'
mag_c1.name = 'Магистратура, 1-й курс'
mag_c1.shortname = 'mag_c1'

mag_c2.url = 'https://law.bsu.by/pub/2/Raspisanie_mag_2_kurs.xls'
mag_c2.name = 'Магистратура, 2-й курс'
mag_c2.shortname = 'mag_c2'


# This part is for credits and exams
# The complication caused by division into summer and 
# winter exam/credit timetable files on the site

zachet_c1 = TTBS()
ekz_c1 = TTBS()
zachet_c2 = TTBS()
ekz_c2 = TTBS()
zachet_c3 = TTBS()
ekz_c3 = TTBS()
zachet_c4 = TTBS()
ekz_c4 = TTBS()

zachet_c1.name = 'Зачеты, 1-й курс'
zachet_c1.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_zachet_1k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_zachet_1k.xls'}
zachet_c1.shortname = 'zachet_c1'

ekz_c1.name = 'Экзамены, 1-й курс'
ekz_c1.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_ekz_1k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_ekz_1k.xls'}
ekz_c1.shortname = 'ekz_c1'


zachet_c2.name = 'Зачеты, 2-й курс'
zachet_c2.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_zachet_2k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_zachet_2k.xls'}
zachet_c2.shortname = 'zachet_c2'

ekz_c2.name = 'Экзамены, 2-й курс'
ekz_c2.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_ekz_2k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_ekz_2k.xls'}
ekz_c2.shortname = 'ekz_c2'


zachet_c3.name = 'Зачеты, 3-й курс'
zachet_c3.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_zachet_3k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_zachet_3k.xls'}
zachet_c3.shortname = 'zachet_c3'

ekz_c3.name = 'Экзамены, 3-й курс'
ekz_c3.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_ekz_3k.xls',
                  'summer' : 'https://law.bsu.by/pub/2/leto_ekz_3k.xls'}
ekz_c3.shortname = 'ekz_c3'


# Only winter timetable avaliable for course 4
zachet_c4.name = 'Зачеты, 4-й курс'
zachet_c4.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_zachet_4k.xls'}
zachet_c4.shortname = 'zachet_c4'

ekz_c4.name = 'Экзамены, 4-й курс'
ekz_c4.urls = {'winter' : 'https://law.bsu.by/pub/2/zima_ekz_4k.xls'}
ekz_c4.shortname = 'ekz_c4'


# Timetable lists to make the code simplier
all_timetables = [pravo_c1, pravo_c2, pravo_c3, pravo_c4,
                  ek_polit_c1, ek_polit_c2, ek_polit_c3, ek_polit_c4,
                  mag_c1,
                  zachet_c1, zachet_c2, zachet_c3, zachet_c4,
                  ekz_c1, ekz_c2, ekz_c3, ekz_c4]

# List for only credits and exams 
credit_exam_timetables = [zachet_c1, ekz_c1, zachet_c2, ekz_c2,
                              zachet_c3, ekz_c3, zachet_c4, ekz_c4]
                              
