import sqlite3
import src.static

# TimesDB, NotificaitonsDB and StatisticsDB are inherited from this
class CommonDB():
	# Used to set the path to a database
    def __init__(self, db_path):
        self.db_path = db_path

    # Connects to the databas
    # Also creates an empty base if there is still no 'db_path' base
    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    # Closes the db
    def close(self):
        self.connection.commit()
        self.connection.close()


# Stores update time of each timetable
class TimesDB(CommonDB):
    def __init__(self):
		# Set path to the db
        super().__init__(src.static.timesdb_path)

    # Creates necessary tables after db was created
    def construct(self):
        self.cursor.execute('CREATE TABLE times (ttb, time)')

        for timetable in src.static.all_timetables:
            self.cursor.execute('INSERT INTO times VALUES ("' + timetable.shortname + '", "")')

        self.connection.commit()

    # Get timetable's update time written before
    def get_time(self, timetable_name):
        self.cursor.execute("SELECT time FROM times WHERE (ttb = ?)", (timetable_name,))
        time = self.cursor.fetchall()[0][0]
        return(time)

    # Write a new update time to the db
    def write_time(self, timetable_name, update_time):
        self.cursor.execute("UPDATE times SET time = '" + update_time + "' WHERE (ttb = ?)", (timetable_name,))
        self.connection.commit()


# Stores user_id's of those who enabled notifications
class NotificationsDB(CommonDB):
    def __init__(self):
		# Set path to the db
        super().__init__(src.static.notificationsdb_path)

    # Creates necessary tables after db was created
    def construct(self):
        for timetable in src.static.all_timetables:
            self.cursor.execute('CREATE TABLE ' + timetable.shortname + ' (users)')
        self.connection.commit()

    # Returns list of users notified about certain timetable
    def get_notified_users(self, timetable_name):
        self.cursor.execute('SELECT users FROM ' + timetable_name)
        result = self.cursor.fetchall()

        notified_users = []
        for i in result:
           notified_users.append(i[0])

        return(notified_users)

    # Checks if user is in get_notified_users() list
    def check_if_user_notified(self, user_id, timetable_name):

        all_notified_users = self.get_notified_users(timetable_name)

        if user_id in all_notified_users:
            return True
        else:
            return False

    # Writes user id to the db
    def enable_notifications(self, user_id, timetable_name):
        self.cursor.execute('INSERT INTO ' + timetable_name + ' VALUES (\'' + user_id + '\')')
        self.connection.commit()

    # Deletes user id from the db
    def disable_notifications(self, user_id, timetable_name):
        self.cursor.execute('DELETE FROM ' + timetable_name + ' WHERE (users = \'' + user_id + '\')')
        self.connection.commit()


class StatisticsDB(CommonDB):
    def __init__(self):
		# Set path to the db
        super().__init__(src.static.statisticsdb_path)

    # Creates necessary tables after db was created
    def construct(self):
        self.cursor.execute('CREATE TABLE uniq_users (users)')
        self.connection.commit()

    # Returns list of unique users
    def get_unique_users(self):
        self.cursor.execute('SELECT * FROM uniq_users')
        result = self.cursor.fetchall()

        unique_users = []
        for i in result:
            unique_users.append(i[0])

        return(unique_users)

    # Add a new user to this database (when '/start' command is sent)
    def add_uniq_user(self, user_id):
        self.cursor.execute('INSERT INTO uniq_users VALUES (?)', (user_id,))
        self.connection.commit()
