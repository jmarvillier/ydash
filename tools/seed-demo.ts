/**
 * Jeu de données de démo pour les émulateurs Firebase (ticket D10).
 *
 *   npm run seed            (émulateurs lancés : npm run dev)
 *   npm run seed -- --env prod   → écrit sous ydash_v2 au lieu de ydash_v2_stg
 *
 * Données fictives et déterministes (aucune donnée réelle de compte). Le schéma est PROVISOIRE :
 * il sera aligné sur le modèle Firestore v2 du ticket C04, puis enrichi pour couvrir tous les cas
 * des tests de parité (C05).
 */
import { initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore, type WriteBatch } from 'firebase-admin/firestore';

const PROJECT_ID = process.env.GCLOUD_PROJECT ?? 'demo-ydash';
const env = process.argv.includes('--env') && process.argv.includes('prod') ? 'prod' : 'stg';
const ROOT = env === 'prod' ? 'ydash_v2' : 'ydash_v2_stg';

// Garde-fous : uniquement contre les émulateurs, uniquement sur un projet « demo-* ».
process.env.FIRESTORE_EMULATOR_HOST ??= '127.0.0.1:8080';
process.env.FIREBASE_AUTH_EMULATOR_HOST ??= '127.0.0.1:9099';
if (!PROJECT_ID.startsWith('demo-')) {
  throw new Error(`Refus : le seed ne s'exécute que sur un projet demo-* (reçu ${PROJECT_ID})`);
}

const DEMO_USER = {
  uid: 'demo-user',
  email: 'demo@ydash.local',
  password: 'ydash-demo',
  displayName: 'Démo Ydash',
};

/** Générateur pseudo-aléatoire déterministe (mulberry32). */
function rng(seed: number) {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand = rng(42);
const DAY = 86_400_000;
const START = Date.UTC(2026, 3, 1); // 1er avril 2026
const round = (v: number, d = 2) => Math.round(v * 10 ** d) / 10 ** d;

const PAIRS = [
  { instId: 'BTC-USDC', price: 84_000, drift: 0.0012, vol: 0.025, size: 0.004 },
  { instId: 'ETH-USDC', price: 1_900, drift: 0.0018, vol: 0.035, size: 0.15 },
  { instId: 'SOL-USDC', price: 130, drift: 0.0005, vol: 0.045, size: 2 },
];

function* fills() {
  let n = 0;
  for (const pair of PAIRS) {
    let price = pair.price;
    for (let day = 0; day < 210; day += 1) {
      price *= 1 + pair.drift + (rand() - 0.5) * pair.vol;
      if (rand() > 0.12) continue; // ~1 opération tous les 8 jours par paire
      const side = rand() > 0.3 ? 'buy' : 'sell';
      const sz = round(pair.size * (0.5 + rand()), 6);
      const ts = START + day * DAY + Math.floor(rand() * DAY);
      n += 1;
      yield {
        id: `demo-fill-${n}`,
        instType: 'SPOT',
        instId: pair.instId,
        side,
        ordId: `demo-ord-${n}`,
        tradeId: `demo-trade-${n}`,
        fillPx: round(price, 2),
        fillSz: sz,
        quoteCcy: 'USDC',
        quoteAmt: round(price * sz, 2),
        fee: round(price * sz * 0.001, 4),
        feeCcy: 'USDC',
        ts,
        source: 'demo',
      };
    }
  }
}

const transfers = [
  { id: 'demo-dep-1', type: 'deposit', ccy: 'EUR', amt: 5_000, amtUsd: 5_420, ts: START - 2 * DAY },
  {
    id: 'demo-dep-2',
    type: 'deposit',
    ccy: 'USDC',
    amt: 3_000,
    amtUsd: 3_000,
    ts: START + 60 * DAY,
  },
  {
    id: 'demo-dep-3',
    type: 'deposit',
    ccy: 'EUR',
    amt: 2_000,
    amtUsd: 2_330,
    ts: START + 120 * DAY,
  },
  {
    id: 'demo-wd-1',
    type: 'withdrawal',
    ccy: 'USDC',
    amt: 500,
    amtUsd: 500,
    ts: START + 150 * DAY,
  },
];

function* xperps() {
  for (let i = 1; i <= 24; i += 1) {
    const side = rand() > 0.45 ? 'long' : 'short';
    const r = round((rand() - 0.42) * 4, 2); // espérance légèrement positive
    const risk = 25;
    const closeTimeMs = START + Math.floor(rand() * 200) * DAY + Math.floor(rand() * DAY);
    yield {
      id: `demo-pos-${i}`,
      instId: ['BTC-USDC-SWAP', 'ETH-USDC-SWAP', 'SOL-USDC-SWAP'][i % 3],
      side,
      riskModel: i % 5 === 0 ? 'fixed' : 'stop',
      riskUsd: risk,
      rMultiple: r,
      netPnlUsd: round(r * risk, 2),
      result: r > 0.05 ? 'win' : r < -0.05 ? 'loss' : 'be',
      closeTimeMs,
    };
  }
}

const earnPositions = [
  {
    id: 'demo-earn-usdc',
    product: 'simple-earn-flexible',
    ccy: 'USDC',
    amt: 1_500,
    apr: 0.05,
    since: START + 30 * DAY,
    entryPx: 1,
  },
  {
    id: 'demo-earn-lyusdc',
    product: 'defi-lyusdc',
    ccy: 'USDC',
    amt: 800,
    apr: 0.082,
    since: START + 90 * DAY,
    entryPx: 1,
  },
  {
    id: 'demo-earn-oksol',
    product: 'staking-oksol',
    ccy: 'SOL',
    amt: 6,
    apr: 0.071,
    since: START + 45 * DAY,
    entryPx: 142.3,
  },
];

const dcaPlan = {
  id: 'demo-dca-btc',
  pair: 'BTC/USDC',
  startDate: START,
  endDate: null,
  baseAmount: 100,
  frequency: 'week',
  debtCeiling: 600,
  zones: [
    { type: 'accum', label: 'Accumulation forte', ecart: -15, action: 2, color: '#2e7d32' },
    { type: 'accum', label: 'Accumulation', ecart: -5, action: 1.5, color: '#66bb6a' },
    { type: 'ralent', label: 'Ralentissement', ecart: 10, action: 0.5, color: '#fbc02d' },
    { type: 'profit', label: 'Prise de profit', ecart: 25, action: 20, color: '#d32f2f' },
  ],
};

async function writeAll(
  name: string,
  docs: Iterable<{ id: string }>,
  base: FirebaseFirestore.DocumentReference,
) {
  const db = base.firestore;
  let batch: WriteBatch = db.batch();
  let count = 0;
  for (const { id, ...data } of docs) {
    batch.set(base.collection(name).doc(id), { ...data, _demo: true });
    count += 1;
    if (count % 400 === 0) {
      await batch.commit();
      batch = db.batch();
    }
  }
  await batch.commit();
  console.info(`  ${name.padEnd(16)} ${count}`);
}

async function main() {
  initializeApp({ projectId: PROJECT_ID });
  const auth = getAuth();
  const db = getFirestore();

  await auth.deleteUser(DEMO_USER.uid).catch(() => undefined);
  await auth.createUser(DEMO_USER);
  console.info(`Utilisateur ${DEMO_USER.email} / ${DEMO_USER.password} (uid ${DEMO_USER.uid})`);

  const userDoc = db.collection(ROOT).doc(DEMO_USER.uid);
  await db.recursiveDelete(userDoc);
  await userDoc.set({
    schemaVersion: 0,
    refCurrency: 'USD',
    okx: { status: 'mock', keyLast4: 'demo', perm: 'read_only' },
    _demo: true,
  });

  console.info(`Écriture sous ${ROOT}/${DEMO_USER.uid} :`);
  await writeAll('fills', fills(), userDoc);
  await writeAll('transfers', transfers, userDoc);
  await writeAll('xperps', xperps(), userDoc);
  await writeAll('earn_positions', earnPositions, userDoc);
  await writeAll('dca_plans', [dcaPlan], userDoc);
  console.info('✓ Seed terminé — Emulator UI : http://127.0.0.1:4000');
}

main().catch((err: unknown) => {
  console.error(err);
  process.exit(1);
});
