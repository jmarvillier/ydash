import { beforeEach, describe, expect, it, vi } from 'vitest';

const calls: { level: string; msg: string; entry: Record<string, unknown> }[] = [];
vi.mock('firebase-functions/logger', () => ({
  info: (msg: string, entry: Record<string, unknown>) => calls.push({ level: 'info', msg, entry }),
  warn: (msg: string, entry: Record<string, unknown>) => calls.push({ level: 'warn', msg, entry }),
  error: (msg: string, entry: Record<string, unknown>) =>
    calls.push({ level: 'error', msg, entry }),
}));

const { hashUid, logEvent, logSyncResult, newRequestId, sanitize } = await import('./logger');

describe('logger', () => {
  beforeEach(() => {
    calls.length = 0;
  });

  it('remplace l’uid par une empreinte stable', () => {
    const out = sanitize({ uid: 'abc', endpoint: '/x' });
    expect(out).toEqual({ uidHash: hashUid('abc'), endpoint: '/x' });
    expect(hashUid('abc')).toHaveLength(16);
    expect(hashUid('abc')).not.toBe(hashUid('abd'));
  });

  it('masque tout champ ressemblant à un secret', () => {
    expect(sanitize({ apiKey: 'k', okxSecret: 's', passphrase: 'p', durationMs: 3 })).toEqual({
      apiKey: '[redacted]',
      okxSecret: '[redacted]',
      passphrase: '[redacted]',
      durationMs: 3,
    });
  });

  it('émet un événement structuré avec l’environnement', () => {
    logEvent('http.request', { requestId: 'r1', status: 200 });
    expect(calls[0]).toMatchObject({
      level: 'info',
      msg: 'http.request',
      entry: { event: 'http.request', env: 'stg', requestId: 'r1', status: 200 },
    });
  });

  it('journalise les résultats de sync en succès ou en erreur', () => {
    logSyncResult({ uid: 'u', scope: 'fills', durationMs: 120 });
    logSyncResult({ uid: 'u', scope: 'fills' }, { message: 'Invalid key', okxCode: '50111' });
    expect(calls.map((c) => [c.level, c.msg])).toEqual([
      ['info', 'sync.success'],
      ['error', 'sync.error'],
    ]);
    expect(calls[1]?.entry).toMatchObject({
      okxCode: '50111',
      error: 'Invalid key',
      scope: 'fills',
    });
    expect(calls[1]?.entry).not.toHaveProperty('uid');
  });

  it('reprend l’identifiant de trace Cloud si présent', () => {
    expect(newRequestId('105445aa7843bc8bf206b120001000/1;o=1')).toBe(
      '105445aa7843bc8bf206b120001000',
    );
    expect(newRequestId(undefined)).toMatch(/^[0-9a-f-]{36}$/);
  });
});
