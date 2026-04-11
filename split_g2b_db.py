#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""기존 단일 db/g2b.db 를 연도별 db/g2b_<year>.db 로 분할.

GitHub 100MB 한계를 우회하기 위해 연도별로 파일을 쪼갠다.
크롤러는 이후 db/g2b_module.py 의 G2bDB 라우터를 통해 연도별 DB 에 직접 쓴다.
이 스크립트는 1회성 — 기존 통합 DB 가 있을 때만 실행.
"""

import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
SOURCE = os.path.join(DB_DIR, "g2b.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bid_results (
    bid_pbanc_no TEXT NOT NULL,
    bid_pbanc_ord TEXT NOT NULL,
    bid_clsf_no TEXT NOT NULL,
    prcm_bsne_se_cd TEXT NOT NULL,
    bid_pbanc_nm TEXT,
    date TEXT NOT NULL,
    base_amount INTEGER NOT NULL,
    predict_price INTEGER NOT NULL,
    rsve_price_1 INTEGER, rsve_price_2 INTEGER, rsve_price_3 INTEGER,
    rsve_price_4 INTEGER, rsve_price_5 INTEGER, rsve_price_6 INTEGER,
    rsve_price_7 INTEGER, rsve_price_8 INTEGER, rsve_price_9 INTEGER,
    rsve_price_10 INTEGER, rsve_price_11 INTEGER, rsve_price_12 INTEGER,
    rsve_price_13 INTEGER, rsve_price_14 INTEGER, rsve_price_15 INTEGER,
    PRIMARY KEY (bid_pbanc_no, bid_pbanc_ord, bid_clsf_no)
)
"""


def main():
    if not os.path.exists(SOURCE):
        print(f"ERROR: {SOURCE} 가 없습니다.")
        sys.exit(1)

    src = sqlite3.connect(SOURCE)
    src_cur = src.cursor()
    src_cur.execute("SELECT DISTINCT substr(date, 1, 4) FROM bid_results ORDER BY 1")
    years = [r[0] for r in src_cur.fetchall() if r[0]]
    print(f"분할 대상 연도: {years}")

    for year in years:
        dest_path = os.path.join(DB_DIR, f"g2b_{year}.db")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        dest = sqlite3.connect(dest_path)
        dest.execute(SCHEMA)

        src_cur.execute(
            "SELECT * FROM bid_results WHERE date LIKE ? ORDER BY date",
            (f"{year}/%",),
        )
        cols = [d[0] for d in src_cur.description]
        placeholders = ",".join(["?"] * len(cols))
        rows = src_cur.fetchall()

        dest_cur = dest.cursor()
        dest_cur.executemany(
            f"INSERT INTO bid_results ({','.join(cols)}) VALUES ({placeholders})",
            rows,
        )
        dest.commit()

        dest_cur.execute("SELECT COUNT(*) FROM bid_results")
        cnt = dest_cur.fetchone()[0]
        size_mb = os.path.getsize(dest_path) / 1024 / 1024
        print(f"  g2b_{year}.db: {cnt:,} 건, {size_mb:.1f} MB")
        dest.close()

    src.close()
    print("분할 완료.")


if __name__ == "__main__":
    main()
