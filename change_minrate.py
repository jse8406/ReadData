from selenium import webdriver
import sqlite3
import pandas as pd
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller

chromedriver_autoinstaller.install() 

options = webdriver.ChromeOptions()
options.add_argument("headless")

db_path = 'db/priceDB.db'
# db_path = 'db/yongyuk.db'

conn = sqlite3.connect(db_path)

df = pd.read_sql("SELECT ann_num, min_rate FROM price_set", conn)
driver = webdriver.Chrome(options=options)

for i in range(len(df['ann_num'])):
    if df.at[i,'min_rate'] == '0':
        url = f"https://ebid.korail.com/goods/printIn.do?gubun=1&zzbidinv={df.at[i,'ann_num']}-00&zzstnum=00"
        driver.get(url)
        
        pre_ann_num = driver.find_element(By.ID, "zzbidinv_old_t").text
        min_rate = driver.find_element(By.ID, 'zzselrate').text
        while min_rate == '0' and pre_ann_num != '':    
            url = f"https://ebid.korail.com/goods/printIn.do?gubun=1&zzbidinv={pre_ann_num}&zzstnum=00"
            driver.get(url)
            pre_ann_num = driver.find_element(By.ID, "zzbidinv_old_t").text
            min_rate = driver.find_element(By.ID, 'zzselrate').text
        if pre_ann_num !='' and min_rate != '0':
            cursor = conn.cursor()
            cursor.execute("""UPDATE price_set SET min_rate = ? WHERE ann_num = ?""", (min_rate, df.at[i, 'ann_num']))
            conn.commit()
        