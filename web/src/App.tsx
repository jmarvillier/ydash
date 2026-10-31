import { pctChange, round } from '@core';
import { buildInfo, versionLabel } from './buildInfo';

export function App() {
  const demo = pctChange(100, 112.5);
  return (
    <main className="app">
      <h1>Hello Ydash v2</h1>
      <p>Socle en cours de construction — milestone 0 · Fondations DevOps.</p>
      <p className="muted">Moteur `core` branché : variation démo {round(demo ?? 0)} %.</p>
      <footer className="muted" data-testid="version">
        {versionLabel()} · {buildInfo.env}
      </footer>
    </main>
  );
}
