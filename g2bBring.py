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
import argparse
import logging
import requests
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


def close_site_popups(driver):
    """나라장터 사이트 공지 팝업 닫기 — 위에 있는 팝업부터 역순으로 닫기"""
    try:
        driver.execute_script("""
            // poup ID로 끝나는 _close 버튼 수집 후 역순으로 닫기 (위에 있는 팝업부터)
            var btns = document.querySelectorAll("button[id$='_close']");
            var targets = [];
            for(var i=0; i<btns.length; i++){
                if(btns[i].id.indexOf('poup') >= 0 && btns[i].offsetParent !== null){
                    targets.push(btns[i]);
                }
            }
            for(var i=targets.length-1; i>=0; i--){
                try { targets[i].click(); } catch(e){}
            }
        """)
        time.sleep(1)
    except:
        pass


def open_search_page(driver):
    try:
        driver.get("https://www.g2b.go.kr")
    except:
        driver.execute_script("window.stop();")
    time.sleep(4)
    # 사이트 공지 팝업 닫기
    close_site_popups(driver)
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth1"):
        if '입찰' in m.text:
            m.click(); time.sleep(0.5); break
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth2"):
        if '개찰' in m.text:
            m.click(); time.sleep(0.5); break
    for m in driver.find_elements(By.CSS_SELECTOR, "a.depth3"):
        if '개찰결과분류조회' in m.text:
            m.click(); time.sleep(7); break
    # 검색 페이지 로드 후에도 팝업 닫기
    close_site_popups(driver)
    for _ in range(10):
        try:
            if driver.execute_script("return typeof WebSquare !== 'undefined' && WebSquare.util !== undefined;"):
                break
        except:
            pass
        time.sleep(0.5)
    # 업무구분에서 '기타' 해제, 업무여부에서 '리스' 해제 (예비가격 없는 유형)
    try:
        driver.execute_script("""
            var inputs = document.querySelectorAll("input[type='checkbox']");
            for(var i=0; i<inputs.length; i++){
                var li = inputs[i].closest('li');
                if(!li) continue;
                var txt = li.textContent.trim();
                // 기타 해제
                if(txt === '기타' && inputs[i].checked) inputs[i].click();
                // 리스 해제
                if(txt === '리스' && inputs[i].checked) inputs[i].click();
            }
        """)
        time.sleep(0.3)
    except:
        pass
    return True


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


def scroll_collect(driver, max_items=0):
    """스크롤해서 추가 목록 수집. max_items > 0이면 해당 건수에서 중단"""
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
        if max_items > 0 and len(all_items) >= max_items:
            print(f"  스크롤 수집 상한 도달 ({max_items}건)")
            break
    return all_items


def get_detail(driver, grid_row_index, log_func=None, bid_info=""):
    """상세페이지 진입 → 예비가격 조회 → 목록 복귀"""
    def _log(msg):
        if log_func:
            log_func(msg)

    btn_id = f"mf_wfm_container_onbsRsltClsfInqyGrd_button_{grid_row_index}_7"
    try:
        driver.execute_script(f"document.getElementById('{btn_id}').click();")
    except:
        _log(f"    [DEBUG] {bid_info} 그리드 버튼({btn_id}) 클릭 실패")
        return None

    # 상세 페이지 로딩 대기 — 보기 버튼이 나타날 때까지 최대 10초
    time.sleep(2)
    close_site_popups(driver)  # 공지 팝업이 상세 페이지를 덮는 경우 처리
    view_ready = False
    for wait in range(10):
        time.sleep(1)
        try:
            view_ready = driver.execute_script("""
                var g = document.getElementById('mf_wfm_container_godsBtnRsvePrce');
                var s = document.getElementById('mf_wfm_container_srvcBtnRsvePrce');
                var c = document.getElementById('mf_wfm_container_cstnBtnRsvePrce');
                return (g && g.offsetParent !== null) || (s && s.offsetParent !== null) || (c && c.offsetParent !== null);
            """)
            if view_ready:
                break
        except:
            pass
    _log(f"    [DEBUG] {bid_info} 상세 진입 후 URL: {driver.current_url} (로딩 {wait+1}초, ready={view_ready})")

    # 상세 페이지에 열린 팝업/탭 확인
    if not view_ready:
        popup_info = driver.execute_script("""
            var info = {};
            // 보기 버튼 상태
            var g = document.getElementById('mf_wfm_container_godsBtnRsvePrce');
            var c = document.getElementById('mf_wfm_container_cstnBtnRsvePrce');
            info.gods_exists = !!g;
            info.gods_display = g ? getComputedStyle(g).display : null;
            info.gods_visibility = g ? getComputedStyle(g).visibility : null;
            info.gods_parent_display = g && g.parentElement ? getComputedStyle(g.parentElement).display : null;
            info.cstn_exists = !!c;
            info.cstn_display = c ? getComputedStyle(c).display : null;
            info.cstn_parent_display = c && c.parentElement ? getComputedStyle(c.parentElement).display : null;
            // 열린 팝업 확인
            var pops = document.querySelectorAll("[id*='poup']");
            info.open_popups = [];
            for(var i=0; i<pops.length; i++){
                if(pops[i].offsetParent !== null) info.open_popups.push(pops[i].id);
            }
            return info;
        """)
        _log(f"    [DEBUG] {bid_info} 상세 페이지 상태: {json.dumps(popup_info)}")

    flush_logs(driver)
    view_btn = None

    # 1차: 알려진 ID로 검색 (물품/용역/공사)
    for bid in ["mf_wfm_container_godsBtnRsvePrce", "mf_wfm_container_srvcBtnRsvePrce", "mf_wfm_container_cstnBtnRsvePrce"]:
        try:
            b = driver.find_element(By.ID, bid)
            is_disp = b.is_displayed()
            _log(f"    [DEBUG] {bid_info} 버튼 ID={bid} 존재, displayed={is_disp}")
            if is_disp:
                view_btn = b; break
        except:
            _log(f"    [DEBUG] {bid_info} 버튼 ID={bid} 없음")

    # 2차: '보기' 텍스트 검색
    if not view_btn:
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        _log(f"    [DEBUG] {bid_info} 전체 button 수: {len(all_buttons)}")
        for b in all_buttons:
            try:
                btn_text = b.text.strip()
                btn_id_attr = b.get_attribute("id") or ""
                is_disp = b.is_displayed()
                if '보기' in btn_text or '예비' in btn_text or 'Rsve' in btn_id_attr:
                    _log(f"    [DEBUG] {bid_info} 후보 버튼: id={btn_id_attr}, text='{btn_text}', displayed={is_disp}")
                if is_disp and '보기' in btn_text:
                    view_btn = b; break
            except:
                pass

    if not view_btn:
        # 디버그: 페이지 소스 일부 저장
        try:
            visible_texts = driver.execute_script("""
                var result = [];
                var buttons = document.querySelectorAll('button');
                for(var i=0; i<buttons.length; i++){
                    var b = buttons[i];
                    result.push({id: b.id, text: b.innerText.substring(0,30), visible: b.offsetParent !== null});
                }
                return result.slice(0, 30);
            """)
            _log(f"    [DEBUG] {bid_info} 보기버튼 못찾음. 페이지 내 버튼 목록:")
            for vt in visible_texts:
                _log(f"      id={vt['id']}, text='{vt['text']}', visible={vt['visible']}")
        except Exception as e:
            _log(f"    [DEBUG] {bid_info} 버튼 목록 수집 실패: {e}")

        try:
            driver.execute_script("document.getElementById('mf_wfm_container_btnLst').click();")
            time.sleep(1.5)
        except:
            pass
        return None

    flush_logs(driver)  # 클릭 전 로그 비우기

    # WebSquare 버튼은 JS click이 이벤트를 트리거하지 못할 수 있음 → 네이티브 클릭 우선 시도
    btn_id_attr = view_btn.get_attribute("id") or ""
    _log(f"    [DEBUG] {bid_info} 보기 버튼 클릭 시도: id={btn_id_attr}")
    try:
        view_btn.click()  # Selenium 네이티브 클릭
    except Exception as click_err:
        _log(f"    [DEBUG] {bid_info} 네이티브 클릭 실패({click_err}), JS 클릭 시도")
        driver.execute_script("arguments[0].click();", view_btn)

    # 응답을 여러 번 시도하며 대기
    data = None
    for attempt in range(8):
        time.sleep(1)
        data = find_response(driver, "selectRsvePrceInfo")
        if data:
            _log(f"    [DEBUG] {bid_info} 예비가격 응답 수신 (attempt {attempt+1})")
            break
        # 모달이 열렸는지 확인
        if attempt == 2:
            modal_check = driver.execute_script("""
                var popups = document.querySelectorAll("[id*='popup'], [id*='Popup'], [id*='poup'], [class*='modal']");
                var visible = [];
                for(var i=0; i<popups.length; i++){
                    if(popups[i].offsetParent !== null || popups[i].style.display !== 'none'){
                        visible.push(popups[i].id || popups[i].className);
                    }
                }
                return visible;
            """)
            _log(f"    [DEBUG] {bid_info} 모달/팝업 상태: {modal_check}")

    if not data:
        # 디버그: 클릭 후 어떤 네트워크 요청이 있었는지 확인
        remaining_logs = driver.get_log("performance")
        post_urls = []
        for entry in remaining_logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if msg["method"] == "Network.requestWillBeSent":
                    req = msg["params"]["request"]
                    if req["method"] == "POST":
                        post_urls.append(req["url"].split("/")[-1])
            except:
                pass
        _log(f"    [DEBUG] {bid_info} 예비가격 API 응답 없음 (8회 시도). POST 요청들: {post_urls}")

    # 데이터를 얻었으면 바로 반환 — 페이지 정리는 호출자가 담당
    return data


def get_session_from_driver(driver):
    """Selenium 드라이버에서 requests 세션 생성"""
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "https://www.g2b.go.kr/",
        "Usr-Id": "null",
    })
    return session


LIST_URL = "https://www.g2b.go.kr/pb/pbo/pboc/OnbsRslt/selectOnbsRsltClsfList.do"
LIST_HEADERS = {
    "Menu-Info": '{"menuNo":"01522","menuCangVal":"PBOC006_01","bsneClsfCd":"%EC%97%85130028","scrnNo":"02117"}',
    "submissionid": "mf_wfm_container_selectOnbsRsltClsfList",
}

RSVE_PRCE_URL = "https://www.g2b.go.kr/pb/pbo/pboc/OnbsRslt/selectRsvePrceInfo.do"
RSVE_PRCE_HEADERS = {
    "Menu-Info": '{"menuNo":"01558","menuCangVal":"PBOC024_01","bsneClsfCd":"%EC%97%85130028","scrnNo":"04255"}',
    "submissionid": "mf_wfm_container_RsvePrceCmpuRsltPL_wframe_popupCnts_selectRsvePrceInfo",
}


def fetch_list_api(session, date_start, date_end, batch_size=100000):
    """API 직접 호출로 목록 조회 — 스크롤 불필요"""
    payload = {
        "dlSrchOnbsRsltClsfListInM": {
            "bidPbancNo": "",
            "bidPbancOrd": "",
            "bidPbancNm": "",
            "onbsYmdStr": date_start,
            "onbsYmdEnd": date_end,
            # 전체 업무구분
            "prcmBsneSeCd": "0000 조070001 조070002 조070003 조070004 조070005",
            "frcpYn": "Y",
            "rsrvYn": "Y",
            "laseYn": "Y",
            "chkBsneAllYn": "Y",
            "lastIndex": batch_size,
            "firstIndex": 1,
            "inqEnd": "",
            "stepBarYn": "",
            "pbancKndCd": "공440002",
        }
    }
    try:
        resp = session.post(LIST_URL, data=json.dumps(payload), headers=LIST_HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("result", {}).get("onbsRsltClsfList", [])
            if not items:
                print(f"  [API DEBUG] status=200 but 0 items. keys={list(data.get('result', {}).keys())}")
            return items
        else:
            print(f"  [API DEBUG] status={resp.status_code}, body={resp.text[:200]}")
    except Exception as e:
        print(f"  [API DEBUG] error: {e}")
    return []


def fetch_detail_api(session, item):
    """API 직접 호출로 예비가격 상세 데이터 조회"""
    payload = {
        "dlSrchPbancInfoInM": {
            "bidPbancNo": item["bidPbancNo"],
            "bidPbancOrd": item["bidPbancOrd"],
            "bidClsfNo": item["bidClsfNo"],
            "bidPrgrsOrd": item.get("bidPrgrsOrd", "001"),
            "prcmBsneSeCd": item["prcmBsneSeCd"],
            "blffVrfcYn": "",
        }
    }
    try:
        resp = session.post(RSVE_PRCE_URL, json=payload, headers=RSVE_PRCE_HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None


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
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='테스트 모드: 특정 날짜 범위, 제한 건수')
    parser.add_argument('--test-date', type=str, default='20260408', help='테스트 시작 날짜 (기본: 20260408)')
    parser.add_argument('--test-end-date', type=str, default='', help='테스트 종료 날짜 (미지정 시 시작일과 동일)')
    parser.add_argument('--test-limit', type=int, default=500, help='테스트 시 최대 처리 건수 (기본: 500)')
    parser.add_argument('--test-bid', type=str, default='', help='특정 입찰공고번호만 테스트')
    args = parser.parse_args()

    db_path = os.path.join(BASE_DIR, 'db', 'g2b.db')
    db = G2bDB(db_path)
    db.init_db()

    if args.test:
        start_date = datetime.strptime(args.test_date, "%Y%m%d")
        end_date = datetime.strptime(args.test_end_date, "%Y%m%d") if args.test_end_date else start_date
        month_ranges = [(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))]
    else:
        end_date = datetime.now()
        start_date = datetime(2026, 4, 1)
        month_ranges = generate_month_ranges(start_date, end_date)

    log_path = os.path.join(BASE_DIR, 'g2b_crawl.log')
    lf = open(log_path, 'a', encoding='utf-8')

    # --test-bid: 특정 공고번호 단건 테스트
    if args.test_bid:
        bid_no = args.test_bid.strip()
        log(f"[단건 테스트] 공고번호: {bid_no}", lf)
        driver = create_driver()
        try:
            open_search_page(driver)
            # 넓은 날짜 범위로 검색
            result = search(driver, '20260101', '20261231', bid_no=bid_no)
            if not result:
                log(f"  검색결과 없음", lf)
                return
            log(f"  검색결과 {len(result)}건", lf)
            log(f"  목록 데이터: {json.dumps({k: result[0].get(k) for k in ['bidPbancNo','bidPbancOrd','bidClsfNo','prcmBsneSeCd','bidPgstCd','bidPbancNm']}, ensure_ascii=False)}", lf)
            log_detail = partial(log, log_file=lf)
            detail = get_detail(driver, 0, log_func=log_detail, bid_info=bid_no)
            if not detail:
                log(f"  상세 데이터 없음", lf)
                return
            # 전체 데이터 출력
            bsis = detail.get("bsisAmtInfo", {})
            log(f"  bsisAmtInfo: {json.dumps(bsis, ensure_ascii=False)}", lf)
            pbanc = detail.get("pbancInfo", {})
            log(f"  pbancInfo keys: {list(pbanc.keys())}", lf)
            rsve = detail.get("rsvePrceList", [])
            prices = parse_prices(rsve)
            log(f"  예비가격 {len(rsve)}행 → 파싱 결과: {prices}", lf)
            log(f"  detail keys: {list(detail.keys())}", lf)
        finally:
            driver.quit()
            lf.close()
        return

    mode_str = "[테스트 모드] " if args.test else ""
    log(f"{mode_str}수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}", lf)
    log(f"총 {len(month_ranges)}개 구간", lf)

    driver = create_driver()
    total_saved = 0
    total_processed = 0

    try:
        # Selenium으로 페이지 진입 + 검색 한 번 실행하여 세션 초기화
        open_search_page(driver)
        search(driver, month_ranges[0][0], month_ranges[0][1])
        time.sleep(2)
        session = get_session_from_driver(driver)

        for idx, (d_start, d_end) in enumerate(month_ranges):
            log(f"[{idx+1}/{len(month_ranges)}] {d_start} ~ {d_end}", lf)

            # API로 목록 조회
            all_items = fetch_list_api(session, d_start, d_end)
            if not all_items:
                log("  결과 없음", lf)
                continue

            targets = []
            for item in all_items:
                pgst = item.get("bidPgstCd", "")
                if ("완료" in pgst or pgst == "입160004") and \
                   not db.exists(item["bidPbancNo"], item["bidPbancOrd"], item["bidClsfNo"]):
                    targets.append(item)

            if args.test:
                targets = targets[:args.test_limit]

            log(f"  전체 {len(all_items)}건 → 개찰완료 미수집 {len(targets)}건", lf)

            for i, item in enumerate(targets):
                bid_no = item["bidPbancNo"]
                bid_ord = item["bidPbancOrd"]
                bid_info = f"{bid_no}-{bid_ord}"
                total_processed += 1

                detail = fetch_detail_api(session, item)

                if not detail:
                    log(f"  [{i+1}/{len(targets)}] {bid_info} → 스킵(API응답없음)", lf)
                    continue

                bsis = detail.get("bsisAmtInfo") or {}
                bsamt = bsis.get("bsamt")
                pnpr = bsis.get("pnpr")
                if args.test:
                    log(f"    [DEBUG] {bid_info} bsisAmtInfo: bsamt={bsamt}, pnpr={pnpr}, keys={list(bsis.keys())}", lf)
                    log(f"    [DEBUG] {bid_info} detail keys: {list(detail.keys())}", lf)
                if not bsamt or not pnpr:
                    log(f"  [{i+1}/{len(targets)}] {bid_info} → 스킵(기초가/예정가없음)", lf)
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
