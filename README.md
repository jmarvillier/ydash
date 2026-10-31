# Ydash v2

[![ci](https://github.com/jmarvillier/ydash/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/jmarvillier/ydash/actions/workflows/ci.yml)

> Dashboard de trading crypto personnel, **branché en direct sur OKX** (compte EEA) : journal spot, paires,
> futures XPERP, Scaled Mirror DCA et **suivi Earn** (rendement + plus/moins-value marché).
> Successeur de [`dashboard-weex`](https://github.com/jmarvillier/dashboard-weex) (Ydash v1), qui reste en service
> et n'est pas modifié pendant la migration.

## État du projet

🚧 **Migration en cours — phase 0 (backlog & fondations).** Aucune ligne applicative n'est encore écrite :
le dépôt contient l'analyse de l'existant et le backlog complet de la migration.

| | |
|---|---|
| Analyse de v1 | [`docs/ANALYSE-dashboard-weex.md`](docs/ANALYSE-dashboard-weex.md) |
| Backlog (55 tickets, 5 milestones) | [`docs/BACKLOG.md`](docs/BACKLOG.md) · [Issues](https://github.com/jmarvillier/ydash/issues) · [Milestones](https://github.com/jmarvillier/ydash/milestones) |
| Source du backlog initial | [`tickets/tickets.py`](tickets/tickets.py) (régénérable via `tickets/create_issues.py`) |
| Prod (à venir) | `https://jmarvillier.github.io/ydash/` — branche `master` |
| Staging (à venir) | `https://jmarvillier.github.io/ydash/staging/` — branche `develop` |

## Pourquoi v2

v1 stocke un journal **saisi à la main** (ou régularisé via un skill) dans un seul document Firestore, et exige une mise à jour
constante OKX → Firebase. v2 inverse la logique : **OKX est la source de vérité**, un backend léger synchronise fills spot,
positions futures, dépôts/retraits et positions Earn dans un Firestore normalisé (pour dépasser la fenêtre de 3 mois de l'API),
et l'app ne fait que lire, annoter et calculer.

## Architecture cible (proposée — voir ADR-001, ticket `C01`)

```
iPad / desktop ── PWA React (GitHub Pages) ──► Cloud Functions v2 (proxy OKX signé + jobs de sync)
       │                                            ├─ Secret Manager : clé API OKX (lecture seule) par utilisateur
       │                                            └─ Cloud Scheduler : sync horaire, snapshots Earn quotidiens
       └─ Firestore `ydash_v2/{uid}/…` ◄────────────┘   lecture temps réel côté front
                 ▲
                 └─ données v1 (`users/{uid}/…`) lues une seule fois par l'import legacy, jamais modifiées
```

Monorepo npm workspaces : `web/` (Vite + React + TS, PWA) · `functions/` (Firebase Functions v2, Node 22, TS) ·
`core/` (moteur métier pur, typé, testé, partagé front/back) · `docs/`.

## Milestones

0. **Fondations DevOps** — dépôt, branches `master`/`develop`, CI, CD GitHub Pages prod + staging, versioning SemVer & releases, secrets, dev local
1. **Socle technique** — proxy/sync OKX, clés API, modèle Firestore v2, moteur `core` avec tests de parité v1, socle front
2. **Parité fonctionnelle v1** — Dashboard, Paires, Données, XPERPS, DCA, PWA, Réglages
3. **Volet Earn** — positions Earn (Simple Earn, LYUSDC, OKSOL…), intérêts/APR réalisé, PnL marché vs coût moyen et vs date d'entrée
4. **Bascule & qualité** — E2E, recette de parité, documentation, plan de bascule (sans toucher à v1 avant GO)

## Régénérer / compléter le backlog

```bash
python3 tickets/create_issues.py --repo jmarvillier/ydash --dry-run   # aperçu
python3 tickets/create_issues.py --repo jmarvillier/ydash             # crée ce qui manque, résout les #refs, met à jour docs/BACKLOG.md
```

## Sécurité

Aucun secret dans le dépôt — inventaire et procédure dans [`docs/INFRA.md`](docs/INFRA.md).
**Tout token collé par erreur dans un chat, une issue ou un commit doit être révoqué immédiatement.**

## Licence

MIT (voir ticket `D01` pour l'ajout du fichier `LICENSE`).
