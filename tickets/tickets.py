# -*- coding: utf-8 -*-
"""
Backlog de migration Ydash v1 (dashboard-weex) → Ydash v2 (jmarvillier/ydash).

Source de vérité du backlog initial : ce fichier est lu par create_issues.py qui crée
labels, milestones et issues sur GitHub, puis remplace les références {{KEY}} par #numéro.
"""

MILESTONES = [
    ("0 · Fondations DevOps",
     "Dépôt, branches, CI/CD, environnements, versioning, secrets, dev local. Rien de métier."),
    ("1 · Socle technique",
     "Backend proxy/sync OKX, clés API, modèle Firestore v2, moteur métier `core`, socle front."),
    ("2 · Parité fonctionnelle v1",
     "Toutes les pages et fonctionnalités de Ydash v1 reconstruites sur les données OKX."),
    ("3 · Volet Earn",
     "Suivi des positions Earn : rendement (intérêts/APR) et plus/moins-value marché."),
    ("4 · Bascule & qualité",
     "Tests E2E, recette de parité, documentation, plan de bascule, performance/coûts."),
]

LABELS = [
    # type
    ("epic",       "5319e7", "Épique : regroupe un ensemble de tickets"),
    ("devops",     "0e8a16", "Dépôt, CI/CD, environnements, infra"),
    ("feature",    "1d76db", "Fonctionnalité métier visible par l'utilisateur"),
    ("tech",       "6a737d", "Tâche technique / refactoring / socle"),
    ("doc",        "fbca04", "Documentation, ADR, runbook"),
    ("test",       "c2e0c6", "Tests unitaires, parité, E2E"),
    ("security",   "b60205", "Sécurité, secrets, règles d'accès"),
    ("decision",   "d4c5f9", "Nécessite une décision avant implémentation"),
    ("bug",        "d73a4a", "Comportement incorrect (gabarit bug.yml)"),
    # area
    ("area/frontend",  "bfdadc", "Application web (web/)"),
    ("area/backend",   "f9d0c4", "Cloud Functions (functions/)"),
    ("area/core",      "fef2c0", "Moteur métier partagé (core/)"),
    ("area/okx",       "000000", "Intégration API OKX (EEA)"),
    ("area/firebase",  "e99695", "Firestore, Auth, règles, index"),
    ("area/earn",      "0052cc", "Volet Earn"),
    ("area/dca",       "5319e7", "Scaled Mirror DCA"),
    ("area/xperps",    "d93f0b", "Futures XPERP"),
    ("area/journal",   "006b75", "Journal spot, dépôts, métadonnées"),
    ("area/pwa",       "1d76db", "PWA, service worker, installation"),
    ("area/prices",    "fbca04", "Cours live et conversions"),
    ("area/migration", "c5def5", "Reprise des données v1 et bascule"),
    # priority / size
    ("P0", "b60205", "Bloquant pour avancer"),
    ("P1", "d93f0b", "Nécessaire à la parité / au MVP"),
    ("P2", "fbca04", "Souhaitable, après le MVP"),
    ("size/S", "ededed", "≤ ½ journée"),
    ("size/M", "ededed", "1 à 2 jours"),
    ("size/L", "ededed", "3 jours et +"),
]

# ---------------------------------------------------------------------------
# Helpers de rédaction
# ---------------------------------------------------------------------------

def body(contexte, objectif, taches, criteres, deps=None, notes=None):
    parts = ["## Contexte", contexte.strip(), "", "## Objectif", objectif.strip(), "",
             "## Tâches"]
    parts += [f"- [ ] {t}" for t in taches]
    parts += ["", "## Critères d'acceptation"]
    parts += [f"- [ ] {c}" for c in criteres]
    if deps:
        parts += ["", "## Dépendances"]
        parts += [f"- {d}" for d in deps]
    if notes:
        parts += ["", "## Notes", notes.strip()]
    return "\n".join(parts) + "\n"


def epic_body(intro, children, done):
    parts = [intro.strip(), "", "## Tickets rattachés"]
    parts += [f"- [ ] {{{{{k}}}}}" for k in children]
    parts += ["", "## Définition de « terminé »"]
    parts += [f"- [ ] {d}" for d in done]
    return "\n".join(parts) + "\n"


T = []  # liste ordonnée des tickets


def add(key, title, labels, milestone, text):
    T.append({"key": key, "title": title, "labels": labels, "milestone": milestone, "body": text})


# ===========================================================================
# ÉPIQUES (créées en premier pour avoir des numéros bas)
# ===========================================================================

add("EPIC-DEVOPS", "[EPIC] DevOps — dépôt, CI/CD, environnements, versioning", ["epic", "devops"],
    "0 · Fondations DevOps",
    epic_body("""
Mettre en place l'outillage du nouveau dépôt `jmarvillier/ydash` avant toute ligne métier : structure
monorepo, branches `master` (prod) / `develop` (staging), CI (lint, typecheck, tests, build),
CD GitHub Pages prod + staging, déploiement backend Firebase, versioning SemVer et releases,
secrets, dev local, monitoring minimal.

Le dépôt v1 `dashboard-weex` n'est pas touché.
""", ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11"], [
        "Un push sur `develop` publie automatiquement le staging ; un merge sur `master` publie la prod et crée une release taguée",
        "Aucune PR ne peut être fusionnée sans CI verte",
        "Aucun secret dans le dépôt ; l'onboarding dev local est documenté et fonctionne de zéro",
    ]))

add("EPIC-CORE", "[EPIC] Socle technique — backend OKX, modèle de données, moteur métier", ["epic", "tech"],
    "1 · Socle technique",
    epic_body("""
Construire les fondations de v2 : l'app ne saisit plus les données, elle **les lit depuis OKX**.
Un backend (Cloud Functions) signe les appels à l'API privée OKX (compte EEA, host `eea.okx.com`),
synchronise fills spot, positions futures, dépôts/retraits et Earn dans un **Firestore normalisé**
(persistance au-delà de la fenêtre de 3 mois de l'API), et un package `core` typé et testé porte
toute la logique métier (prix moyens, breakeven, PnL, périodes, DCA, Earn).
""", ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15"], [
        "Les clés OKX de l'utilisateur sont saisies dans l'app, stockées hors Firestore, et un test de connexion réussit",
        "Une sync planifiée + à la demande alimente Firestore sans doublon et reprend après erreur",
        "`core` reproduit les KPIs v1 à l'identique sur un jeu de données de référence (tests de parité verts)",
        "Le socle front (auth, shell, PWA, accès données) est prêt à accueillir les pages",
    ]))

add("EPIC-PARITY", "[EPIC] Parité fonctionnelle avec Ydash v1", ["epic", "feature"],
    "2 · Parité fonctionnelle v1",
    epic_body("""
Reconstruire toutes les pages de v1 (Dashboard, Paires, Données, XPERPS, Scaled Mirror DCA, PWA,
Réglages) sur le nouveau socle, avec les mêmes KPIs, formules et tooltips, mais alimentées par OKX.
Référence : `docs/ANALYSE-dashboard-weex.md` §3.
""", ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P09", "P10", "P11", "P12", "P13"], [
        "Chaque écran v1 a son équivalent v2 et la checklist de recette {{Q02}} est verte",
        "Plus aucune saisie manuelle n'est nécessaire pour les opérations faites sur OKX",
        "Les opérations hors OKX (Ledger, transferts) restent saisissables manuellement",
    ]))

add("EPIC-EARN", "[EPIC] Volet Earn — rendement et plus/moins-value marché", ["epic", "feature", "area/earn"],
    "3 · Volet Earn",
    epic_body("""
Nouveau volet : suivre ce que rapportent les positions Earn OKX (Simple Earn flexible, DeFi Earn
LYUSDC, staking SOL/ETH, on-chain earn, fixed) — **intérêts perçus et APR réalisé** — et aussi la
**plus/moins-value liée aux fluctuations du marché** sur le capital placé, par rapport au **cours
moyen d'acquisition** et/ou au **cours à la date de mise en earn**.
""", ["E01", "E02", "E03", "E04", "E05", "E06"], [
        "Pour chaque position Earn : valorisation, intérêts cumulés (coin + devise), APR réalisé, PnL marché vs coût moyen, PnL marché vs entrée en earn, PnL total",
        "Historique quotidien persistant (snapshots) permettant des graphiques sur 1s/1m/1a/tout",
        "Formules documentées dans les tooltips comme sur les autres pages",
    ]))

add("EPIC-CUTOVER", "[EPIC] Bascule v1 → v2, qualité et décommissionnement", ["epic", "area/migration"],
    "4 · Bascule & qualité",
    epic_body("""
Sécuriser la mise en service de v2 : tests E2E, recette de parité KPI par KPI avec v1, documentation,
plan de bascule (bannière/redirection v1, archivage, retrait du skill `ydash-regul-okx`) — **le
dépôt v1 n'est modifié qu'à la toute fin, après GO explicite**, hors périmètre de cette migration.
""", ["Q01", "Q02", "Q03", "Q04", "Q05"], [
        "Recette de parité signée (écarts expliqués et acceptés)",
        "Documentation à jour (README, ADR, runbook de sync)",
        "Plan de bascule rédigé ; aucune action sur v1 sans GO",
    ]))

# ===========================================================================
# M0 — DEVOPS
# ===========================================================================

add("D01", "Initialiser le dépôt et le scaffold du monorepo (web / functions / core)", ["devops", "tech", "P0", "size/M"],
    "0 · Fondations DevOps", body(
    """
Le dépôt `jmarvillier/ydash` vient d'être créé vide. v1 était un projet Vite JS mono-dossier sans lint ni tests.
v2 sépare l'app web, le backend Firebase et le moteur métier partagé.
""", """
Un monorepo npm workspaces prêt à coder, avec les mêmes outils partout (TypeScript, ESLint, Prettier, Vitest).
""", [
        "Racine : `package.json` (workspaces `web`, `functions`, `core`), `.nvmrc` (Node 22), `.editorconfig`, `.gitignore` (Node, Vite, Firebase, `.env*`, `dist/`), `LICENSE` (MIT), `README.md` minimal (lien vers `docs/`)",
        "`core/` : lib TypeScript pure (aucune dépendance runtime), `tsconfig` strict, Vitest, export ESM",
        "`web/` : Vite 6 + React 18 + TypeScript, alias `@core`, `index.html`, `public/` (icônes reprises de v1), Vitest + Testing Library",
        "`functions/` : Firebase Functions v2 (Node 22, TypeScript), `firebase.json`, `.firebaserc` (projet `dashboard-ydash`), dépendance workspace vers `core`",
        "Config ESLint flat + Prettier partagée, scripts racine : `lint`, `typecheck`, `test`, `build`, `dev`",
        "Commit initial sur `master`, création de `develop` depuis `master`",
    ], [
        "`npm ci && npm run lint && npm run typecheck && npm test && npm run build` passent à la racine",
        "`npm run dev -w web` lance l'app (écran vide ou « Hello Ydash v2 »)",
        "Arborescence et conventions décrites dans `docs/CONTRIBUTING.md`",
    ], ["Aucune"], """
Décision par défaut : **TypeScript strict** sur les 3 workspaces (v1 était en JS). Si refus, le noter dans {{C01}}.
"""))

add("D02", "Stratégie de branches, protections et conventions de commit", ["devops", "P0", "size/S"],
    "0 · Fondations DevOps", body(
    """
v1 déployait depuis `master` (prod) et `develop`/`feature/**` (staging) sans protection ni revue.
""", """
Un flux git simple et sûr : `feature/*` → PR → `develop` (staging) → PR → `master` (prod + release).
""", [
        "Branche par défaut `master` ; `develop` créée et protégée",
        "Protection `master` : PR obligatoire, CI « ci / build-test » requise, historique linéaire, pas de force-push, suppression interdite",
        "Protection `develop` : CI requise, pas de force-push",
        "Convention **Conventional Commits** (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`, scopes `web|functions|core|docs`) documentée ; check léger en CI (commitlint ou action équivalente) sur le titre de PR",
        "Règle de merge : squash sur `develop`, merge commit `develop → master`",
    ], [
        "Un push direct sur `master` ou `develop` est refusé",
        "Une PR sans CI verte ne peut pas être fusionnée",
        "`docs/CONTRIBUTING.md` décrit le flux et la convention",
    ], ["{{D01}}"]))

add("D03", "Templates d'issues / PR, CODEOWNERS et projet GitHub", ["devops", "doc", "P1", "size/S"],
    "0 · Fondations DevOps", body(
    """
Le backlog initial est créé par script ; il faut un cadre pour les tickets suivants et pour le suivi (v1 utilisait un GitHub Project).
""", """
Des gabarits homogènes et un tableau de suivi.
""", [
        "`.github/ISSUE_TEMPLATE/` : `feature.yml`, `bug.yml`, `tech.yml` (sections Contexte / Objectif / Tâches / Critères d'acceptation / Dépendances / Taille)",
        "`.github/PULL_REQUEST_TEMPLATE.md` : résumé, ticket lié (`Closes #…`), checklist (tests, doc, captures iPad)",
        "`.github/CODEOWNERS` → `@jmarvillier`",
        "Créer le GitHub Project « Ydash v2 » (vue Board par milestone + vue Table) et y rattacher toutes les issues",
        "Conserver `tickets/` (source du backlog initial) dans le dépôt pour traçabilité",
    ], [
        "Une nouvelle issue propose les 3 gabarits",
        "Toutes les issues du backlog initial apparaissent dans le Project",
    ], ["{{D01}}"]))

add("D04", "CI — lint, typecheck, tests, build sur chaque PR et push", ["devops", "test", "P0", "size/S"],
    "0 · Fondations DevOps", body(
    """
v1 n'avait aucune vérification avant déploiement.
""", """
Un workflow `ci.yml` rapide et obligatoire.
""", [
        "Déclencheurs : `pull_request` (toutes branches) + `push` sur `develop`/`master`",
        "Jobs : `install` (cache npm), `lint`, `typecheck`, `test` (Vitest, couverture `core` publiée en artefact), `build` (web + functions)",
        "Concurrence : annuler les runs obsolètes d'une même PR",
        "Badge CI dans le README",
    ], [
        "Le job `ci / build-test` est celui exigé par les protections de branches ({{D02}})",
        "Durée < 5 min sur un run à froid",
    ], ["{{D01}}"]))

add("D05", "CD — GitHub Pages : prod (master) + staging (develop) en un seul workflow", ["devops", "P0", "size/M"],
    "0 · Fondations DevOps", body(
    """
v1 publiait le staging via une branche `staging-build` force-pushée puis **redéclenchait le workflow prod avec un PAT**
pour injecter `dist/staging/`. Fragile, couplé, et un PAT est nécessaire.
""", """
Un seul workflow `deploy-pages.yml` qui construit **les deux** environnements et publie un artefact Pages unique :
`/ydash/` (master) et `/ydash/staging/` (develop). Plus de PAT, plus de branche de build.
""", [
        "Déclencheurs : push sur `master` ou `develop`, `workflow_dispatch`",
        "Job build : checkout `master` → build `VITE_BASE=/ydash/` ; checkout `develop` → build `VITE_BASE=/ydash/staging/` ; assembler `dist/` + `dist/staging/`, `.nojekyll`, `404.html` (fallback SPA)",
        "Job deploy : `actions/upload-pages-artifact` + `actions/deploy-pages`, environnement `github-pages`, concurrence `pages`",
        "Variables Firebase (`VITE_FIREBASE_*`) via secrets GitHub ; `VITE_API_BASE` (URL des Functions) via variables d'environnement GitHub (prod/staging)",
        "Supprimer toute logique de `PAT_TOKEN` ; vérifier `scope`/`start_url` PWA par base",
        "Badges prod/staging + URLs dans le README",
    ], [
        "Push sur `develop` → `https://jmarvillier.github.io/ydash/staging/` à jour, prod inchangée",
        "Merge sur `master` → prod à jour, staging conservé",
        "Aucun PAT requis",
    ], ["{{D01}}", "{{D04}}"], """
Alternative notée dans {{C01}} : Firebase Hosting (canaux de preview par PR). GitHub Pages est conservé par défaut pour rester iso v1.
"""))

add("D06", "Versioning SemVer, releases automatiques, version.json et cache du service worker", ["devops", "P1", "size/M"],
    "0 · Fondations DevOps", body(
    """
v1 : version manuelle dans `package.json` (1.2.1), SHA git injecté dans `sw.js` et `version.json` au build, aucun tag ni release.
""", """
Une version unique (SemVer) pilotée par les Conventional Commits, visible dans l'app, taguée sur GitHub.
""", [
        "Mettre en place **release-please** (ou équivalent) : PR de release automatique sur `master`, bump de version (web/functions/core synchronisés), `CHANGELOG.md`, tag `vX.Y.Z`, GitHub Release",
        "Plugin Vite (port de v1) : injecter `APP_VERSION` + `GIT_SHA` + `BUILD_TIME` dans l'app et `sw.js`, générer `version.json`",
        "Clé de cache SW = `ydash-{version}-{sha}` ; `version.json` toujours réseau",
        "Afficher version + sha dans la page Réglages ({{P11}}) et dans le toast de mise à jour ({{P10}})",
        "Première release `v2.0.0-alpha.1` dès que {{D05}} publie",
    ], [
        "Chaque merge sur `master` produit (ou met à jour) une PR de release ; sa fusion crée tag + release + changelog",
        "`https://jmarvillier.github.io/ydash/version.json` reflète la version déployée",
    ], ["{{D02}}", "{{D05}}"]))

add("D07", "Déploiement backend Firebase (Functions, règles Firestore, index) depuis la CI", ["devops", "area/backend", "area/firebase", "P0", "size/M"],
    "0 · Fondations DevOps", body(
    """
v2 introduit un backend (Cloud Functions v2) et des règles/index Firestore versionnés. v1 ne versionnait ni règles ni index.
""", """
Un workflow `deploy-firebase.yml` qui déploie fonctions + règles + index depuis `master`, et un déploiement « staging » isolé.
""", [
        "Authentification CI → GCP via **Workload Identity Federation** (pas de clé de service JSON en secret) ; fallback documenté `FIREBASE_SERVICE_ACCOUNT` chiffré si WIF indisponible",
        "`firebase deploy --only functions,firestore:rules,firestore:indexes` sur push `master` (`functions/` ou `firestore.*` modifiés) et `workflow_dispatch`",
        "Staging backend : déployer les fonctions avec un **préfixe/suffixe `stg`** (ou un codebase Firebase séparé) depuis `develop`, pointant sur la collection racine `ydash_v2_stg` (cf. {{C04}}) pour ne jamais mélanger les données",
        "Activer le plan Blaze et les APIs nécessaires (Cloud Functions, Cloud Scheduler, Secret Manager, Artifact Registry) ; documenter dans `docs/INFRA.md`",
        "Smoke test post-déploiement : appel `GET /health` de la fonction",
    ], [
        "Un merge sur `master` déploie les fonctions sans intervention manuelle",
        "Les règles Firestore déployées = celles du dépôt (`firestore.rules`)",
        "Le staging front ({{D05}}) consomme le backend `stg`",
    ], ["{{D01}}", "{{C02}}", "{{C04}}"]))

add("D08", "Gestion des secrets et de la configuration — zéro secret dans le dépôt", ["devops", "security", "P0", "size/S"],
    "0 · Fondations DevOps", body(
    """
v1 : 6 secrets `VITE_FIREBASE_*` + `PAT_TOKEN` dans GitHub ; clé de service Firebase dans le skill `ydash-regul-okx`.
v2 ajoute les clés API OKX des utilisateurs (jamais côté front).
""", """
Une carte claire de « quel secret vit où », appliquée dès le début.
""", [
        "Inventaire dans `docs/INFRA.md` : secrets GitHub (Firebase web config, WIF), variables d'environnement GitHub par environnement (`VITE_API_BASE`, `VITE_BASE`), Secret Manager GCP (clés OKX par utilisateur, cf. {{C03}})",
        "`web/.env.example` et `functions/.env.example` commités ; `.env*` ignorés",
        "Rappel : la config Firebase web n'est pas secrète mais reste en secrets GitHub pour ne pas l'exposer dans le dépôt public",
        "Pre-commit / CI : scan de secrets (gitleaks) bloquant",
        "Note dans le README : tout token collé par erreur dans un chat/issue doit être révoqué immédiatement",
    ], [
        "`gitleaks` passe en CI",
        "Aucun fichier `.env`, aucune clé, aucun PAT dans l'historique git",
    ], ["{{D01}}"]))

add("D09", "Dependabot et audit des dépendances / actions", ["devops", "security", "P2", "size/S"],
    "0 · Fondations DevOps", body(
    """
v1 chargeait SheetJS depuis un CDN sans version verrouillée dans `package.json` et n'avait aucun suivi des dépendances.
""", """
Mises à jour automatiques et contrôlées.
""", [
        "`.github/dependabot.yml` : npm (racine + workspaces, hebdomadaire, groupées), `github-actions`",
        "`npm audit --audit-level=high` en CI (non bloquant au début, bloquant après stabilisation)",
        "Toutes les dépendances front passent par npm (plus de CDN) ; `xlsx` versionné dans `web/package.json`",
    ], [
        "Les PRs Dependabot arrivent sur `develop` avec CI verte",
    ], ["{{D04}}"]))

add("D10", "Environnement de développement local (émulateurs Firebase, scripts, onboarding)", ["devops", "doc", "P1", "size/M"],
    "0 · Fondations DevOps", body(
    """
v1 se développait contre la base de prod avec un `.env.local`. v2 a un backend : il faut pouvoir tout lancer en local
(Auth + Firestore + Functions) sans toucher aux données réelles.
""", """
`npm run dev` lance l'app + les émulateurs, avec des données de démo.
""", [
        "Émulateurs Firebase (Auth, Firestore, Functions) configurés dans `firebase.json` ; `npm run dev` = `concurrently` web + émulateurs",
        "Jeu de données de démo (`tools/seed-demo.ts`) : fills spot, positions XPERP, dépôts, positions Earn, plans DCA — anonymisés, couvrant tous les cas des tests de parité ({{C05}})",
        "Mode « OKX mock » pour les fonctions (fixtures JSON des réponses OKX) activable par variable d'env",
        "`docs/ONBOARDING.md` : prérequis, clés, commandes, debug iPad (Safari Web Inspector / Termius)",
    ], [
        "Un nouveau poste peut lancer l'app et naviguer sur toutes les pages en < 15 min sans accès prod",
    ], ["{{D01}}", "{{C04}}"]))

add("D11", "Monitoring et alerting minimal (fonctions, sync, erreurs front)", ["devops", "area/backend", "P2", "size/S"],
    "0 · Fondations DevOps", body(
    """
La sync OKX tourne sans surveillance humaine : il faut savoir quand elle échoue (clé expirée, quota, changement d'API).
""", """
Être prévenu en cas d'échec, sans usine à gaz.
""", [
        "Logs structurés dans les Functions (requestId, uid haché, endpoint, durée, code OKX)",
        "Alerte Cloud Monitoring : > N erreurs de sync / heure ou aucune sync réussie depuis 24 h → e-mail (et/ou Telegram via le bot existant `xperps_watch`)",
        "Front : `ErrorBoundary` (port v1) + remontée des erreurs dans une collection `ydash_v2/{uid}/client_errors` (rétention 30 j) ou Sentry si souhaité",
        "Page Réglages : dernier statut de sync, dernière erreur ({{P11}})",
    ], [
        "Une clé OKX invalidée volontairement déclenche une alerte en < 1 h",
    ], ["{{C10}}"]))

# ===========================================================================
# M1 — SOCLE TECHNIQUE
# ===========================================================================

add("C01", "ADR-001 — Architecture cible Ydash v2 (à valider avant implémentation)", ["decision", "doc", "tech", "P0", "size/S"],
    "1 · Socle technique", body(
    """
Les appels à l'API **privée** OKX (fills, positions, Earn…) exigent une signature HMAC avec la clé secrète et ne sont pas
accessibles depuis un navigateur (CORS + secret exposé). Seuls les endpoints publics (`/market/*`) le sont (v1 les utilise déjà).
v2 a donc besoin d'un backend. Par ailleurs l'API OKX ne conserve que ~3 mois d'historique de fills : il faut **persister**.
""", """
Figer l'architecture dans `docs/adr/ADR-001-architecture.md` et la faire valider.
""", [
        "Rédiger l'ADR avec le **choix par défaut** ci-dessous et les alternatives écartées (Cloud Run, Cloudflare Worker, VM GCP existante, Firebase Hosting vs GitHub Pages, JS vs TS)",
        "Valider : (1) Cloud Functions v2 comme proxy + sync ; (2) Firestore comme persistance normalisée ; (3) `core` partagé ; (4) GitHub Pages ; (5) TypeScript strict",
        "Décider la devise de référence par défaut (USD ≈ USDT/USDC) et l'affichage EUR optionnel",
        "Schéma d'architecture (Mermaid) dans l'ADR",
    ], [
        "ADR fusionné sur `develop` avec statut « Accepté » ; tous les tickets du socle y font référence",
    ], ["Aucune (mais bloque {{C02}}, {{C04}}, {{C13}})"], """
**Proposition par défaut**

```
iPad/desktop ── PWA React (GitHub Pages) ──► Cloud Functions v2 (Node 22, région europe-west1)
      │                                          ├─ /okx/*  proxy signé, lecture seule, allowlist
      │                                          ├─ sync*   Cloud Scheduler (horaire) + à la demande
      │                                          └─ secrets  Secret Manager (clé OKX par utilisateur)
      └─ Firestore (ydash_v2/{uid}/…)  ◄──────────┘   lecture temps réel côté front (onSnapshot)
                 ▲
                 └─ v1 (users/{uid}/…) lu une seule fois par l'import legacy, jamais modifié
```
- Host OKX EEA : `https://eea.okx.com` (compte `my.okx.com`) ; WS `wss://wseea.okx.com` (non utilisé en v2.0).
- Le front ne reçoit jamais la clé OKX ; il lit Firestore et appelle le backend avec son ID token Firebase.
"""))

add("C02", "Backend — proxy OKX authentifié (signature HMAC, host EEA, allowlist lecture seule)", ["tech", "area/backend", "area/okx", "security", "P0", "size/M"],
    "1 · Socle technique", body(
    """
Cf. {{C01}}. Il faut un client OKX côté serveur, réutilisé par toutes les fonctions de sync, et un endpoint HTTP pour les
lectures à la demande depuis l'app (ex. rafraîchir les soldes Earn).
""", """
Un module `functions/src/okx/client.ts` + une fonction HTTPS `okxProxy` sûrs et testés.
""", [
        "Client : signature `OK-ACCESS-SIGN = base64(HMAC_SHA256(timestamp + method + requestPath + body, secret))`, en-têtes `OK-ACCESS-KEY/TIMESTAMP/PASSPHRASE`, base `https://eea.okx.com` (configurable), timeout, retry avec backoff sur 429/5xx, respect des limites de rate",
        "Pagination générique (`after`/`before`/`limit`) et helper « tout récupérer depuis `begin` »",
        "Gestion des codes OKX (`code !== '0'`), erreurs typées, jamais de secret dans les logs",
        "Fonction HTTPS `okxProxy` : vérifie l'ID token Firebase, charge la clé de l'uid ({{C03}}), n'autorise qu'une **allowlist d'endpoints GET en lecture** (`/api/v5/account/*`, `/api/v5/trade/fills*`, `/api/v5/asset/*`, `/api/v5/finance/*`, `/api/v5/market/*`), CORS restreint aux origines prod/staging/localhost",
        "`GET /health` (version, région)",
        "Tests unitaires : signature vérifiée contre un vecteur connu, allowlist, pagination (fixtures)",
    ], [
        "Depuis l'app authentifiée, `okxProxy` renvoie `/api/v5/account/balance` du compte ; un endpoint de trading (`/trade/order`) est refusé 403",
        "Une requête sans ID token est refusée 401",
    ], ["{{C01}}", "{{D01}}"]))

add("C03", "Clés API OKX par utilisateur — saisie dans l'app, stockage Secret Manager, test de connexion", ["feature", "area/backend", "area/frontend", "security", "P0", "size/M"],
    "1 · Socle technique", body(
    """
Chaque utilisateur Ydash doit fournir une clé API OKX **lecture seule** (créée sur my.okx.com, permissions « Lecture » uniquement,
sans retrait ni trading). Elle ne doit jamais transiter vers le front après saisie ni être stockée en clair dans Firestore.
""", """
Un flux sûr : saisie → stockage chiffré → test → statut.
""", [
        "Fonction callable `setOkxCredentials({apiKey, secret, passphrase})` : vérifie l'auth, teste la clé (`/api/v5/account/config`), refuse une clé avec permissions trading/withdraw (`perm` du résultat), écrit le secret dans **Secret Manager** (`okx-{uid}`), stocke seulement `{ keyLast4, perm, createdAt, status }` dans `ydash_v2/{uid}/profile`",
        "Fonction callable `revokeOkxCredentials()` ; `testOkxCredentials()`",
        "Accès Secret Manager limité au compte de service des fonctions ; chargement avec cache mémoire court",
        "UI (page Réglages, {{P11}}) : formulaire, guide pas-à-pas de création de clé sur my.okx.com, affichage du statut (dernier test, permissions), bouton révoquer",
        "Option : restriction IP côté OKX documentée (les Functions n'ont pas d'IP fixe sans VPC/NAT ; laisser « aucune restriction » ou prévoir un connecteur VPC + Cloud NAT en P2)",
    ], [
        "Une clé avec droit de trading est refusée avec un message clair",
        "Après saisie, aucune valeur de clé n'est lisible depuis le front ni Firestore",
    ], ["{{C02}}", "{{C04}}"]))

add("C04", "Modèle de données Firestore v2 — collections normalisées, règles de sécurité, index", ["tech", "area/firebase", "security", "P0", "size/M"],
    "1 · Socle technique", body(
    """
v1 stocke tout le journal dans **un seul document** (`users/{uid}/snapshots/latest`). v2 normalise : un document par
opération, séparé des métadonnées utilisateur, dans une racine **distincte de v1** pour garantir que v1 n'est jamais touché.
""", """
Un schéma documenté, des règles « propriétaire uniquement », les index nécessaires, et des types partagés dans `core`.
""", [
        "Racine `ydash_v2/{uid}/…` (staging : `ydash_v2_stg/{uid}/…`). Collections : `profile` (doc unique), `okx_fills/{tradeId}`, `okx_orders/{ordId}` (agrégat par ordre : VWAP, volume, frais), `okx_positions/{posId-cTime}` (futures clôturées), `funding_events/{id}` (dépôts/retraits/transferts crypto & fiat), `manual_ops/{id}` (hors OKX), `op_meta/{opId}` (notes, `dashboard`, `planId`), `earn_positions/{key}`, `earn_events/{id}`, `earn_snapshots/{yyyymmdd}`, `dca_plans/{id}`, `dca_templates/{id}`, `sync_state/{job}`, `client_errors/{id}`",
        "Types TypeScript dans `core/src/model/*.ts` (source unique, utilisée par web et functions) + `docs/DATA-MODEL.md` avec exemples",
        "`firestore.rules` : lecture/écriture limitées à `request.auth.uid == uid` ; collections alimentées par le backend (`okx_*`, `earn_*`, `sync_state`) en **lecture seule** côté client ; validation de schéma basique sur `manual_ops` et `op_meta`",
        "`firestore.indexes.json` : index composites prévus (ex. `okx_fills` par `instId`+`ts`, `okx_positions` par `closeTimeMs`)",
        "Tests des règles avec `@firebase/rules-unit-testing`",
    ], [
        "Un utilisateur A ne peut lire aucune donnée de B (test automatisé)",
        "Le client ne peut pas écrire dans `okx_fills` (test automatisé)",
        "`docs/DATA-MODEL.md` fusionné",
    ], ["{{C01}}"]))

add("C05", "Package `core` — moteur métier typé et testé (agrégation paires, breakeven, PnL, périodes) + tests de parité v1", ["tech", "area/core", "test", "P0", "size/L"],
    "1 · Socle technique", body(
    """
En v1 la logique est dispersée (`process.js`, `usePeriodFilter.js`, `useDcaStrategy.js`, fallbacks dans `KpiRow`/`SummaryTable`)
avec de légères divergences. v2 la centralise dans `core`, sans dépendance React ni Firestore.
""", """
Un moteur pur `core` reproduisant exactement les résultats v1 sur des données de référence, puis étendu aux besoins v2.
""", [
        "Modèle d'entrée unifié `Operation` (spot buy/sell, dépôt, retrait, manuel) avec devise réelle (`USDT`/`USDC`/`EUR`), horodatage ms, `source` (`okx`, `manual`, `legacy`, `grid`)",
        "`aggregateByPair()` : position nette, prix moyen d'achat/vente pondérés, coût des ventes, PnL réalisé, breakeven, PnL latent (cours live), deltas vs moyennes — port de `process.js` + `enrichWithPrices()`",
        "`computeKpis(period)` : capital déposé/disponible/investi, PnL réalisé/latent/total (+%), compteurs ordres, barres achats/ventes — port de `usePeriodFilter.js` (fenêtres 1j/1s/1m/1a/tout, capital dispo all-time)",
        "Normalisation des paires (`BTC-USDC` → `BTC/USDC`, legacy `BTC/USDT`), conversion devise de référence",
        "**Tests de parité** : extraire (lecture seule) le snapshot v1 anonymisé en fixture, le convertir en `Operation[]`, comparer KPI par KPI avec les valeurs calculées par le code v1 (script `tools/v1-reference.mjs` exécutant `process.js`/`usePeriodFilter` d'origine) — tolérance 1e-6",
        "Couverture `core` ≥ 90 %",
    ], [
        "Tests de parité verts sur Dashboard (KPIs, récap) et Paires",
        "Aucun import React/Firebase dans `core`",
    ], ["{{D01}}", "{{C04}}"], """
Les écarts volontaires (ex. USDC non assimilé à USDT) sont listés dans `docs/PARITY.md` et remontés dans {{Q02}}.
"""))

add("C06", "Sync OKX — fills spot (récents + archive 3 mois), pagination, déduplication, agrégation par ordre", ["feature", "area/backend", "area/okx", "area/journal", "P0", "size/L"],
    "1 · Socle technique", body(
    """
Remplace la régularisation manuelle. Référence : `ydash-regul-okx/references/okx-fills.md` (règles : 1 ligne par ordre, VWAP,
dédup par `tradeId`, fenêtre 3 jours `/trade/fills` + 3 mois `/trade/fills-history`).
""", """
Les fills spot du compte sont dans Firestore, à jour, sans doublon, avec l'ordre agrégé.
""", [
        "Job `syncSpotFills(uid)` : `GET /api/v5/trade/fills-history?instType=SPOT&begin=…` paginé + `GET /api/v5/trade/fills` (3 j), curseur `sync_state/spotFills.lastBillId/lastTs`, premier run = backfill complet des 3 mois",
        "Écriture idempotente `okx_fills/{tradeId}` : `instId`, `base`, `quote`, `side`, `fillPx`, `fillSz`, `fee`, `feeCcy`, `fillTime`, `ordId`, `clOrdId`, `tag`, `source`",
        "Agrégation `okx_orders/{ordId}` : VWAP, Σ taille, Σ frais, montant quote, première/dernière exécution, statut",
        "Conserver la devise réelle de règlement (USDC vs USDT) — plus d'assimilation",
        "Batch writes (≤ 500) ; journal d'exécution dans `sync_state`",
        "Tests avec fixtures réelles anonymisées (pagination, doublons entre les deux endpoints, fill partiel)",
    ], [
        "Après deux exécutions successives, aucun doublon ; un fill ajouté sur OKX apparaît au run suivant",
        "Le nombre d'ordres agrégés sur une période correspond à l'historique d'ordres OKX",
    ], ["{{C02}}", "{{C03}}", "{{C04}}", "{{C10}}"]))

add("C07", "Sync OKX — dépôts, retraits et transferts (crypto + fiat EUR) → capital déposé", ["feature", "area/backend", "area/okx", "area/journal", "P1", "size/M"],
    "1 · Socle technique", body(
    """
v1 : « Capital déposé = Σ dépôts USDT » saisis à la main. Sur le compte EEA les apports sont des virements SEPA en EUR,
des dépôts crypto (ex. BTC depuis un hardware wallet) et des transferts internes funding ↔ trading.
""", """
Une collection `funding_events` fiable alimentant les KPIs Capital.
""", [
        "Job `syncFunding(uid)` : `GET /api/v5/asset/deposit-history`, `GET /api/v5/asset/withdrawal-history`, historique fiat (`/api/v5/fiat/deposit-order-history`, `/withdrawal-order-history`), transferts internes via `GET /api/v5/asset/bills` (types transfert) — paginés, idempotents",
        "Modèle `FundingEvent { kind: deposit|withdrawal|transfer, ccy, amt, ts, chain?, txId?, valuationRef? }`",
        "Valorisation : montant en devise de référence au **cours du jour de l'événement** (candle journalière OKX publique) pour les dépôts crypto ; EUR converti via EUR-USDT/USDC",
        "`core` : `capitalDepose = Σ dépôts − Σ retraits` (règle v1 adaptée : les retraits réduisent le capital déposé ? → à trancher dans l'ADR, défaut : afficher déposé, retiré, net)",
        "Possibilité de **compléter manuellement** (ex. BTC reçu hors OKX) via `manual_ops` ({{P04}})",
    ], [
        "Le KPI « Capital déposé » v2 = total des apports réels du compte (vérifié contre l'export OKX)",
    ], ["{{C06}}", "{{C10}}"]))

add("C08", "Sync OKX — positions futures XPERP clôturées + récupération automatique des stops (R exact)", ["feature", "area/backend", "area/okx", "area/xperps", "P1", "size/L"],
    "1 · Socle technique", body(
    """
v1 : collection `xperps` peuplée hors app par le skill (`ingest_okx.py`, `recover_stops.py`, `build_xperps.py`) depuis
`account/positions-history` + ordres algo (`effective` **et** `canceled`) pour retrouver le stop initial et calculer un R exact.
Référence : `ydash-regul-okx/references/okx-positions.md`.
""", """
Le même résultat, automatisé dans le backend, avec la logique de calcul dans `core`.
""", [
        "Job `syncPositions(uid)` : `GET /api/v5/account/positions-history` (`instType=FUTURES` puis `SWAP`), pagination `after`, clé `posId-cTime`, `ctVal` via `GET /api/v5/public/instruments` (cache)",
        "Récupération des stops : `GET /api/v5/trade/orders-algo-history` en `state=effective` et `state=canceled` (type `conditional`/`oco`), fenêtre autour de `cTime`, **garde-fou de côté** (short → stop au-dessus de l'entrée ; long → en dessous), sinon `riskModel: fixed` (risque par défaut paramétrable, 10 USDC)",
        "`core/xperps` : port de `build_xperps.py` (netPnlUsd = `realizedPnl`, grossPnl, fees, funding, liqPenalty, `rMultiple`, `returnPct`, `result`, champs locaux Europe/Paris `closeHourLocal`/`closeDowLocal`) + port de `aggregateXperps()` (`xperps.js`) avec tests (fixtures réelles anonymisées)",
        "Override manuel du stop dans `op_meta/{posId-cTime}.stopPx` (UI dans {{P06}}) → recalcul du R",
        "Migration : documents v1 `users/{uid}/xperps` importés comme `source: legacy` ({{C12}}), non dupliqués avec la sync",
    ], [
        "Pour les positions déjà en v1, `netPnlUsd` et `rMultiple` v2 = v1 (test de parité)",
        "Une position clôturée sur OKX apparaît au run suivant avec son R (exact ou `fixed` signalé)",
    ], ["{{C06}}", "{{C10}}"]))

add("C09", "Sync OKX — bots grid spot : décision d'inclusion et tagging des fills issus des bots", ["decision", "feature", "area/backend", "area/okx", "P1", "size/M"],
    "1 · Socle technique", body(
    """
Des bots grid spot tournent sur le compte (suivis par le skill `okx-grid-monitor`). Leurs sous-ordres génèrent des fills qui
fausseraient les prix moyens/breakeven des paires et le pointage DCA s'ils étaient mélangés aux achats discrétionnaires.
""", """
Décider et implémenter le traitement des fills de bots.
""", [
        "Investiguer : les fills des sous-ordres grid remontent-ils dans `/trade/fills(-history)` ? avec quel `tag`/`clOrdId`/`algoId` ? (vérifier sur le compte réel)",
        "Récupérer `GET /api/v5/tradingBot/grid/orders-algo-history` + `orders-algo-pending` + `sub-orders` ; marquer `okx_fills.source = 'grid'` + `algoId` par correspondance d'`ordId`",
        "Règle par défaut : fills `grid` **exclus** des agrégats Paires/Dashboard/DCA, mais visibles dans l'explorateur ({{P03}}) et comptés dans une section « Bots » (KPI PnL grille vs flottant, port light de `okx-grid-monitor`) — P2",
        "Documenter la décision dans l'ADR ou `docs/DATA-MODEL.md`",
    ], [
        "Aucun fill de bot ne modifie le breakeven d'une paire sauf choix explicite de l'utilisateur (toggle)",
    ], ["{{C06}}"]))

add("C10", "Orchestrateur de synchronisation — planification, à la demande, état, idempotence, reprise", ["tech", "area/backend", "P0", "size/M"],
    "1 · Socle technique", body(
    """
Plusieurs jobs de sync (fills, funding, positions, earn) doivent tourner régulièrement pour chaque utilisateur ayant une clé,
sans dépasser les quotas OKX/Firestore, et être relançables depuis l'app.
""", """
Un cadre commun robuste pour tous les jobs.
""", [
        "Fonction planifiée (Cloud Scheduler) `syncAll` : toutes les heures, pour chaque `profile.okxStatus == 'ok'` ; décalage aléatoire par utilisateur",
        "Fonction callable `syncNow({jobs?})` déclenchée depuis l'app (bouton ↻), avec verrou anti-concurrence (`sync_state/{job}.running`, TTL)",
        "Contrat `SyncJob { run(ctx): { fetched, written, cursor, errors } }` ; état persistant `sync_state/{job}` : `lastRunAt`, `lastSuccessAt`, `cursor`, `lastError`, `stats`",
        "Backoff et quarantaine : après N échecs consécutifs (clé invalide), `okxStatus = 'error'` + notification ({{D11}})",
        "Rejouabilité : un job peut être relancé depuis `begin` (backfill) via `workflow_dispatch`/callable admin",
    ], [
        "Deux `syncNow` simultanés n'exécutent qu'une sync",
        "Un job en erreur n'empêche pas les autres de tourner",
    ], ["{{C02}}", "{{C04}}"]))

add("C11", "Cours live et conversions — service prix (OKX public) + fallback, USDC/USDT/EUR", ["tech", "area/frontend", "area/prices", "P1", "size/S"],
    "1 · Socle technique", body(
    """
v1 : cascade OKX → Binance → Kraken → CryptoCompare pour la crypto et 8 sources pour les métaux (XAG/XAU), rafraîchissement 60 s.
En v2 OKX reste la référence (c'est l'exchange tradé) ; les métaux ne sont plus tradés (à confirmer).
""", """
Un hook `usePrices()` simple, fiable, avec source affichée.
""", [
        "`core/prices` : `fetchOkxTickers()` (`GET https://eea.okx.com/api/v5/market/tickers?instType=SPOT` ou `www.okx.com`, CORS public), cache 30 s, résolution `BASE-USDC` → `BASE-USDT` → `BASE-USD`",
        "Taux `EUR` via tickers `USDT-EUR`/`USDC-EUR` ou `EUR-USDT` ; conversion devise de référence (ADR)",
        "Fallback unique Binance (ou aucun, à trancher) ; **supprimer** la cascade métaux sauf si XAG/XAU réapparaît dans les données legacy",
        "Rafraîchissement 60 s + bouton manuel + indicateur source/heure (port v1)",
        "Prix historique à une date : `GET /api/v5/market/history-candles` (utilisé par {{C07}} et {{E04}}) — helper partagé côté backend",
    ], [
        "Toutes les paires présentes dans Firestore obtiennent un cours ou un état « indisponible » explicite",
    ], ["{{C13}}"]))

add("C12", "Reprise des données v1 — import one-shot du journal, des plans/templates DCA et des xperps (lecture seule de v1)", ["feature", "area/migration", "area/backend", "P1", "size/M"],
    "1 · Socle technique", body(
    """
L'historique OKX via API ne remonte que 3 mois : les opérations plus anciennes n'existent que dans le journal v1
(`users/{uid}/snapshots/latest`, ~240 lignes, source Google Sheet) et dans `xperps`, `dca_plans`, `dca_templates`.
Ces collections v1 doivent être **lues, jamais modifiées**.
""", """
Un import idempotent et traçable des données v1 dans `ydash_v2`, exécutable depuis l'app (page Réglages) ou en ligne de commande.
""", [
        "Fonction callable `importLegacyV1()` (+ script `tools/import-v1.ts` pour exécution hors app) : lit v1 avec le même uid, convertit chaque ligne de journal en `manual_ops` (`source: legacy`, `legacyRowIndex`, `ordId` extrait des Notes, devise rétablie quand la Note l'indique, `dashboard`, `planId` → `op_meta`)",
        "Règle anti-doublon avec la sync OKX : une ligne legacy portant un `ordId` déjà présent dans `okx_orders` est marquée `supersededBy` (masquée, non comptée)",
        "Import `dca_plans`/`dca_templates` → `ydash_v2/{uid}/dca_plans` (format `zones[]` unifié, migration des anciens formats comme `migratePlanZones()`)",
        "Import `xperps` → `okx_positions` avec `source: legacy` ; la sync {{C08}} ne réécrit pas un doc legacy sauf si le `posId-cTime` est retrouvé (alors `source: okx`)",
        "Rapport d'import (lignes lues/écrites/ignorées/doublons) affiché dans l'app et stocké dans `sync_state/importV1`",
        "Rejouable sans doublon ; option `--dry-run`",
    ], [
        "Après import, Dashboard/Paires v2 reproduisent v1 (tests de parité {{C05}} sur les mêmes données)",
        "Aucune écriture dans `users/{uid}/…` (vérifié par les règles et un test)",
    ], ["{{C04}}", "{{C05}}"]))

add("C13", "Front — socle applicatif (Vite + React + TS, routing, auth gate, shell, design tokens, PWA de base)", ["tech", "area/frontend", "P0", "size/M"],
    "1 · Socle technique", body(
    """
v1 : `App.jsx` + `AppShell` (sidebar/topbar), `AuthGate`, `Landing`, tokens dans `variables.css`, Space Mono, ciblage iPad.
Pas de routeur (état `activePage`).
""", """
La coquille v2 prête à recevoir les pages, fidèle au design v1.
""", [
        "Routing (`react-router`) : `/` landing, `/dashboard`, `/paires`, `/xperps`, `/donnees`, `/dca`, `/earn`, `/reglages` ; `basename` = `VITE_BASE`",
        "Auth : port de `AuthGate` (email/mdp + Google, messages FR), `onAuthStateChanged`, garde de routes",
        "Shell : sidebar (icônes + libellés v1 + **Earn**), topbar (burger, breadcrumb, bouton install/màj), `ErrorBoundary`, `LoadingOverlay`, `Logo`",
        "Design : reprendre `variables.css` (palette bleu nuit · or · silver, contrastes AA), Space Mono (auto-hébergée ou Google Fonts), composants de base (`KpiCard` + tooltip (i) avec formule, `PeriodTabs`, `Table`, `Badge`, `Toggle`, `Modal`)",
        "PWA de base : `manifest.webmanifest` (scope par base), icônes v1, enregistrement SW (le SW complet est dans {{P10}})",
        "Storybook léger ou page `/kitchen-sink` (optionnel) pour vérifier les composants sur iPad",
    ], [
        "Connexion/déconnexion fonctionnent sur staging ; navigation entre routes vides OK sur iPad et desktop",
    ], ["{{D01}}", "{{C01}}"]))

add("C14", "Front — couche d'accès aux données (hooks Firestore temps réel, cache, états chargement/erreur)", ["tech", "area/frontend", "area/firebase", "P0", "size/M"],
    "1 · Socle technique", body(
    """
v1 chargeait tout le snapshot en mémoire puis recalculait. v2 lit des collections (potentiellement quelques milliers de docs)
et doit rester fluide sur iPad.
""", """
Des hooks simples : `useFills()`, `useOrders()`, `usePositions()`, `useFundingEvents()`, `useManualOps()`, `useOpMeta()`, `useEarnPositions()`, `useSyncState()`, `useProfile()`.
""", [
        "Lecture temps réel (`onSnapshot`) avec requêtes bornées (période/paire) et pagination pour l'explorateur ; persistance hors-ligne Firestore activée (IndexedDB) pour l'usage PWA",
        "Fusion `okx_orders` + `manual_ops` (non supersedées) + `op_meta` → `Operation[]` (type `core`) mémoïsée",
        "Appels backend : `callSyncNow()`, `callOkxProxy(path)`, `setOkxCredentials()` avec gestion d'erreurs uniformes",
        "États : chargement, vide (« Connecte ta clé OKX »), erreur, hors-ligne (données en cache + bandeau)",
        "Tests des hooks avec émulateur Firestore ({{D10}})",
    ], [
        "Le Dashboard reste réactif (< 100 ms de recalcul) avec 5 000 opérations",
    ], ["{{C04}}", "{{C13}}"]))

add("C15", "Métadonnées utilisateur sur les opérations (notes, exclusion dashboard, planId) découplées des données OKX", ["feature", "area/journal", "area/frontend", "P1", "size/S"],
    "1 · Socle technique", body(
    """
v1 mélangeait dans la même ligne les données d'exécution et les annotations (Notes, `Dashboard=false`, `planId`, `isRegul`).
En v2 les données OKX sont en lecture seule ; les annotations vivent dans `op_meta/{opId}` (`opId` = `ordId` spot, `posId-cTime` futures, id manuel).
""", """
Annoter n'importe quelle opération sans jamais altérer la donnée source.
""", [
        "`core` : type `OpMeta { notes?, dashboard: boolean (défaut true), planId?, tags?: string[], stopPx? }` et fonction `applyMeta(ops, meta)`",
        "Écriture côté client autorisée par les règles ({{C04}}) uniquement sur `op_meta`",
        "UI : édition inline dans l'explorateur ({{P03}}), toggle « Inclure dans le Dashboard », rattachement à un plan DCA ({{P09}})",
        "Le flag v1 `isRegul` disparaît : remplacé par la requête « opérations sans `planId` » dans le wizard DCA",
    ], [
        "Exclure une opération recalcule immédiatement Dashboard/Paires ; la donnée OKX reste intacte",
    ], ["{{C04}}", "{{C14}}"]))

# ===========================================================================
# M2 — PARITÉ FONCTIONNELLE
# ===========================================================================

add("P01", "Page Dashboard — filtre de période, KPIs Capital / Performance / Ordres, récapitulatif par paire", ["feature", "area/frontend", "area/journal", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `KpiRow.jsx`, `SummaryTable.jsx`, `PeriodFilter.jsx`, `usePeriodFilter.js` (voir `docs/ANALYSE-dashboard-weex.md` §3.2).
""", """
Le même écran, alimenté par `core.computeKpis()` sur les opérations OKX + manuelles.
""", [
        "Onglets 1j / 1s / 1m / 1a / Tout avec notice (port `periodNotice`)",
        "Section Capital : déposé (+ retiré / net, cf. {{C07}}), disponible (all-time), investi (période) — tooltips et formules v1",
        "Section Performance (cours actuel) : PnL réalisé / latent / total en devise de référence et % du capital déposé, indicateur live (source, heure, ↺)",
        "Section Ordres : total/exécutés/annulés/taux (les ordres annulés viennent de `GET /trade/orders-history-archive`, à ajouter au job {{C06}} si on garde ce KPI), barres achats vs ventes (nombre et volume)",
        "Récapitulatif par paire (Paire · Investi · Valeur act. · Breakeven · PnL réalisé / latent / total + % + ligne Total)",
        "Devise de référence sélectionnable (USD/EUR) selon l'ADR",
    ], [
        "Checklist de recette {{Q02}} « Dashboard » verte",
        "Rendu iPad portrait/paysage et iPhone vérifié (captures dans la PR)",
    ], ["{{C05}}", "{{C06}}", "{{C07}}", "{{C11}}", "{{C14}}"]))

add("P02", "Page Paires — cartes par paire, écarts vs moyennes, exclusion", ["feature", "area/frontend", "area/journal", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `PairesView.jsx`, `PairCard.jsx`, `KpiBox`, `KpiTooltip` (§3.3).
""", """
Les cartes paires v1 sur données OKX, avec les frais réels et la devise réelle.
""", [
        "Carte : position nette, montant investi, moyenne d'achat (+ nb ordres), moyenne de vente, breakeven, PnL réalisé/latent/total (valeur + %), cours live + source, écarts cours vs moy. achat / moy. vente / breakeven",
        "Nouveaux champs v2 : frais cumulés, devise de règlement, dernière opération, nombre de fills `grid` exclus ({{C09}})",
        "Toggle d'exclusion persistant (`profile.excludedPairs`) ; paires stables exclues par défaut",
        "Tri (investi, PnL, nom) et recherche",
    ], [
        "Parité des valeurs avec v1 sur les données legacy ({{Q02}})",
    ], ["{{C05}}", "{{C14}}", "{{P01}}"]))

add("P03", "Page Données — explorateur des opérations (table, recherche, filtres, pagination) + édition des métadonnées", ["feature", "area/frontend", "area/journal", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `DataPanel.jsx` (menu), `DataBrowser.jsx` (table 20/page, recherche, édition inline, suppression).
En v2 les opérations OKX sont en lecture seule ; seules les métadonnées et les opérations manuelles sont modifiables.
""", """
Un explorateur unique de toutes les opérations (OKX spot, manuelles, legacy, bots) avec leurs métadonnées.
""", [
        "Colonnes : date/heure (seconde), source (badge okx/manuel/legacy/grid), paire, sens, cours, volume, montant + devise, frais, ordId, plan DCA, Dashboard, notes",
        "Recherche plein texte, filtres (période, paire, source, sens, « sans plan »), tri, pagination serveur (curseurs Firestore)",
        "Édition inline des métadonnées ({{C15}}) ; édition/suppression complète uniquement pour `manual_ops`",
        "Menu Données v2 : Explorer · Nouvelle entrée manuelle ({{P04}}) · Exporter .xlsx ({{P05}}) · Import v1 ({{C12}}) · Synchroniser maintenant ({{C10}}) — l'import fichier/Google Sheet v1 est **retiré** (hors import legacy)",
    ], [
        "Toutes les opérations synchronisées sont visibles et filtrables ; une opération OKX n'est pas supprimable",
    ], ["{{C14}}", "{{C15}}"]))

add("P04", "Saisie manuelle d'opérations hors OKX (Ledger, transferts, dépôts non détectés)", ["feature", "area/frontend", "area/journal", "P1", "size/S"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `EntryForm.jsx` (date/heure, paire avec autocomplétion, sens Achat/Vente/Dépôt/Retrait, statut, cours, volume,
montants USDT/USDC/EUR, notes, toggle Dashboard, rattachement DCA). Cas réel : lot BTC transféré depuis un hardware wallet.
""", """
Le formulaire v1, simplifié, écrivant dans `manual_ops` avec une devise unique explicite.
""", [
        "Champs : date/heure, paire (autocomplétion depuis les instruments OKX + paires connues), sens, cours, volume, montant + **devise** (USDT/USDC/EUR/autre), frais optionnels, notes, Dashboard, plan DCA",
        "Validation (`core`), calcul automatique montant ↔ cours × volume",
        "Édition/suppression depuis l'explorateur ({{P03}}) avec confirmation",
        "Marqueur visuel « manuel » partout où l'opération apparaît",
    ], [
        "Une opération manuelle entre dans les agrégats exactement comme un fill OKX",
    ], ["{{C04}}", "{{C15}}", "{{P03}}"]))

add("P05", "Export .xlsx du journal consolidé (opérations + positions + earn)", ["feature", "area/frontend", "P2", "size/S"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `ExportXlsx.jsx` (SheetJS via CDN, compat Safari iPad par Blob). Utile pour archivage/compta.
""", """
Un export multi-onglets à jour, sans dépendance CDN.
""", [
        "`xlsx` (SheetJS) en dépendance npm ; génération côté client via Blob (port v1)",
        "Onglets : Opérations (toutes sources, devise réelle, frais, ordId), Positions XPERP, Earn (positions + événements), Dépôts/Retraits, Paires (agrégats du jour)",
        "Filtre période appliqué à l'export ; nom de fichier `ydash-YYYY-MM-DD.xlsx`",
    ], [
        "Export ouvert dans Numbers/Excel sans erreur ; nombres typés (pas de texte)",
    ], ["{{C14}}"]))

add("P06", "Page XPERPS — KPIs, équité, répartition, long/short, par paire, heatmap horaire, distribution en R", ["feature", "area/frontend", "area/xperps", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `XperpsView.jsx`, `xperps.js` (§3.5). Données désormais synchronisées automatiquement ({{C08}}).
""", """
La page v1 à l'identique + gestion des stops manquants dans l'app.
""", [
        "Périodes Jour/Semaine/Mois/Tout ; KPIs : PnL net réalisé (+R net, retour moyen), win rate (G/P/BE), R net exact, profit factor + expectancy, nb trades (gain/perte moyens)",
        "Courbe d'équité (USDC ou R), donut, Long vs Short, table par paire, heatmap par heure, meilleurs jour/heure/paire, distribution en R, mention des R `fixed`",
        "Liste des positions avec détail (entrée/sortie VWAP, stop retrouvé ou non, frais, funding) ; **saisie du stop initial** pour les positions `fixed` → recalcul R ({{C15}})",
        "Positions **ouvertes** (`GET /account/positions` via proxy) en encart « En cours » — nouveau v2, P2",
    ], [
        "Parité des KPIs avec v1 sur les positions legacy ({{Q02}})",
    ], ["{{C08}}", "{{C14}}"]))

add("P07", "DCA — reprise du moteur Scaled Mirror DCA dans `core` + tests", ["tech", "area/core", "area/dca", "test", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `useDcaStrategy.js` (breakeven, prix moyen, date de début effective, solde de rechargement par cycle, ops du cycle
courant, timeline 15 cycles, signal zones accum/ralent/profit), `dcaUtils.js`, `DCA_Strategy.MD`.
""", """
Le moteur DCA en TypeScript pur, testé, consommant des `Operation[]` rattachées à un plan.
""", [
        "Port de `computeBreakeven`, `computeAvgPrice`, `getEffectiveStart`, `computeRechargement`, `getCurrentPeriodOps`, `generateTimeline`, `computeSignal` avec types `DcaPlan`, `Zone`, `Signal`",
        "Tests unitaires sur cas documentés (exemple du solde −2 dans le code v1, bull run multi-paliers, plan sans date de début, sur-investissement)",
        "Test de parité : plans réels v1 (anonymisés) → mêmes breakeven/rechargement/signal",
        "Copier `DCA_Strategy.MD` dans `docs/DCA-STRATEGY.md` et le mettre en cohérence avec le code (zones unifiées)",
    ], [
        "Couverture ≥ 90 % sur `core/dca` ; parité verte",
    ], ["{{C05}}"]))

add("P08", "DCA — liste des plans, templates et wizard (paire, pointage des opérations OKX, paramètres)", ["feature", "area/frontend", "area/dca", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `DcaList`, `DcaStep1/2/3`, `DcaStepper`, `DcaView` (§3.6). Le pointage v1 écrivait `planId` dans la ligne du journal ;
en v2 il écrit `op_meta/{opId}.planId`.
""", """
Le wizard v1 sur les opérations synchronisées.
""", [
        "Liste des plans (icônes BTC/ETH), suppression avec confirmation, gestion des templates (créer/charger/supprimer)",
        "Étape 1 : paire (depuis les paires présentes dans les données) + période ; alerte si pas BTC (règle v1)",
        "Étape 2 : pointage des opérations exécutées de la paire (tout coché par défaut) — exclut les fills `grid` par défaut ({{C09}})",
        "Étape 3 : montant de base, fréquence, zones (validation : ≥ 1 zone profit, total ≤ 100 %), plafond de rechargement, templates ; récap breakeven",
        "Enregistrement dans `ydash_v2/{uid}/dca_plans` + écriture des `planId` dans `op_meta`",
    ], [
        "Un plan créé en v2 produit le même tableau de bord qu'en v1 pour les mêmes opérations",
    ], ["{{P07}}", "{{C15}}", "{{C14}}"]))

add("P09", "DCA — tableau de bord d'un plan (signal, rechargement, timeline, affiliation de fills, saisie)", ["feature", "area/frontend", "area/dca", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `DcaDashboard.jsx` (KPIs avec tooltips, signal du cycle, timeline, cycle en cours, cours live/manuel, « Sync lignes DCA »,
« Régularisation » = affilier des lignes importées).
""", """
Le tableau de bord v1, où la « régularisation » devient « affecter les opérations OKX non rattachées ».
""", [
        "KPIs : breakeven, prix moyen achat/vente, total investi/réalisé, position, PnL latent, solde de rechargement (+ % du plafond), zones",
        "Signal du cycle (zone active, montant à déployer ou % à vendre), timeline 15 cycles, cycle en cours (achats/ventes)",
        "Cours live ({{C11}}) avec saisie manuelle de secours",
        "Bouton « Opérations non rattachées (n) » → pointage filtré (remplace Régularisation) ; bouton « Nouvelle entrée manuelle rattachée »",
        "Supprimer « Sync lignes DCA » (plus de lignes à resynchroniser : `op_meta` est la vérité)",
    ], [
        "Parité signal/rechargement avec v1 ({{Q02}})",
    ], ["{{P07}}", "{{P08}}"]))

add("P10", "PWA — manifest, service worker versionné, installation iOS/Android, mise à jour", ["feature", "area/pwa", "area/frontend", "P1", "size/S"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `sw.js` (Cache First, cache `weex-{version}-{sha}`, `version.json` réseau, `SKIP_WAITING`), `InstallPrompt.jsx`,
bouton topbar 📲/🔄, guide iOS, `manifest.json`.
""", """
Le même comportement, via `vite-plugin-pwa` (Workbox) ou port direct du SW v1.
""", [
        "Choisir `vite-plugin-pwa` (recommandé) : précache des assets hashés, `registerType: 'prompt'`, `navigateFallback`, `scope`/`start_url` par base ({{D05}})",
        "Toast/bouton « Mettre à jour » (port UX v1), guide d'installation iOS, prompt Android, mémorisation des refus (localStorage)",
        "Stratégie réseau pour Firestore/Functions : jamais en cache SW (laisser Firestore gérer l'offline)",
        "Version/sha affichés ({{D06}})",
    ], [
        "Installation sur iPad OK ; après un déploiement, le bouton « Màj » apparaît et recharge la nouvelle version",
    ], ["{{C13}}", "{{D06}}"]))

add("P11", "Page Réglages — clés OKX, statut de sync, import v1, devise de référence, préférences, danger zone", ["feature", "area/frontend", "P1", "size/M"],
    "2 · Parité fonctionnelle v1", body(
    """
Nouvelle page v2 : regroupe ce qui était dispersé (effacer le repository, import) et ce qui est nouveau (clés OKX, sync).
""", """
Un seul endroit pour piloter la connexion OKX et les données.
""", [
        "Bloc OKX : saisie/test/révocation de clé ({{C03}}), guide de création (my.okx.com → API → lecture seule)",
        "Bloc Synchronisation : état par job (`sync_state`), dernier succès/erreur, bouton « Synchroniser maintenant », bouton « Backfill 3 mois »",
        "Bloc Données : import v1 ({{C12}}) avec rapport, export ({{P05}}), **danger zone** : purger toutes les données v2 de l'utilisateur (double confirmation)",
        "Préférences : devise de référence (USD/EUR), période par défaut, paires exclues, risque fixe par défaut XPERP",
        "À propos : version, sha, date de build, liens (dépôt, changelog)",
    ], [
        "Tous les blocs fonctionnent sur staging avec un compte de test",
    ], ["{{C03}}", "{{C10}}", "{{C12}}"]))

add("P12", "Landing / accueil et navigation", ["feature", "area/frontend", "P2", "size/S"],
    "2 · Parité fonctionnelle v1", body(
    """
Référence v1 : `Landing.jsx` (4 cartes + import rapide). En v2 l'accueil reflète l'état de la connexion OKX.
""", """
Un accueil utile : état du compte, raccourcis, premier pas si aucune clé.
""", [
        "Cartes : Dashboard, Paires, XPERPS, Earn, DCA, Données, Réglages ; cartes verrouillées tant qu'aucune donnée",
        "État : clé OKX connectée ? dernière sync ? nb opérations ? (lecture `profile` + `sync_state`)",
        "Parcours d'onboarding en 3 étapes (créer la clé → coller → première sync) si aucune clé",
    ], [
        "Un nouvel utilisateur comprend quoi faire sans documentation",
    ], ["{{C13}}", "{{P11}}"]))

add("P13", "Accessibilité, responsive iPad/iPhone/desktop et finitions UI (audit)", ["tech", "area/frontend", "P2", "size/S"],
    "2 · Parité fonctionnelle v1", body(
    """
v1 était conçue pour iPad (position fixed, overflow hidden, topbar 54 px). v2 doit rester irréprochable sur iPad et correcte ailleurs.
""", """
Un passage qualité avant la recette.
""", [
        "Audit Lighthouse (PWA, a11y, perf) sur staging ; corriger les contrastes/aria manquants (tooltips (i), toggles, tableaux)",
        "Vérifier `safe-area-inset`, rotation, clavier iPad dans les formulaires, scroll des tables",
        "Dark mode uniquement (v1) — confirmer ; thème clair hors périmètre",
    ], [
        "Lighthouse a11y ≥ 90, PWA installable, pas de scroll horizontal parasite",
    ], ["{{P01}}", "{{P02}}", "{{P03}}", "{{P06}}", "{{P09}}"]))

# ===========================================================================
# M3 — EARN
# ===========================================================================

add("E01", "Earn — découverte des produits du compte et modèle unifié `EarnPosition`", ["feature", "area/earn", "area/okx", "area/core", "decision", "P1", "size/M"],
    "3 · Volet Earn", body(
    """
État constaté sur le compte EEA (31/10/2026) : **Simple Earn flexible BTC** (`/finance/savings/balance` : ~0,11 BTC, intérêts horaires,
`earnings` cumulé), **DeFi Earn USDC représenté par le token LYUSDC** (~2 790 LYUSDC dans le compte funding ; 1:1 USDC, le solde
croît quotidiennement), **staking SOL via OKSOL** (~2,15 OKSOL), ETH en funding, aucun ordre on-chain earn actif ni fixed.
Les produits ont des APIs différentes et des mécaniques différentes (solde qui grossit vs taux de conversion).
""", """
Un modèle unique dans `core` et une cartographie produit → endpoints → règle de valorisation.
""", [
        "Inventorier via le proxy : `/finance/savings/balance`, `/finance/staking-defi/orders-active` + `orders-history`, `/finance/staking-defi/sol/balance`, `/finance/staking-defi/eth/balance`, `/asset/balances` (tokens LYUSDC, OKSOL, BETH…), fixed earn (endpoint à confirmer dans la doc OKX), `/finance/stable-rewards/balance`",
        "Modèle `EarnPosition { key, product: simple_flex|defi_lyusdc|sol_staking|eth_staking|onchain|fixed|stable_rewards, ccy, underlying, amount, amountUnderlying, earningsAccrued, aprCurrent?, startedAt?, state, raw }`",
        "Règles de valorisation : LYUSDC → USDC 1:1 (rendement = croissance du solde) ; OKSOL → SOL via taux de conversion OKX (rendement = variation du taux) ; Simple Earn → `earnings` ; staking-defi → `earnings` des ordres",
        "`docs/EARN.md` : tableau produit / endpoint / champs / formule de rendement / limites connues",
    ], [
        "Toutes les positions Earn réelles du compte sont reconnues et typées ; un produit inconnu est listé comme `unknown` sans casser la page",
    ], ["{{C02}}", "{{C04}}"]))

add("E02", "Earn — synchronisation des soldes et historiques + snapshots quotidiens", ["feature", "area/earn", "area/backend", "area/okx", "P1", "size/M"],
    "3 · Volet Earn", body(
    """
L'API OKX donne l'état courant et certains historiques (`/finance/savings/lending-history` horaire, `purchase-redeem-history`,
`orders-history`, `asset/bills` types Earn) mais **pas** de série temporelle des soldes/valorisations : il faut la constituer.
""", """
Des jobs `syncEarn` (horaire) et `snapshotEarn` (quotidien) alimentant `earn_positions`, `earn_events`, `earn_snapshots`.
""", [
        "`syncEarn(uid)` : rafraîchit `earn_positions/{key}` depuis les endpoints de {{E01}} ; détecte les entrées/sorties (souscription, rachat, intérêts crédités) → `earn_events/{id}` (depuis `lending-history`, `purchase-redeem-history`, `asset/bills` filtrés sur les types Earn, diff de solde LYUSDC/OKSOL)",
        "Date d'entrée en earn (`startedAt`) : premier événement de souscription connu, sinon premier `lending-history`, sinon saisie manuelle (métadonnée)",
        "`snapshotEarn(uid)` (quotidien 00:05 Europe/Paris) : `earn_snapshots/{yyyymmdd}` = par position `{ amount, amountUnderlying, price, valueRef, earningsAccrued, apr }` + totaux",
        "Backfill initial des snapshots passés à partir des événements + prix historiques (approximation documentée)",
        "Idempotence, curseurs dans `sync_state/earn`",
    ], [
        "Après 2 jours de fonctionnement, 2 snapshots existent et les intérêts crédités apparaissent dans `earn_events`",
    ], ["{{E01}}", "{{C10}}", "{{C11}}"]))

add("E03", "Earn — calcul du rendement (intérêts cumulés coin + devise, APR réalisé, par période)", ["feature", "area/earn", "area/core", "test", "P1", "size/M"],
    "3 · Volet Earn", body(
    """
« Ce que le earning rapporte » : intérêts perçus, exprimés dans la devise du produit (BTC, USDC, SOL) **et** en devise de référence,
avec un APR réalisé comparable entre produits.
""", """
`core/earn/yield.ts` testé.
""", [
        "Par position : `earningsCcy` (cumul depuis l'entrée, et sur la période 1s/1m/1a/tout), `earningsRef` (au cours courant **et** au cours de chaque crédit si disponible — les deux affichés), `aprRealized = (Σ intérêts période / capital moyen période) × 365 / jours`",
        "Produits à solde croissant (LYUSDC) : intérêts = Δ solde hors souscriptions/rachats ; produits à taux (OKSOL) : intérêts = amount × Δ taux",
        "Totaux portefeuille Earn : intérêts totaux, APR pondéré, part du PnL global",
        "Tests unitaires sur fixtures réelles (lending-history BTC) + cas limites (rachat partiel, souscription en cours de période)",
    ], [
        "Pour la position BTC Simple Earn, `earningsCcy` = champ `earnings` OKX (± arrondi) ; APR réalisé cohérent avec le taux affiché par OKX",
    ], ["{{E02}}"]))

add("E04", "Earn — plus/moins-value marché des positions (vs cours moyen d'acquisition, vs cours à la mise en earn)", ["feature", "area/earn", "area/core", "test", "P1", "size/M"],
    "3 · Volet Earn", body(
    """
Deuxième dimension demandée : combien le capital placé en earn a gagné/perdu **du fait du marché**, en fonction du
**cours moyen d'acquisition** (issu des achats spot / dépôts valorisés, moteur {{C05}}) **et/ou** de la **date de mise en earn**
(cours à cette date).
""", """
`core/earn/marketPnl.ts` testé, avec deux références explicites et une vue combinée.
""", [
        "`pnlVsCost = amount × (priceNow − avgCostPrice)` où `avgCostPrice` = prix moyen d'achat pondéré de la paire (ou, pour un dépôt crypto, cours à la date du dépôt) ; indiquer la couverture (part de la position dont le coût est connu)",
        "`pnlVsEntry = amount × (priceNow − priceAtEntry)` avec `priceAtEntry` = candle journalière/horaire OKX à `startedAt` ({{C11}}) ; par **lot** si plusieurs souscriptions (table `earn_lots` dérivée des `earn_events`)",
        "Décomposition affichée : valorisation actuelle = capital au coût + PnL marché + intérêts ; « sans earn » (buy & hold) vs « avec earn » = + intérêts",
        "Stablecoins (LYUSDC) : PnL marché = variation EUR/USD uniquement si devise de référence EUR, sinon 0",
        "Tests : scénarios BTC (acheté 2 lots, placé en earn à une 3e date), OKSOL, LYUSDC",
    ], [
        "Les deux PnL sont expliqués par tooltip (formule + références de prix et dates utilisées)",
    ], ["{{E02}}", "{{C05}}", "{{C11}}"]))

add("E05", "Page Earn — synthèse, détail par position, graphiques rendement et valorisation", ["feature", "area/frontend", "area/earn", "P1", "size/M"],
    "3 · Volet Earn", body(
    """
Nouvelle page `/earn`, dans le style des autres pages (KPI cards + tooltips (i), tableaux, graphiques simples).
""", """
Lire en un écran ce que rapporte le earn et ce que fait le marché sur le capital placé.
""", [
        "Filtre période 1s / 1m / 1a / Tout ; devise de référence",
        "KPIs : capital placé (valeur actuelle), intérêts cumulés (période / total), APR réalisé pondéré, PnL marché vs coût, PnL marché vs entrée, PnL total (marché + intérêts)",
        "Table par position : produit, actif, montant, valeur, intérêts (coin / devise), APR, entrée (date, cours), coût moyen, PnL vs coût, PnL vs entrée, total",
        "Graphiques (SVG maison ou lib légère) : valorisation + intérêts cumulés dans le temps (depuis `earn_snapshots`), répartition par produit",
        "Encart « événements récents » (`earn_events`) et bouton ↻ (sync à la demande)",
        "Saisie manuelle de `startedAt` / coût moyen si inconnus (métadonnée)",
    ], [
        "La page reflète les 3 positions réelles (BTC flexible, LYUSDC, OKSOL) avec des chiffres cohérents avec l'app OKX",
    ], ["{{E03}}", "{{E04}}", "{{C14}}"]))

add("E06", "Earn — alertes et insights (APR en baisse, produit terminé, position non placée)", ["feature", "area/earn", "P2", "size/S"],
    "3 · Volet Earn", body(
    """
Une fois les données en place, quelques signaux utiles au quotidien.
""", """
Des alertes simples, calculées à chaque snapshot.
""", [
        "Règles : APR réalisé < seuil pendant N jours ; produit arrivé à échéance / rachat en attente ; actif en funding **non placé** depuis > X jours (ex. ETH) ; valorisation sous le coût moyen de plus de Y %",
        "Affichage dans la page Earn + (option) notification Telegram via le bot existant",
    ], [
        "Chaque règle est testée et paramétrable dans Réglages",
    ], ["{{E05}}"]))

# ===========================================================================
# M4 — BASCULE & QUALITÉ
# ===========================================================================

add("Q01", "Tests E2E smoke (Playwright) sur staging", ["test", "devops", "P2", "size/M"],
    "4 · Bascule & qualité", body(
    """
Les tests unitaires couvrent `core` ; il faut un filet sur les parcours réels (auth, navigation, sync, pages).
""", """
Une suite E2E courte exécutée après chaque déploiement staging.
""", [
        "Playwright (Chromium + WebKit pour approcher Safari iPad) contre `…/ydash/staging/` avec un compte de test et le backend `stg` en mode OKX mock ({{D10}})",
        "Scénarios : connexion, onboarding clé (mock), sync, Dashboard/Paires/XPERPS/Earn/DCA affichent des valeurs, export xlsx, mise à jour PWA",
        "Job `e2e.yml` déclenché après `deploy-pages` (develop) ; captures en artefact",
    ], [
        "Suite verte sur staging en < 5 min",
    ], ["{{D05}}", "{{D10}}", "{{EPIC-PARITY}}"]))

add("Q02", "Recette de parité v1 ↔ v2 — checklist KPI par KPI sur les mêmes données", ["test", "area/migration", "doc", "P1", "size/M"],
    "4 · Bascule & qualité", body(
    """
Avant de considérer v2 utilisable, comparer **écran par écran** les valeurs v1 (prod actuelle) et v2 (staging après import legacy + sync).
""", """
`docs/PARITY.md` : tableau des KPIs, valeurs v1/v2, écart, explication, statut.
""", [
        "Dashboard (toutes périodes), Paires (chaque paire), XPERPS (KPIs + table), DCA (chaque plan : breakeven, rechargement, signal), Données (compte d'opérations)",
        "Écarts attendus et acceptés : devise réelle USDC vs USDT, frais, horodatage à la seconde, fills `grid`, retraits dans le capital — chacun documenté",
        "Procédure reproductible (captures + export xlsx v1 et v2 à la même date)",
    ], [
        "Tous les écarts sont soit nuls, soit expliqués et validés par Jérémie",
    ], ["{{EPIC-PARITY}}", "{{C12}}"]))

add("Q03", "Documentation utilisateur et technique (README, docs/, ADR, runbook de sync)", ["doc", "P1", "size/S"],
    "4 · Bascule & qualité", body(
    """
v1 avait un README minimal. v2 a un backend, des jobs et des règles de calcul qui doivent être explicables (y compris aux futurs
skills Claude qui liront le dépôt).
""", """
Une documentation complète et à jour dans `docs/`.
""", [
        "`README.md` : vision, captures, liens prod/staging, badges, démarrage rapide",
        "`docs/` : `ANALYSE-dashboard-weex.md` (déjà là), `adr/`, `DATA-MODEL.md`, `INFRA.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `EARN.md`, `DCA-STRATEGY.md`, `PARITY.md`, `RUNBOOK-SYNC.md` (que faire si la sync échoue, backfill, rotation de clé)",
        "Formules de chaque KPI (reprises des tooltips) dans `docs/KPIS.md`",
    ], [
        "Un relecteur externe peut comprendre l'architecture et relancer une sync depuis la doc seule",
    ], ["{{C01}}", "{{C04}}", "{{E01}}"]))

add("Q04", "Plan de bascule v1 → v2 et décommissionnement (hors périmètre tant que v1 reste intouchée)", ["decision", "area/migration", "doc", "P2", "size/S"],
    "4 · Bascule & qualité", body(
    """
Consigne : **ne pas toucher au dashboard existant** pendant la migration. Ce ticket prépare seulement la bascule ; aucune action
sur `dashboard-weex` n'est réalisée sans GO explicite.
""", """
Un plan écrit, prêt à exécuter le jour J.
""", [
        "Critères de GO : recette {{Q02}} validée, sync stable ≥ 2 semaines, Earn opérationnel, sauvegarde export v1",
        "Jour J (après GO) : geler v1 (bannière + lien vers v2 — modification minimale de v1), réaffecter le PWA installé sur iPad, archiver le dépôt `dashboard-weex` (lecture seule), retirer/adapter le skill `ydash-regul-okx` (la sync remplace la régularisation), mettre à jour les skills Claude qui lisent Firestore (`okx-grid-monitor` non concerné)",
        "Plan de retour arrière : v1 reste déployée et fonctionnelle (données v1 jamais modifiées)",
    ], [
        "Document `docs/CUTOVER.md` validé ; checklist jour J prête",
    ], ["{{Q02}}", "{{Q03}}"]))

add("Q05", "Performance et coûts — quotas Firestore, fréquence de sync, taille du bundle, budget GCP", ["tech", "devops", "P2", "size/S"],
    "4 · Bascule & qualité", body(
    """
v2 introduit des coûts (Functions, Scheduler, Secret Manager, lectures Firestore) : rester dans le gratuit/quasi-gratuit pour un usage
personnel, et garder l'app rapide sur iPad.
""", """
Mesurer, fixer des budgets, optimiser si besoin.
""", [
        "Estimer lectures/écritures par jour (sync horaire × collections) ; ajuster fréquence (ex. fills toutes les heures, earn toutes les 6 h, snapshots 1/j) et requêtes bornées côté front",
        "Budget GCP + alerte à 5 €/mois ; vérifier le free tier Functions v2 / Scheduler (3 jobs gratuits)",
        "Bundle web : analyse (`rollup-plugin-visualizer`), code-splitting par route, `xlsx` chargé à la demande",
        "Mesure LCP/TTI sur iPad en 4G",
    ], [
        "Coût mensuel estimé < 5 € ; LCP < 2,5 s sur staging",
    ], ["{{C10}}", "{{EPIC-PARITY}}"]))
