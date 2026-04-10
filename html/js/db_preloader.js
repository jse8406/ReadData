// SQLite DB 파일들을 백그라운드에서 IndexedDB에 캐싱
// 모든 페이지에 로드하면 사용자가 다른 페이지를 보는 동안 미리 받음
// 캐시 무효화는 HEAD 요청의 Last-Modified / Content-Length로 자동 처리

(function () {
    const IDB_NAME = "g2bCache";
    const STORE_NAME = "files";

    // 캐싱 대상 DB 목록
    const DBS = [
        { key: "g2b.db", url: "../db/g2b.db" },
        { key: "priceDB.db", url: "../db/priceDB.db" },
        { key: "yongyuk.db", url: "../db/yongyuk.db" },
    ];

    // 다운로드 중복 방지: window 단위 Promise 캐시
    if (!window.__dbLoadPromises) window.__dbLoadPromises = {};

    function openIDB() {
        return new Promise((resolve, reject) => {
            const req = indexedDB.open(IDB_NAME, 1);
            req.onupgradeneeded = () => {
                const db = req.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    db.createObjectStore(STORE_NAME);
                }
            };
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });
    }

    async function getCached(key) {
        try {
            const idb = await openIDB();
            return new Promise((resolve) => {
                const tx = idb.transaction(STORE_NAME, "readonly");
                const store = tx.objectStore(STORE_NAME);
                let buf = null, meta = null, done = 0;
                const check = () => {
                    if (++done === 2) {
                        idb.close();
                        resolve({ buf, meta });
                    }
                };
                store.get(key).onsuccess = (e) => { buf = e.target.result; check(); };
                store.get(key + ".meta").onsuccess = (e) => { meta = e.target.result; check(); };
                tx.onerror = () => { idb.close(); resolve({ buf: null, meta: null }); };
            });
        } catch (e) {
            console.warn("[db cache] openIDB 실패:", e);
            return { buf: null, meta: null };
        }
    }

    async function saveCached(key, buf, meta) {
        try {
            const idb = await openIDB();
            return new Promise((resolve) => {
                const tx = idb.transaction(STORE_NAME, "readwrite");
                const store = tx.objectStore(STORE_NAME);
                store.put(buf, key);
                store.put(meta, key + ".meta");
                tx.oncomplete = () => {
                    console.log(`[db cache] ${key} 저장 완료 (${(meta.size / 1024 / 1024).toFixed(1)}MB)`);
                    idb.close();
                    resolve(true);
                };
                tx.onerror = () => {
                    console.error(`[db cache] ${key} 저장 실패:`, tx.error);
                    idb.close();
                    resolve(false);
                };
            });
        } catch (e) {
            console.warn("[db cache] saveCached 실패:", e);
            return false;
        }
    }

    // HEAD 요청으로 파일의 현재 메타데이터(Last-Modified, Content-Length) 가져오기
    async function fetchRemoteMeta(url) {
        try {
            const resp = await fetch(url, { method: "HEAD", cache: "no-store" });
            if (!resp.ok) return null;
            return {
                lastModified: resp.headers.get("Last-Modified") || "",
                size: parseInt(resp.headers.get("Content-Length") || "0", 10),
            };
        } catch (e) {
            console.warn("[db cache] HEAD 요청 실패:", e);
            return null;
        }
    }

    function metaMatches(local, remote) {
        if (!local || !remote) return false;
        // Last-Modified가 있으면 그걸 우선, 없으면 size로 비교
        if (local.lastModified && remote.lastModified) {
            return local.lastModified === remote.lastModified && local.size === remote.size;
        }
        return local.size === remote.size && local.size > 0;
    }

    // 핵심: 캐시 또는 네트워크에서 DB를 가져옴 (페이지 간 중복 방지)
    async function loadDb(key, url) {
        if (window.__dbLoadPromises[key]) {
            return window.__dbLoadPromises[key];
        }

        window.__dbLoadPromises[key] = (async () => {
            // 1. 캐시 + 원격 메타 동시 조회
            const [cached, remoteMeta] = await Promise.all([
                getCached(key),
                fetchRemoteMeta(url),
            ]);

            // 2. 캐시 유효성 검증
            if (cached.buf && remoteMeta && metaMatches(cached.meta, remoteMeta)) {
                console.log(`[db cache] ${key} 캐시 히트 (${(cached.meta.size / 1024 / 1024).toFixed(1)}MB)`);
                return cached.buf instanceof ArrayBuffer ? cached.buf : (cached.buf.buffer || cached.buf);
            }
            if (cached.buf) {
                console.log(`[db cache] ${key} 파일 변경 감지, 재다운로드`);
            } else {
                console.log(`[db cache] ${key} 캐시 없음, 다운로드 시작`);
            }

            // 3. 네트워크 다운로드
            const t0 = performance.now();
            const resp = await fetch(url);
            if (!resp.ok) throw new Error("HTTP " + resp.status);
            const ab = await resp.arrayBuffer();
            const t1 = performance.now();
            console.log(`[db cache] ${key} 다운로드 완료 (${(ab.byteLength / 1024 / 1024).toFixed(1)}MB, ${((t1 - t0) / 1000).toFixed(1)}초)`);

            // 4. 메타와 함께 저장 (HEAD 결과 기반, 못 받았으면 응답 헤더에서 추출)
            const meta = remoteMeta || {
                lastModified: resp.headers.get("Last-Modified") || "",
                size: ab.byteLength,
            };
            meta.size = ab.byteLength;
            meta.savedAt = Date.now();
            await saveCached(key, ab, meta);
            return ab;
        })();

        return window.__dbLoadPromises[key];
    }

    // 외부에서 사용할 헬퍼: Uint8Array로 반환
    window.getDbBytes = async function (key) {
        const target = DBS.find(d => d.key === key);
        if (!target) throw new Error("Unknown DB key: " + key);
        const ab = await loadDb(target.key, target.url);
        return new Uint8Array(ab);
    };

    // 호환용 별칭 (g2b_detail.html에서 쓰던 이름)
    window.getG2bDbBytes = () => window.getDbBytes("g2b.db");

    // 백그라운드 자동 프리로드
    function startPreload() {
        DBS.forEach(d => {
            loadDb(d.key, d.url).catch(e => console.warn(`[db cache] ${d.key} 프리로드 실패:`, e));
        });
    }

    if ("requestIdleCallback" in window) {
        requestIdleCallback(startPreload, { timeout: 1500 });
    } else {
        setTimeout(startPreload, 800);
    }
})();
