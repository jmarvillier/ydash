/**
 * Mode « OKX mock » : les appels à l'API privée OKX sont servis par des fixtures JSON
 * (`functions/fixtures/okx`). Actif si `OKX_MOCK=true`, ou par défaut dans l'émulateur
 * (sauf `OKX_MOCK=false`). Le client OKX réel (ticket C02) passe par `mockOkxResponse` en premier.
 */
import accountBalance from '../../fixtures/okx/account-balance.json';
import financeSavingsBalance from '../../fixtures/okx/finance-savings-balance.json';
import tradeFillsHistory from '../../fixtures/okx/trade-fills-history.json';

const FIXTURES: Record<string, unknown> = {
  'account-balance': accountBalance,
  'trade-fills-history': tradeFillsHistory,
  'finance-savings-balance': financeSavingsBalance,
};

export function isOkxMock(env: NodeJS.ProcessEnv = process.env): boolean {
  if (env.OKX_MOCK === 'true') return true;
  if (env.OKX_MOCK === 'false') return false;
  return env.FUNCTIONS_EMULATOR === 'true';
}

/** `/api/v5/trade/fills-history?instType=SPOT` → `trade-fills-history`. */
export function fixtureName(requestPath: string): string {
  const [path = ''] = requestPath.split('?');
  return path
    .replace(/^\/?api\/v5\//, '')
    .replace(/\/+$/, '')
    .replaceAll('/', '-');
}

export class MissingFixtureError extends Error {
  constructor(public readonly requestPath: string) {
    super(
      `Aucune fixture OKX pour ${requestPath} (attendu : fixtures/okx/${fixtureName(requestPath)}.json)`,
    );
    this.name = 'MissingFixtureError';
  }
}

export function mockOkxResponse<T = unknown>(requestPath: string): T {
  const fixture = FIXTURES[fixtureName(requestPath)];
  if (fixture === undefined) throw new MissingFixtureError(requestPath);
  return structuredClone(fixture) as T;
}
