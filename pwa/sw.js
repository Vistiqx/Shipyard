const CACHE = 'shipyard-v1';
const SHELL = ['/', '/app.js', '/manifest.json', '/icon-192.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/api/')) {
    return;
  }

  e.respondWith(
    fetch(e.request).catch(async () => {
      const cached = await caches.match(e.request);
      if (cached) {
        return cached;
      }
      return new Response('<!doctype html><html><body style="background:#121212;color:#E8E8F8;font-family:serif;padding:24px;">Shipyard is not running.</body></html>', {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      });
    })
  );
});
