# Onboarding — développer Ydash v2 en local

Objectif : de zéro à l'app qui tourne avec des données de démo en **moins de 15 minutes**, **sans aucun
accès à la prod** (ni Firebase réel, ni clé OKX).

## 1. Prérequis

| Outil   | Version              | Vérifier            |
| ------- | -------------------- | ------------------- |
| Node.js | 22 (`.nvmrc`)        | `node -v`           |
| npm     | ≥ 10                 | `npm -v`            |
| Java    | ≥ 11 (émulateurs Firebase) | `java -version` |
| git     | récent               | `git --version`     |

`nvm use` dans le dossier sélectionne la bonne version de Node. La CLI Firebase est une dépendance du
projet (`npx firebase …`), inutile de l'installer globalement.

## 2. Installation

```bash
git clone https://github.com/jmarvillier/ydash.git && cd ydash
git switch develop
npm ci
```

Aucun fichier `.env` n'est nécessaire pour le mode local. Les modèles sont `web/.env.example` et
`functions/.env.example` (à copier en `.env.local` seulement pour surcharger une valeur).

## 3. Lancer tout le stack

```bash
npm run dev
```

| Processus | Rôle                                                                                       | URL                             |
| --------- | ------------------------------------------------------------------------------------------ | ------------------------------- |
| `emu`     | émulateurs Firebase Auth, Firestore, Functions (projet **`demo-ydash`**, isolé du cloud)    | UI : http://127.0.0.1:4000      |
| `fn`      | esbuild en mode watch : `functions/src` + `core/src` → `functions/lib/{prod,stg}` (rechargés à chaud) | `…:5001/demo-ydash/europe-west1/stg-health` |
| `web`     | Vite, branché sur les émulateurs (`VITE_USE_EMULATORS=true`, API `stg-*`)                  | http://localhost:5173           |
| `seed`    | attend les émulateurs puis charge le jeu de démo                                          | —                               |

Compte de démo : **`demo@ydash.local` / `ydash-demo`** (uid `demo-user`).
Données : `ydash_v2_stg/demo-user/{fills, transfers, xperps, earn_positions, dca_plans}` — fictives et
déterministes (`tools/seed-demo.ts`, schéma provisoire jusqu'au ticket C04). Recharger : `npm run seed`.

Variantes :

- `npm run dev:web` — l'app seule, sans émulateurs ;
- `npm run emulators` — émulateurs seuls (après `npm run build -w functions`) ;
- `npm run seed -- --env prod` — seed sous `ydash_v2` au lieu de `ydash_v2_stg`.

## 4. Mode « OKX mock »

Dans l'émulateur, les fonctions ne contactent **jamais** OKX : les réponses viennent de
`functions/fixtures/okx/*.json` (`functions/src/okx/mock.ts`). Nom de fixture = chemin de l'endpoint
(`/api/v5/trade/fills-history` → `trade-fills-history.json`). Forcer : `OKX_MOCK=true|false` dans
`functions/.env.local` (recopié dans `functions/lib/<env>/` au build).

## 5. Qualité avant de pousser

```bash
npm run lint && npm run typecheck && npm test && npm run build
```

C'est exactement ce que vérifie le job CI `build-test`. Voir `docs/CONTRIBUTING.md` pour le flux git.

## 6. Debug sur iPad / iPhone

- **Depuis le Mac** : `npm run dev:web -- --host` puis ouvrir `http://<ip-du-mac>:5173` sur l'iPad
  (même Wi-Fi). Inspecter avec **Safari › Développement › [iPad] › page** (activer *Réglages › Safari ›
  Avancé › Inspecteur web* sur l'iPad).
- **Depuis une VM / Termius** : lancer `npm run dev` sur la VM puis un tunnel
  `ssh -L 5173:localhost:5173 -L 4000:localhost:4000 -L 5001:localhost:5001 -L 8080:localhost:8080 -L 9099:localhost:9099 vm`.
- Staging : https://jmarvillier.github.io/ydash/staging/ (vider le cache de la PWA via le
  `version.json` affiché en pied de page si une ancienne version reste servie).

## 7. Problèmes fréquents

| Symptôme                                     | Solution                                                                          |
| -------------------------------------------- | --------------------------------------------------------------------------------- |
| `Could not spawn java`                       | installer un JDK ≥ 11                                                             |
| Port 8080/9099/5001/4000 occupé              | arrêter l'ancien `npm run dev` (`pkill -f "firebase emulators"`)                   |
| `Function …stg-health does not exist`        | attendre « Loaded functions definitions » (quelques secondes après le démarrage)  |
| Avertissements `MetadataLookupWarning` / MOTD | sans gravité hors ligne : les émulateurs n'ont pas besoin d'Internet               |
