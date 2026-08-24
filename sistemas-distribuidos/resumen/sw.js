// Service worker de despedida: borra el cache de este origen y se
// desinstala, para que el apunte viejo se cargue siempre de la red (con la
// banda de mudanza) y no de una copia guardada.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys()
    .then((ks) => Promise.all(ks.map((k) => caches.delete(k))))
    .then(() => self.registration.unregister())
    .then(() => self.clients.matchAll({ type: 'window' }))
    .then((cs) => cs.forEach((c) => c.navigate(c.url))));
});
