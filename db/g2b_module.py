# db/g2b_module.py
import os
import sqlite3


class G2bDB:
    def __init__(self, db_name):
        self.db_name = db_name

    def init_db(self):
        if os.path.isfile(self.db_name):
            print("DB : g2b Database exists!")
            return
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE bid_results (
                bid_pbanc_no TEXT NOT NULL,
                bid_pbanc_ord TEXT NOT NULL,
                bid_clsf_no TEXT NOT NULL,
                prcm_bsne_se_cd TEXT NOT NULL,
                bid_pbanc_nm TEXT,
                date TEXT NOT NULL,
                base_amount INTEGER NOT NULL,
                predict_price INTEGER NOT NULL,
                rsve_price_1 INTEGER,
                rsve_price_2 INTEGER,
                rsve_price_3 INTEGER,
                rsve_price_4 INTEGER,
                rsve_price_5 INTEGER,
                rsve_price_6 INTEGER,
                rsve_price_7 INTEGER,
                rsve_price_8 INTEGER,
                rsve_price_9 INTEGER,
                rsve_price_10 INTEGER,
                rsve_price_11 INTEGER,
                rsve_price_12 INTEGER,
                rsve_price_13 INTEGER,
                rsve_price_14 INTEGER,
                rsve_price_15 INTEGER,
                PRIMARY KEY (bid_pbanc_no, bid_pbanc_ord, bid_clsf_no)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def insert_result(self, data: dict):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bid_results (
                bid_pbanc_no, bid_pbanc_ord, bid_clsf_no, prcm_bsne_se_cd,
                bid_pbanc_nm, date, base_amount, predict_price,
                rsve_price_1, rsve_price_2, rsve_price_3, rsve_price_4,
                rsve_price_5, rsve_price_6, rsve_price_7, rsve_price_8,
                rsve_price_9, rsve_price_10, rsve_price_11, rsve_price_12,
                rsve_price_13, rsve_price_14, rsve_price_15
            ) VALUES (
                :bid_pbanc_no, :bid_pbanc_ord, :bid_clsf_no, :prcm_bsne_se_cd,
                :bid_pbanc_nm, :date, :base_amount, :predict_price,
                :rsve_price_1, :rsve_price_2, :rsve_price_3, :rsve_price_4,
                :rsve_price_5, :rsve_price_6, :rsve_price_7, :rsve_price_8,
                :rsve_price_9, :rsve_price_10, :rsve_price_11, :rsve_price_12,
                :rsve_price_13, :rsve_price_14, :rsve_price_15
            )
        """, data)
        conn.commit()
        cursor.close()
        conn.close()

    def exists(self, bid_pbanc_no, bid_pbanc_ord, bid_clsf_no):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM bid_results WHERE bid_pbanc_no=? AND bid_pbanc_ord=? AND bid_clsf_no=?",
            (bid_pbanc_no, bid_pbanc_ord, bid_clsf_no)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
