from pymongo import MongoClient

class SearchBooks:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def get_books(self, search_query, search_scopes):
        # 构建查询条件
        """
        search_scopes:题目，标签，目录，内容；全站搜索或是当前店铺搜索。
        
        """
        query = {}
        search_criteria = []

        if 'title' in search_scopes:
            search_criteria.append({'title': {'$regex': search_query, '$options': 'i'}})

        if 'tags' in search_scopes:
            search_criteria.append({'tags': {'$in': [search_query]}})

        if 'book_intro' in search_scopes:
            search_criteria.append({'book_intro': {'$regex': search_query, '$options': 'i'}})

        if 'content' in search_scopes:
            search_criteria.append({'content': {'$regex': search_query, '$options': 'i'}})

        if search_criteria:
            query['$or'] = search_criteria

        # 获取总结果数
        total_results = self.db.book.count_documents(query)

        books = self.db.book.find(query)
        book_titles = [book['title'] for book in books]

        if total_results == 0:
            return 404, "Not Found"
        else:
            return 200, {"titles": book_titles, "num": total_results}


    def get_stores(self, store_name, search_query, search_scopes):
        # 初始化结果列表
        stores = self.db.store.find({'store_id': store_name})

        query = {}  # 初始化一个空的query字典
        for store in stores:
            # 在每个店铺数据中查找符合搜索关键词的书本
            store_id = store['store_id']

            query = {
                '$and': [
                    {'store_id': store_id},
                    {
                        '$or': []
                        }
                    ]
                }
            # 根据选择的搜索范围构建查询条件
            if 'title' in search_scopes:
                query['$and'][1]['$or'].append({'book_info.title': {'$regex': search_query, '$options': 'i'}})

            if 'tags' in search_scopes:
                query['$and'][1]['$or'].append({'book_info.tags': {'$in': [search_query]}})

            if 'book_intro' in search_scopes:
                query['$and'][1]['$or'].append({'book_info.book_intro': {'$regex': search_query, '$options': 'i'}})

            if 'content' in search_scopes:
                query['$and'][1]['$or'].append({'book_info.content': {'$regex': search_query, '$options': 'i'}})

            if not query['$and'][1]['$or']:
                query['$and'].pop(1)

        if not query:  # 如果没有匹配的店铺，设置一个默认的查询条件
            query = {'store_id': 'non_existent_store_id'}

        total_results = self.db.store.count_documents(query)
        books = self.db.store.find(query)
        book_titles = [book['book_info']['title'] for book in books]

        if total_results == 0:
            return 404, "Not Found"
        else:
            return 200, {"titles": book_titles, "num": total_results}