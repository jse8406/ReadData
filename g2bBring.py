#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""나라장터 개찰결과 크롤러 - 단일 브라우저 순차 처리
스크롤로 목록 수집 → 각 건 입찰번호 검색 → 상세 조회 → DB 저장 → 다음 건
"""

import sys
import time
import json
import os
import sqlite3
from functools import partial
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from db.g2b_module import G2bDB

print = partial(print, flush=True)
chromedriver_autoinstaller.install()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.execute_cdp_cmd("Network.enable", {})
    return driver


def flush_logs(driver):
    return driver.get_log("performance")


def get_cdp_body(driver, request_id):
    try:
        return driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}).get("body", "")
    except:
        return ""


def find_response(driver, url_keyword):
    for entry in driver.get_log("performance"):
        try:
            msg = json.loads(entry["message"])["message"]
            if msg["method"] == "Network.requestWillBeSent":
                req = msg["params"]["request"]
                if req["method"] == "POST" and url_keyword in req["url"]:
                    body = get_cdp_body(driver, msg["params"]["requestId"])
                    if body:
                        return json.loads(body)
        except:
            pass
    return None


def open_search_page(driver):
    try:
        driver.get("https://www.g2b.go.kr")
    except:
        driver.execute_script("window.stop();")
    time.sleep(4)
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth1"):
        if '입찰' in m.text:
            m.click(); time.sleep(0.5); break
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth2"):
        if '개찰' in m.text:
            m.click(); time.sleep(0.5); break
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth3"):
        if '개찰결과분류조회' in m.text:
            m.click(); time.sleep(7); break
    for _ in range(10):
        try:
            if driver.execute_script("return typeof WebSquare !== 'undefined' && WebSquare.util !== undefined;"):
                return True
        except:
            pass
        time.sleep(0.5)
    return False


def find_date_ids(driver):
    return driver.execute_script(r"""
        var r = [];
        var inputs = document.querySelectorAll("input[type='text']");
        for(var i=0; i<inputs.length; i++){
            var id = inputs[i].id || '';
            if(inputs[i].value && inputs[i].value.match(/^20[0-9]{2}\//)
               && (id.indexOf('ibxStrDay') >= 0 || id.indexOf('ibxEndDay') >= 0)
               && id.indexOf('popupCnts') < 0) {
                r.push(id);
            }
        }
        return r;
    """)


def search(driver, date_start, date_end, bid_no=''):
    ids = find_date_ids(driver)
    if len(ids) < 2:
        return []
    driver.execute_script(f"""
        WebSquare.util.getComponentById('{ids[0]}').setValue('{date_start}');
        WebSquare.util.getComponentById('{ids[1]}').setValue('{date_end}');
        WebSquare.util.getComponentById('mf_wfm_container_ibxBidPbancNo').setValue('{bid_no}');
    """)
    time.sleep(0.3)
    flush_logs(driver)
    driver.execute_script("document.getElementById('mf_wfm_container_btnS0001').click();")
    time.sleep(4)
    data = find_response(driver, "selectOnbsRsltClsfList")
    if data:
        return data.get("result", {}).get("onbsRsltClsfList", [])
    return []


def scroll_collect(driver):
    """스크롤해서 추가 목록 수집"""
    all_items = []
    seen = set()
    for _ in range(500):
        flush_logs(driver)
        driver.execute_script("""
            var el = document.getElementById('mf_wfm_container_onbsRsltClsfInqyGrd_scrollY_div');
            if (el) el.scrollTop = el.scrollHeight;
        """)
        time.sleep(1.5)
        data = find_response(driver, "selectOnbsRsltClsfList")
        if not data:
            break
        items = data.get("result", {}).get("onbsRsltClsfList", [])
        if not items:
            break
        new_count = 0
        for item in items:
            key = item["bidPbancNo"] + item["bidPbancOrd"] + item["bidClsfNo"]
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        if new_count == 0:
            break
        if len(all_items) % 500 < 10:
            print(f"  스크롤 누적 {len(all_items)}건")
    return all_items


def get_detail(driver, grid_row_index):
    """상세페이지 진입 → 예비가격 조회 → 목록 복귀"""
    btn_id = f"mf_wfm_container_onbsRsltClsfInqyGrd_button_{grid_row_index}_7"
    try:
        driver.execute_script(f"document.getElementById('{btn_id}').click();")
    except:
        return None
    time.sleep(5)

    flush_logs(driver)
    view_btn = None
    for bid in ["mf_wfm_container_godsBtnRsvePrce", "mf_wfm_container_cstnBtnRsvePrce"]:
        try:
            b = driver.find_element(By.ID, bid)
            if b.is_displayed():
                view_btn = b; break
        except:
            pass
    if not view_btn:
        for b in driver.find_elements(By.CSS_SELECTOR, "button"):
            try:
                if b.is_displayed() and '보기' in b.text:
                    view_btn = b; break
            except:
                pass
    if not view_btn:
        try:
            driver.execute_script("document.getElementById('mf_wfm_container_btnLst').click();")
            time.sleep(1.5)
        except:
            pass
        return None

    driver.execute_script("arguments[0].click();", view_btn)
    time.sleep(3)
    data = find_response(driver, "selectRsvePrceInfo")

    # 모달 닫기 + 목록 복귀
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
        for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
            try:
                bid = btn.get_attribute("id") or ""
                if btn.is_displayed() and ('Close' in bid or 'close' in bid) and 'poup' in bid:
                    btn.click(); time.sleep(0.2); break
            except:
                continue
    except:
        pass
    try:
        driver.execute_script("document.getElementById('mf_wfm_container_btnLst').click();")
        time.sleep(1.5)
    except:
        pass
    return data


def parse_prices(rsve_list):
    prices = []
    for row in rsve_list:
        if "plrlRsvePrce1" in row:
            prices.append(row["plrlRsvePrce1"])
        if "plrlRsvePrce2" in row:
            prices.append(row["plrlRsvePrce2"])
    return prices if len(prices) == 15 else None


def generate_month_ranges(start_date, end_date):
    ranges = []
    current = start_date
    while current < end_date:
        month_end = current.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        if month_end > end_date:
            month_end = end_date
        ranges.append((current.strftime("%Y%m%d"), month_end.strftime("%Y%m%d")))
        current = month_end + timedelta(days=1)
    return ranges


def log(msg, log_file=None):
    """콘솔 + 로그 파일에 동시 출력"""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    if log_file:
        log_file.write(line + "\n")
        log_file.flush()


def main():
    db_path = os.path.join(BASE_DIR, 'db', 'g2b.db')
    db = G2bDB(db_path)
    db.init_db()

    end_date = datetime.now()
    start_date = datetime(2026, 4, 1)
    month_ranges = generate_month_ranges(start_date, end_date)

    log_path = os.path.join(BASE_DIR, 'g2b_crawl.log')
    lf = open(log_path, 'a', encoding='utf-8')

    log(f"수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}", lf)
    log(f"총 {len(month_ranges)}개 구간", lf)

    driver = create_driver()
    total_saved = 0
    total_processed = 0

    try:
        for idx, (d_start, d_end) in enumerate(month_ranges):
            log(f"[{idx+1}/{len(month_ranges)}] {d_start} ~ {d_end}", lf)

            try:
                open_search_page(driver)
                first_items = search(driver, d_start, d_end)
            except Exception as e:
                log(f"  검색 실패({e}), 재시작", lf)
                try: driver.quit()
                except: pass
                driver = create_driver()
                try:
                    open_search_page(driver)
                    first_items = search(driver, d_start, d_end)
                except:
                    log(f"  재시도 실패, 건너뜀", lf)
                    continue

            if not first_items:
                log("  결과 없음", lf)
                continue

            all_items = list(first_items)
            seen = {item["bidPbancNo"] + item["bidPbancOrd"] + item["bidClsfNo"] for item in all_items}
            if len(first_items) >= 10:
                extra = scroll_collect(driver)
                for item in extra:
                    key = item["bidPbancNo"] + item["bidPbancOrd"] + item["bidClsfNo"]
                    if key not in seen:
                        seen.add(key)
                        all_items.append(item)

            targets = []
            for item in all_items:
                pgst = item.get("bidPgstCd", "")
                if ("완료" in pgst or pgst == "입160004") and \
                   not db.exists(item["bidPbancNo"], item["bidPbancOrd"], item["bidClsfNo"]):
                    targets.append(item)

            log(f"  전체 {len(all_items)}건 → 개찰완료 미수집 {len(targets)}건", lf)

            for i, item in enumerate(targets):
                bid_no = item["bidPbancNo"]
                bid_ord = item["bidPbancOrd"]
                total_processed += 1

                try:
                    result = search(driver, d_start, d_end, bid_no=bid_no)
                    if not result:
                        log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 검색결과없음", lf)
                        open_search_page(driver)
                        continue
                    detail = get_detail(driver, 0)
                except Exception as e:
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 에러({e})", lf)
                    try: open_search_page(driver)
                    except:
                        try: driver.quit()
                        except: pass
                        driver = create_driver()
                        try: open_search_page(driver)
                        except: break
                    continue

                if not detail:
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 스킵(보기버튼없음)", lf)
                    continue

                bsis = detail.get("bsisAmtInfo", {})
                bsamt = bsis.get("bsamt")
                pnpr = bsis.get("pnpr")
                if not bsamt or not pnpr:
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 스킵(기초가/예정가없음)", lf)
                    continue

                prices = parse_prices(detail.get("rsvePrceList", []))
                if not prices:
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 스킵(예비가격15건아님)", lf)
                    continue

                pbanc = detail.get("pbancInfo", {})
                real_dt = pbanc.get("realOnbsPrnmntDt", "")
                date_str = real_dt.split(" ")[0] if real_dt else item.get("onbsPrnmntDt", "").split(" ")[0]

                row = {
                    "bid_pbanc_no": bid_no,
                    "bid_pbanc_ord": bid_ord,
                    "bid_clsf_no": item["bidClsfNo"],
                    "prcm_bsne_se_cd": item["prcmBsneSeCd"],
                    "bid_pbanc_nm": pbanc.get("bidPbancNm", item.get("bidPbancNm", "")),
                    "date": date_str,
                    "base_amount": bsamt,
                    "predict_price": pnpr,
                }
                for j, p in enumerate(prices, 1):
                    row[f"rsve_price_{j}"] = p

                try:
                    db.insert_result(row)
                    total_saved += 1
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → [저장] {date_str} | 기초:{bsamt:,} | 예정:{pnpr:,} | {item['prcmBsneSeCd']}", lf)
                except sqlite3.IntegrityError:
                    log(f"  [{i+1}/{len(targets)}] {bid_no}-{bid_ord} → 이미존재", lf)

                if total_processed % 100 == 0:
                    log(f"  --- 진행: {total_processed}건 처리, {total_saved}건 저장 ---", lf)

        log(f"완료! 처리: {total_processed}건, 저장: {total_saved}건", lf)

    finally:
        driver.quit()
        lf.close()


if __name__ == "__main__":
    main()
