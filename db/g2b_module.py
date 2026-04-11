# db/g2b_module.py
"""연도별로 분할된 g2b DB 라우터.

실제 파일은 db/g2b_<year>.db 형태로 분리 저장.
insert 시 row['date'] (YYYY/MM/DD) 의 연도로 자동 라우팅.
중복 검사는 모든 연도 DB 에서 미리 로드한 in-memory set 으로 처리 (O(1)).

GitHub 100MB 파일 한계 회피 + 점진적 갱신 (변경된 연도 파일만 push) 목적.
"""
import glob
import os
import sqlite3


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


class G2bDB:
    def __init__(self, db_dir):
        """db_dir: 연도별 파일들이 위치하는 디렉토리 (예: 'db/').
        호환성: 기존처럼 'db/g2b.db' 같은 파일 경로를 넘겨도 부모 디렉토리만 사용."""
        if db_dir.endswith(".db"):
            db_dir = os.path.dirname(db_dir)
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)
        self.existing_keys = set()

    def _path_for_year(self, year):
        return os.path.join(self.db_dir, f"g2b_{year}.db")

    def _open_year_db(self, year):
        """해당 연도 DB 를 열고 (없으면 생성) 스키마를 보장한 뒤 connection 반환."""
        path = self._path_for_year(year)
        conn = sqlite3.connect(path)
        conn.execute(SCHEMA)
        return conn

    def init_db(self):
        """기존 연도 DB 들에서 PK 모두 로드해 중복검사 캐시 구성."""
        for path in sorted(glob.glob(os.path.join(self.db_dir, "g2b_*.db"))):
            try:
                conn = sqlite3.connect(path)
                cur = conn.cursor()
                cur.execute(
                    "SELECT bid_pbanc_no, bid_pbanc_ord, bid_clsf_no FROM bid_results"
                )
                for row in cur:
                    self.existing_keys.add(row)
                conn.close()
            except sqlite3.OperationalError:
                # 테이블이 없는 빈 DB
                pass
        print(
            f"DB : g2b 연도별 분할 — 기존 키 {len(self.existing_keys):,}개 로드 ({self.db_dir})"
        )

    def exists(self, bid_pbanc_no, bid_pbanc_ord, bid_clsf_no):
        return (bid_pbanc_no, bid_pbanc_ord, bid_clsf_no) in self.existing_keys

    def insert_result(self, data: dict):
        """data['date'] (YYYY/MM/DD) 의 연도로 라우팅하여 INSERT."""
        date_str = data.get("date", "")
        try:
            year = int(date_str.split("/")[0])
        except (ValueError, IndexError):
            raise ValueError(f"insert_result: date 형식 오류 — {date_str!r}")

        conn = self._open_year_db(year)
        cursor = conn.cursor()
        cursor.execute(
            """
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
            """,
            data,
        )
        conn.commit()
        cursor.close()
        conn.close()
        # 캐시 갱신
        self.existing_keys.add(
            (data["bid_pbanc_no"], data["bid_pbanc_ord"], data["bid_clsf_no"])
        )
