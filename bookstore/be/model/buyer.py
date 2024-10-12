import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error

from pymongo import MongoClient

class Buyer(db_conn.DBConn):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = self.db.stores.find_one({"store_id": store_id, "book_id": book_id})

                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = result[1]
                book_info = result[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                self.db.stores.update_one(condition,{"$inc": {"stock_level": -1}})

                self.db.new_order_details.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                    "books_status": 2
                })

            self.db.new_orders.insert_one({
                    "order_id": uid,
                    "user_id": user_id,
                    "store_id": store_id,
                    "books_status": 2,
                    # "order_time": now_time,
            })
            order_id = uid
        except Exception as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:

            order_info = self.db.new_order.find_one({"order_id": order_id})
            if order_info is None:
                return error.error_invalid_order_id(order_id)
            
            order_id = order_info["order_id"]
            buyer_id = order_info["user_id"]
            store_id = order_info["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            usr_info = self.db.users.find_one({"user_id": buyer_id})
            if usr_info is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = usr_info["balance"]
            if password != usr_info["passwprd"]:
                return error.error_authorization_fail()


            store_info = self.db.user_store.find_one({"store_id": store_id})
            if  store_info is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store_info["user_id"]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)


            new_order_details_info = self.db.new_order_detail.find({"order_id": order_id})
            total_price = 0
            for row in new_order_details_info:
                count = row["count"]
                price = row["price"]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)


            result = self.db.users.update_many(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result = self.db.users.update_many(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            # 已经付款的会从order的两个表里面删除掉
            # 删除订单和订单详细信息
            delete_count = self.db.new_order.delete_many({"order_id": order_id})
            
            if delete_count == 0:
                return error.error_invalid_order_id(order_id)
            
            delete_count = self.db.new_order_detail.delete_many({"order_id": order_id})
            if delete_count == 0:
                return error.error_invalid_order_id(order_id)

        except Exception as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # 查找用户信息
            user_info = self.db.users.find_one({"user_id": user_id})
            
            # 检查用户是否存在
            if user_info is None:
                return error.error_authorization_fail()
            
            # 验证密码
            if user_info["password"] != password:
                return error.error_authorization_fail()

            # 更新用户余额
            self.db.users.update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
