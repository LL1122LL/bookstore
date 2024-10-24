import pytest
import os
import sys
sys.path.append("E:\\juypter\\DataSql\\bookstore3\\CDMS.Xuan_ZHOU.2024Fall.DaSE\\project1\\bookstore")
os.chdir('E:\\juypter\\DataSql\\bookstore3\\CDMS.Xuan_ZHOU.2024Fall.DaSE\\project1\\bookstore')
from fe.test.gen_book_data import GenBook

from fe.access.new_buyer import register_new_buyer

from fe.access.new_seller import register_new_seller
from fe.access import book
from fe.access.auth import Auth
from fe import conf

import uuid


class TestAddBook:
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 2)

        # do after test

    def test_ok(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200


class TestReceive:
    def pre_run_initialization(self):
        #the func of receiving after the buyer,so minic buyer_test
        self.seller_id = "test_receive_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_receive_books_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_receive_books_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        # self.buyer = register_new_buyer(self.buyer_id, self.password)
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.buyer_id)#password:self.buyer_id
        self.buyer = b

        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        
        code = self.buyer.add_funds(self.total_price + 100)
        assert code == 200
        # code = self.buyer.payment(self.order_id)
        # assert code == 200

    
    #-------------------------------------seller--------------------------#
    def test_send_ok(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200

    # 权限错误 seller_id 与 user_id 不对应
    def test_authorization_error_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.send_books(self.seller_id + 'x', self.order_id)
        assert code != 200

    # 订单号不存在
    def test_invalid_order_id_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id+ 'x')
        assert code != 200

    def test_books_repeat_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code != 200

        # 订单发货，但是未付款
    def test_books_not_paid_receive(self):
        # code = self.buyer.payment(self.order_id)
        # assert code == 200
        code = self.seller.send_books(self.buyer_id, self.order_id)
        assert code != 200
    #--------------------------------------buyer--------------------------#

    def test_receive_ok(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id, self.order_id)
        assert code == 200

    # 权限错误 buyer_id 与 user_id 不对应
    def test_authorization_error_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # 订单号不存在
    def test_invalid_order_id_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 订单未发货
    def test_books_not_send_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.buyer.receive_books(self.buyer_id, self.order_id)
        assert code != 200

    #订单重复接收
    def test_books_repeat_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
    
        code = self.seller.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_books(self.buyer_id, self.order_id)
        assert code != 200

a = TestReceive()
a.pre_run_initialization()
a.test_books_repeat_receive()
#coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data .\\bookstore\\fe\\test\\test_receive_books.py
