import { describe, test, expect, beforeEach } from 'vitest';
import { genFirstDelivery, acceptContract, completeDelivery, getActiveContracts, _resetContracts } from '../campaign-sim/Contracts';
import { worldStore, Fleet } from '../campaign-sim/WorldState';

describe('Contracts', () => {
  beforeEach(() => {
    _resetContracts();
    const player: Fleet = {
      id: 'player',
      name: 'Player',
      systemId: 'core',
      pos: { x: 0, y: 0 },
      transponderOn: true,
      suspicion: 0,
      cargo: { food: 80 },
      credits: 0,
    };
    worldStore.set({ fleets: [player], interactables: [], markets: [] });
  });

  test('accept shows active', () => {
    const c = genFirstDelivery(worldStore.get());
    acceptContract(c.id);
    expect(getActiveContracts().length).toBe(1);
  });

  test('completion requires cargo and pays', () => {
    const c = genFirstDelivery(worldStore.get());
    acceptContract(c.id);
    const world = worldStore.get();
    const player = world.fleets[0];
    player.cargo.food = 40;
    expect(completeDelivery(c.id)).toBe('notReady');
    player.cargo.food = 80;
    worldStore.set(world);
    expect(completeDelivery(c.id)).toEqual({ paidCents: 6000 });
    expect(player.cargo.food).toBe(0);
    expect(player.credits).toBe(6000);
  });
});
