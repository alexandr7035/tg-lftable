import sqlite3
from src.static import *
from src.logger import *

class CommonDB():
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.commit()
        self.connection.close()


class TimesDB(CommonDB):
    def __init__(self):
        super().__init__(times_db)

    def get_time(self, timetable_name):
        self.cursor.execute("SELECT time FROM times WHERE (ttb = ?)", (timetable_name,))
        time = self.cursor.fetchall()[0][0]
        return(time)

    def write_time(self, timetable_name, update_time):
        self.cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable_name,))
        self.connection.commit()
