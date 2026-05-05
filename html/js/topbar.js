// 공용 상단 네비게이션 바 컴포넌트 (그룹 드롭다운)
// 사용법: 페이지 내 <div id="topbar"></div> 두고 이 스크립트 로드
(function () {
    const page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    const isIndex = page === 'index.html' || page === '';

    // 그룹별 메뉴 정의 — activePages 안에 현재 page 가 있으면 부모 버튼 active
    const groups = [
        {
            label: '입찰분석',
            activePages: ['index.html', ''],
            items: [
                { label: '물품', onclick: isIndex ? 'change2Mp()' : "location.href='index.html'" },
                { label: '용역', onclick: isIndex ? 'change2Yy()' : "location.href='index.html'" },
            ],
        },
        {
            label: '가격정보',
            activePages: ['price_mp.html', 'price.html'],
            items: [
                { label: '물품', match: 'price_mp.html', onclick: "location.href='price_mp.html'" },
                { label: '용역', match: 'price.html',    onclick: "location.href='price.html'" },
            ],
        },
        {
            label: '나라장터',
            activePages: ['g2b.html', 'g2b_detail.html', 'g2b_ratio.html'],
            items: [
                { label: '분류조회',    match: 'g2b.html',        onclick: "location.href='g2b.html'" },
                { label: '상세조회',    match: 'g2b_detail.html', onclick: "location.href='g2b_detail.html'" },
                { label: '예가율 분석', match: 'g2b_ratio.html',  onclick: "location.href='g2b_ratio.html'" },
            ],
        },
    ];

    function escapeAttr(s) { return String(s).replace(/"/g, '&quot;'); }

    const html = groups.map((g, gi) => {
        const isParentActive = g.activePages.includes(page);
        const items = g.items.map(it => {
            const itemActive = it.match === page;
            return `<button class="fb-item${itemActive ? ' active' : ''}" onclick="${escapeAttr(it.onclick)}">${it.label}</button>`;
        }).join('');
        return `<div class="fb-group" data-group-idx="${gi}">` +
            `<button class="fb fb-parent${isParentActive ? ' active' : ''}" type="button">` +
            `${g.label}<span class="fb-caret">▾</span>` +
            `</button>` +
            `<div class="fb-menu">${items}</div>` +
            `</div>`;
    }).join('');

    function render() {
        const el = document.getElementById('topbar');
        if (!el) return;
        el.className = 'top-bar';
        el.innerHTML = html;

        // 부모 버튼 클릭 → 같은 그룹 토글, 다른 그룹 닫기 (호버 안 되는 환경 대응)
        el.querySelectorAll('.fb-group').forEach(grp => {
            const parent = grp.querySelector('.fb-parent');
            parent.addEventListener('click', e => {
                e.stopPropagation();
                const wasOpen = grp.classList.contains('open');
                el.querySelectorAll('.fb-group.open').forEach(g => g.classList.remove('open'));
                if (!wasOpen) grp.classList.add('open');
            });
        });

        // 바깥 클릭 → 모든 드롭다운 닫기
        document.addEventListener('click', () => {
            el.querySelectorAll('.fb-group.open').forEach(g => g.classList.remove('open'));
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', render);
    } else {
        render();
    }
})();
