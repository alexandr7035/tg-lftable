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

    def construct(self):
        self.cursor.execute('CREATE TABLE times (ttb, time)')

        for timetable in all_timetables:
            self.cursor.execute('INSERT INTO times VALUES ("' + timetable.shortname + '", "")')

        self.connection.commit()

    def get_time(self, timetable_name):
        self.cursor.execute("SELECT time FROM times WHERE (ttb = ?)", (timetable_name,))
        time = self.cursor.fetchall()[0][0]
        return(time)

    def write_time(self, timetable_name, update_time):
        self.cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable_name,))
        self.connection.commit()


class NotificationsDB(CommonDB):
    def __init__(self):
        super().__init__(notifications_db)

    def construct(self):
        for timetable in all_timetables:
            self.cursor.execute('CREATE TABLE ' + timetable.shortname + ' (users)')
        self.connection.commit()

    def get_notified_users(self, timetable_name):
        self.cursor.execute('SELECT users FROM ' + timetable_name)
        result = self.cursor.fetchall()

        notified_users = []
        for i in result:
           notified_users.append(i[0])

        return(notified_users)

    def check_if_user_notified(self, user_id, timetable_name):

        all_notified_users = self.get_notified_users(timetable_name)

        if user_id in all_notified_users:
            return True
        else:
            return False

    def enable_notifications(self, user_id, timetable_name):
        self.cursor.execute('INSERT INTO ' + timetable_name + ' VALUES (\'' + user_id + '\')')
        self.connection.commit()

    def disable_notifications(self, user_id, timetable_name):
        self.cursor.execute('DELETE FROM ' + timetable_name + ' WHERE (users = \'' + user_id + '\')')
        self.connection.commit()


class StatisticsDB(CommonDB):
    def __init__(self):
        super().__init__(statistics_db)

    def construct(self):
        self.cursor.execute('CREATE TABLE uniq_users (users)')
        self.connection.commit()

    def get_unique_users(self):
        self.cursor.execute('SELECT * FROM uniq_users')
        result = self.cursor.fetchall()

        unique_users = []
        for i in result:
            unique_users.append(i[0])

        return(unique_users)

    def add_uniq_user(self, user_id):
        self.cursor.execute('INSERT INTO uniq_users VALUES (?)', (user_id,))
        self.connection.commit()


timesdb = TimesDB()
notificationsdb = NotificationsDB()
