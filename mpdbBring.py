from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from db.db_module import *
import chromedriver_autoinstaller
from expectedBring import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install() 

# 크롬 창 열리지 않는 옵션
options = webdriver.ChromeOptions()
options.add_argument("headless")
column = ['날짜', '기초가', '예가', '투찰가' , '공고번호']

# init DB
base_dir = os.path.dirname(__file__)
db_path = os.path.join(base_dir, 'db', 'priceDB.db')
conn = sqlite3.connect(db_path)
price_db = PriceDB(db_path)
price_db.init_db()

# search from the last bid
maximum = pd.read_sql("SELECT max(ann_num) FROM price_set", conn)
start_num = int(maximum.values[0,0] + 1)
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)  # 최대 10초까지 대기
# 9247000 ~ 끝
# Search and get Data
for i in range(500):
    url = f"https://ebid.korail.com/goods/printOpen.do?gubun=1&zzbidinv={start_num + i}-00&zzstnum=00"
    driver.get(url)
    try:
        open_result = wait.until(EC.presence_of_element_located((By.ID, "openresult_t"))).text
        confirm_price = wait.until(EC.presence_of_element_located((By.ID, "confirm_fcast"))).text
        title = wait.until(EC.presence_of_element_located((By.ID, "description"))).text
        # open_result = driver.find_element(By.ID, "openresult_t").text
        # confirm_price = driver.find_element(By.ID, "confirm_fcast").text
        # title = driver.find_element(By.ID, "description").text
        if open_result == "낙찰업체상신" and confirm_price != '-' and confirm_price != '' and '용역' not in title:
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
            print(start_num + i, date, base_price, predict_price, bring_bid_amount(url), min_rate)
            try:
                price_db.insert_info(start_num + i, date, base_price, predict_price, bring_bid_amount(url), min_rate)
            except sqlite3.IntegrityError:
                print(f"중복 데이터 발생: {start_num + i}, 데이터 저장 건너뜀.")
            
    except Exception as e:
        print(f"오류 발생: {e}, 공고번호: {start_num + i}")
        continue  # 오류가 발생하더라도 다음 루프 계속 진행

# Selenium 종료
#driver.quit()

# https://ebid.korail.com/goods/printOpen.do?gubun=1&zzbidinv=9242021-00&zzstnum=00 여기서 구분에 페이지 넘버, zzbidinv가 입찰공보 번호-00, zzstnum이 차수

#https://ebid.korail.com/goods/printIn.do?zzbidinv=9242115-00&zzstnum=00 낙찰하한률 URL 필요하면 이걸로

#https://ebid.korail.com/goods/printOpen.do?zzbidinv=9220395-00&zzstnum=00
# 2020년도부터