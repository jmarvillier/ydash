import { describe, expect, it } from 'vitest';
import { buildHealth } from './health';

describe('buildHealth', () => {
  it('renvoie un statut ok avec la région et l’heure', () => {
    const now = new Date('2026-10-31T12:00:00Z');
    const health = buildHealth('stg', 'europe-west1', now);
    expect(health).toMatchObject({
      status: 'ok',
      service: 'ydash-functions',
      env: 'stg',
      region: 'europe-west1',
      time: '2026-10-31T12:00:00.000Z',
    });
    expect(health.uptimeSeconds).toBeGreaterThanOrEqual(0);
  });
});
