/* v4.0 service worker — fast repeat loads, offline fallback.
   Static = cache-first. Pages = network-first (fresh hisab), cache fallback offline.
   Forms/POST are never intercepted. */
const CACHE = "mmm-v17";
const CORE = [
  "/static/css/reset.css",
  "/static/css/variables.css",
  "/static/css/global.css",
  "/static/css/responsive.css",
  "/static/css/dark.css",
  "/static/css/public/public.css",
  "/static/css/public/dashboard.css",
  "/static/css/public/month.css",
  "/static/css/public/day.css",
  "/static/css/public/premium.css",
  "/static/js/core/utils.js",
  "/static/js/core/api.js",
  "/static/js/core/csrf.js",
  "/static/js/core/modal.js",
  "/static/js/core/toast.js",
  "/static/js/core/theme.js",
  "/static/js/core/pwa.js",
  "/static/js/core/app.js",
  "/static/js/core/charts.js",
  "/static/js/public/dashboard.js",
  "/static/js/public/filters.js",
  "/static/js/public/premium.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => Promise.allSettled(
      CORE.map((u) => c.add(u).catch(() => null))
    )).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // Never cache private/admin pages or error responses.
  if (url.pathname.startsWith("/panel/") || url.pathname.startsWith("/accounts/")) return;
  if (url.pathname.startsWith("/static/") || url.pathname.startsWith("/media/")) {
    // cache-first for assets (only cache successful responses)
    e.respondWith(
      caches.match(req).then((hit) =>
        hit || fetch(req).then((res) => {
          if (res && res.ok){
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
      )
    );
  } else {
    // network-first for pages (always fresh totals), cache fallback offline
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok){
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match("/")))
    );
  }
});
