/**
 * Configuration backend figée au build (esbuild remplace `process.env.YDASH_ENV`) :
 * le bundle `prod` écrit dans `ydash_v2`, le bundle `stg` dans `ydash_v2_stg` — jamais de mélange.
 */
export type YdashEnv = 'prod' | 'stg';

export const REGION = 'europe-west1';

export function resolveEnv(raw: string | undefined): YdashEnv {
  return raw === 'prod' ? 'prod' : 'stg';
}

export const YDASH_ENV: YdashEnv = resolveEnv(process.env.YDASH_ENV);

export function rootCollection(env: YdashEnv): 'ydash_v2' | 'ydash_v2_stg' {
  return env === 'prod' ? 'ydash_v2' : 'ydash_v2_stg';
}

export const ROOT_COLLECTION = rootCollection(YDASH_ENV);
