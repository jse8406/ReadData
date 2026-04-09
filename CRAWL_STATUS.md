# 나라장터(g2b) 크롤러 실행 가이드 및 수집 현황

## 실행 방법

### 가상환경 활성화
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 월별 크롤링 (기본)
```bash
python g2bBring.py --test --test-date 20260401 --test-end-date 20260430 --test-limit 99999
```

### 병렬 실행 (메모리 8GB 기준 최대 3개 권장)
```bash
nohup python g2bBring.py --test --test-date 20250501 --test-end-date 20250531 --test-limit 99999 > /tmp/g2b_may.log 2>&1 &
nohup python g2bBring.py --test --test-date 20250601 --test-end-date 20250630 --test-limit 99999 > /tmp/g2b_jun.log 2>&1 &
nohup python g2bBring.py --test --test-date 20250701 --test-end-date 20250731 --test-limit 99999 > /tmp/g2b_jul.log 2>&1 &
```

### 진행 확인
```bash
grep -E '완료!|전체.*건' /tmp/g2b_*.log
```

### 단건 테스트
```bash
python g2bBring.py --test-bid R26BK01440199
```

## 수집 완료 현황 (2026-04-09 기준)

| 월 | DB 건수 | 상태 |
|---|---------|------|
| 2025/08 | 14,939 | 완료 |
| 2025/09 | 15,755 | 완료 |
| 2025/10 | 16,551 | 완료 |
| 2025/11 | 21,319 | 완료 |
| 2025/12 | 31,476 | 완료 |
| 2026/01 | 14,479 | 완료 |
| 2026/02 | 21,048 | 완료 |
| 2026/03 | 28,648 | 완료 |
| 2026/04 | 2,073 | 완료 (9일까지) |
| **합계** | **166,288** | |

**미수집**: 2025/07 이전

## 주의사항

- `batch_size` (현재 100,000): 월별 전체 데이터가 이보다 많으면 누락 발생
- 이미 DB에 있는 건은 자동 스킵되므로 같은 월을 다시 돌려도 안전
- 크롤링 대상: 물품, 일반용역, 기술용역, 공사 (기타/리스는 예비가격 없어 제외)
- 개찰완료 건 중 기초금액 + 예정가격 + 예비가격 15건이 모두 있는 건만 저장
