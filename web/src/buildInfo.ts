declare const __APP_VERSION__: string;
declare const __GIT_SHA__: string;
declare const __BUILD_TIME__: string;
declare const __YDASH_ENV__: string;

/** Informations de build injectées par `versionPlugin` (valeurs de repli en test). */
export const buildInfo = {
  version: typeof __APP_VERSION__ === 'string' ? __APP_VERSION__ : '0.0.0-test',
  sha: typeof __GIT_SHA__ === 'string' ? __GIT_SHA__ : 'test',
  buildTime: typeof __BUILD_TIME__ === 'string' ? __BUILD_TIME__ : '',
  env: typeof __YDASH_ENV__ === 'string' ? __YDASH_ENV__ : 'test',
} as const;

export function versionLabel(info: { version: string; sha: string } = buildInfo): string {
  return `v${info.version} · ${info.sha}`;
}
