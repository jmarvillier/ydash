import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from './ErrorBoundary';
import {
  buildReport,
  installGlobalErrorHandlers,
  reportError,
  resetErrorReporter,
  setErrorSink,
  type ClientErrorReport,
} from './errorReporter';

function Boom(): never {
  throw new Error('kaboom');
}

describe('monitoring front', () => {
  let reports: ClientErrorReport[];

  beforeEach(() => {
    resetErrorReporter();
    reports = [];
    setErrorSink((r) => {
      reports.push(r);
    });
  });

  it('construit un rapport daté avec expiration à 30 jours', () => {
    const r = buildReport('texte', 'manual', {}, new Date('2026-10-01T00:00:00Z'));
    expect(r.message).toBe('texte');
    expect(r.expireAt).toBe('2026-10-31T00:00:00.000Z');
  });

  it('ErrorBoundary affiche un écran de secours et remonte l’erreur', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('kaboom');
    expect(reports).toHaveLength(1);
    expect(reports[0]).toMatchObject({ source: 'boundary', message: 'kaboom' });
    expect(reports[0]?.componentStack).toContain('Boom');
  });

  it('limite le nombre de rapports par session', () => {
    for (let i = 0; i < 50; i += 1) reportError(new Error(`e${i}`));
    expect(reports).toHaveLength(20);
  });

  it('capture les erreurs globales et les promesses rejetées', () => {
    const uninstall = installGlobalErrorHandlers(window);
    window.dispatchEvent(new ErrorEvent('error', { error: new Error('globale') }));
    const rejection = new Event('unhandledrejection') as PromiseRejectionEvent;
    Object.defineProperty(rejection, 'reason', { value: 'refus' });
    window.dispatchEvent(rejection);
    uninstall();
    expect(reports.map((r) => [r.source, r.message])).toEqual([
      ['window.error', 'globale'],
      ['unhandledrejection', 'refus'],
    ]);
  });

  it('ne casse jamais l’app si le sink échoue', () => {
    setErrorSink(() => {
      throw new Error('sink KO');
    });
    expect(() => reportError(new Error('x'))).not.toThrow();
  });
});
