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
