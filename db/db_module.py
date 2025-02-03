import os
import sqlite3

class PriceDB:
    def __init__(self, db_name) -> None:
        self.db_name = db_name
    
    def init_db(self):
        if os.path.isfile(self.db_name):
            print("DB : price Database exists!")
        else:
            conn_init = sqlite3.connect(self.db_name)
            cursor_init = conn_init.cursor()
            cursor_init.execute("""
                CREATE TABLE price_set (
                    ann_num INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    base_price INTEGER NOT NULL,
                    predict_price INTEGER NOT NULL,
                    bid_price INTEGER NOT NULL,
                    min_rate TEXT NOT NULL
                )
            """)
            conn_init.commit()
            cursor_init.close()
            conn_init.close()
    def insert_info(self, ann_num, date, base_price, predict_price, bid_price, min_rate):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO price_set (ann_num, date, base_price, predict_price, bid_price, min_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ann_num, date, base_price, predict_price, bid_price, min_rate))
        conn.commit()
        cursor.close()
        conn.close()
        
    def change_minrate():
        #  min_rate 값 0인 것들에 대해 재공고 일어나기 전의 공고로 가서 min_rate 다시 가져올 것
        pass
    # 따로 만듬
