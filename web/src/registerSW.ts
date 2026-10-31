/** Enregistre le service worker en production uniquement, avec une portée = base de l'app. */
export function registerServiceWorker(base: string): void {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(`${base}sw.js`, { scope: base }).catch((err: unknown) => {
      console.warn('Service worker non enregistré', err);
    });
  });
}
