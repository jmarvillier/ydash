import { apiUrl } from './api';

describe('apiUrl', () => {
  it('concatène la base (préfixe stg- compris) et le nom de fonction', () => {
    expect(apiUrl('health', 'https://europe-west1-dashboard-ydash.cloudfunctions.net/stg-')).toBe(
      'https://europe-west1-dashboard-ydash.cloudfunctions.net/stg-health',
    );
    expect(apiUrl('/okxProxy', 'https://x.net/')).toBe('https://x.net/okxProxy');
  });

  it('échoue explicitement sans base', () => {
    expect(() => apiUrl('health', '')).toThrow(/VITE_API_BASE/);
  });
});
