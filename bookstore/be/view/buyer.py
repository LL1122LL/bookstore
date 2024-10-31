from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code


# 收货，调用be/model/buyer.py中的receive_book.def receive_book(self,user_id: str, order_id: str) -> (int, str):
@bp_buyer.route("/receive_book", methods=["POST"])
def receive_book():
    user_id = request.json.get("user_id")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.receive_book(user_id, order_id)
    return jsonify({"message": message}), code


# 搜索订单，调用be/model/buyer.py中的search_order方法.def search_order(self, user_id: str, password: str) -> (int, str, [(str, str, str, int, int, int)]):
@bp_buyer.route("/search_order", methods=["POST"])
def search_order():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    b = Buyer()
    code, message, orders = b.search_order(user_id, password)
    return jsonify({"message": message, "orders": orders}), code


# 取消订单，调用be/model/buyer.py中的cancel_order方法def cancel_order(self, user_id: str, password: str, order_id: str) -> (int, str):
@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    order_id = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel_order(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/search", methods=["POST"])
def search_books():
    keyword = request.json.get("keyword")
    store_id = request.json.get("store_id")
    page = request.json.get("page")

    b = Buyer()
    code, message = b.search(keyword, store_id, page)
    return jsonify({"message": message}), code

@bp_buyer.route("/recommend_books", methods=["POST"])
def recommend_books():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    b = Buyer()
    code, message, books = b.recommend_books(user_id, password)
    return jsonify({"message": message, "books": books}), code


