import traceback
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(override=True)

class HistoryDBError(Exception):
    pass

class HistoryPersist:
    def __init__(self):
        try:
            self.client = MongoClient(f'mongodb+srv://mothishdeenadayalan:{os.getenv("MONGO_PASSWORD")}@qtell.38uyh.mongodb.net/?retryWrites=true&w=majority&appName=qtell')
            self.db = self.client['qtell']
            self.collection = self.db['history']
        except Exception:
            traceback.print_exc()
            raise HistoryDBError
        
    def insert_history(self, user_id, data):
        try:
            self.collection.insert_one({'user_id': user_id, 'chat': data, 'load_timestamp': datetime.now()})
        except Exception:
            traceback.print_exc()
            raise HistoryDBError()
    
    def get_history(self, user_id, order=1):
        try:
            return self.collection.find({'user_id': user_id}).sort('load_timestamp', order)                            
        except Exception:
            traceback.print_exc()
            raise HistoryDBError()
        
    def delete_history(self, user_id):
        try:
            self.collection.delete_many({'user_id': user_id})
        except Exception:
            traceback.print_exc()
            raise HistoryDBError()
        
    def close_connection(self):
        try:
            self.client.close()
        except Exception:
            traceback.print_exc()
            raise HistoryDBError()
            