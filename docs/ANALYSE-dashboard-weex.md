# Analyse du dashboard existant — `jmarvillier/dashboard-weex` (Ydash v1)

> Analyse réalisée le 31/10/2026 sur le commit `a75af6c` (20/08/2026), version `1.2.1`.
> Objectif : cartographier l'existant pour préparer la migration vers **Ydash v2** (`jmarvillier/ydash`).
> Le dépôt v1 n'est **pas modifié** par cette migration.

---

## 1. Vue d'ensemble

| Élément | Valeur |
|---|---|
| Nom produit | **Ydash** — « Journal de trading — suivi de tes investissements crypto » |
| Stack | React 18.3 · Vite 6 · Firebase 10 (Auth + Firestore) · PWA (Service Worker maison) |
| Langage | JavaScript (JSX), pas de TypeScript, pas de tests, pas de lint |
| Taille | 71 fichiers · ~7 600 lignes (composants + CSS) · 14 composants principaux + 7 DCA + 1 XPERP |
| Dépendances runtime | `firebase`, `react`, `react-dom` + **SheetJS (`xlsx`) chargé via CDN dans `index.html`** |
| Hébergement | GitHub Pages — prod `https://jmarvillier.github.io/dashboard-weex/` (branche `master`), staging `…/dashboard-weex/staging/` (branche `develop` + branches `feature/**`, `test/**`, `dev/**`, `staging`) |
| Backlog | GitHub Project `users/jmarvillier/projects/1` |
| Auth | Firebase Auth — Email/Mot de passe + Google (popup) |
| Base | Firestore, projet Firebase `dashboard-ydash`, données isolées par `users/{uid}/…` |
| Cible | iPad / Safari mobile en priorité (PWA installable, SW, guide d'installation iOS) |

### Le problème que v2 doit résoudre
Le journal v1 est **une feuille de calcul sérialisée dans Firestore** (`users/{uid}/snapshots/latest`, tableau de lignes à 13 colonnes). Il est alimenté **à la main** (formulaire de saisie), par import de fichier `.xlsx/.csv` ou Google Sheet, ou par « régularisation » via le skill `ydash-regul-okx` qui lit les fills OKX et **réécrit le document Firestore** après validation. Chaque trade exécuté sur OKX exige donc une mise à jour manuelle ou assistée → **source de vérité dupliquée, décalage permanent, risque de doublons**.

---

## 2. Architecture technique v1

```
index.html (SW register, SheetJS CDN, fonts)
└─ src/main.jsx → <ErrorBoundary><App/></ErrorBoundary>
   App.jsx ─ Firebase Auth gate → Landing (4 cartes) → AppShell (sidebar + topbar + pages)
   ├─ hooks/
   │  ├─ useTrading.js      état global (view, pairList, rawRows, excluded…) + import/regul/drive
   │  ├─ usePrices.js       cours live, refresh 60 s
   │  ├─ usePeriodFilter.js KPIs globaux filtrés par période (1j/1s/1m/1a/tout)
   │  ├─ useXperps.js       lecture collection xperps + agrégation
   │  └─ useDcaStrategy.js  moteur Scaled Mirror DCA (breakeven, rechargement, signal, timeline)
   ├─ lib/
   │  ├─ firebase.js        init app/auth/db
   │  ├─ repository.js      CRUD du snapshot journal (serialize/deserialize des lignes)
   │  ├─ parser.js          normalisation paires, parse nombres FR/EN, CSV, statuts
   │  ├─ process.js         agrégation par paire (positions, prix moyens, breakeven, PnL)
   │  ├─ priceRepository.js cascade de sources de cours (OKX → Binance → Kraken → CryptoCompare ; métaux : Bitfinex → GoldPrice → OKX → Stooq → Yahoo → metals.live → CF → jsDelivr)
   │  ├─ xperps.js / xperpsRepository.js  agrégation + lecture des trades perp
   │  └─ dcaRepository.js / dcaUtils.js  CRUD plans/templates DCA + helpers
   ├─ components/ (Landing, AppShell, AuthGate, KpiRow, SummaryTable, PairesView/PairCard,
   │               DataPanel, EntryForm, DataBrowser, ExportXlsx, PeriodFilter, InstallPrompt…)
   ├─ components/dca/ (DcaView orchestrateur, DcaList, DcaStep1/2/3, DcaStepper, DcaDashboard)
   ├─ components/xperps/XperpsView.jsx
   ├─ styles/ (variables.css = design tokens, + 1 CSS par composant)
   └─ sw.js (cache versionné `weex-{version}-{sha}-assets`, Cache First, SKIP_WAITING)
```

### Build & déploiement
- `vite.config.js` : injecte `__APP_VERSION__` (package.json) + `__GIT_SHA__` dans `sw.js`, génère `dist/version.json`, `base` pilotée par `VITE_BASE` (`/dashboard-weex/` ou `/dashboard-weex/staging/`).
- `.github/workflows/.deploy.yml` (prod) : push `master` → build → **injecte le contenu de la branche `staging-build` dans `dist/staging/`** → `actions/deploy-pages`.
- `.github/workflows/deploy-staging.yml` : push `develop`/`feature/**`… → build staging → force-push de `dist` sur la branche `staging-build` → **`workflow_dispatch` du workflow prod via un `PAT_TOKEN`** pour republier.
- Secrets GitHub : `VITE_FIREBASE_*` (6 variables), `PAT_TOKEN`.
- ⚠️ Points faibles : couplage prod/staging (un push staging redéploie la prod), branche `staging-build` force-pushée, PAT nécessaire, pas de CI (lint/test), pas de tag/release, versioning manuel dans `package.json`.

### Modèle de données Firestore (v1)
| Chemin | Contenu | Écrit par |
|---|---|---|
| `users/{uid}/snapshots/latest` | `{ rows: [{i, r: JSON(ligne)}], source, loadedAt, version: 3 }` — **tout le journal dans un seul document** | App (saisie, import, édition, suppression), skill `ydash-regul-okx` |
| `users/{uid}/xperps/{posId-cTime}` | 1 doc par position perp clôturée (schéma v1 : `netPnlUsd`, `rMultiple`, `returnPct`, `result`, `side`, `pair/instId`, `closeTime/closeTimeMs`, `closeHourLocal`, `closeDowLocal`, `riskModel` stop/fixed…) | skill `ydash-regul-okx` uniquement (app en lecture seule) |
| `users/{uid}/dca_plans/{id}` | plan DCA : `pair`, `startDate`, `endDate`, `baseAmount`, `frequency` (day/week/month), `zones[] {type accum/ralent/profit, label, ecart, action, color}`, `debtCeiling`, `createdAt/updatedAt` (+ anciens formats `accZones/debtZones/profitZones` migrés à la volée) | App |
| `users/{uid}/dca_templates/{id}` | jeux de zones réutilisables | App |

Schéma d'une ligne de journal (13 colonnes, 0-indexé) :
`0 Date | 1 Paire | 2 Sens (Achat/Vente/Dépôt/Retrait) | 3 Statut (Exécuté/Annulé/En attente) | 4 Cours | 5 Montant USDT | 6 Montant USDC | 7 Montant EUR | 8 planId (affiliation DCA) | 9 isRegul (flag technique) | 10 Volume | 11 Notes (contient l'ordId OKX) | 12 Dashboard (true/false)`

Conventions héritées à connaître pour la migration :
- **USDC assimilé à USDT** (montant écrit en « Montant USDT », paire `BASE/USDT` même si réglée en USDC) ; la devise réelle est seulement en Notes.
- Dates stockées à la **minute** (fills OKX à la seconde) → anti-doublon par `ordId` dans les Notes.
- `Dashboard=false` exclut une ligne des calculs ; `planId` (col 8) est la source de vérité de l'affiliation DCA ; `isRegul=true` marque une ligne importée non encore affiliée.
- Les perps ne sont plus dans le journal depuis la v2 du skill : ils vivent dans `xperps`.

---

## 3. Inventaire fonctionnel (à reprendre en v2)

### 3.1 Authentification & coquille
- Écran de connexion (email/mdp + Google), gestion des erreurs Firebase en français.
- Landing à 4 cartes (Dashboard, Paires, Données, Scaled Mirror DCA) + import rapide si repo vide.
- Shell : sidebar (Dashboard · Paires · XPERPS · Données · Scaled Mirror DCA · Accueil · Déconnexion), topbar avec burger, breadcrumb, bouton contextuel **📲 Installer** (iOS guide / Android prompt) ou **🔄 Màj** (SW en attente → `SKIP_WAITING` → reload).
- `ErrorBoundary`, `LoadingOverlay`, `InstallPrompt`.
- Design : palette « bleu nuit · or · silver » (`variables.css`), police Space Mono, tooltips (i) avec formule sur chaque KPI.

### 3.2 Dashboard (vue globale)
- Filtre de période : **1j / 1s / 1m / 1a / Tout** (fenêtres glissantes, notice explicative).
- KPIs **Capital** : déposé (Σ dépôts, non filtré), disponible (= déposé − (Σ achats − Σ ventes) all time), investi (Σ achats − Σ ventes sur la période).
- KPIs **Performance (cours actuel)** : PnL réalisé, PnL latent, PnL total, chacun en USDT et en % du capital déposé ; indicateur live (source, heure, bouton ↺).
- KPIs **Ordres** : total / exécutés / annulés / taux d'exécution ; barres achats vs ventes (nombre et volume USDT).
- **Récapitulatif par paire** : Paire · Investi · Valeur actuelle · Breakeven · PnL réalisé · PnL latent · PnL total (+ % vs investi) + ligne Total.

### 3.3 Paires (détail par paire)
- Une carte par paire : position nette, montant investi, prix moyen d'achat (+ nb ordres), prix moyen de vente, breakeven, PnL réalisé / latent / total (valeur + %), cours live + source, écarts cours vs moyenne d'achat / de vente / breakeven, toggle d'exclusion (les paires `USD*` sont exclues automatiquement).
- Moteur de calcul (`process.js`) : prix moyens pondérés par volume, coût des ventes au prix moyen d'achat, PnL réalisé = reçu − coût, breakeven = capital encore engagé / position nette, PnL latent = position × (cours − breakeven).

### 3.4 Données (gestion du journal)
- **Nouvelle entrée** : formulaire (date/heure, paire avec autocomplétion, sens, statut, cours, volume, montants USDT/USDC/EUR, notes, toggle Dashboard, rattachement optionnel à un plan DCA).
- **Parcourir** : table paginée (20/page), recherche plein texte, édition inline, suppression avec confirmation, tri anti-chronologique.
- **Importer** : fichier local `.xlsx/.csv` (SheetJS) ou Google Sheet publié en CSV → **remplace** tout le journal.
- **Régularisation** : import de lignes **additives** (OKX / Ledger) avec flag `isRegul`.
- **Exporter .xlsx** : tout le journal (compat Safari iPad via Blob).

### 3.5 XPERPS (trades futures USDC)
- Lecture de `users/{uid}/xperps`, période Jour / Semaine / Mois / Tout.
- KPIs : PnL net réalisé (+ R net, retour moyen), win rate (G/P/BE), R net exact (+R gagnés / −R perdus), profit factor + expectancy/trade, nb trades (gain moyen / perte moyenne).
- Courbe d'équité cumulée (USDC ou R), donut de répartition, Long vs Short, performance par paire (table), heatmap par heure, meilleur jour/heure/paire, distribution des trades en R (6 buckets), mention des R « approx » (riskModel fixed).
- Le peuplement se fait **hors app** par le skill `ydash-regul-okx` (positions-history OKX + récupération automatique du stop initial dans les ordres algo pour un R exact).

### 3.6 Scaled Mirror DCA (stratégie)
- Liste des plans (icônes BTC/ETH), templates, wizard en 3 étapes : **1** paire + période (alerte si pas BTC), **2** pointage des opérations du journal à rattacher (mode normal ou « régularisation » filtré sur `isRegul`), **3** paramètres (montant de base, fréquence jour/semaine/mois, zones accum/ralent/profit avec écart % et action, plafond de rechargement, templates).
- Tableau de bord d'un plan : breakeven, prix moyen d'achat/vente, total investi / réalisé, position, PnL latent, **solde de rechargement** (Σ base − injecté par cycle), signal du jour (zone active → montant à déployer ou % à vendre), timeline des 15 derniers cycles (acheté/raté/vendu/futur), cycle en cours, cours live ou saisie manuelle, bouton « Sync lignes DCA », bouton « Régularisation » (affilier des lignes importées), saisie directe d'une entrée rattachée au plan.
- Référence : `DCA_Strategy.MD` (principes, zones, dette/rechargement, paliers de distribution).

### 3.7 Cours live
- Crypto : **OKX `GET /api/v5/market/tickers?instType=SPOT`** (1 appel, cache 30 s) → Binance → Kraken → CryptoCompare. Métaux (XAG/XAU) : cascade de 8 sources. Rafraîchissement toutes les 60 s + bouton manuel. Affichage de la source par paire.

### 3.8 PWA
- `manifest.json` (standalone, icônes 180/192/512), SW Cache First avec purge par version, `version.json` toujours réseau, détection iOS/Android, prompt d'installation et de mise à jour.

---

## 4. Dette technique et limites constatées (à ne pas reproduire)

1. **Journal = un seul document Firestore** (tableau sérialisé) : pas de requête, pas d'index, réécriture complète à chaque modification, limite 1 Mo du document à terme, concurrence (app vs skill) non gérée.
2. **Pas de synchronisation OKX dans l'app** : dépend du skill externe + validation humaine ; historique OKX des fills limité à 3 mois → données perdues si non régularisées à temps.
3. **Perte d'information** : USDC → USDT, dates à la minute, frais non structurés (dans Notes), pas de `tradeId/ordId` en colonne dédiée.
4. **Logique métier dupliquée** : calculs de breakeven/PnL présents dans `process.js`, `usePeriodFilter.js`, `useDcaStrategy.js`, `KpiRow.jsx` (fallback) et `SummaryTable.jsx` (fallback) — avec de petites divergences (ex. PnL latent « journal » basé sur le dernier prix saisi).
5. **Code mort / doublons** : `Topbar.jsx` et `DataMenu.jsx` non utilisés (remplacés par `AppShell` et `DataPanel`), `KpiBox/KpiTooltip` vs tooltip interne de `KpiRow`, `config.js` (ID d'un Google Sheet par défaut) inutilisé.
6. **Aucun test, aucun lint, aucun typage** ; dépendance CDN (`xlsx`) non versionnée dans `package.json`.
7. **CI/CD fragile** : staging injecté dans la prod via branche force-pushée + PAT ; aucune vérification avant déploiement ; version non taguée.
8. **Prix** : cascade très large (8 sources métaux) héritée d'un besoin ponctuel (XAG) ; CORS dépendants de tiers.
9. **Sécurité** : règles Firestore non versionnées dans le repo ; clé de service Firebase dans le skill (hors repo).

---

## 5. Ce que v2 doit conserver / changer

| Conserver (parité) | Changer |
|---|---|
| Auth Firebase (email + Google), isolation par `uid` | **Source de vérité = OKX** (fills spot, positions futures, dépôts/retraits, Earn) synchronisés automatiquement côté backend, avec persistance Firestore pour dépasser la fenêtre de 3 mois |
| Pages Dashboard / Paires / XPERPS / Données / DCA et leurs KPIs, formules et tooltips | Modèle Firestore **normalisé** (1 doc par fill / position / événement) + métadonnées utilisateur séparées (notes, flag dashboard, planId) |
| Moteur DCA Scaled Mirror (zones, rechargement, signal, timeline) | Moteur métier **unique, typé et testé** (`core`), partagé front/back |
| Design tokens, Space Mono, ergonomie iPad, PWA + mise à jour SW | Devises réelles (USDC/USDT/EUR distinguées), horodatage à la seconde, identifiants OKX en colonnes |
| Export .xlsx, saisie manuelle pour les opérations hors OKX (Ledger, transferts) | Import fichier/Google Sheet → relégué à un import **legacy one-shot** (reprise v1) |
| Cours OKX comme source primaire | **Nouveau volet Earn** (rendement + plus/moins-value marché) |
| GitHub Pages prod/staging | CI (lint/test/build) + CD propre par environnement + versioning SemVer et releases |
