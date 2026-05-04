# 나라장터 예가율 분석 대시보드 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 나라장터 데이터에 대해 (1) 기간 내 공고들의 예비가격 1~15 비율을 한 화면에서 가로로 비교하는 매트릭스, (2) 최근 100/200/300건의 예가율 추이 라인 차트를 한 페이지에서 제공한다.

**Architecture:** sql.js + IndexedDB로 클라이언트 사이드에서 연도별 g2b DB를 조회하는 단일 HTML 페이지 (`html/g2b_ratio.html`). `g2b_detail.html`의 검색/페이지네이션/연도 분배 패턴을 그대로 차용한다. 차트는 Chart.js 2.9.4 사용 — 한 번에 300건을 받아두고 토글 시 메모리에서 `slice` + `chart.update()`로 추가 쿼리 없이 갱신한다.

**Tech Stack:** HTML/CSS/Vanilla JS, sql.js 1.8.0 (CDN), Chart.js 2.9.4 (CDN), 기존 `js/db_preloader.js` / `js/topbar.js` / `css/style.css`.

**Spec:** `docs/superpowers/specs/2026-05-04-g2b-ratio-dashboard-design.md`

**Verification approach:** 이 프로젝트에는 JS 테스트 인프라가 없다. 각 태스크는 브라우저에서 페이지를 새로고침해 동작을 시각적으로 확인한다 (브라우저 콘솔 + 화면). 가능한 경우 검증 명령(예: `python -m http.server`)을 명시한다.

---

## File Structure

| 경로 | 작업 | 책임 |
|------|------|------|
| `html/g2b_ratio.html` | **Create** | 페이지 마크업 + 인라인 JS (initDB, 검색, 매트릭스, 페이지네이션, 차트, 토글) |
| `html/js/topbar.js` | **Modify** | `items` 배열에 `예가율 분석` 메뉴 항목 한 줄 추가 |

`g2b_detail.html`이 모든 JS를 인라인으로 두는 패턴을 그대로 따른다(파일 분리 없음). 페이지 단위로 자기완결적이며 다른 페이지가 이 JS를 재사용하지 않는다.

---

## Task 1: 페이지 스켈레톤 + 토픽바 + 검색 패널 (DB 로딩 없음)

**목표:** 페이지가 열리고 헤더/검색 패널/빈 영역이 보인다. JS 동작은 아직 없음.

**Files:**
- Create: `html/g2b_ratio.html`

- [ ] **Step 1: 페이지 스켈레톤 작성**

`html/g2b_ratio.html`을 다음 내용으로 생성:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>나라장터 예가율 분석</title>
    <link rel="stylesheet" href="css/style.css">
    <script src="js/db_preloader.js"></script>
    <script src="js/topbar.js" defer></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0 20px 20px 20px; }

        #loading {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.9); display: flex; justify-content: center;
            align-items: center; z-index: 1000; flex-direction: column;
        }
        #loading .spinner {
            width: 50px; height: 50px; border: 5px solid #ddd;
            border-top: 5px solid #6b93d6; border-radius: 50%;
            animation: spin 1s linear infinite; margin-bottom: 16px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .search-panel {
            background: #f8f9fa; border-radius: 10px; padding: 16px 20px;
            margin: 16px auto; max-width: 1400px;
            display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }
        .search-panel label { font-size: 0.85em; color: #555; display: block; margin-bottom: 4px; }
        .search-panel input {
            padding: 8px 12px; border: 1px solid #ccc; border-radius: 6px;
            font-size: 0.95em; outline: none;
        }
        .search-panel input:focus { border-color: #6b93d6; }
        .search-panel .field { display: flex; flex-direction: column; }
        .search-btn {
            background: #6b93d6; color: #fff; border: none; border-radius: 8px;
            padding: 9px 24px; font-size: 1em; cursor: pointer; font-weight: bold;
        }
        .search-btn:hover { background: #4666a3; }
        .reset-btn {
            background: #999; color: #fff; border: none; border-radius: 8px;
            padding: 9px 18px; font-size: 1em; cursor: pointer;
        }
        .reset-btn:hover { background: #777; }

        #result-count { margin: 10px auto; max-width: 1400px; font-size: 0.9em; color: #666; text-align: center; }

        .section-title { max-width: 1400px; margin: 24px auto 8px; font-size: 1.05em; color: #333; }

        #matrix-table { width: 100%; max-width: 1400px; margin: 8px auto 0; font-size: 13px; }
        #matrix-table th { padding: 8px 6px; text-align: center; white-space: nowrap; }
        #matrix-table td { padding: 6px; text-align: center; }
        #matrix-table td.label-col, #matrix-table th.label-col { font-weight: bold; background: #f0f3f7; }
        #matrix-table td.num-col { font-family: Arial, sans-serif; }

        .pagination {
            display: flex; justify-content: center; gap: 4px; margin: 16px 0; flex-wrap: wrap;
        }
        .pagination button {
            padding: 6px 12px; border: 1px solid #ccc; background: #fff;
            border-radius: 4px; cursor: pointer; font-size: 0.9em;
        }
        .pagination button:hover { background: #e8e8e8; }
        .pagination button.active { background: #6b93d6; color: #fff; border-color: #6b93d6; }
        .pagination button:disabled { opacity: 0.4; cursor: default; }

        #trend-section { max-width: 1400px; margin: 8px auto 0; }
        #trend-toggle { display: flex; justify-content: center; gap: 8px; margin: 8px 0; }
        #trend-toggle button {
            padding: 6px 16px; border: 1px solid #ccc; background: #fff;
            border-radius: 6px; cursor: pointer; font-size: 0.9em;
        }
        #trend-toggle button.active { background: #6b93d6; color: #fff; border-color: #6b93d6; }
        #trend-toggle button:disabled { opacity: 0.4; cursor: default; }
        #trend-chart-wrap { background: #fff; padding: 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    </style>
</head>
<body>
    <div id="loading">
        <div class="spinner"></div>
        <div>데이터베이스 로딩 중...</div>
    </div>

    <div id="topbar"></div>

    <header>
        <h1>나라장터 예가율 분석</h1>
    </header>

    <div class="search-panel">
        <div class="field">
            <label>시작일</label>
            <input type="date" id="date-from">
        </div>
        <div class="field">
            <label>종료일</label>
            <input type="date" id="date-to">
        </div>
        <button class="search-btn" onclick="doSearch()">검색</button>
        <button class="reset-btn" onclick="resetSearch()">초기화</button>
    </div>

    <div id="result-count"></div>

    <div class="section-title">예비가격 비율 매트릭스 (기초금액 대비, %)</div>
    <table id="matrix-table">
        <thead><tr id="matrix-head"></tr></thead>
        <tbody id="matrix-body"></tbody>
    </table>
    <div class="pagination" id="pagination"></div>

    <div class="section-title">예가율 추이 (예정가격 ÷ 기초금액 × 100)</div>
    <div id="trend-section">
        <div id="trend-toggle">
            <button data-limit="100" onclick="setTrendLimit(100)">최근 100건</button>
            <button data-limit="200" onclick="setTrendLimit(200)">최근 200건</button>
            <button data-limit="300" onclick="setTrendLimit(300)">최근 300건</button>
        </div>
        <div id="trend-chart-wrap">
            <canvas id="trend-chart" height="120"></canvas>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/sql-wasm.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
    <script>
        // 다음 태스크에서 채움
        function doSearch() {}
        function resetSearch() {}
        function setTrendLimit(n) {}
    </script>
</body>
</html>
```

- [ ] **Step 2: 브라우저에서 페이지 확인**

프로젝트 루트에서 정적 서버 실행:

```bash
cd html && python -m http.server 8000
```

브라우저로 `http://localhost:8000/g2b_ratio.html` 열기.
기대: 토픽바, 헤더 "나라장터 예가율 분석", 검색 패널(시작일/종료일/검색/초기화), 빈 매트릭스/차트 영역이 보인다. 로딩 스피너는 계속 떠 있다(아직 `initDB` 없음 — Task 2에서 해결).

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 분석 페이지 스켈레톤 추가"
```

---

## Task 2: 토픽바 메뉴 추가

**Files:**
- Modify: `html/js/topbar.js:9-16`

- [ ] **Step 1: `items` 배열에 메뉴 추가**

`html/js/topbar.js`의 9~16번 줄 `items` 배열에서 마지막 항목(`나라장터 상세`) 뒤에 줄을 추가:

```javascript
    const items = [
        { label: '물품',            active: false,                        onclick: isIndex ? 'change2Mp()' : "location.href='index.html'" },
        { label: '용역',            active: false,                        onclick: isIndex ? 'change2Yy()' : "location.href='index.html'" },
        { label: '가격정보 (물품)', active: page === 'price_mp.html',     onclick: "location.href='price_mp.html'" },
        { label: '가격정보 (용역)', active: page === 'price.html',        onclick: "location.href='price.html'" },
        { label: '나라장터',        active: page === 'g2b.html',          onclick: "location.href='g2b.html'" },
        { label: '나라장터 상세',   active: page === 'g2b_detail.html',   onclick: "location.href='g2b_detail.html'" },
        { label: '예가율 분석',     active: page === 'g2b_ratio.html',    onclick: "location.href='g2b_ratio.html'" },
    ];
```

- [ ] **Step 2: 브라우저 확인**

`http://localhost:8000/g2b_ratio.html` 새로고침.
기대: 토픽바 마지막에 "예가율 분석" 버튼이 active 상태로 표시. 다른 페이지(`g2b_detail.html`)에서도 메뉴가 보이고 클릭 시 이 페이지로 이동.

- [ ] **Step 3: 커밋**

```bash
git add html/js/topbar.js
git commit -m "토픽바에 예가율 분석 메뉴 추가"
```

---

## Task 3: DB 로딩 + 기본 검색 핸들러

**목표:** 페이지 진입 시 sql.js + 연도별 g2b DB를 로드해 메모리에 띄우고, 로딩 스피너를 제거한다. 검색 버튼은 아직 결과 카운트만 갱신한다.

**Files:**
- Modify: `html/g2b_ratio.html` (`<script>` 블록)

- [ ] **Step 1: 인라인 JS에 DB 초기화 코드 추가**

`<script>` 블록 안의 placeholder를 다음으로 교체 (마지막 `</script>` 위):

```javascript
        let dbs = {};        // {year: SQL.Database}
        let years = [];      // 내림차순 정렬된 연도
        let totalCount = 0;

        function fmt(n) {
            if (n == null) return '-';
            return Number(n).toLocaleString();
        }

        function ratio(a, b) {
            if (!b || b === 0) return '-';
            return (a / b * 100).toFixed(2);
        }

        async function initDB() {
            // 종료일 default = 오늘
            const today = new Date();
            const todayStr = today.getFullYear() + '-' +
                String(today.getMonth() + 1).padStart(2, '0') + '-' +
                String(today.getDate()).padStart(2, '0');
            document.getElementById('date-to').value = todayStr;

            const t0 = performance.now();
            const SQL = await initSqlJs({
                locateFile: file => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`
            });
            const t1 = performance.now();
            console.log(`[g2b ratio] sql.js init: ${((t1 - t0)/1000).toFixed(2)}s`);

            const yearBytes = await window.getAllG2bYearDbs();
            const t2 = performance.now();
            console.log(`[g2b ratio] DB bytes 로드 (${Object.keys(yearBytes).length}개): ${((t2 - t1)/1000).toFixed(2)}s`);

            for (const [y, bytes] of Object.entries(yearBytes)) {
                dbs[y] = new SQL.Database(bytes);
                try {
                    dbs[y].exec("CREATE INDEX IF NOT EXISTS idx_date ON bid_results(date DESC)");
                } catch (e) { console.warn(`[${y}] 인덱스 생성 실패:`, e); }
            }
            years = Object.keys(dbs).sort((a, b) => Number(b) - Number(a));
            const t3 = performance.now();
            console.log(`[g2b ratio] sql.js DB 파싱 (${years.length}개): ${((t3 - t2)/1000).toFixed(2)}s`);

            document.getElementById('loading').style.display = 'none';
            doSearch();
        }

        function buildWhere() {
            const where = [];
            const params = {};
            const dateFrom = document.getElementById('date-from').value;
            const dateTo = document.getElementById('date-to').value;
            if (dateFrom) { where.push("date >= :dateFrom"); params[':dateFrom'] = dateFrom.replace(/-/g, '/'); }
            if (dateTo)   { where.push("date <= :dateTo");   params[':dateTo']   = dateTo.replace(/-/g, '/'); }
            const whereClause = where.length ? 'WHERE ' + where.join(' AND ') : '';
            return { whereClause, params };
        }

        function yearOutOfRange(year, params) {
            if (params[':dateFrom'] && params[':dateFrom'].substr(0, 4) > year) return true;
            if (params[':dateTo']   && params[':dateTo'].substr(0, 4)   < year) return true;
            return false;
        }

        function countMatching() {
            if (!years.length) return 0;
            const { whereClause, params } = buildWhere();
            let total = 0;
            for (const y of years) {
                if (yearOutOfRange(y, params)) continue;
                const stmt = dbs[y].prepare("SELECT COUNT(*) as cnt FROM bid_results " + whereClause);
                stmt.bind(params);
                stmt.step();
                total += stmt.getAsObject().cnt;
                stmt.free();
            }
            return total;
        }

        function doSearch() {
            if (!years.length) return;
            totalCount = countMatching();
            document.getElementById('result-count').textContent = '총 ' + fmt(totalCount) + '건';
        }

        function resetSearch() {
            document.getElementById('date-from').value = '';
            document.getElementById('date-to').value = '';
            doSearch();
        }

        function setTrendLimit(n) { /* Task 5 */ }

        // Enter 키로 검색
        document.querySelectorAll('.search-panel input').forEach(input => {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') doSearch();
            });
        });

        initDB();
```

- [ ] **Step 2: 브라우저 확인**

`http://localhost:8000/g2b_ratio.html` 새로고침. 콘솔에서 `[g2b ratio] sql.js init`, `DB bytes 로드`, `sql.js DB 파싱` 로그가 차례로 나오고 로딩 스피너가 사라진다. 종료일이 오늘 날짜로 채워지고 결과 카운트("총 N건")가 표시된다. 시작일/종료일을 바꾸고 [검색] 클릭 시 카운트가 갱신된다.

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 분석 페이지 DB 로딩 + 검색 핸들러 구현"
```

---

## Task 4: 매트릭스 쿼리 + 렌더링

**목표:** 검색 결과 중 첫 페이지(20건)를 매트릭스 테이블로 그린다. 페이지네이션 없이 단순히 첫 20건만 표시.

**Files:**
- Modify: `html/g2b_ratio.html` (`<script>` 블록)

- [ ] **Step 1: 매트릭스 상수 + 쿼리/렌더 함수 추가**

`<script>` 블록 상단(`let dbs = {};` 바로 아래)에 상수 선언:

```javascript
        const MATRIX_PAGE_SIZE = 20;
        let matrixPage = 1;
        let matrixRows = [];   // 현재 페이지의 결과
```

`countMatching()` 함수 아래에 다음 함수들 추가:

```javascript
        function runMatrixQuery(page) {
            if (!years.length) return;
            const { whereClause, params } = buildWhere();
            const startIdx = (page - 1) * MATRIX_PAGE_SIZE;
            const endIdx = startIdx + MATRIX_PAGE_SIZE;

            // 연도별 카운트
            const yearCounts = {};
            for (const y of years) {
                if (yearOutOfRange(y, params)) { yearCounts[y] = 0; continue; }
                const stmt = dbs[y].prepare("SELECT COUNT(*) as cnt FROM bid_results " + whereClause);
                stmt.bind(params);
                stmt.step();
                yearCounts[y] = stmt.getAsObject().cnt;
                stmt.free();
            }

            // 페이지 컷 분배
            const cols = ['bid_pbanc_no', 'bid_pbanc_ord', 'date', 'base_amount'];
            for (let i = 1; i <= 15; i++) cols.push('rsve_price_' + i);

            matrixRows = [];
            let cumStart = 0;
            for (const y of years) {
                const cnt = yearCounts[y];
                if (cnt === 0) continue;
                const cumEnd = cumStart + cnt;
                if (cumEnd <= startIdx) { cumStart = cumEnd; continue; }
                if (cumStart >= endIdx) break;

                const dbOffset = Math.max(0, startIdx - cumStart);
                const dbLimit = Math.min(endIdx, cumEnd) - cumStart - dbOffset;

                const sql = "SELECT " + cols.join(', ') + " FROM bid_results " + whereClause +
                    " ORDER BY date DESC, bid_pbanc_no DESC LIMIT " + dbLimit + " OFFSET " + dbOffset;
                const stmt = dbs[y].prepare(sql);
                stmt.bind(params);
                while (stmt.step()) matrixRows.push(stmt.getAsObject());
                stmt.free();

                cumStart = cumEnd;
            }
        }

        function renderMatrix() {
            const head = document.getElementById('matrix-head');
            const body = document.getElementById('matrix-body');
            head.innerHTML = '';
            body.innerHTML = '';

            if (matrixRows.length === 0) {
                head.innerHTML = '<th class="label-col">구분</th>';
                body.innerHTML = '<tr><td colspan="1" style="padding:24px; color:#888;">결과 없음</td></tr>';
                return;
            }

            // 헤더: 구분 | 공고번호-차수 들
            let headHtml = '<th class="label-col">구분</th>';
            matrixRows.forEach(r => {
                const label = r.bid_pbanc_no + '-' + r.bid_pbanc_ord;
                headHtml += '<th title="' + label + ' (' + (r.date || '') + ')">' + label + '</th>';
            });
            head.innerHTML = headHtml;

            // 행 1~15
            let bodyHtml = '';
            for (let i = 1; i <= 15; i++) {
                bodyHtml += '<tr><td class="label-col">' + i + '</td>';
                matrixRows.forEach(r => {
                    const v = r['rsve_price_' + i];
                    bodyHtml += '<td class="num-col">' + ratio(v, r.base_amount) + '</td>';
                });
                bodyHtml += '</tr>';
            }
            body.innerHTML = bodyHtml;
        }
```

`doSearch()` 함수를 다음으로 교체:

```javascript
        function doSearch() {
            if (!years.length) return;
            matrixPage = 1;
            totalCount = countMatching();
            document.getElementById('result-count').textContent = '총 ' + fmt(totalCount) + '건';
            runMatrixQuery(matrixPage);
            renderMatrix();
        }
```

- [ ] **Step 2: 브라우저 확인**

페이지 새로고침. 기대: 매트릭스 테이블 헤더에 "구분 | <공고번호-차수>×20" 이 표시되고, 각 행에 1~15번 예비가격 비율(소수점 2자리)이 들어간다. 첫 셀들의 값이 대략 99.0~101.0% 범위에 있는지 확인. 시작일을 좁게 조정해서 결과가 0건이 되면 "결과 없음"이 보인다.

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 분석 페이지 매트릭스 쿼리/렌더 구현"
```

---

## Task 5: 매트릭스 페이지네이션

**목표:** 결과가 20건을 초과하면 페이지네이션 버튼이 나오고 클릭 시 해당 페이지의 매트릭스가 갱신된다.

**Files:**
- Modify: `html/g2b_ratio.html` (`<script>` 블록)

- [ ] **Step 1: 페이지네이션 함수 추가**

`renderMatrix()` 함수 아래에 추가:

```javascript
        function renderPagination() {
            const totalPages = Math.ceil(totalCount / MATRIX_PAGE_SIZE);
            const container = document.getElementById('pagination');
            if (totalPages <= 1) { container.innerHTML = ''; return; }

            let html = '';
            html += '<button ' + (matrixPage === 1 ? 'disabled' : '') + ' onclick="goPage(1)">&laquo;</button>';
            html += '<button ' + (matrixPage === 1 ? 'disabled' : '') + ' onclick="goPage(' + (matrixPage - 1) + ')">&lsaquo;</button>';

            let startP = Math.max(1, matrixPage - 4);
            let endP = Math.min(totalPages, startP + 9);
            if (endP - startP < 9) startP = Math.max(1, endP - 9);

            for (let p = startP; p <= endP; p++) {
                html += '<button class="' + (p === matrixPage ? 'active' : '') + '" onclick="goPage(' + p + ')">' + p + '</button>';
            }

            html += '<button ' + (matrixPage === totalPages ? 'disabled' : '') + ' onclick="goPage(' + (matrixPage + 1) + ')">&rsaquo;</button>';
            html += '<button ' + (matrixPage === totalPages ? 'disabled' : '') + ' onclick="goPage(' + totalPages + ')">&raquo;</button>';
            container.innerHTML = html;
        }

        function goPage(p) {
            const totalPages = Math.ceil(totalCount / MATRIX_PAGE_SIZE);
            if (p < 1 || p > totalPages) return;
            matrixPage = p;
            runMatrixQuery(matrixPage);
            renderMatrix();
            renderPagination();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
```

`doSearch()`의 마지막 줄(`renderMatrix();`) 뒤에 `renderPagination();` 추가:

```javascript
        function doSearch() {
            if (!years.length) return;
            matrixPage = 1;
            totalCount = countMatching();
            document.getElementById('result-count').textContent = '총 ' + fmt(totalCount) + '건';
            runMatrixQuery(matrixPage);
            renderMatrix();
            renderPagination();
        }
```

- [ ] **Step 2: 브라우저 확인**

페이지 새로고침 후 결과가 20건 이상인 날짜 범위로 검색 (예: 시작일 비우고 종료일=오늘). 페이지네이션 버튼이 나오는지, 페이지 클릭 시 매트릭스가 다음 20건으로 교체되는지, 마지막 페이지에서 다음 버튼이 비활성화되는지 확인.

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 분석 페이지 페이지네이션 구현"
```

---

## Task 6: 예가율 추이 차트 (단일 라인, 토글 없음)

**목표:** 검색 시 최근 300건의 예가율을 받아 차트로 그린다. 토글 버튼은 다음 태스크에서 연결.

**Files:**
- Modify: `html/g2b_ratio.html` (`<script>` 블록)

- [ ] **Step 1: 차트 상태 변수 + 쿼리/렌더 함수 추가**

`let matrixRows = [];` 줄 아래에 추가:

```javascript
        const TREND_MAX = 300;
        const TREND_OPTIONS = [100, 200, 300];
        let trendData = [];     // 최근 300건 (date DESC) — slice 후 reverse 해서 표시
        let currentLimit = 100;
        let trendChart = null;
```

`renderPagination()` / `goPage()` 아래에 추가:

```javascript
        function runTrendQuery() {
            if (!years.length) { trendData = []; return; }
            const { whereClause, params } = buildWhere();

            // 각 연도에서 TREND_MAX 만큼씩 가져온 뒤 합쳐서 정렬, 상위 TREND_MAX 만 유지
            const cols = ['bid_pbanc_no', 'bid_pbanc_ord', 'date', 'base_amount', 'predict_price'];
            const merged = [];
            for (const y of years) {
                if (yearOutOfRange(y, params)) continue;
                const sql = "SELECT " + cols.join(', ') + " FROM bid_results " + whereClause +
                    " ORDER BY date DESC, bid_pbanc_no DESC LIMIT " + TREND_MAX;
                const stmt = dbs[y].prepare(sql);
                stmt.bind(params);
                while (stmt.step()) merged.push(stmt.getAsObject());
                stmt.free();
                if (merged.length >= TREND_MAX * 2) break;  // 여유분 확보 후 조기 종료
            }
            // base_amount > 0 인 것만 + 예가율 계산
            trendData = merged
                .filter(r => r.base_amount && r.base_amount > 0)
                .sort((a, b) => {
                    if (a.date !== b.date) return a.date < b.date ? 1 : -1;
                    return a.bid_pbanc_no < b.bid_pbanc_no ? 1 : -1;
                })
                .slice(0, TREND_MAX)
                .map(r => ({
                    label: r.bid_pbanc_no + '-' + r.bid_pbanc_ord,
                    date: r.date,
                    rate: r.predict_price / r.base_amount * 100,
                }));
        }

        function renderTrend() {
            const wrap = document.getElementById('trend-section');
            if (trendData.length === 0) {
                wrap.style.display = 'none';
                return;
            }
            wrap.style.display = '';

            // 토글 버튼 활성/비활성
            document.querySelectorAll('#trend-toggle button').forEach(btn => {
                const lim = Number(btn.dataset.limit);
                btn.disabled = trendData.length < lim;
                btn.classList.toggle('active', lim === currentLimit);
            });

            // 가용 데이터에 맞춰 currentLimit 조정 (예: 검색 결과 80건이면 100/200/300 모두 disabled → 가용 최대값 사용)
            const effective = Math.min(currentLimit, trendData.length);
            const slice = trendData.slice(0, effective).reverse();  // 시간 오름차순
            const labels = slice.map(d => d.label);
            const data = slice.map(d => Number(d.rate.toFixed(3)));
            const tooltipMeta = slice.map(d => d.date);

            const cfg = {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '예가율(%)',
                        data: data,
                        borderColor: 'rgba(107,147,214,1)',
                        backgroundColor: 'rgba(107,147,214,0.15)',
                        fill: false,
                        pointRadius: 1.5,
                        borderWidth: 1.5,
                        tension: 0,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        xAxes: [{
                            ticks: { autoSkip: true, maxTicksLimit: 20, fontSize: 10 },
                        }],
                        yAxes: [{
                            ticks: { fontSize: 11, callback: v => v.toFixed(2) + '%' },
                        }],
                    },
                    tooltips: {
                        callbacks: {
                            title: items => {
                                const i = items[0].index;
                                return labels[i] + ' (' + tooltipMeta[i] + ')';
                            },
                            label: item => '예가율: ' + Number(item.value).toFixed(3) + '%',
                        },
                    },
                    legend: { display: false },
                },
            };

            const canvas = document.getElementById('trend-chart');
            canvas.parentElement.style.height = '320px';
            if (trendChart) {
                trendChart.data = cfg.data;
                trendChart.options = cfg.options;
                trendChart.update();
            } else {
                trendChart = new Chart(canvas.getContext('2d'), cfg);
            }
        }
```

`doSearch()`에 trend 호출 추가:

```javascript
        function doSearch() {
            if (!years.length) return;
            matrixPage = 1;
            totalCount = countMatching();
            document.getElementById('result-count').textContent = '총 ' + fmt(totalCount) + '건';
            runMatrixQuery(matrixPage);
            renderMatrix();
            renderPagination();
            runTrendQuery();
            renderTrend();
        }
```

- [ ] **Step 2: 브라우저 확인**

페이지 새로고침. 기대: 차트 영역에 라인 차트가 그려지고 X축에는 일부 공고번호 라벨이, Y축에는 예가율 % 가 표시된다. 마우스 호버 시 툴팁에 "공고번호-차수 (날짜)" + "예가율: NN.NNN%" 가 보인다. 라인은 왼쪽(과거) → 오른쪽(최신) 방향. 결과 0건일 때는 차트 섹션이 숨겨진다.

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 추이 차트 구현"
```

---

## Task 7: 차트 100/200/300 토글

**목표:** `[100][200][300]` 버튼 클릭 시 추가 쿼리 없이 메모리에서 슬라이스해 차트가 갱신된다.

**Files:**
- Modify: `html/g2b_ratio.html` (`<script>` 블록)

- [ ] **Step 1: `setTrendLimit` 구현**

기존 `function setTrendLimit(n) { /* Task 5 */ }` 줄을 다음으로 교체:

```javascript
        function setTrendLimit(n) {
            if (!TREND_OPTIONS.includes(n)) return;
            currentLimit = n;
            renderTrend();
        }
```

- [ ] **Step 2: 브라우저 확인**

페이지 새로고침 후 `[100] [200] [300]` 버튼 클릭. 기대: 활성 버튼이 시각적으로 강조되고(파란색) 차트의 X축 라벨 개수와 라인 길이가 즉시 바뀐다. 가용 데이터가 100건 미만이면 200/300 버튼이 disabled로 나오고, 200건 미만이면 300이 disabled. 페이지네이션 버튼을 누를 때는 차트가 그대로 유지된다(매트릭스만 갱신).

- [ ] **Step 3: 커밋**

```bash
git add html/g2b_ratio.html
git commit -m "예가율 추이 차트 100/200/300 토글 구현"
```

---

## Task 8: 최종 통합 검증

**목표:** 모든 기능이 함께 동작하는지 시나리오별로 확인.

**Files:** 없음 (수동 검증)

- [ ] **Step 1: 시나리오 검증 — 기본 흐름**

브라우저 새로고침. 다음을 순서대로 확인:
1. 로딩 스피너 → 사라짐.
2. 종료일 = 오늘로 자동 채워짐.
3. 결과 카운트 "총 N건" 표시.
4. 매트릭스 첫 페이지(20건) 표시.
5. 페이지네이션 표시 (총 N건 > 20일 때).
6. 차트 영역 표시 (총 N건 > 0일 때), 기본 [최근 100건] 활성.

- [ ] **Step 2: 시나리오 검증 — 날짜 좁히기**

시작일 = 종료일과 가까운 날짜로 변경 → 결과 5건 정도가 되도록. [검색] 클릭.
1. 카운트 갱신.
2. 매트릭스 5건만 표시, 페이지네이션 사라짐.
3. 차트의 100/200/300 버튼 모두 disabled (가용 < 100).
4. 차트는 5건이라도 그려짐.

- [ ] **Step 3: 시나리오 검증 — 결과 0건**

미래 날짜(예: 2027-01-01 ~ 2027-01-02)로 검색.
1. "총 0건" 표시.
2. 매트릭스 영역에 "결과 없음".
3. 차트 섹션 숨김.
4. 페이지네이션 사라짐.

- [ ] **Step 4: 시나리오 검증 — 토픽바 이동**

토픽바의 "나라장터 상세" 클릭 → `g2b_detail.html` 이동. 거기서 다시 "예가율 분석" 클릭 → 본 페이지 복귀. 메뉴 active 상태가 일관되게 표시.

- [ ] **Step 5: 시나리오 검증 — 초기화 버튼**

날짜 좁힌 상태에서 [초기화] 클릭. 두 날짜 필드가 비워지고 전체 결과가 다시 표시됨.

- [ ] **Step 6: 콘솔 에러 확인**

브라우저 콘솔(F12)에 에러가 없는지 확인. `[g2b ratio]` 로그만 보이면 OK. 빨간 에러가 있으면 해당 태스크로 돌아가 수정.

- [ ] **Step 7: 커밋 (필요 시)**

수정 사항이 있었다면:

```bash
git add html/g2b_ratio.html
git commit -m "예가율 분석 페이지 최종 검증 후 미세 수정"
```

수정이 없으면 이 단계는 스킵.

---

## Self-Review Checklist (작성자 메모)

- [x] **Spec 커버리지:** R1(새 페이지) Task 1, R2(날짜 2필드) Task 1, R3(페이지네이션 20건) Task 5, R4(매트릭스 구조) Task 4, R5(토글) Task 7, R6(정렬) Task 4/6, R7(X축 라벨) Task 6, R8(컴포넌트 재사용) 전 태스크. 토픽바(R1) Task 2.
- [x] **Placeholder 스캔:** 없음. 모든 코드 블록은 실행 가능한 완전한 코드.
- [x] **타입/함수명 일관성:** `runMatrixQuery / renderMatrix / runTrendQuery / renderTrend / setTrendLimit / goPage / buildWhere / yearOutOfRange / countMatching` 모든 호출처와 정의 일치.
