import json
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str, # Unused
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            # self.conn.execute(
            #     "INSERT into store(store_id, book_id, book_info, stock_level)"
            #     "VALUES (?, ?, ?, ?)",
            #     (store_id, book_id, book_json_str, stock_level),
            # )
            # self.conn.commit()
            # self.db.store.insert_one({
            #     "store_id": store_id,
            #     "book_id": book_id,
            #     # "book_info": json.loads(book_json_str),
            #     "stock_level": stock_level
            # })

            self.db.store.update_one(
                {"store_id": store_id},
                {
                    "$push": {
                        "book_stock_info": {
                            "book_id": book_id,
                            "stock_level": stock_level
                        }
                    }
                }
            )
        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            # self.conn.execute(
            #     "UPDATE store SET stock_level = stock_level + ? "
            #     "WHERE store_id = ? AND book_id = ?",
            #     (add_stock_level, store_id, book_id),
            # )
            # self.conn.commit()
            res = self.db.store.update_one(
                {"store_id": store_id, "book_stock_info.book_id": book_id},
                {"$inc": {"book_stock_info.$.stock_level": add_stock_level}}
            )
            assert res.modified_count > 0
        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            # self.conn.execute(
            #     "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
            #     (store_id, user_id),
            # )
            # self.conn.commit()
            self.db.user_store.insert_one({
                "store_id": store_id,
                "user_id": user_id
            })
            
            self.db.store.insert_one({
                "store_id":store_id,
                "book_stock_info":[]
            })

        except Exception as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def send_books(self,user_id: str,order_id: str):
        res = self.db.new_order.find_one({"order_id": order_id})
        if res is None:
            return error.error_invalid_order_id(order_id)

        store_id = res["store_id"]
        books_status = res["books_status"]

        # ¸ù¾Ý store_id ÕÒÂô¼Ò
        result = self.db.user_store.find_one({"store_id": store_id})
        seller_id = result["user_id"]

        if seller_id != user_id:
            return error.error_authorization_fail()

        if books_status == 0:
            return error.error_book_has_sent(order_id)

        if books_status == 2:
            return error.error_not_paid_book(order_id)

        if books_status == 3:
            return error.error_book_has_received(order_id)

        res = self.db.new_order.update_one({"order_id": order_id}, {"$set": {"books_status": 0}})
        assert res.modified_count > 0 #only for debug£¬it may also be equal to zero when multi-proc.
        return 200, "ok"
