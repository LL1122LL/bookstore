import sqlite3
from pymongo import MongoClient


sqlite_conn = sqlite3.connect('fe/data/book.db')
sqlite_cursor = sqlite_conn.cursor()


client = MongoClient('localhost', 27017) 
db = client['bookstore']  
book_collection = db['books'] 


sqlite_cursor.execute("SELECT * FROM book")
rows = sqlite_cursor.fetchall()


columns = [
    "id", "title", "author", "publisher", "original_title", "translator", 
    "pub_year", "pages", "price", "currency_unit", "binding", "isbn", 
    "author_intro", "book_intro", "content", "tags", "picture"
]


for row in rows:
    book_document = {columns[i]: row[i] for i in range(len(columns))}
    book_collection.insert_one(book_document) 

sqlite_conn.close()
client.close()

print("successfully transfer")