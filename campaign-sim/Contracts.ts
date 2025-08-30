import { worldStore, WorldState } from './WorldState';

export type Contract = {
  id: string;
  type: 'delivery';
  from: string;
  to: string;
  commodityId: string;
  qty: number;
  payCents: number;
  deadlineDay: number;
  state: 'offered' | 'accepted' | 'completed' | 'failed';
};

let contracts: Contract[] = [];

export function genFirstDelivery(world: WorldState): Contract {
  const contract: Contract = {
    id: 'delivery-1',
    type: 'delivery',
    from: 'core-station',
    to: 'outpost',
    commodityId: 'food',
    qty: 80,
    payCents: 6000,
    deadlineDay: 20,
    state: 'offered',
  };
  contracts.push(contract);
  return contract;
}

export function acceptContract(id: string): void {
  const c = contracts.find((c) => c.id === id);
  if (c) c.state = 'accepted';
}

export function completeDelivery(id: string): { paidCents: number } | 'notReady' {
  const c = contracts.find((c) => c.id === id && c.state === 'accepted');
  if (!c) return 'notReady';
  const world = worldStore.get();
  const player = world.fleets.find((f) => f.id === 'player');
  if (!player) return 'notReady';
  const cargoQty = player.cargo[c.commodityId] || 0;
  if (cargoQty < c.qty) return 'notReady';
  player.cargo[c.commodityId] = cargoQty - c.qty;
  player.credits = (player.credits || 0) + c.payCents;
  c.state = 'completed';
  worldStore.set(world);
  return { paidCents: c.payCents };
}

export function getActiveContracts(): Contract[] {
  return contracts.filter((c) => c.state === 'accepted');
}

export function _resetContracts() {
  contracts = [];
}

export function _getContracts(): Contract[] {
  return contracts;
}

export function _setContracts(cs: Contract[]) {
  contracts = cs;
}
