import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import type { Plugin } from 'vite';

export interface BuildInfo {
  version: string;
  sha: string;
  buildTime: string;
  env: string;
}

function gitSha(): string {
  // git d'abord : en CD, prod et staging sont deux checkouts d'un même run (même GITHUB_SHA).
  try {
    return execSync('git rev-parse --short=7 HEAD', { stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim();
  } catch {
    return process.env.GITHUB_SHA?.slice(0, 7) ?? 'dev';
  }
}

export function readBuildInfo(pkgPath: string): BuildInfo {
  const pkg = JSON.parse(readFileSync(pkgPath, 'utf8')) as { version: string };
  return {
    version: pkg.version,
    sha: gitSha(),
    buildTime: new Date().toISOString(),
    env: process.env.VITE_YDASH_ENV ?? 'local',
  };
}

/** Clé de cache du service worker : change à chaque version ET à chaque commit. */
export function cacheKey(info: BuildInfo): string {
  return `ydash-${info.version}-${info.sha}`;
}

/**
 * Port du plugin v1 :
 * - injecte `__APP_VERSION__`, `__GIT_SHA__`, `__BUILD_TIME__`, `__YDASH_ENV__` dans l'app ;
 * - émet `version.json` (toujours lu sur le réseau par le SW) ;
 * - émet `sw.js` à partir de `swTemplatePath` en remplaçant `__CACHE_KEY__`.
 */
export function versionPlugin(info: BuildInfo, swTemplatePath: string): Plugin {
  return {
    name: 'ydash-version',
    config() {
      return {
        define: {
          __APP_VERSION__: JSON.stringify(info.version),
          __GIT_SHA__: JSON.stringify(info.sha),
          __BUILD_TIME__: JSON.stringify(info.buildTime),
          __YDASH_ENV__: JSON.stringify(info.env),
        },
      };
    },
    generateBundle() {
      this.emitFile({
        type: 'asset',
        fileName: 'version.json',
        source: `${JSON.stringify({ ...info, cacheKey: cacheKey(info) }, null, 2)}\n`,
      });
      const sw = readFileSync(swTemplatePath, 'utf8').replaceAll('__CACHE_KEY__', cacheKey(info));
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: sw });
    },
  };
}
