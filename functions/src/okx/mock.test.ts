import { describe, expect, it } from 'vitest';
import { fixtureName, isOkxMock, MissingFixtureError, mockOkxResponse } from './mock';

describe('OKX mock', () => {
  it('dérive le nom de fixture du chemin de requête', () => {
    expect(fixtureName('/api/v5/trade/fills-history?instType=SPOT')).toBe('trade-fills-history');
    expect(fixtureName('/api/v5/account/balance')).toBe('account-balance');
  });

  it('est actif dans l’émulateur sauf désactivation explicite', () => {
    expect(isOkxMock({ FUNCTIONS_EMULATOR: 'true' })).toBe(true);
    expect(isOkxMock({ FUNCTIONS_EMULATOR: 'true', OKX_MOCK: 'false' })).toBe(false);
    expect(isOkxMock({ OKX_MOCK: 'true' })).toBe(true);
    expect(isOkxMock({})).toBe(false);
  });

  it('sert une copie de la fixture au format OKX', () => {
    const res = mockOkxResponse<{ code: string; data: unknown[] }>('/api/v5/trade/fills-history');
    expect(res.code).toBe('0');
    expect(res.data).toHaveLength(3);
    res.data.length = 0;
    expect(mockOkxResponse<{ data: unknown[] }>('/api/v5/trade/fills-history').data).toHaveLength(
      3,
    );
  });

  it('signale une fixture manquante', () => {
    expect(() => mockOkxResponse('/api/v5/asset/bills')).toThrow(MissingFixtureError);
  });
});
