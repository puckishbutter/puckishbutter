import { describe, test, expect } from 'vitest';
import { shouldHail, scanOutcome } from '../campaign-sim/ScanService';
import { Fleet } from '../campaign-sim/WorldState';

describe('ScanService', () => {
  test('transponder off triggers hail', () => {
    const player: Fleet = { id: 'player', name: 'p', systemId: 'core', pos: { x: 0, y: 0 }, transponderOn: false, suspicion: 0, cargo: {} };
    const patrol: Fleet = { id: 'patrol', name: 'pat', systemId: 'core', pos: { x: 0, y: 100 }, transponderOn: true, suspicion: 0, cargo: {} };
    expect(shouldHail(player, patrol)).toBe(true);
  });

  test('suspicion triggers hail', () => {
    const player: Fleet = { id: 'player', name: 'p', systemId: 'core', pos: { x: 0, y: 0 }, transponderOn: true, suspicion: 1, cargo: {} };
    const patrol: Fleet = { id: 'patrol', name: 'pat', systemId: 'core', pos: { x: 0, y: 100 }, transponderOn: true, suspicion: 0, cargo: {} };
    expect(shouldHail(player, patrol)).toBe(true);
  });

  test('scan outcome clean when no suspicion', () => {
    expect(
      scanOutcome({ playerCargo: {}, suspicion: 0, transponderOn: true })
    ).toBe('clean');
  });
});
