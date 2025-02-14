import sqlite3
import pandas as pd

# 데이터베이스 경로
db_path = 'db/priceDB.db'
# db_path = 'db/yongyuk.db'

# 가져올 연도
year = '2025'

# 날짜 구간 설정 (1~10일, 11~20일, 21~31일)
date_ranges = [("01", "10"), ("11", "20"), ("21", "31")]

# SQLite 연결
conn = sqlite3.connect(db_path)

# 1월부터 12월까지 반복
total = []
for month in range(1, 13):
    month_str = f"{month:02d}"  # 1 → '01', 2 → '02', ..., 10 → '10'
    value = []
    for start, end in date_ranges:
        query = f"""
        SELECT date, predict_price, base_price
        FROM price_set
        WHERE date BETWEEN '{year}.{month_str}.{start}' AND '{year}.{month_str}.{end}'
        ORDER BY date ASC;
        """
        df = pd.read_sql(query, conn)

        # 데이터가 있는 경우만 비율 계산 및 출력
        if not df.empty:
            df["ratio"] = df["predict_price"] / df["base_price"] * 100
            ratio_mean = round(df["ratio"].mean(), 1)
            value.append(ratio_mean)
        else:
            print(f"{year}년 {month_str}월 {start}일 ~ {end}일 데이터가 없습니다.")
    total.append(value)

print(total)
# 연결 종료
conn.close()
