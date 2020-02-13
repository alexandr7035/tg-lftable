# Change directory to the one in wich the module is located
# And then to the parent one
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, '..')

import src.db_classes
import src.static
os.chdir('..')

# Writes old times to times db on start to artificially trigger notifications
# Only for debug
def test_notifications():
	
	timesdb = src.db_classes.TimesDB()
	timesdb.connect()
	
	for ttb in src.static.all_timetables:
	    timesdb.write_time(ttb.shortname, '01.01.1970 00:00:00')
	
	timesdb.close()
	
if __name__ == '__main__':
	test_notifications()
		
