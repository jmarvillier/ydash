import { restoreSpaPath } from './spaRedirect';

function fakeLocation(search: string, hash = ''): Location {
  return { search, hash } as Location;
}

describe('restoreSpaPath', () => {
  it('reconstruit le chemin demandé sous la base', () => {
    const replaceState = vi.fn();
    restoreSpaPath(
      '/ydash/staging/',
      fakeLocation('?p=' + encodeURIComponent('paires?x=1'), '#top'),
      { state: null, replaceState } as unknown as History,
    );
    expect(replaceState).toHaveBeenCalledWith(null, '', '/ydash/staging/paires?x=1#top');
  });

  it('ne fait rien sans paramètre p', () => {
    const replaceState = vi.fn();
    restoreSpaPath('/ydash/', fakeLocation('?x=1'), { replaceState } as unknown as History);
    expect(replaceState).not.toHaveBeenCalled();
  });
});
