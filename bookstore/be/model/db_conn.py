
from be.model import store
from pymongo import MongoClient

class DBConn:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def user_id_exist(self, user_id):
        return self.db["user"].find_one({"user_id": user_id}) is not None


    def book_id_exist(self, store_id = None, book_id = None):

        assert book_id is not None

        if store_id is None:
            result = self.db["book"].find_one({"book_id": book_id})
        else:
            result = self.db["store"].find_one({
                "store_id": store_id,
                "book_stock_info.book_id": book_id
            })
            # result = self.db["book"].find_one({"store_id": store_id, "book_id": book_id})
        return result is not None

    # def book_id_exist(self,book_id):
    #     result = self.db["book"].find_one({"book_id": book_id})
    #     return result is not None
   

    def store_id_exist(self, store_id):
        result = self.db["user_store"].find_one({"store_id": store_id})
        return result is not None

    def get_store(self,store_id):
        #debug
        stores_cursor = self.db.store.find()
        stores_list = list(stores_cursor)
        return self.db.store.find_one({"store_id": store_id})
    
    def get_book_price(self,book_id):
        #line_from_store: self.db.store.find_one
        res = self.db["book"].find_one({
            "id":book_id
        })
        return res["price"]
