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
        
