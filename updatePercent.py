import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from count import count_nums

# 99.9 ~ 100.4  6개의 예가율을 1~12월 12개로
y_values = [[0 for _ in range(12)] for _ in range(6)] # 치역
y_range = [i for i in range(25)] # 각 예가율의 값의 범위(임의로 정함)
dates = [str(i)+"월" for i in range(1,13)] # 1~12월 까지의 정의역


# 가져올 연도 하드코딩
year = '2025'

# SQLite 연결 및 데이터 가져오기
db_path = 'db/priceDB.db'
db_path = 'db/yongyuk.db'

conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT date, predict_price, base_price FROM price_set ORDER BY date ASC", conn)




# 범위에 따른 예가율 갯수 세기
for i in range(len(df['date'])):
    for j in range(12):
        month = j+1
        if month < 10:
            if f'{year}.0{month}' in df.at[i,'date']:
                predict_rate = round(df.at[i, 'predict_price'] / df.at[i, 'base_price'] * 100, 1)
                count_nums(y_values, predict_rate, j)

        else:
             if f'{year}.{month}' in df.at[i,'date']:
                predict_rate = round(df.at[i, 'predict_price'] / df.at[i, 'base_price'] * 100, 1)
                count_nums(y_values, predict_rate, j)

result = []
for i in range(len(y_values)):
    result.append(sum(y_values[i]))

# print(y_values, result)
for i in range(6):
    for j in range(12):
        if result[i] != 0:
            y_values[i][j] = round(y_values[i][j]/result[i]*100, 2)
print(y_values)
