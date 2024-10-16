from pymongo import MongoClient

class SearchBooks:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['bookstore']

    def get_books(self, search_query, search_scopes):
        # ������ѯ����
        """
        search_scopes:��Ŀ����ǩ��Ŀ¼�����ݣ�ȫվ�������ǵ�ǰ����������
        
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

        # ��ȡ�ܽ����
        total_results = self.db.book.count_documents(query)

        books = self.db.book.find(query)
        book_titles = [book['title'] for book in books]

        if total_results == 0:
            return 404, "Not Found"
        else:
            return 200, {"titles": book_titles, "num": total_results}


    def get_stores(self, store_name, search_query, search_scopes):
        # ��ʼ������б�
        stores = self.db.store.find({'store_id': store_name})

        query = {}  # ��ʼ��һ���յ�query�ֵ�
        for store in stores:
            # ��ÿ�����������в��ҷ��������ؼ��ʵ��鱾
            store_id = store['store_id']

            query = {
                '$and': [
                    {'store_id': store_id},
                    {
                        '$or': []
                        }
                    ]
                }
            # ����ѡ���������Χ������ѯ����
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

        if not query:  # ���û��ƥ��ĵ��̣�����һ��Ĭ�ϵĲ�ѯ����
            query = {'store_id': 'non_existent_store_id'}

        total_results = self.db.store.count_documents(query)
        books = self.db.store.find(query)
        book_titles = [book['book_info']['title'] for book in books]

        if total_results == 0:
            return 404, "Not Found"
        else:
            return 200, {"titles": book_titles, "num": total_results}