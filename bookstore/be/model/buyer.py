import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error

from pymongo import MongoClient

class Buyer(db_conn.DBConn):
    def __init__(self):
        # self.client = MongoClient('localhost', 27017)
        # self.db = self.client['bookstore']
        super().__init__()

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            user = self.db.user.find_one({"user_id": user_id})
            if user is None:
                return error.error_non_exist_user_id(user_id) + (order_id,)
            
            if self.store_id_exist(store_id) is False:
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                result = self.db.store.find_one(
                    {"store_id": store_id,"book_stock_info.book_id": book_id},
                    {"book_stock_info.$": 1}
                    )
                # result = self.db.store.find_one({"store_id": store_id, "book_id": book_id})
                if result is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)
                
                stock_level = result["book_stock_info"][0]["stock_level"]
                #stock_level = result["stock_level"]
                price = self.get_book_price(book_id)

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # condition = {"store_id": store_id, "book_id": book_id, "stock_level": {'$gte': count}}
                # self.db.store.update_one(condition, {"$inc": {"stock_level": -1}})
                condition = {
                    "store_id": store_id, 
                    "book_stock_info.book_id": book_id, 
                    "book_stock_info.stock_level": {'$gte': count}
                }
                self.db.store.update_one(
                    condition, 
                    {"$inc": {"book_stock_info.$.stock_level": -1}}
                )

                new_order_detail = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price,
                }
                self.db.new_order_detail.insert_one(new_order_detail)

            new_order = {
                "order_id": uid,
                "user_id": user_id,
                "store_id": store_id,
                "books_status": 2,
            }

            self.db.new_order.insert_one(new_order)
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

            # 只有未付款的订单可以付款
            if order_info["books_status"] != 2:
                return error.error_repeated_payment(order_id)

            usr_info = self.db.user.find_one({"user_id": buyer_id})
            if usr_info is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = usr_info["balance"]
            if password != usr_info["password"]:
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


            result = self.db.user.update_many(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            result = self.db.user.update_many(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )
            if result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            # 要查看历史订单，故不再删除
            # delete_count = self.db.new_order.delete_many({"order_id": order_id})
            #
            # if delete_count == 0:
            #     return error.error_invalid_order_id(order_id)
            #
            # delete_count = self.db.new_order_detail.delete_many({"order_id": order_id})
            # if delete_count == 0:
            #     return error.error_invalid_order_id(order_id)

            # 更近订单状态，status code	status -1	取消 0	已发货，未收货 1	已付款,待发货 2	初始值，未付款 3	已收货
            result = self.db.new_order.update_one({"order_id": order_id}, {"$set": {"books_status": 1}})
            if result.matched_count == 0:
                return error.error_invalid_order_id(order_id)

        except Exception as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            # find user
            user_info = self.db.user.find_one({"user_id": user_id})

            if user_info is None:
                return error.error_authorization_fail()

            if user_info.get("password") != password:
                return error.error_authorization_fail()

            res = self.db.user.update_one({"user_id": user_id}, {"$inc": {"balance": add_value}})
            if res.matched_count == 0:
                return error.error_non_exist_user_id(user_id)

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive_book(self,user_id: str, order_id: str) -> (int, str):
        try :
            res = self.db.new_order.find_one({"order_id": order_id})
            if res == None:
                return error.error_invalid_order_id(order_id)
            buyer_id = res["user_id"]
            paid_status = res["books_status"]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if paid_status == 2:
                return error.error_books_not_sent(order_id)
            if paid_status == 3:
                return error.error_books_repeat_receive(order_id)
            self.db.new_order.update_one({"order_id": order_id}, {"$set": {"status": 3}})
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    # 用户查询历史订单
    def search_order(self, user_id: str, password: str) -> (int, str, [(str, str, str, int, int, int)]):
        try:
            # find user
            user_info = self.db.user.find_one({"user_id": user_id})
            if user_info is None:
                return error.error_authorization_fail() + ([])
            if user_info.get("password") != password:
                return error.error_authorization_fail() + ([])

            # find order
            res = self.db.new_order.find({"user_id": user_id})
            order_list = []

            # no orders，return empty list, message to hint no orders
            if res is None:
                return 200, "no orders", []

            # find order detail
            for row in res:
                order_id = row["order_id"]
                store_id = row["store_id"]
                status = row["books_status"]
                book_list = self.db.new_order_detail.find({"order_id": order_id})

                # find book
                for book in book_list:
                    book_id = book["book_id"]
                    count = book["count"]
                    price = book["price"]
                    order_list.append((order_id, store_id, book_id, count, price, status))

        except BaseException as e:
            return 528, "{}".format(str(e)), []

        return 200, "ok", order_list

    # 用户登录并主动取消订单，需要分为未付款的订单和已付款的订单待发货的，已发货或已收货不可以取消
    # 对于前者，只需要返还书籍数量即可，对于后者，需要返还书籍数量并且返还金额，返还金额需要从商家账户扣除

    def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            # find user
            user_info = self.db.user.find_one({"user_id": user_id})
            if user_info is None:
                return error.error_authorization_fail()
            if user_info.get("password") != password:
                return error.error_authorization_fail()

            # find order
            res = self.db.new_order.find_one({"order_id": order_id})
            if res == None:
                return error.error_invalid_order_id(order_id)

            # check order status
            status = res["books_status"]
            store_id = res["store_id"]
            book_list = self.db.new_order_detail.find({"order_id": order_id})

            if status == 2:
                # 返还书籍
                for book in book_list:
                    book_id = book["book_id"]
                    count = book["count"]
                    self.db.store.update_one({"store_id": store_id, "book_stock_info.book_id": book_id}, {"$inc": {"book_stock_info.$.stock_level": count}})
                self.db.new_order.delete_one({"order_id": order_id})
                self.db.new_order_detail.delete_many({"order_id": order_id})

            elif status == 1:
                # 检查商家余额是否足够退款
                store_info = self.db.user_store.find_one({"store_id": store_id})
                seller_id = store_info["user_id"]
                seller_info = self.db.user.find_one({"user_id": seller_id})
                total_price = 0
                for book in book_list:
                    count = book["count"]
                    price = book["price"]
                    total_price += count * price
                if seller_info["balance"] < total_price:
                    return error.error_not_sufficient_funds(order_id)

                # 返还书籍
                for book in book_list:
                    book_id = book["book_id"]
                    count = book["count"]
                    self.db.store.update_one({"store_id": store_id, "book_stock_info.book_id": book_id}, {"$inc": {"book_stock_info.$.stock_level": count}})

                # 返还金额
                self.db.user.update_one({"user_id": seller_id}, {"$inc": {"balance": -total_price}})
                self.db.user.update_one({"user_id": user_id}, {"$inc": {"balance": total_price}})
                self.db.new_order.delete_one({"order_id": order_id})
                self.db.new_order_detail.delete_many({"order_id": order_id})

            elif status == 0:
                return error.error_book_has_sent(order_id)
            elif status == 3:
                return error.error_book_has_received(order_id)

        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
