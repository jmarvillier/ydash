/**
 * Utilitaires numériques purs partagés par le front et le backend.
 * Le moteur métier (agrégation, breakeven, PnL…) arrivera avec le ticket C05.
 */

/** Arrondi décimal sûr (évite 1.005 → 1.00). */
export function round(value: number, decimals = 2): number {
  if (!Number.isFinite(value)) return value;
  const factor = 10 ** decimals;
  return Math.round((value + Number.EPSILON) * factor) / factor;
}

/**
 * Variation relative en % de `from` vers `to`.
 * Retourne `null` si la base est nulle ou si une valeur n'est pas finie.
 */
export function pctChange(from: number, to: number): number | null {
  if (!Number.isFinite(from) || !Number.isFinite(to) || from === 0) return null;
  return ((to - from) / Math.abs(from)) * 100;
}
