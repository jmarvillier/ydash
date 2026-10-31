import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { ErrorBoundary } from './monitoring/ErrorBoundary';
import { installGlobalErrorHandlers } from './monitoring/errorReporter';
import { registerServiceWorker } from './registerSW';
import { restoreSpaPath } from './spaRedirect';
import './styles.css';

restoreSpaPath(import.meta.env.BASE_URL, window.location, window.history);
registerServiceWorker(import.meta.env.BASE_URL);
installGlobalErrorHandlers();

const container = document.getElementById('root');
if (!container) throw new Error('Élément #root introuvable');

createRoot(container).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
);
