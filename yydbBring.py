

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from expectedBring import bring_bid_amount
from db.db_module import PriceDB
import os

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(options=options)
base_dir = os.path.dirname(__file__)
db_path = os.path.join(base_dir, 'db', 'yongyuk.db')
conn = sqlite3.connect(db_path)
maximum = pd.read_sql("SELECT max(ann_num) FROM price_set", conn)
print(maximum)
price_db = PriceDB(db_path)
price_db.init_db()
start_num = int(maximum.values[0,0] + 1)
for i in range(2000):
    try:
        url = f"https://ebid.korail.com/goods/printOpen.do?gubun=1&zzbidinv={start_num+i}-00&zzstnum=00"
        driver.get(url)
        title = driver.find_element(By.ID, "description").text
        open_result = driver.find_element(By.ID, "openresult_t").text
        confirm_price = driver.find_element(By.ID, "confirm_fcast").text

    # open_result이 특정 값이며, confirm_price가 유효한 값일 때만 처리
        # 주의: and/or 우선순위 때문에 괄호가 필요합니다. open_result가 조건에 해당하고
        # confirm_price가 '-' 또는 빈 문자열이 아니어야 합니다.
        if open_result in ("낙찰업체상신", "유찰 처리") and confirm_price not in ('-', '', None):
            if '용역' in title:
                print(i + start_num, title, open_result, confirm_price)
                # 날짜
                date_with_time = driver.find_element(By.ID, "zzopen").text
                date = date_with_time.split(' ')[0]

                # 기초가
                base_price = driver.find_element(By.ID, "fcastprice").text
                base_price = int(base_price.replace(',', ''))

                # 예가: 안전하게 파싱 (예: '-' 인 경우 또는 파싱 실패 시 0으로 처리)
                try:
                    predict_price = int(confirm_price.replace(',', ''))
                except Exception:
                    predict_price = 0
                    print(f"[WARN] {start_num + i}: 예가값 파싱 실패: {confirm_price}")

                # 낙찰하한율
                url_min = f"https://ebid.korail.com/goods/printIn.do?zzbidinv={start_num + i}-00&zzstnum=00"
                driver.get(url_min)
                min_rate = driver.find_element(By.ID, "zzselrate").text

                # 낙찰가
                bid_price = bring_bid_amount(url)
                
                # 예외 처리: bid_price가 None이면 skip
                if bid_price is None:
                    bid_price = 0

                price_db.insert_info(start_num + i, date, base_price, predict_price, bid_price, min_rate)
                print(start_num + i, date, base_price, predict_price, bid_price, min_rate)
    except Exception as e:
        print(f"[ERROR] {start_num + i}: {e}")
