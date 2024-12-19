import sqlite3

from configs.config import Config_
rdv_db_path = Config_.DBs.rdv_db

with sqlite3.connect(rdv_db_path) as conn:
    cursor = conn.cursor()
    cursor.execute('''''')