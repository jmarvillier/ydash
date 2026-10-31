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
