from be.model import db_conn


class BookSearcher(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)
    def search_title_in_store(self, title: str, store_id: str, page_num: int, page_size: int):
        book_collection = self.db.book
        store_collection = self.db.store

        # ��ѯָ��������鼮
        condition = {"title": title}
        books = list(book_collection.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size))

        # ��ָ���̵꣬����˽��ڸ��̵��п����鼮
        if store_id:
            books = [
                book for book in books 
                if store_collection.count_documents({"store_id": store_id, "book_stock_info.book_id": book.get('id')}) > 0
            ]

        # ���ؽ��
        if not books:
            return 501, f"for title:{title}, book not exist", []
        return 200, "ok", books

    def search_title(self, title: str, page_num: int, page_size: int):
        return self.search_title_in_store(title, "", page_num, page_size)

    def search_tag_in_store(self, tag: str, store_id: str, page_num: int, page_size: int):
        condition = {"tags": {"$regex": tag}}
        books = list(self.db.book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size))

        # ���ָ���̵�ID������˳��ڸ��̵����п����鼮
        if store_id:
            store_collection = self.db.store
            books = [
                book for book in books 
                if store_collection.count_documents({"store_id": store_id, "book_stock_info.book_id": book.get('id')}) > 0
            ]

        # ���ؽ��
        if not books:
            return 501, f"for tag:{tag},book not exist", []
        return 200, "ok", books

    def search_tag(self, tag: str, page_num: int, page_size: int):
        return self.search_tag_in_store(tag, "", page_num, page_size)

    def search_content_in_store(self, content: str, store_id: str, page_num: int, page_size: int):
        # ʹ��ȫ�ļ������������鼮
        condition = {"$text": {"$search": content}}
        books = list(self.db.book.find(condition, {"_id": 0}).skip((page_num - 1) * page_size).limit(page_size))

        # ���ָ���̵�ID������˳��ڸ��̵����п����鼮
        if store_id:
            store_collection = self.db.store
            books = [
                book for book in books
                if store_collection.count_documents({"store_id": store_id, "book_stock_info.book_id": book.get('id')}) > 0
            ]

        # ���ؽ��
        if not books:
            return 501, f"for content:{content},book not exist", []
        return 200, "ok", books

    def search_content(self, content: str, page_num: int, page_size: int):
        return self.search_content_in_store(content, "", page_num, page_size)

    def search_author_in_store(self, author: str, store_id: str, page_num: int, page_size: int):
        # ��ѯָ�����ߵ��鼮
        condition = {"author": author}
        books = list(
            self.db.book.find(condition, {"_id": 0})
            .skip((page_num - 1) * page_size)
            .limit(page_size)
        )

        # ���ָ�����̵�ID��������ڸ��̵��п����鼮
        if store_id:
            store_collection = self.db.store
            books = [
                book for book in books
                if store_collection.count_documents({"store_id": store_id, "book_stock_info.book_id": book.get('id')}) > 0
            ]

        # ���ؽ��
        if not books:
            return 501, f"for author:{author}, book not exist", []
        return 200, "ok", books

    def search_author(self, author: str, page_num: int, page_size: int):
        return self.search_author_in_store(author, "", page_num, page_size)