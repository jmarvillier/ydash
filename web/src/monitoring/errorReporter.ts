/**
 * Remontée des erreurs front. Le « sink » par défaut écrit dans la console ; le ticket C14 branche
 * un sink Firestore (`ydash_v2[_stg]/{uid}/client_errors`, rétention 30 j via TTL sur `expireAt`).
 */
import { buildInfo } from '../buildInfo';

export interface ClientErrorReport {
  message: string;
  stack?: string;
  componentStack?: string;
  source: 'boundary' | 'window.error' | 'unhandledrejection' | 'manual';
  url: string;
  userAgent: string;
  version: string;
  sha: string;
  env: string;
  at: string;
  expireAt: string;
}

export type ErrorSink = (report: ClientErrorReport) => void | Promise<void>;

const RETENTION_DAYS = 30;
const MAX_PER_SESSION = 20;

const consoleSink: ErrorSink = (report) => {
  console.error('[ydash] erreur client', report);
};

let sink: ErrorSink = consoleSink;
let sent = 0;

export function setErrorSink(next: ErrorSink | null): void {
  sink = next ?? consoleSink;
}

/** Réinitialise le compteur anti-tempête (tests). */
export function resetErrorReporter(): void {
  sent = 0;
  sink = consoleSink;
}

function toError(value: unknown): Error {
  if (value instanceof Error) return value;
  return new Error(typeof value === 'string' ? value : JSON.stringify(value));
}

export function buildReport(
  error: unknown,
  source: ClientErrorReport['source'],
  extra: { componentStack?: string } = {},
  now: Date = new Date(),
): ClientErrorReport {
  const err = toError(error);
  return {
    message: err.message.slice(0, 1000),
    stack: err.stack?.slice(0, 4000),
    componentStack: extra.componentStack?.slice(0, 4000),
    source,
    url: typeof location === 'undefined' ? '' : location.href,
    userAgent: typeof navigator === 'undefined' ? '' : navigator.userAgent,
    version: buildInfo.version,
    sha: buildInfo.sha,
    env: buildInfo.env,
    at: now.toISOString(),
    expireAt: new Date(now.getTime() + RETENTION_DAYS * 86_400_000).toISOString(),
  };
}

export function reportError(
  error: unknown,
  source: ClientErrorReport['source'] = 'manual',
  extra: { componentStack?: string } = {},
): void {
  if (sent >= MAX_PER_SESSION) return;
  sent += 1;
  try {
    void Promise.resolve(sink(buildReport(error, source, extra))).catch(() => undefined);
  } catch {
    // La remontée d'erreur ne doit jamais casser l'app.
  }
}

/** Capture les erreurs hors React (scripts, promesses non gérées). */
export function installGlobalErrorHandlers(target: Window = window): () => void {
  const onError = (event: ErrorEvent) => reportError(event.error ?? event.message, 'window.error');
  const onRejection = (event: PromiseRejectionEvent) =>
    reportError(event.reason, 'unhandledrejection');
  target.addEventListener('error', onError);
  target.addEventListener('unhandledrejection', onRejection);
  return () => {
    target.removeEventListener('error', onError);
    target.removeEventListener('unhandledrejection', onRejection);
  };
}
