/**
 * URL d'une Cloud Function. `VITE_API_BASE` contient le préfixe de l'environnement :
 *   prod    → https://europe-west1-dashboard-ydash.cloudfunctions.net/
 *   staging → https://europe-west1-dashboard-ydash.cloudfunctions.net/stg-
 *   local   → http://127.0.0.1:5001/dashboard-ydash/europe-west1/stg-
 */
export function apiUrl(name: string, base: string = import.meta.env.VITE_API_BASE ?? ''): string {
  if (!base) throw new Error('VITE_API_BASE non configurée');
  return `${base}${name.replace(/^\//, '')}`;
}
