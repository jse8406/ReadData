# 대시보드 자동 업데이트 시스템

코레일 / 나라장터 입찰 데이터를 크롤링하고 SQLite 에 적재한 뒤, 웹 대시보드(`html/`)를 자동으로 갱신합니다.

## 폴더 구조

```
crawlers/                  # Selenium 크롤러
  mpdbBring.py             # 코레일 물품
  yydbBring.py             # 코레일 용역
  g2bBring.py              # 나라장터 (G2B)
  expectedBring.py         # 낙찰가 추출 헬퍼
pipeline/                  # 자동화 / 집계
  auto_update_dashboard.py # 메인 자동화 (DashboardAutomator)
  scheduled_update.py      # Windows 작업 스케줄러용 진입점
  count.py                 # 비율 카운팅 헬퍼
  average.py               # 10일 단위 평균 예가율 -> JSON
  g2b_generate_data.py     # g2b_*.db -> g2bRateData.json
db/                        # SQLite DB + 액세스 모듈
  db_module.py             # PriceDB (코레일)
  g2b_module.py            # G2bDB (나라장터)
  *.db
html/                      # 정적 대시보드
docs/                      # 스펙 / 플랜 문서
run_update.bat             # 윈도우 GUI 메뉴 (배치)
requirements.txt
```

## 사용법

모든 진입점은 **프로젝트 루트에서 모듈 형태로 실행**합니다 (`-m` 옵션).

### 윈도우 GUI 메뉴

```cmd
run_update.bat
```

### 명령줄

```bash
# 전체 자동화 (크롤링 + 집계 + script.js + JSON 갱신)
python -m pipeline.auto_update_dashboard

# 기존 데이터로만 집계 (크롤링 스킵)
python -m pipeline.auto_update_dashboard --no-crawl

# 특정 연도 집계
python -m pipeline.auto_update_dashboard --year 2024

# 나라장터 크롤러 (별도 파이프라인)
python -m crawlers.g2bBring

# 나라장터 비율 JSON 생성
python -m pipeline.g2b_generate_data
```

### 스케줄러 자동화

Windows 작업 스케줄러:
- 프로그램: `python`
- 인수: `-m pipeline.scheduled_update`
- 시작 위치: 프로젝트 루트 경로

## 의존성

- Python 3.10+
- selenium, pandas, beautifulsoup4, chromedriver-autoinstaller, requests
- Chrome 브라우저 (headless)
- SQLite (stdlib)

```bash
pip install -r requirements.txt
```

## 데이터 흐름 (코레일)

1. `crawlers.mpdbBring` / `crawlers.yydbBring` → `db/priceDB.db` / `db/yongyuk.db`
2. `pipeline.auto_update_dashboard` → 월별·예가율범위별 집계 → `html/js/script.js` 의 `yValamt{연도}` / `yValrate{연도}` 배열 갱신
3. `pipeline.average` → `html/data/avgRateDataMp.json` / `avgRateDataYy.json`

## 데이터 흐름 (나라장터)

1. `crawlers.g2bBring` → `db/g2b_<연도>.db` (GitHub 100MB 제한 회피용 연도별 분할)
2. `pipeline.g2b_generate_data` → `html/data/g2bRateData.json` (모든 연도 DB 합산)
3. `html/g2b.html` / `g2b_detail.html` / `g2b_ratio.html` 가 위 JSON / DB 를 표시

## 로그

`dashboard_update.log` (스케줄러 실행 시 생성), `g2b_crawl.log` (g2bBring 실행 시).
