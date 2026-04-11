// 공용 상단 네비게이션 바 컴포넌트
// 사용법: 페이지 내 <div id="topbar"></div> 두고 이 스크립트 로드
(function () {
    const page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
    const isIndex = page === 'index.html' || page === '';

    // index.html 에서는 같은 페이지 내 탭 전환 함수(change2Mp/change2Yy) 호출
    // 다른 페이지에서는 index.html 로 이동
    const items = [
        { label: '물품',            active: false,                        onclick: isIndex ? 'change2Mp()' : "location.href='index.html'" },
        { label: '용역',            active: false,                        onclick: isIndex ? 'change2Yy()' : "location.href='index.html'" },
        { label: '가격정보 (물품)', active: page === 'price_mp.html',     onclick: "location.href='price_mp.html'" },
        { label: '가격정보 (용역)', active: page === 'price.html',        onclick: "location.href='price.html'" },
        { label: '나라장터',        active: page === 'g2b.html',          onclick: "location.href='g2b.html'" },
        { label: '나라장터 상세',   active: page === 'g2b_detail.html',   onclick: "location.href='g2b_detail.html'" },
    ];

    const html = items.map(i =>
        `<button class="fb${i.active ? ' active' : ''}" onclick="${i.onclick}">${i.label}</button>`
    ).join('');

    function render() {
        const el = document.getElementById('topbar');
        if (!el) return;
        el.className = 'top-bar';
        el.innerHTML = html;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', render);
    } else {
        render();
    }
})();
