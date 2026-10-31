import { cacheKey } from '../build/versionPlugin';
import { versionLabel } from './buildInfo';

describe('version', () => {
  it('formate le libellé affiché dans l’app', () => {
    expect(versionLabel({ version: '2.0.0-alpha.1', sha: 'abc1234' })).toBe(
      'v2.0.0-alpha.1 · abc1234',
    );
  });

  it('dérive la clé de cache du SW de la version et du sha', () => {
    expect(cacheKey({ version: '2.0.0', sha: 'abc1234', buildTime: '', env: 'prod' })).toBe(
      'ydash-2.0.0-abc1234',
    );
  });
});
