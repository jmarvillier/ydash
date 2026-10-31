/**
 * Restaure l'URL d'origine après le détour par 404.html (GitHub Pages) :
 * `/ydash/?p=paires%3Fx%3D1` → `/ydash/paires?x=1`.
 */
export function restoreSpaPath(base: string, location: Location, history: History): void {
  const params = new URLSearchParams(location.search);
  const p = params.get('p');
  if (p === null) return;
  const target = base.replace(/\/?$/, '/') + p.replace(/^\//, '');
  history.replaceState(history.state, '', target + location.hash);
}
