

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
db_path = os.path.join(base_dir, 'db', 'priceDB.db')
conn = sqlite3.connect(db_path)
maximum = pd.read_sql("SELECT max(ann_num) FROM price_set", conn)

price_db = PriceDB(db_path)
price_db.init_db()
start_num = int(maximum.values[0,0] + 1)

for i in range(500):
    url = f"https://ebid.korail.com/goods/printOpen.do?gubun=1&zzbidinv={start_num+i}-00&zzstnum=00"
    driver.get(url)
    title = driver.find_element(By.ID, "description").text
    open_result = driver.find_element(By.ID, "openresult_t").text
    confirm_price = driver.find_element(By.ID, "confirm_fcast").text
    if open_result == "낙찰업체상신" and confirm_price != '-' and confirm_price != '':
        if '용역' in title:
            # 날짜
            date_with_time = driver.find_element(By.ID, "zzopen").text
            date = date_with_time.split(' ')[0]

            # 기초가
            base_price = driver.find_element(By.ID, "fcastprice").text
            base_price = int(base_price.replace(',', ''))
    
            # 예가
            predict_price = driver.find_element(By.ID, "confirm_fcast").text
            predict_price = int(predict_price.replace(',', ''))
            
            # 낙찰하한율
            url_min = f"https://ebid.korail.com/goods/printIn.do?zzbidinv={start_num + i}-00&zzstnum=00"
            driver.get(url_min)
            min_rate = driver.find_element(By.ID, "zzselrate").text
            price_db.insert_info(start_num + i, date, base_price, predict_price, bring_bid_amount(url), min_rate)
            print(start_num + i, date, base_price, predict_price, bring_bid_amount(url), min_rate)
            