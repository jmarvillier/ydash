import { Component, type ErrorInfo, type ReactNode } from 'react';
import { reportError } from './errorReporter';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Port de l'ErrorBoundary v1 : écran de secours + remontée de l'erreur. */
export class ErrorBoundary extends Component<Props, State> {
  override state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    reportError(error, 'boundary', { componentStack: info.componentStack ?? undefined });
  }

  override render() {
    if (!this.state.error) return this.props.children;
    return (
      <main className="app" role="alert">
        <h1>Oups, quelque chose s'est mal passé</h1>
        <p className="muted">{this.state.error.message}</p>
        <button type="button" onClick={() => window.location.reload()}>
          Recharger l'application
        </button>
      </main>
    );
  }
}
