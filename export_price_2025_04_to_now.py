import sqlite3
import pandas as pd
from datetime import datetime
import calendar

# DB 파일 경로
DB_PATH = './db/yongyuk.db'
# 저장할 CSV 파일명
CSV_PATH = './html/price_2025_04_to_now.csv'

# 오늘 날짜 구하기
now = datetime.now()
last_day = calendar.monthrange(now.year, now.month)[1]
now_str = now.strftime(f'%Y.%m.{last_day:02d}')

# 2025년 4월 ~ 현재까지
start_date = '2025.04'

# 쿼리: 공고번호, 날짜, 기초가, 예가, 투찰가
query = f'''
SELECT ann_num AS "공고번호", date AS "날짜", base_price AS "기초가", predict_price AS "예가", bid_price AS "투찰가"
FROM price_set
WHERE date >= ? AND date <= ?
ORDER BY date ASC
'''

def main():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=(start_date, now_str))
    conn.close()
    df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"{CSV_PATH} 파일로 저장 완료! (행 개수: {len(df)})")

if __name__ == '__main__':
    main()
