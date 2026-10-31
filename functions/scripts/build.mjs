// Bundle des Cloud Functions avec esbuild.
// Le workspace `core` est inliné dans le bundle : le dossier déployé (`lib/`) ne dépend
// que de paquets publiés sur npm, avec un package.json généré.
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const outdir = resolve(root, 'lib');
const pkg = JSON.parse(await readFile(resolve(root, 'package.json'), 'utf8'));
const runtimeDeps = pkg.dependencies ?? {};

await rm(outdir, { recursive: true, force: true });
await mkdir(outdir, { recursive: true });

await build({
  entryPoints: [resolve(root, 'src/index.ts')],
  outfile: resolve(outdir, 'index.js'),
  bundle: true,
  platform: 'node',
  target: 'node22',
  format: 'esm',
  sourcemap: true,
  external: Object.keys(runtimeDeps),
  alias: { '@core': resolve(root, '../core/src/index.ts') },
  banner: {
    // Permet aux dépendances CommonJS bundlées d'utiliser require().
    js: "import { createRequire as __cr } from 'node:module'; const require = __cr(import.meta.url);",
  },
  logLevel: 'info',
});

const deployPkg = {
  name: pkg.name.replace('@ydash/', 'ydash-'),
  version: pkg.version,
  private: true,
  type: 'module',
  main: 'index.js',
  engines: pkg.engines,
  dependencies: runtimeDeps,
};
await writeFile(resolve(outdir, 'package.json'), `${JSON.stringify(deployPkg, null, 2)}\n`);
