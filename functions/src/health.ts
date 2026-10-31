import { round } from '@core';
import type { YdashEnv } from './config';

export interface HealthPayload {
  status: 'ok';
  service: 'ydash-functions';
  env: YdashEnv;
  region: string;
  time: string;
  uptimeSeconds: number;
}

/** Contenu de `GET /health` — fonction pure pour être testable sans runtime Firebase. */
export function buildHealth(env: YdashEnv, region: string, now: Date = new Date()): HealthPayload {
  return {
    status: 'ok',
    service: 'ydash-functions',
    env,
    region,
    time: now.toISOString(),
    uptimeSeconds: round(process.uptime(), 0),
  };
}
