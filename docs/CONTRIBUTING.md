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
| `master`    | production (`/ydash/`), branche par défaut | PR obligatoire, checks `build-test` + `secrets-scan` + `conventional-title` requis, pas de force-push ni suppression |
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

## Tickets et revue

- Nouvelle issue : gabarits **Fonctionnalité**, **Bug** ou **Technique** (`.github/ISSUE_TEMPLATE/`), toujours
  avec Contexte / Objectif / Tâches / Critères d'acceptation / Dépendances / Taille. Ajouter le milestone et
  les labels `area/*` et `P0|P1|P2`.
- PR : gabarit `.github/PULL_REQUEST_TEMPLATE.md` (`Closes #…`, checklist, captures iPad si UI).
- `CODEOWNERS` : `@jmarvillier` sur tout le dépôt.
- Suivi : GitHub Project « Ydash v2 », créé et alimenté par `./tools/github/create-project.sh`
  (vues Board par milestone + Table à ajouter dans l'UI).
- `tickets/` reste dans le dépôt : c'est la source du backlog initial (55 tickets). Le label `bug` est
  créé par `python3 tickets/create_issues.py --repo jmarvillier/ydash` (idempotent).

## Dépendances

- **Tout passe par npm** et le lockfile (plus aucun script chargé depuis un CDN comme `xlsx` en v1).
  SheetJS sera ajouté avec l'export .xlsx (ticket P05), en version épinglée — la version publiée sur le
  registre npm (`xlsx@0.18.5`) n'est plus maintenue : utiliser le tarball officiel `cdn.sheetjs.com`
  référencé dans `web/package.json` ou une alternative (`exceljs`), à trancher dans P05.
- Versions exactes (`npm i -E`) ; Dependabot (`.github/dependabot.yml`) ouvre chaque lundi des PRs groupées
  vers `develop` (npm mineures/patchs, GitHub Actions). Les montées **majeures** font l'objet d'un ticket.
- `npm audit --audit-level=high --omit=dev` tourne en CI (non bloquant pour l'instant, bloquant après stabilisation).

## Versioning et releases

- **Une seule version SemVer** pour tout le dépôt (racine + `core` + `web` + `functions` + lockfile),
  pilotée par **release-please** (`release-please-config.json`, `.release-please-manifest.json`) à partir des
  Conventional Commits arrivés sur `master`.
- À chaque push sur `master`, le workflow `release-please` ouvre ou met à jour une PR `chore(master): release x.y.z`
  (bump + `CHANGELOG.md`). Sa fusion crée le tag `vX.Y.Z` et la GitHub Release, et redéploie la prod.
- Phase alpha : `versioning: prerelease` (`2.0.0-alpha.N`). Pour passer en `2.0.0` stable, retirer `prerelease`
  / `versioning` de la config.
- **Première release** : `release-as: 2.0.0-alpha.1` est forcé dans la config (le milestone 0 ne contient que des
  commits `chore/ci/docs`, qui ne déclenchent pas de bump). ⚠️ **Retirer `release-as`** juste après la
  publication de `v2.0.0-alpha.1`.
- Sans secret `RELEASE_PLEASE_TOKEN`, la CI ne se lance pas sur la PR de release (limite de `GITHUB_TOKEN`) :
  la fusionner en tant qu'admin, ou créer un jeton (GitHub App ou PAT fin limité à ce dépôt, `contents` +
  `pull-requests` en écriture).
- Le build injecte `version`, `sha`, `buildTime` et l'environnement (`web/build/versionPlugin.ts`) :
  - dans l'app (`buildInfo.ts`, affiché en pied de page, puis Réglages P11 / toast de mise à jour P10) ;
  - dans `version.json` (ex. https://jmarvillier.github.io/ydash/version.json), toujours lu sur le réseau ;
  - dans `sw.js` : clé de cache `ydash-{version}-{sha}`, les anciens caches sont purgés à l'activation.
