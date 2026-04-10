# 데이터 크롤링 & 대시보드 파이프라인

## 1. 환경 설정

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 2. 코레일 크롤링 + 대시보드 갱신 (메인 파이프라인)

```bash
# 전체 자동화 (크롤링 + 집계 + script.js + JSON 갱신)
python auto_update_dashboard.py

# 특정 연도로 집계
python auto_update_dashboard.py --year 2025

# 크롤링 건너뛰고 기존 DB로만 집계 (테스트용)
python auto_update_dashboard.py --no-crawl
```

`auto_update_dashboard.py`가 내부적으로 다음을 순차 실행합니다:

1. `mpdbBring.py` — 코레일 물품 크롤링 → `db/priceDB.db`
2. `yydbBring.py` — 코레일 용역 크롤링 → `db/yongyuk.db`
3. 데이터 집계 → `html/js/script.js`의 `yValrate*`/`yValamt*` 자동 갱신
4. `average.py` 실행 → `html/data/avgRateData{Mp,Yy}.json` 갱신

## 3. 나라장터(g2b) 크롤링

나라장터는 메인 파이프라인과 분리되어 있습니다. 직접 실행:

```bash
# 월별 크롤링
python g2bBring.py --test --test-date 20260401 --test-end-date 20260430 --test-limit 99999

# 단건 테스트
python g2bBring.py --test-bid R26BK01440199

# 병렬 실행 (메모리 8GB 기준 최대 3개 권장)
nohup python g2bBring.py --test --test-date 20250501 --test-end-date 20250531 --test-limit 99999 > /tmp/g2b_may.log 2>&1 &
nohup python g2bBring.py --test --test-date 20250601 --test-end-date 20250630 --test-limit 99999 > /tmp/g2b_jun.log 2>&1 &
nohup python g2bBring.py --test --test-date 20250701 --test-end-date 20250731 --test-limit 99999 > /tmp/g2b_jul.log 2>&1 &

# 진행 확인
grep -E '완료!|전체.*건' /tmp/g2b_*.log

# 크롤링 완료 후 비율 JSON 생성 (대시보드용)
python g2b_generate_data.py
```

## 4. 파일 구조

```
ReadData/
├── auto_update_dashboard.py    # 메인 자동화 진입점
├── mpdbBring.py                # 코레일 물품 크롤러
├── yydbBring.py                # 코레일 용역 크롤러
├── g2bBring.py                 # 나라장터 크롤러
├── expectedBring.py            # 입찰액 추출 (mp/yy 헬퍼)
├── count.py                    # 비율 카운트 헬퍼
├── average.py                  # 평균 예가율 JSON 생성
├── g2b_generate_data.py        # 나라장터 비율 JSON 생성
├── scheduled_update.py         # 스케줄러 진입점
├── config.ini
├── run_update.bat              # Windows 실행 메뉴
│
├── db/
│   ├── priceDB.db              # 코레일 물품
│   ├── yongyuk.db              # 코레일 용역
│   ├── g2b.db                  # 나라장터
│   ├── db_module.py
│   └── g2b_module.py
│
└── html/
    ├── index.html              # 물품/용역 대시보드
    ├── g2b.html                # 나라장터 비율 분포
    ├── g2b_detail.html         # 나라장터 상세조회 (sql.js)
    ├── price.html              # 가격정보 (용역)
    ├── price_mp.html           # 가격정보 (물품)
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── script.js           # 물품/용역 대시보드 로직
    │   ├── g2b_script.js       # 나라장터 차트
    │   └── db_preloader.js     # IndexedDB 캐싱
    └── data/
        ├── avgRateDataMp.json  # 물품 평균 예가율
        ├── avgRateDataYy.json  # 용역 평균 예가율
        └── g2bRateData.json    # 나라장터 비율
```

## 5. 데이터 흐름

```
[크롤러]              [DB]                [집계]                  [표시]
mpdbBring.py    →    priceDB.db    →    auto_update_dashboard  →  index.html
yydbBring.py    →    yongyuk.db          → script.js
g2bBring.py     →    g2b.db
                                    →    average.py
                                          → avgRateData*.json    →  index.html
                                    →    g2b_generate_data.py
                                          → g2bRateData.json     →  g2b.html

(sql.js 직접 읽기): priceDB.db / yongyuk.db / g2b.db
                    → price.html / price_mp.html / g2b_detail.html
```

## 6. 나라장터 크롤러 주의사항

- `batch_size` (`g2bBring.py:fetch_list_api` 기본 100,000): 월별 전체 데이터가 이보다 많으면 누락 발생
- 이미 DB에 있는 건은 자동 스킵 (같은 월 재실행 안전)
- 크롤링 대상: 물품, 일반용역, 기술용역, 공사 (기타/리스는 예비가격 없어 제외)
- 개찰완료 건 중 기초금액 + 예정가격 + 예비가격 15건이 모두 있는 건만 저장

## 7. 나라장터 수집 완료 현황 (2026-04-10 기준)

| 월 | DB 건수 |
|---|---------|
| 2025/01 | 10,101 |
| 2025/02 | 25,561 |
| 2025/03 | 29,495 |
| 2025/04 | 25,603 |
| 2025/05 | 19,862 |
| 2025/06 | 21,752 |
| 2025/07 | 18,638 |
| 2025/08 | 15,170 |
| 2025/09 | 15,769 |
| 2025/10 | 16,552 |
| 2025/11 | 21,320 |
| 2025/12 | 31,477 |
| 2026/01 | 14,479 |
| 2026/02 | 21,048 |
| 2026/03 | 28,648 |
| 2026/04 | 2,073 (9일까지) |
| **합계** | **317,548** |

**미수집**: 2024/12 이전
