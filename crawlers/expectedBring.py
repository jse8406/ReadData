from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller

# 크롬 창 열리지 않는 옵션
options = webdriver.ChromeOptions()
options.add_argument("headless")
chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
driver = webdriver.Chrome(options=options)
#url = 'https://ebid.korail.com/goods/printOpen.do?zzbidinv=9236708-00&zzstnum=00'

#예가 가져오기

def bring_bid_amount(url):

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='generalTab1')
    if table:
        tbody = table.find('tbody')
        if tbody:
            td_ele = tbody.find_all('td', class_='tdac')
            result = []
            if td_ele:
                for td_e in td_ele:
                    result.append(td_e.text)
                    if td_e.text == "적격":
                        result.pop()
                        result.pop()
                        bid_amount = result.pop()
                        bid_amount = int(bid_amount.replace(',', ''))
                        return bid_amount
