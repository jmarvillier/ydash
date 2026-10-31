import { render, screen } from '@testing-library/react';
import { App } from './App';

describe('App', () => {
  it('affiche le titre et utilise le moteur core', () => {
    render(<App />);
    expect(screen.getByRole('heading', { name: 'Hello Ydash v2' })).toBeInTheDocument();
    expect(screen.getByText(/12\.5 %/)).toBeInTheDocument();
  });
});
