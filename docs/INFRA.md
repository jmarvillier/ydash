# Infrastructure, secrets et configuration — Ydash v2

> Règle d'or : **zéro secret dans le dépôt** (public). Le scan `gitleaks` (job `secrets-scan` de la CI) est bloquant.

## 1. Où vit chaque secret / paramètre

| Nom                                   | Type                               | Où                                         | Utilisé par                                  | Secret ? |
| ------------------------------------- | ---------------------------------- | ------------------------------------------ | -------------------------------------------- | -------- |
| `VITE_FIREBASE_API_KEY` … `_APP_ID` (6) | config Firebase web               | **Secrets GitHub** (repo)                  | `deploy-pages.yml` (build web)                 | non¹     |
| `VITE_API_BASE_PROD`                  | URL des Functions prod             | **Variable GitHub** (repo)                 | `deploy-pages.yml` (build `/ydash/`)          | non      |
| `VITE_API_BASE_STAGING`               | URL des Functions staging          | **Variable GitHub** (repo)                 | `deploy-pages.yml` (build `/ydash/staging/`)  | non      |
| `VITE_BASE`                           | chemin de publication              | fixé dans `deploy-pages.yml`               | build web                                    | non      |
| `GCP_WIF_PROVIDER`                    | fournisseur Workload Identity Fed. | **Secrets GitHub** (repo)                  | `deploy-firebase.yml`                        | non²     |
| `GCP_SERVICE_ACCOUNT`                 | e-mail du compte de service CI     | **Secrets GitHub** (repo)                  | `deploy-firebase.yml`                        | non²     |
| `FIREBASE_SERVICE_ACCOUNT`            | clé JSON (fallback si pas de WIF)  | **Secrets GitHub** (repo) — à éviter       | `deploy-firebase.yml`                        | **oui**  |
| `RELEASE_PLEASE_TOKEN`                | token GitHub App / PAT fin (opt.)  | **Secrets GitHub** (repo) — optionnel      | `release-please.yml` (déclencher la CI des PRs de release) | **oui** |
| `okx-{uid}`                           | clé API OKX lecture seule          | **Secret Manager GCP** (une par utilisateur) | Cloud Functions uniquement (ticket C03)      | **oui**  |
| `YDASH_ENV`, `OKX_BASE_URL`, `OKX_MOCK` | config backend                    | paramètres Firebase / `functions/.env.*`  | Cloud Functions                              | non      |

¹ La config Firebase web est publique par nature (elle part dans le bundle JS) ; la sécurité repose sur les
**règles Firestore** et l'Auth. Elle reste en secrets GitHub pour ne pas l'exposer en clair dans le dépôt public.
² Identifiants non sensibles seuls (WIF n'émet un jeton que pour ce dépôt/cette branche), gardés en secrets par hygiène.

**Supprimé par rapport à v1** : `PAT_TOKEN` (le staging n'a plus besoin de redéclencher la prod).

## 2. Fichiers d'environnement locaux

- `web/.env.example` → copier en `web/.env.local`
- `functions/.env.example` → copier en `functions/.env.local`
- Tous les `.env*` sont ignorés par git sauf `*.env.example` ; `.secret.local` (émulateur) aussi.

## 3. Clés OKX

- Créées par l'utilisateur sur my.okx.com, **permission « Lecture » uniquement** (ni trading, ni retrait).
- Saisies dans l'app → envoyées une seule fois à une fonction callable → écrites dans Secret Manager.
  Firestore ne stocke que `keyLast4`, `perm`, `status`. Le front ne les relit jamais.

## 4. En cas de fuite

> **Tout token, clé ou mot de passe collé par erreur** dans un chat, une issue, une PR, un log ou un commit
> doit être **révoqué immédiatement** à la source (OKX, GitHub, GCP), puis remplacé. Réécrire l'historique
> git ne suffit pas : considérer la valeur comme compromise.

Scan local facultatif avant de pousser : `gitleaks git .` (même config `.gitleaks.toml` que la CI).

## 5. Front — GitHub Pages (prod + staging)

Workflow `.github/workflows/deploy-pages.yml`, déclenché par un push sur `master` **ou** `develop`
(et `workflow_dispatch`) :

1. checkout de `master` et de `develop` côte à côte ;
2. build web `VITE_BASE=/ydash/` (prod) et `VITE_BASE=/ydash/staging/` (staging), chacun avec sa
   `VITE_API_BASE` (`vars.VITE_API_BASE_PROD` / `vars.VITE_API_BASE_STAGING`) ;
3. assemblage `site/` + `site/staging/` + `.nojekyll` ; la `404.html` racine redirige les liens profonds
   vers la bonne app (`?p=…`, restauré par `web/src/spaRedirect.ts`) ;
4. `upload-pages-artifact` + `deploy-pages` (environnement `github-pages`, concurrence `pages`), puis
   smoke test HTTP 200 sur les deux URLs.

Conséquence : un push sur `develop` republie aussi la prod **à l'identique** (même commit `master`) et
inversement ; aucun PAT, aucune branche de build. Le manifest PWA utilise `start_url`/`scope` relatifs
(`./`), donc chaque environnement est une PWA distincte.

**Mise en place (une fois, admin)** : `./tools/github/setup-pages.sh` — active Pages en mode
« GitHub Actions » et autorise `master` + `develop` sur l'environnement `github-pages` (par défaut seule
la branche par défaut peut y déployer). Renseigner ensuite les 6 secrets `VITE_FIREBASE_*` et, quand
les Functions existent, les variables `VITE_API_BASE_PROD` / `VITE_API_BASE_STAGING`.

> Alternative (à trancher dans l'ADR C01) : Firebase Hosting avec canaux de preview par PR.

## 6. Backend — Firebase (Functions, règles, index)

### 6.1 Deux codebases, un seul projet

Le projet Firebase **`dashboard-ydash`** (déjà utilisé par v1) héberge les deux environnements backend :

| Codebase | Source            | Branche   | Fonctions          | Collection racine | URL de base (`VITE_API_BASE_*`)                                 |
| -------- | ----------------- | --------- | ------------------ | ----------------- | --------------------------------------------------------------- |
| `prod`   | `functions/lib/prod` | `master`  | `health`, …        | `ydash_v2`        | `https://europe-west1-dashboard-ydash.cloudfunctions.net/`      |
| `stg`    | `functions/lib/stg`  | `develop` | `stg-health`, …    | `ydash_v2_stg`    | `https://europe-west1-dashboard-ydash.cloudfunctions.net/stg-`  |

`functions/scripts/build.mjs` produit les deux bundles (esbuild, `core` inliné, `YDASH_ENV` figé au build).
Le front appelle `apiUrl('health')` (`web/src/api.ts`) : le préfixe `stg-` est porté par `VITE_API_BASE_STAGING`.

### 6.2 Workflow `deploy-firebase.yml`

- push `master` → `firebase deploy --only functions:prod[,firestore:rules,firestore:indexes]`
- push `develop` → `firebase deploy --only functions:stg`
- déclenché seulement si `functions/`, `core/`, `firebase.json`, `firestore.*` ou le lockfile changent ;
  `workflow_dispatch` possible (prod refusé hors `master`)
- typecheck + tests + build avant déploiement, puis **smoke test** `GET /health` (`status: ok` et bon `env`)
- sans identifiants GCP configurés, le job se termine en **warning** (pas d'échec) : rien n'est déployé.

### 6.3 Mise en place GCP (une fois)

1. Passer le projet au **plan Blaze** (requis pour Functions v2, Scheduler, Secret Manager).
2. Activer les APIs :
   ```bash
   gcloud services enable cloudfunctions.googleapis.com run.googleapis.com cloudbuild.googleapis.com \
     artifactregistry.googleapis.com eventarc.googleapis.com cloudscheduler.googleapis.com \
     secretmanager.googleapis.com firebaserules.googleapis.com firestore.googleapis.com \
     iamcredentials.googleapis.com --project dashboard-ydash
   ```
3. Compte de service de déploiement + **Workload Identity Federation** (aucune clé JSON) :
   ```bash
   PROJECT=dashboard-ydash
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
   gcloud iam service-accounts create github-deployer --project $PROJECT
   SA=github-deployer@$PROJECT.iam.gserviceaccount.com
   for role in roles/cloudfunctions.admin roles/run.admin roles/iam.serviceAccountUser \
               roles/artifactregistry.admin roles/firebaserules.admin roles/datastore.indexAdmin \
               roles/cloudscheduler.admin roles/secretmanager.viewer roles/serviceusage.serviceUsageConsumer \
               roles/firebase.viewer; do
     gcloud projects add-iam-policy-binding $PROJECT --member "serviceAccount:$SA" --role $role
   done
   gcloud iam workload-identity-pools create github --location global --project $PROJECT
   gcloud iam workload-identity-pools providers create-oidc ydash --location global \
     --workload-identity-pool github --project $PROJECT \
     --issuer-uri https://token.actions.githubusercontent.com \
     --attribute-mapping "google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
     --attribute-condition "assertion.repository == 'jmarvillier/ydash'"
   gcloud iam service-accounts add-iam-policy-binding $SA --project $PROJECT \
     --role roles/iam.workloadIdentityUser \
     --member "principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/jmarvillier/ydash"
   ```
4. Secrets GitHub : `GCP_WIF_PROVIDER` =
   `projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/ydash`,
   `GCP_SERVICE_ACCOUNT` = `github-deployer@dashboard-ydash.iam.gserviceaccount.com`.
   *Fallback (déconseillé)* : clé JSON du compte de service dans `FIREBASE_SERVICE_ACCOUNT`.
5. Variables GitHub : `VITE_API_BASE_PROD` et `VITE_API_BASE_STAGING` (tableau 6.1).
6. Optionnel : protéger l'environnement GitHub `firebase-prod` (relecture requise avant déploiement prod).

### 6.4 ⚠️ Règles Firestore — projet partagé avec v1

Déployer `firestore.rules` **remplace** les règles de production de v1 (`users/{uid}/…`). Avant le premier
déploiement des règles :

1. Exporter les règles actuellement en prod (console Firebase › Firestore › Règles, ou
   `npx firebase firestore:rules:get` selon la version de la CLI) et les comparer au bloc « v1 » de
   `firestore.rules` ; reporter toute différence.
2. Tester avec l'émulateur (`npm run dev:full`), puis seulement alors créer la variable GitHub
   **`FIRESTORE_RULES_VERIFIED=true`**. Tant qu'elle est absente, la CI déploie les fonctions mais **jamais** les règles.

## 7. Monitoring et alerting

### 7.1 Logs structurés (Functions)

`functions/src/logger.ts` émet du JSON vers Cloud Logging : `event`, `env` (`prod`/`stg`), `requestId`,
`uidHash` (SHA-256 tronqué, **jamais l'uid en clair**), `endpoint`, `durationMs`, `status`, `okxCode`.
Les champs ressemblant à un secret (`secret`, `passphrase`, `apiKey`, `signature`, `token`…) sont masqués.

| Événement      | Émis par                                   | Usage                         |
| -------------- | ------------------------------------------ | ----------------------------- |
| `http.request` | chaque fonction HTTP (`health`, proxy C02) | latence, codes HTTP           |
| `sync.success` | orchestrateur de sync (C10) via `logSyncResult` | alerte « aucune sync »  |
| `sync.error`   | idem, avec `okxCode`                       | alerte « erreurs de sync »    |
| `okx.error`    | client OKX (C02)                           | diagnostic                    |

Requête Logs Explorer : `jsonPayload.event="sync.error" AND jsonPayload.env="prod"`.

### 7.2 Alertes (e-mail)

```bash
./infra/monitoring/setup-monitoring.sh jeremie.marvillier@gmail.com dashboard-ydash
```

Crée (idempotent) les métriques `ydash_sync_errors` / `ydash_sync_success` (label `env`) et deux politiques
(`infra/monitoring/policy-*.json`), limitées à la prod :

- **> 3 `sync.error` en 1 h** → une clé OKX révoquée déclenche l'alerte dès la sync horaire suivante (< 1 h) ;
- **aucun `sync.success` depuis 23 h 30** (durée d'absence maximale de Cloud Monitoring, ≈ 24 h).

Telegram (optionnel) : ajouter un canal *webhook* Cloud Monitoring pointant vers le relais du bot existant
`xperps_watch`, puis l'ajouter aux `notificationChannels` des politiques.

> Les métriques n'ont de données qu'une fois l'orchestrateur de sync (C10) en place ; d'ici là, l'alerte
> « aucune sync » se déclencherait à vide : lancer le script **après** la mise en service de C10.

### 7.3 Erreurs front

- `ErrorBoundary` (port v1) autour de l'app + capture de `window.error` et `unhandledrejection`
  (`web/src/monitoring/`), 20 rapports max par session, jamais bloquant.
- Sink par défaut : console. Le ticket C14 branche le sink Firestore
  `ydash_v2[_stg]/{uid}/client_errors` (création seule par le propriétaire, schéma borné — `firestore.rules`),
  avec `expireAt` en **Timestamp** pour la rétention de 30 jours :
  ```bash
  gcloud firestore fields ttls update expireAt --collection-group=client_errors --enable-ttl --project dashboard-ydash
  ```
- Alternative : Sentry (plan gratuit) en remplaçant le sink, si un suivi plus riche est souhaité.
- Page Réglages (P11) : dernier statut de sync et dernière erreur.
