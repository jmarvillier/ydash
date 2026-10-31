import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { restoreSpaPath } from './spaRedirect';
import './styles.css';

restoreSpaPath(import.meta.env.BASE_URL, window.location, window.history);

const container = document.getElementById('root');
if (!container) throw new Error('Élément #root introuvable');

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
