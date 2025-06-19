# 📊 대시보드 자동 업데이트 시스템

이 시스템은 웹 크롤링, 데이터 집계, 대시보드 업데이트를 완전 자동화합니다.

## 🚀 주요 기능

- **자동 웹 크롤링**: `mpdbBring.py`, `yydbBring.py` 자동 실행
- **데이터 집계**: SQLite 데이터베이스에서 데이터 자동 집계
- **대시보드 업데이트**: `script.js` 파일의 const 변수 자동 업데이트
- **스케줄링 지원**: Windows 작업 스케줄러 연동 가능
- **백업 기능**: 기존 데이터 백업 후 업데이트

## 📁 파일 구조

```
├── auto_update_dashboard.py    # 메인 자동화 스크립트
├── scheduled_update.py         # 스케줄러용 실행 스크립트
├── run_update.bat             # Windows 배치 파일 (GUI)
├── config.ini                 # 설정 파일
├── mpdbBring.py              # 물품 크롤러
├── yydbBring.py              # 용역 크롤러
├── updateAmount.py           # 수량 집계 (참고용)
├── updatePercent.py          # 비율 집계 (참고용)
├── db/
│   ├── priceDB.db           # 물품 데이터베이스
│   └── yongyuk.db           # 용역 데이터베이스
└── html/
    ├── script.js            # 대시보드 JavaScript 파일
    ├── index.html           # 대시보드 메인 페이지
    └── ...
```

## 🔧 사용법

### 1. 간단한 실행 (Windows)

```cmd
# 배치 파일 실행 (GUI 메뉴)
run_update.bat
```

### 2. 명령줄 실행

```cmd
# 전체 자동화 (크롤링 + 집계 + 업데이트)
python auto_update_dashboard.py

# 기존 데이터만으로 업데이트 (크롤링 제외)
python auto_update_dashboard.py --no-crawl

# 특정 연도 데이터 업데이트
python auto_update_dashboard.py --year 2024

# 도움말
python auto_update_dashboard.py --help
```

### 3. 스케줄 자동화

Windows 작업 스케줄러에서 `scheduled_update.py`를 등록하면 자동 실행됩니다.

**스케줄러 등록 예시:**
1. Windows 작업 스케줄러 열기
2. 기본 작업 만들기
3. 프로그램: `python`
4. 인수: `scheduled_update.py`
5. 시작 위치: `C:\Users\jse\Desktop\vscode\ReadData`
6. 트리거: 매일 오전 9시

## ⚙️ 설정

`config.ini` 파일에서 다양한 설정을 변경할 수 있습니다:

- 크롤링 범위 조정
- 데이터베이스 경로 변경
- 로그 레벨 설정
- 백업 옵션 등

## 📝 작업 과정

1. **웹 크롤링 단계**
   - `mpdbBring.py`: 물품 입찰 정보 크롤링 → `priceDB.db`
   - `yydbBring.py`: 용역 입찰 정보 크롤링 → `yongyuk.db`

2. **데이터 집계 단계**
   - 각 데이터베이스에서 월별/예가율별 데이터 집계
   - 수량 데이터와 비율 데이터 계산

3. **대시보드 업데이트 단계**
   - `script.js` 파일의 const 변수들 자동 업데이트
   - `yValamt{연도}`, `yValrate{연도}` 등 업데이트

## 🔍 로그 및 모니터링

- 실행 로그: `dashboard_update.log`
- 에러 발생 시 상세 정보 기록
- 각 단계별 진행 상황 표시

## 🛠️ 문제 해결

### 크롤링 실패 시
- 네트워크 연결 확인
- Chrome 드라이버 업데이트
- 웹사이트 구조 변경 여부 확인

### 데이터베이스 오류 시
- 데이터베이스 파일 권한 확인
- 디스크 공간 확인
- 백업 파일에서 복구

### script.js 업데이트 실패 시
- 파일 권한 확인
- 기존 백업에서 복구
- 수동으로 변수 확인

## 📞 기술 지원

시스템 관련 문의나 오류 발생 시:
1. 로그 파일 (`dashboard_update.log`) 확인
2. 에러 메시지 및 로그와 함께 문의
3. 실행 환경 정보 (Python 버전, OS 등) 제공

## 🔄 업그레이드

새로운 기능이나 버그 수정이 있을 때:
1. 기존 설정 파일 백업
2. 새 파일들로 교체
3. 설정 파일 복원 및 확인
