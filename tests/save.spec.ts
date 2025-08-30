import { describe, test, expect } from 'vitest';
import { save, load, setSuspicion, getSuspicion } from '../shared/save';
import { worldStore, Fleet } from '../campaign-sim/WorldState';
import { genFirstDelivery, acceptContract, getActiveContracts, _resetContracts } from '../campaign-sim/Contracts';

describe('save/load', () => {
  test('save and load preserve world and contracts', async () => {
    _resetContracts();
    const player: Fleet = {
      id: 'player',
      name: 'Player',
      systemId: 'core',
      pos: { x: 0, y: 0 },
      transponderOn: true,
      suspicion: 0,
      cargo: { food: 80 },
      credits: 123,
    };
    worldStore.set({ fleets: [player], interactables: [], markets: [] });
    const c = genFirstDelivery(worldStore.get());
    acceptContract(c.id);
    setSuspicion(2);
    await save('s1');

    player.credits = 0;
    worldStore.set({ fleets: [player], interactables: [], markets: [] });
    _resetContracts();
    setSuspicion(0);

    await load('s1');
    const w = worldStore.get();
    expect(w.fleets[0].credits).toBe(123);
    expect(getActiveContracts().length).toBe(1);
    expect(getSuspicion()).toBe(2);
  });
});
