import sqlite3
import pandas as pd

# 데이터베이스 경로
db_path = 'db/priceDB.db'

# 가져올 연도와 월
year = '2024'
month = '01'

# 날짜 구간 설정
date_ranges = [("01", "10"), ("11", "20"), ("21", "31")]

# SQLite 연결
conn = sqlite3.connect(db_path)

for start, end in date_ranges:
    query = f"""
    SELECT date, predict_price, base_price
    FROM price_set
    WHERE date BETWEEN '{year}.{month}.{start}' AND '{year}.{month}.{end}'
    ORDER BY date ASC;
    """
    df = pd.read_sql(query, conn)

    # 데이터가 있는 경우만 비율 계산 및 출력
    if not df.empty:
        df["ratio"] = df["predict_price"] / df["base_price"]
        ratio_mean = round(df["ratio"].mean(), 3)
        print(f"2024년 {month}월 {start}일 ~ {end}일 평균 비율:", ratio_mean)
    else:
        print(f"2024년 {month}월 {start}일 ~ {end}일 데이터가 없습니다.")

# 연결 종료
conn.close()
