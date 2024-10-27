# 测试用户取消订单

import pytest

from fe.access.new_buyer import register_new_buyer
from fe.test.gen_book_data import GenBook
import uuid


class TestCancel:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield

    def test_cancel_order_and_repeated_cancel(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        code = self.buyer.cancel_order(order_id)
        assert code == 200
        code  = self.buyer.cancel_order(order_id)
        assert code != 200


    def test_cancel_order_authorization_error(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        self.buyer.password = self.buyer.password + "_x"
        code = self.buyer.cancel_order(order_id)
        assert code != 200


    def test_cancel_order_non_exist_order_id(self):
            ok, buy_book_id_list = self.gen_book.gen(
                non_exist_book_id=False, low_stock_level=False
            )
            assert ok
            code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200

            order_id = order_id + "_x"
            code = self.buyer.cancel_order(order_id)
            assert code != 200


    def test_cancel_order_non_exist_user_id(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        self.buyer.user_id = self.buyer.user_id + "_x"
        code = self.buyer.cancel_order(order_id)
        assert code != 200


    def test_cancel_order_after_pay(self):
        ok, buy_book_id_list = self.gen_book.gen(
            non_exist_book_id=False, low_stock_level=False
        )
        assert ok
        code, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        code = self.buyer.add_funds(99999999)
        assert code == 200

        code = self.buyer.payment(order_id)
        assert code == 200

        code = self.buyer.cancel_order(order_id)
        assert code == 200




