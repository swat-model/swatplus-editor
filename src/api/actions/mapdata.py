# src/api/actions/check_map_data.py
from peewee import SqliteDatabase
from database import lib as db_lib # Menggunakan lib.py yang sudah ada di proyek Anda

class CheckMapData:
    def __init__(self, project_db, table_name):
        self.project_db = project_db
        self.table_name = table_name

    def check(self):
        # Buka koneksi database
        db = SqliteDatabase(self.project_db)
        db.connect()
        
        # Gunakan fungsi exists_table dari lib.py Anda
        is_exists = db_lib.exists_table(db, self.table_name)
        
        db.close()
        return is_exists