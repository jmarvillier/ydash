import { setGlobalOptions } from 'firebase-functions/v2';
import { onRequest } from 'firebase-functions/v2/https';
import { buildHealth } from './health';

export const REGION = 'europe-west1';

setGlobalOptions({ region: REGION, maxInstances: 5 });

/** `GET /health` — sonde publique utilisée par le smoke test de déploiement. */
export const health = onRequest({ cors: false }, (req, res) => {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'method_not_allowed' });
    return;
  }
  res.set('Cache-Control', 'no-store').json(buildHealth(REGION));
});
