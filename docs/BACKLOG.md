# Backlog initial Ydash v2

Généré par `tickets/create_issues.py` depuis `tickets/tickets.py` — 55 tickets.

## 0 · Fondations DevOps

| # | Clé | Titre | Labels |
|---|---|---|---|
| [#1](https://github.com/jmarvillier/ydash/issues/1) | `EPIC-DEVOPS` | [EPIC] DevOps — dépôt, CI/CD, environnements, versioning | epic, devops |
| [#6](https://github.com/jmarvillier/ydash/issues/6) | `D01` | Initialiser le dépôt et le scaffold du monorepo (web / functions / core) | devops, tech, P0, size/M |
| [#7](https://github.com/jmarvillier/ydash/issues/7) | `D02` | Stratégie de branches, protections et conventions de commit | devops, P0, size/S |
| [#8](https://github.com/jmarvillier/ydash/issues/8) | `D03` | Templates d'issues / PR, CODEOWNERS et projet GitHub | devops, doc, P1, size/S |
| [#9](https://github.com/jmarvillier/ydash/issues/9) | `D04` | CI — lint, typecheck, tests, build sur chaque PR et push | devops, test, P0, size/S |
| [#10](https://github.com/jmarvillier/ydash/issues/10) | `D05` | CD — GitHub Pages : prod (master) + staging (develop) en un seul workflow | devops, P0, size/M |
| [#11](https://github.com/jmarvillier/ydash/issues/11) | `D06` | Versioning SemVer, releases automatiques, version.json et cache du service worker | devops, P1, size/M |
| [#12](https://github.com/jmarvillier/ydash/issues/12) | `D07` | Déploiement backend Firebase (Functions, règles Firestore, index) depuis la CI | devops, area/backend, area/firebase, P0, size/M |
| [#13](https://github.com/jmarvillier/ydash/issues/13) | `D08` | Gestion des secrets et de la configuration — zéro secret dans le dépôt | devops, security, P0, size/S |
| [#14](https://github.com/jmarvillier/ydash/issues/14) | `D09` | Dependabot et audit des dépendances / actions | devops, security, P2, size/S |
| [#15](https://github.com/jmarvillier/ydash/issues/15) | `D10` | Environnement de développement local (émulateurs Firebase, scripts, onboarding) | devops, doc, P1, size/M |
| [#16](https://github.com/jmarvillier/ydash/issues/16) | `D11` | Monitoring et alerting minimal (fonctions, sync, erreurs front) | devops, area/backend, P2, size/S |

## 1 · Socle technique

| # | Clé | Titre | Labels |
|---|---|---|---|
| [#2](https://github.com/jmarvillier/ydash/issues/2) | `EPIC-CORE` | [EPIC] Socle technique — backend OKX, modèle de données, moteur métier | epic, tech |
| [#17](https://github.com/jmarvillier/ydash/issues/17) | `C01` | ADR-001 — Architecture cible Ydash v2 (à valider avant implémentation) | decision, doc, tech, P0, size/S |
| [#18](https://github.com/jmarvillier/ydash/issues/18) | `C02` | Backend — proxy OKX authentifié (signature HMAC, host EEA, allowlist lecture seule) | tech, area/backend, area/okx, security, P0, size/M |
| [#19](https://github.com/jmarvillier/ydash/issues/19) | `C03` | Clés API OKX par utilisateur — saisie dans l'app, stockage Secret Manager, test de connexion | feature, area/backend, area/frontend, security, P0, size/M |
| [#20](https://github.com/jmarvillier/ydash/issues/20) | `C04` | Modèle de données Firestore v2 — collections normalisées, règles de sécurité, index | tech, area/firebase, security, P0, size/M |
| [#21](https://github.com/jmarvillier/ydash/issues/21) | `C05` | Package `core` — moteur métier typé et testé (agrégation paires, breakeven, PnL, périodes) + tests de parité v1 | tech, area/core, test, P0, size/L |
| [#22](https://github.com/jmarvillier/ydash/issues/22) | `C06` | Sync OKX — fills spot (récents + archive 3 mois), pagination, déduplication, agrégation par ordre | feature, area/backend, area/okx, area/journal, P0, size/L |
| [#23](https://github.com/jmarvillier/ydash/issues/23) | `C07` | Sync OKX — dépôts, retraits et transferts (crypto + fiat EUR) → capital déposé | feature, area/backend, area/okx, area/journal, P1, size/M |
| [#24](https://github.com/jmarvillier/ydash/issues/24) | `C08` | Sync OKX — positions futures XPERP clôturées + récupération automatique des stops (R exact) | feature, area/backend, area/okx, area/xperps, P1, size/L |
| [#25](https://github.com/jmarvillier/ydash/issues/25) | `C09` | Sync OKX — bots grid spot : décision d'inclusion et tagging des fills issus des bots | decision, feature, area/backend, area/okx, P1, size/M |
| [#26](https://github.com/jmarvillier/ydash/issues/26) | `C10` | Orchestrateur de synchronisation — planification, à la demande, état, idempotence, reprise | tech, area/backend, P0, size/M |
| [#27](https://github.com/jmarvillier/ydash/issues/27) | `C11` | Cours live et conversions — service prix (OKX public) + fallback, USDC/USDT/EUR | tech, area/frontend, area/prices, P1, size/S |
| [#28](https://github.com/jmarvillier/ydash/issues/28) | `C12` | Reprise des données v1 — import one-shot du journal, des plans/templates DCA et des xperps (lecture seule de v1) | feature, area/migration, area/backend, P1, size/M |
| [#29](https://github.com/jmarvillier/ydash/issues/29) | `C13` | Front — socle applicatif (Vite + React + TS, routing, auth gate, shell, design tokens, PWA de base) | tech, area/frontend, P0, size/M |
| [#30](https://github.com/jmarvillier/ydash/issues/30) | `C14` | Front — couche d'accès aux données (hooks Firestore temps réel, cache, états chargement/erreur) | tech, area/frontend, area/firebase, P0, size/M |
| [#31](https://github.com/jmarvillier/ydash/issues/31) | `C15` | Métadonnées utilisateur sur les opérations (notes, exclusion dashboard, planId) découplées des données OKX | feature, area/journal, area/frontend, P1, size/S |

## 2 · Parité fonctionnelle v1

| # | Clé | Titre | Labels |
|---|---|---|---|
| [#3](https://github.com/jmarvillier/ydash/issues/3) | `EPIC-PARITY` | [EPIC] Parité fonctionnelle avec Ydash v1 | epic, feature |
| [#32](https://github.com/jmarvillier/ydash/issues/32) | `P01` | Page Dashboard — filtre de période, KPIs Capital / Performance / Ordres, récapitulatif par paire | feature, area/frontend, area/journal, P1, size/M |
| [#33](https://github.com/jmarvillier/ydash/issues/33) | `P02` | Page Paires — cartes par paire, écarts vs moyennes, exclusion | feature, area/frontend, area/journal, P1, size/M |
| [#34](https://github.com/jmarvillier/ydash/issues/34) | `P03` | Page Données — explorateur des opérations (table, recherche, filtres, pagination) + édition des métadonnées | feature, area/frontend, area/journal, P1, size/M |
| [#35](https://github.com/jmarvillier/ydash/issues/35) | `P04` | Saisie manuelle d'opérations hors OKX (Ledger, transferts, dépôts non détectés) | feature, area/frontend, area/journal, P1, size/S |
| [#36](https://github.com/jmarvillier/ydash/issues/36) | `P05` | Export .xlsx du journal consolidé (opérations + positions + earn) | feature, area/frontend, P2, size/S |
| [#37](https://github.com/jmarvillier/ydash/issues/37) | `P06` | Page XPERPS — KPIs, équité, répartition, long/short, par paire, heatmap horaire, distribution en R | feature, area/frontend, area/xperps, P1, size/M |
| [#38](https://github.com/jmarvillier/ydash/issues/38) | `P07` | DCA — reprise du moteur Scaled Mirror DCA dans `core` + tests | tech, area/core, area/dca, test, P1, size/M |
| [#39](https://github.com/jmarvillier/ydash/issues/39) | `P08` | DCA — liste des plans, templates et wizard (paire, pointage des opérations OKX, paramètres) | feature, area/frontend, area/dca, P1, size/M |
| [#40](https://github.com/jmarvillier/ydash/issues/40) | `P09` | DCA — tableau de bord d'un plan (signal, rechargement, timeline, affiliation de fills, saisie) | feature, area/frontend, area/dca, P1, size/M |
| [#41](https://github.com/jmarvillier/ydash/issues/41) | `P10` | PWA — manifest, service worker versionné, installation iOS/Android, mise à jour | feature, area/pwa, area/frontend, P1, size/S |
| [#42](https://github.com/jmarvillier/ydash/issues/42) | `P11` | Page Réglages — clés OKX, statut de sync, import v1, devise de référence, préférences, danger zone | feature, area/frontend, P1, size/M |
| [#43](https://github.com/jmarvillier/ydash/issues/43) | `P12` | Landing / accueil et navigation | feature, area/frontend, P2, size/S |
| [#44](https://github.com/jmarvillier/ydash/issues/44) | `P13` | Accessibilité, responsive iPad/iPhone/desktop et finitions UI (audit) | tech, area/frontend, P2, size/S |

## 3 · Volet Earn

| # | Clé | Titre | Labels |
|---|---|---|---|
| [#4](https://github.com/jmarvillier/ydash/issues/4) | `EPIC-EARN` | [EPIC] Volet Earn — rendement et plus/moins-value marché | epic, feature, area/earn |
| [#45](https://github.com/jmarvillier/ydash/issues/45) | `E01` | Earn — découverte des produits du compte et modèle unifié `EarnPosition` | feature, area/earn, area/okx, area/core, decision, P1, size/M |
| [#46](https://github.com/jmarvillier/ydash/issues/46) | `E02` | Earn — synchronisation des soldes et historiques + snapshots quotidiens | feature, area/earn, area/backend, area/okx, P1, size/M |
| [#47](https://github.com/jmarvillier/ydash/issues/47) | `E03` | Earn — calcul du rendement (intérêts cumulés coin + devise, APR réalisé, par période) | feature, area/earn, area/core, test, P1, size/M |
| [#48](https://github.com/jmarvillier/ydash/issues/48) | `E04` | Earn — plus/moins-value marché des positions (vs cours moyen d'acquisition, vs cours à la mise en earn) | feature, area/earn, area/core, test, P1, size/M |
| [#49](https://github.com/jmarvillier/ydash/issues/49) | `E05` | Page Earn — synthèse, détail par position, graphiques rendement et valorisation | feature, area/frontend, area/earn, P1, size/M |
| [#50](https://github.com/jmarvillier/ydash/issues/50) | `E06` | Earn — alertes et insights (APR en baisse, produit terminé, position non placée) | feature, area/earn, P2, size/S |

## 4 · Bascule & qualité

| # | Clé | Titre | Labels |
|---|---|---|---|
| [#5](https://github.com/jmarvillier/ydash/issues/5) | `EPIC-CUTOVER` | [EPIC] Bascule v1 → v2, qualité et décommissionnement | epic, area/migration |
| [#51](https://github.com/jmarvillier/ydash/issues/51) | `Q01` | Tests E2E smoke (Playwright) sur staging | test, devops, P2, size/M |
| [#52](https://github.com/jmarvillier/ydash/issues/52) | `Q02` | Recette de parité v1 ↔ v2 — checklist KPI par KPI sur les mêmes données | test, area/migration, doc, P1, size/M |
| [#53](https://github.com/jmarvillier/ydash/issues/53) | `Q03` | Documentation utilisateur et technique (README, docs/, ADR, runbook de sync) | doc, P1, size/S |
| [#54](https://github.com/jmarvillier/ydash/issues/54) | `Q04` | Plan de bascule v1 → v2 et décommissionnement (hors périmètre tant que v1 reste intouchée) | decision, area/migration, doc, P2, size/S |
| [#55](https://github.com/jmarvillier/ydash/issues/55) | `Q05` | Performance et coûts — quotas Firestore, fréquence de sync, taille du bundle, budget GCP | tech, devops, P2, size/S |
