import { describe, expect, it } from 'vitest';
import { mulberry32 } from '../shared/rng';

describe('mulberry32', () => {
  it('produces deterministic sequence', () => {
    const rngA = mulberry32(1);
    const rngB = mulberry32(1);
    const seqA = [rngA(), rngA(), rngA()];
    const seqB = [rngB(), rngB(), rngB()];
    expect(seqA).toEqual(seqB);
  });
});
