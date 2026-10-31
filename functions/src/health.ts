import { round } from '@core';

export interface HealthPayload {
  status: 'ok';
  service: 'ydash-functions';
  region: string;
  time: string;
  uptimeSeconds: number;
}

/** Contenu de `GET /health` — fonction pure pour être testable sans runtime Firebase. */
export function buildHealth(region: string, now: Date = new Date()): HealthPayload {
  return {
    status: 'ok',
    service: 'ydash-functions',
    region,
    time: now.toISOString(),
    uptimeSeconds: round(process.uptime(), 0),
  };
}
