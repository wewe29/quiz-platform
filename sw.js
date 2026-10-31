/* 复习刷题平台 service worker
   策略（D17）：
     - 导航请求（页面）：network-first，断网回退缓存的 index.html——保证更新可达；
     - 同域静态资源与数据 JSON（assets/ subjects/*/assets subjects/*/data）：stale-while-revalidate，
       首次访问后即可离线；二次访问先用缓存、后台更新；
     - activate：清理旧版本缓存；版本号手动递增 + 构建时间戳，配页面「检测到新版本」横幅。
   范围：dist 根（sw.js 所在目录）覆盖门户与全部子站。 */
var VERSION = 'v3';
var BUILD = '20261031';
var SHELL_CACHE = 'quizp-shell-' + VERSION + '-' + BUILD;
var RUNTIME_CACHE = 'quizp-runtime-' + VERSION + '-' + BUILD;

var SHELL_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './assets/css/tokens.css',
  './assets/css/portal.css',
  './assets/js/portal.js',
  './assets/icons/icon.svg'
];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(SHELL_CACHE).then(function (c) {
    return Promise.all(SHELL_FILES.map(function (u) {
      return c.add(new Request(u, { cache: 'reload' })).catch(function () { /* 单项失败不拦安装 */ });
    }));
  }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.map(function (k) {
      if (k !== SHELL_CACHE && k !== RUNTIME_CACHE) return caches.delete(k);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('message', function (e) {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
});

function isData(url) {
  return url.pathname.includes('/data/') && url.pathname.endsWith('.json');
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // 页面导航：network-first（更新可达），断网回退首页
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(function (res) {
        return res;
      }).catch(function () {
        return caches.match('./index.html').then(function (r) { return r || Response.error(); });
      })
    );
    return;
  }

  // 同域资源与数据：stale-while-revalidate
  if (url.pathname.indexOf('/assets/') >= 0 || isData(url)) {
    e.respondWith(
      caches.open(RUNTIME_CACHE).then(function (cache) {
        return cache.match(req).then(function (cached) {
          var fetching = fetch(req).then(function (res) {
            if (res && res.status === 200) cache.put(req, res.clone());
            return res;
          }).catch(function () { return null; });
          return cached || fetching.then(function (r) { return r || Response.error(); });
        });
      })
    );
  }
});
