/**
 * Catalogue des fonctions. Ne pas importer directement pour le déploiement :
 * `entry/prod.ts` les exporte telles quelles, `entry/stg.ts` les regroupe sous `stg-*`.
 */
import { setGlobalOptions } from 'firebase-functions/v2';
import { onRequest } from 'firebase-functions/v2/https';
import { REGION, YDASH_ENV } from './config';
import { buildHealth } from './health';
import { logEvent, newRequestId } from './logger';

setGlobalOptions({ region: REGION, maxInstances: 5 });

/** `GET /health` — sonde publique utilisée par le smoke test de déploiement. */
export const health = onRequest({ cors: false }, (req, res) => {
  const started = Date.now();
  const requestId = newRequestId(req.header('x-cloud-trace-context'));
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'method_not_allowed' });
  } else {
    res.set('Cache-Control', 'no-store').json(buildHealth(YDASH_ENV, REGION));
  }
  logEvent('http.request', {
    requestId,
    endpoint: 'health',
    status: res.statusCode,
    durationMs: Date.now() - started,
  });
});
