/**
 * Logs structurés (JSON → Cloud Logging) : chaque entrée porte `event`, `env`, et selon le cas
 * `requestId`, `uidHash` (jamais l'uid en clair), `endpoint`, `durationMs`, `okxCode`.
 * Les événements `sync.success` / `sync.error` alimentent les métriques et alertes
 * (infra/monitoring, docs/INFRA.md §7). Ne JAMAIS logger de clé, secret, passphrase ou signature.
 */
import { createHash, randomUUID } from 'node:crypto';
import * as logger from 'firebase-functions/logger';
import { YDASH_ENV } from './config';

export type LogEvent =
  'http.request' | 'sync.success' | 'sync.error' | 'okx.error' | 'client.error';

export interface LogFields {
  requestId?: string;
  uid?: string;
  endpoint?: string;
  durationMs?: number;
  okxCode?: string;
  status?: number;
  [key: string]: unknown;
}

const FORBIDDEN = /secret|passphrase|apikey|api_key|signature|password|token/i;

/** Empreinte stable et non réversible de l'uid (corrélation des logs sans donnée personnelle). */
export function hashUid(uid: string): string {
  return createHash('sha256').update(`ydash:${uid}`).digest('hex').slice(0, 16);
}

/** Retire l'uid en clair et toute clé ressemblant à un secret. */
export function sanitize(fields: LogFields): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(fields)) {
    if (value === undefined) continue;
    if (key === 'uid') out.uidHash = hashUid(String(value));
    else if (FORBIDDEN.test(key)) out[key] = '[redacted]';
    else out[key] = value;
  }
  return out;
}

export function logEvent(
  event: LogEvent,
  fields: LogFields = {},
  severity: 'INFO' | 'WARNING' | 'ERROR' = 'INFO',
): void {
  const entry = { event, env: YDASH_ENV, ...sanitize(fields) };
  if (severity === 'ERROR') logger.error(event, entry);
  else if (severity === 'WARNING') logger.warn(event, entry);
  else logger.info(event, entry);
}

/** Résultat d'une synchronisation OKX (appelé par l'orchestrateur, ticket C10). */
export function logSyncResult(
  fields: LogFields & { uid: string; scope: string },
  error?: { message: string; okxCode?: string },
): void {
  if (error) {
    logEvent('sync.error', { ...fields, error: error.message, okxCode: error.okxCode }, 'ERROR');
  } else {
    logEvent('sync.success', fields);
  }
}

export function newRequestId(header?: string | string[]): string {
  const fromHeader = Array.isArray(header) ? header[0] : header;
  return fromHeader?.split('/')[0] || randomUUID();
}
