import sqlite3
from pymongo import MongoClient
import os
print(os.getcwd())

#sqlite_conn = sqlite3.connect('fe/data/book.db')
sqlite_conn = sqlite3.connect('E:\\juypter\\DataSql\\bookstore3\\CDMS.Xuan_ZHOU.2024Fall.DaSE\\project1\\bookstore\\fe\\data\\book.db')

sqlite_cursor = sqlite_conn.cursor()


mongo_client = MongoClient('localhost', 27017) 


db_list = mongo_client.list_database_names()

print("db_list",db_list)

if 'bookstore' in db_list:
    mongo_client.drop_database('bookstore')
    print("Existing 'bookstore' database found and deleted.")



db = mongo_client['bookstore']  
book_collection = db['book'] 

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
mongo_client.close()

print("successfully transfer")