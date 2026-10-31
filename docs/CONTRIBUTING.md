# Contribuer à Ydash v2

## Arborescence

```
ydash/
├─ core/                 Moteur métier pur (TypeScript, aucune dépendance runtime, testé avec Vitest)
│  └─ src/               index.ts = API publique ; *.test.ts à côté du code testé
├─ web/                  PWA React 18 + Vite 6 + TypeScript
│  ├─ public/            fichiers statiques copiés tels quels (icônes…)
│  └─ src/               composants, hooks, styles ; *.test.tsx (Testing Library)
├─ functions/            Firebase Cloud Functions v2 (Node 22, TypeScript)
│  ├─ src/               une fonction = un module ; index.ts exporte les fonctions déployées
│  └─ scripts/build.mjs  bundle esbuild → functions/lib (core inliné, package.json généré)
├─ docs/                 analyse v1, backlog, ADR, infra, onboarding
├─ tickets/              source du backlog initial (traçabilité)
├─ firebase.json         Functions, règles et index Firestore (+ émulateurs)
├─ firestore.rules       règles versionnées (⚠️ projet partagé avec v1)
└─ eslint.config.js      lint partagé (flat config) ; Prettier : .prettierrc.json
```

## Conventions de code

- **TypeScript strict** partout (`tsconfig.base.json`, `noUncheckedIndexedAccess`).
- Le moteur métier se consomme via l'alias **`@core`** (web et functions pointent sur `core/src`) :
  `import { round } from '@core';`
- `core` ne dépend de rien (ni DOM, ni Node, ni Firebase) : uniquement des fonctions pures.
- Imports de types : `import type { … }` (règle `consistent-type-imports`).
- Formatage Prettier (quotes simples, `;`, 100 colonnes) ; ne pas débattre du style en revue.

## Commandes (à la racine)

| Commande                                       | Effet                                                 |
| ---------------------------------------------- | ----------------------------------------------------- |
| `npm ci`                                       | installe tous les workspaces                          |
| `npm run dev`                                  | lance l'app web (Vite)                                |
| `npm run lint` / `npm run format`              | ESLint (0 warning toléré) / Prettier                  |
| `npm run typecheck`                            | `tsc --noEmit` dans chaque workspace                  |
| `npm test` / `npm run test:coverage`           | Vitest dans chaque workspace                          |
| `npm run build`                                | build `core` (dist), `web` (dist), `functions` (lib)  |
| `npm run <script> -w web` (ou `core`, `functions`) | cible un seul workspace                           |

## Flux git

```
feature/<clé>-<slug>  ──PR (squash)──►  develop  ──PR (merge commit)──►  master
     (ex. feature/c02-okx-proxy)        = staging                          = prod + release
```

| Branche     | Rôle                                   | Protection                                                                                         |
| ----------- | -------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `master`    | production (`/ydash/`), branche par défaut | PR obligatoire, checks `build-test` + `conventional-title` requis, pas de force-push ni suppression |
| `develop`   | staging (`/ydash/staging/`)            | idem + historique linéaire (squash uniquement)                                                     |
| `feature/*` | une branche par ticket (`fix/*`, `chore/*` acceptés) | aucune ; supprimée automatiquement après fusion                                       |

1. Partir de `develop` à jour : `git switch develop && git pull && git switch -c feature/d04-ci`.
2. Ouvrir une PR vers `develop` dont le **titre** respecte Conventional Commits et dont le corps
   référence le ticket (`Closes #9`). La PR est **squashée** : le titre devient le message du commit.
3. Pour livrer en prod : PR `develop → master` (titre `chore(release): …`), fusionnée en **merge commit**
   pour que `develop` reste un ancêtre de `master`.
4. Après une release (PR release-please fusionnée sur `master`), resynchroniser :
   PR `master → develop` en merge commit (ou `git merge origin/master` sur une branche dédiée).

> **Décision** : le ticket D02 demandait à la fois un historique linéaire sur `master` et des merge commits
> `develop → master`, ce qui est incompatible. On garde les merge commits et la linéarité sur `develop` seulement.

Les protections sont appliquées par script (compte admin requis) :

```bash
./tools/github/protect-branches.sh jmarvillier/ydash
```

## Convention de commits — Conventional Commits

Format : `type(scope)!: description à l'impératif, en minuscule` — vérifié sur le **titre de PR** par le
workflow `pr-title` (le squash en fait le message de commit, lu ensuite par release-please).

| Type                               | Usage                                   | Effet sur la version |
| ---------------------------------- | --------------------------------------- | -------------------- |
| `feat`                             | nouvelle fonctionnalité                 | mineure              |
| `fix` / `perf`                     | correction / performance                | patch                |
| `feat!` ou `BREAKING CHANGE:`      | rupture de compatibilité                | majeure              |
| `refactor` `test` `docs` `chore` `ci` `build` `revert` | le reste       | aucune               |

Scopes : `web`, `functions`, `core`, `docs`, `deps`, `ci`, `release`, `main` (facultatif).
Exemples : `feat(functions): proxy OKX signé`, `fix(web): arrondi du PnL latent`, `ci: cache npm`.
