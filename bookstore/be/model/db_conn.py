
from be.model import store
from pymongo import MongoClient

class DBConn:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def user_id_exist(self, user_id):
        return self.db["users"].find_one({"user_id": user_id}) is not None

    def book_id_exist(self, store_id, book_id):
        result = self.db["books"].find_one({"store_id": store_id, "book_id": book_id})
        return result is not None


    def store_id_exist(self, store_id):
        result = self.db["stores"].find_one({"store_id": store_id})
        return result is not None
