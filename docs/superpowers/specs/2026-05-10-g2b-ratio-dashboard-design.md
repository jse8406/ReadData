# 나라장터 예가율 분석 대시보드 — 2026-05-10 변경분

- 베이스 문서: ./2026-05-04-g2b-ratio-dashboard-design.md
- 작성일: 2026-05-10

## 변경 요약

예비가격 비율 매트릭스의 **연도별 엑셀 다운로드** 기능을 추가했다. 화면 매트릭스(행=1~15, 열=공고)는 시각 비교용이지만 분석/필터링 편의를 위해 엑셀은 1행=1공고로 전치한 형태로 출력한다. 베이스 문서 §9(비범위)에서 "CSV / 이미지 내보내기"로 제외했던 항목을 부분적으로 되돌리는 결정.

## 변경 사항

### 신규 기능 — 매트릭스 엑셀 내보내기 (베이스 §1, §3, §5.1, §9 보강)

- **위치(§3 화면 레이아웃)**: 매트릭스 섹션 제목 행을 `section-title-row` 플렉스로 재구성, 우측에 `[엑셀 다운로드: <연도▼> [다운로드]]` 컨트롤 그룹 배치.
- **연도 선택**: `getAllG2bYearDbs()` 로 로드된 연도 키를 내림차순 정렬해 `<select id="download-year">` 에 채움(최신연도가 default). 다운로드는 검색 필터(시작일/종료일)와 **무관하게** 선택된 연도의 전체 데이터를 출력.

### 신규 컴포넌트 — `downloadMatrixExcel()` (베이스 §5.1 함수표에 신규 행 추가)

| 함수 | 책임 |
|------|------|
| `downloadMatrixExcel()` | 선택 연도 DB에서 `bid_pbanc_no, bid_pbanc_ord, date, base_amount, rsve_price_1..15` 를 `ORDER BY date DESC, bid_pbanc_no DESC` 로 전체 조회 → 비율 계산 → SheetJS `aoa_to_sheet` 로 워크북 생성 → `예비가격비율매트릭스_{연도}.xlsx` 로 저장. 작업 중 버튼 disabled + "생성 중..." 라벨. |

### 데이터 흐름 (베이스 §4 흐름도에 노드 추가)

```
download_year_select [라벨="<select> 연도 선택", 모양=상자];
download_btn [라벨="downloadMatrixExcel()", 모양=상자];
xlsx_writer [라벨="XLSX.utils.aoa_to_sheet → writeFile()", 모양=상자];
download_year_select -> download_btn;
download_btn -> xlsx_writer;
xlsx_writer -> "사용자 다운로드";
```

기존 `doSearch()`/`runMatrixQuery()` 흐름과 **독립**. 페이지네이션·검색 상태에 영향을 주지 않음.

### 외부 의존성 추가 (베이스 §8/§9 영향)

- 신규 CDN: `cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js` (SheetJS).
- 페이지 로드 시점에 추가로 받는 스크립트 1개. 캐시 후 재방문 비용 무시 가능.

### 출력 스키마 — 엑셀 컬럼 (베이스 §6 보강)

| 컬럼 | 비고 |
|------|------|
| 공고번호 | `bid_pbanc_no` |
| 차수 | `bid_pbanc_ord` (재공고 식별자) |
| 날짜 | `date` (DB 원본 형식 그대로) |
| 기초금액 | `base_amount` 정수 |
| 비율1(%) ~ 비율15(%) | `rsve_price_N / base_amount * 100`, 소수점 4자리 반올림. `base_amount` 가 0/null 이면 빈 셀. |

시트명: `{연도}년`. 컬럼 폭 고정(공고번호 16, 차수 6, 날짜 12, 기초금액 14, 비율 각 10).

### 엣지 케이스 (베이스 §7 보강)

| 케이스 | 동작 |
|--------|------|
| 선택 연도 DB가 비어 있음 | `alert('{년}년 데이터가 없습니다.')` 후 종료. |
| `XLSX` 라이브러리 로드 실패 / writeFile 예외 | `try/catch` 로 잡아 `alert('엑셀 파일 생성 중 오류가 발생했습니다: ' + e.message)`, 콘솔에 스택. |
| 다운로드 처리 중 사용자가 다른 연도 재선택 | 버튼이 `disabled` 라 추가 클릭 차단. 진행 중 작업은 그대로 완료. |

### 비범위 갱신 (베이스 §9 일부 철회)

- ❌ → ✅: **CSV/엑셀 내보내기** — 이번 변경으로 매트릭스에 한해 도입.
- 그 외 §9 항목(이미지 내보내기, 히트맵, 통계 요약, 모바일 반응형)은 여전히 비범위.
