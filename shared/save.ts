import { worldStore, WorldState } from '../campaign-sim/WorldState';
import { Contract, _getContracts, _setContracts } from '../campaign-sim/Contracts';

export type SaveBlobV1 = {
  world: WorldState;
  contracts: Contract[];
  suspicion: number;
  playerId: string;
  version: 1;
};

const slots = new Map<string, SaveBlobV1>();
let suspicion = 0;

export function setSuspicion(v: number) {
  suspicion = v;
}

export function getSuspicion() {
  return suspicion;
}

export async function save(slot: string): Promise<void> {
  const blob: SaveBlobV1 = {
    world: JSON.parse(JSON.stringify(worldStore.get())),
    contracts: JSON.parse(JSON.stringify(_getContracts())),
    suspicion,
    playerId: 'player',
    version: 1,
  };
  slots.set(slot, blob);
}

export async function load(slot: string): Promise<void> {
  const blob = slots.get(slot);
  if (!blob) throw new Error('no save');
  worldStore.set(blob.world);
  _setContracts(blob.contracts);
  suspicion = blob.suspicion;
}
