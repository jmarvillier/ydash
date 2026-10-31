import { describe, expect, it } from 'vitest';
import { resolveEnv, rootCollection } from './config';

describe('config', () => {
  it('ne résout « prod » que sur demande explicite', () => {
    expect(resolveEnv('prod')).toBe('prod');
    expect(resolveEnv('stg')).toBe('stg');
    expect(resolveEnv(undefined)).toBe('stg');
    expect(resolveEnv('production')).toBe('stg');
  });

  it('isole les collections racine', () => {
    expect(rootCollection('prod')).toBe('ydash_v2');
    expect(rootCollection('stg')).toBe('ydash_v2_stg');
  });
});
