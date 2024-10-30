import os
from pymongo import MongoClient
import random
import base64
import simplejson as json


class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        # parent_path = os.path.dirname(os.path.dirname(__file__))
        # self.db_s = os.path.join(parent_path, "data/book.db")
        # self.db_l = os.path.join(parent_path, "data/book_lx.db")
        # if large:
        #     self.book_db = self.db_l
        # else:
        #     self.book_db = self.db_s
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def get_book_count(self):
        return self.db.book.count_documents({})

    def get_book_info(self, start, size) -> [Book]:
        books = []
        # conn = sqlite.connect(self.book_db)
        # cursor = conn.execute(
        #     "SELECT id, title, author, "
        #     "publisher, original_title, "
        #     "translator, pub_year, pages, "
        #     "price, currency_unit, binding, "
        #     "isbn, author_intro, book_intro, "
        #     "content, tags, picture FROM book ORDER BY id "
        #     "LIMIT ? OFFSET ?",
        #     (size, start),
        # )
        cursor = self.db.book.find().sort([("id", 1)]).skip(start).limit(size)#�豣֤books��collection�Ĵ���
        for row in cursor:
            book = Book()
            book.id = row['id']
            book.title = row['title']
            book.author = row['author']
            book.publisher = row['publisher']
            book.original_title = row['original_title']
            book.translator = row['translator']
            book.pub_year = row['pub_year']
            book.pages = row['pages']
            book.price = row['price']

            book.currency_unit = row["currency_unit"]
            book.binding = row['binding']
            book.isbn = row['isbn']
            book.author_intro = row['author_intro']
            book.book_intro = row['book_intro']
            book.content = row['content']
            tags = row['tags']
            #picture = row['picture']

            for tag in tags.split("\n"):
                if tag.strip() != "":
                   book.tags.append(tag)
            # for i in range(0, random.randint(0, 9)):
            #     if picture is not None:
            #         encode_str = base64.b64encode(picture).decode("utf-8")
            #         book.pictures.append(encode_str)
            book.pictures = []
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
