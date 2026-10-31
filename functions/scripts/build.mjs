// Bundle des Cloud Functions avec esbuild, une sortie par codebase Firebase :
//   lib/prod → fonctions sous leur nom, YDASH_ENV=prod (collection ydash_v2)
//   lib/stg  → fonctions préfixées stg-, YDASH_ENV=stg (collection ydash_v2_stg)
// Le workspace `core` est inliné : chaque dossier déployé ne dépend que de paquets npm publiés,
// avec un package.json généré.
import { existsSync } from 'node:fs';
import { copyFile, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { context } from 'esbuild';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const pkg = JSON.parse(await readFile(resolve(root, 'package.json'), 'utf8'));
const runtimeDeps = pkg.dependencies ?? {};
const watch = process.argv.includes('--watch');
const targets = ['prod', 'stg'];
const envLocal = resolve(root, '.env.local');

// En mode watch, ne jamais vider lib/ : l'émulateur est en train de le lire.
if (!watch) await rm(resolve(root, 'lib'), { recursive: true, force: true });

for (const env of targets) {
  const outdir = resolve(root, 'lib', env);
  await mkdir(outdir, { recursive: true });

  const ctx = await context({
    entryPoints: [resolve(root, `src/entry/${env}.ts`)],
    outfile: resolve(outdir, 'index.js'),
    bundle: true,
    platform: 'node',
    target: 'node22',
    format: 'esm',
    sourcemap: true,
    external: Object.keys(runtimeDeps),
    alias: { '@core': resolve(root, '../core/src/index.ts') },
    define: { 'process.env.YDASH_ENV': JSON.stringify(env) },
    banner: {
      // Permet aux dépendances CommonJS bundlées d'utiliser require().
      js: "import { createRequire as __cr } from 'node:module'; const require = __cr(import.meta.url);",
    },
    logLevel: 'info',
  });
  if (watch) await ctx.watch();
  else {
    await ctx.rebuild();
    await ctx.dispose();
  }

  const deployPkg = {
    name: `ydash-functions-${env}`,
    version: pkg.version,
    private: true,
    type: 'module',
    main: 'index.js',
    engines: pkg.engines,
    dependencies: runtimeDeps,
  };
  await writeFile(resolve(outdir, 'package.json'), `${JSON.stringify(deployPkg, null, 2)}\n`);
  // Variables locales de l'émulateur (jamais déployées : .env.local n'est lu que par l'émulateur).
  if (existsSync(envLocal)) await copyFile(envLocal, resolve(outdir, '.env.local'));
}

if (watch) console.info('esbuild : surveillance de functions/src et core/src…');
