import sqlite3
import pandas as pd
import json
import argparse

# 데이터베이스 경로
db_path = 'db/priceDB.db'
db_path = 'db/yongyuk.db'

parser = argparse.ArgumentParser(description="입찰 데이터의 평균 비율을 JSON 파일에 업데이트")
parser.add_argument("-y", "--year", type=str, default="2025", required=True, help="가져올 연도 (예: 2024)")
args = parser.parse_args()
year = args.year  # 사용자 입력 연도

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
json_path = './html/avgRateDataMp.json'
with open(json_path, "r", encoding="utf-8") as file:
    json_data = json.load(file)

json_data["avgRateData"][year] = total
with open(json_path, "w", encoding="utf-8") as file:
    json.dump(json_data, file, ensure_ascii=False, indent=2)
# 연결 종료
conn.close()
