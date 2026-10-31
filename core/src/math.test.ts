import { describe, expect, it } from 'vitest';
import { pctChange, round } from './math';

describe('round', () => {
  it('arrondit à 2 décimales par défaut', () => {
    expect(round(1.005)).toBe(1.01);
    expect(round(2.344)).toBe(2.34);
  });

  it('respecte le nombre de décimales demandé', () => {
    expect(round(0.123456, 4)).toBe(0.1235);
    expect(round(1234.5, 0)).toBe(1235);
  });

  it('laisse passer les valeurs non finies', () => {
    expect(round(Number.POSITIVE_INFINITY)).toBe(Number.POSITIVE_INFINITY);
    expect(round(Number.NaN)).toBeNaN();
  });
});

describe('pctChange', () => {
  it('calcule une hausse et une baisse', () => {
    expect(pctChange(100, 110)).toBeCloseTo(10);
    expect(pctChange(200, 150)).toBeCloseTo(-25);
  });

  it('utilise la valeur absolue de la base', () => {
    expect(pctChange(-100, -50)).toBeCloseTo(50);
  });

  it('retourne null sur une base nulle ou non finie', () => {
    expect(pctChange(0, 10)).toBeNull();
    expect(pctChange(Number.NaN, 10)).toBeNull();
  });
});
