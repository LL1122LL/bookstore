import logging
import os
import sqlite3 as sqlite
import threading
from pymongo import MongoClient

class Store:
    database: str

    def __init__(self, db_path):
        #self.database = os.path.join(db_path, "be.db")
        self.client = MongoClient(db_path)
        self.db = self.client['bookstore']
        self.init_tables()

    def init_tables(self):
        self.user = self.db['user']
        self.store = self.db['store']
        self.book = self.db['book']
        self.order_detail = self.db['order_detail']
        self.order = self.db['order']

        # self.store_col.create_index([("store_id", 1)], unique=True)
        # self.user_col.create_index([("user_id", 1)], unique=True)
        # self.book_col.create_index(
        #     [("title", "text"), ("tags", "text"), ("book_intro", "text"), ("content", "text")])

    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    db_url = "mongodb://localhost:27017/"
    database_instance = Store(db_url)
    return database_instance 
