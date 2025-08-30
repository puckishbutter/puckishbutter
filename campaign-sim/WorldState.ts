import { createStore } from '../shared/store';

export interface Cargo {
  [commodityId: string]: number;
}

export interface Fleet {
  id: string;
  name: string;
  systemId: string;
  pos: { x: number; y: number };
  transponderOn: boolean;
  suspicion: number;
  cargo: Cargo;
  credits?: number;
  route?: { x: number; y: number }[];
  routeIndex?: number;
  hailed?: boolean;
}

export interface Interactable {
  id: string;
  type: string;
  position: { x: number; y: number };
}

export interface Market {
  id: string;
  name: string;
  stocks: Record<string, number>;
  prices: Record<string, number>;
  tariffRate: number;
  stability: number;
}

export interface WorldState {
  fleets: Fleet[];
  interactables: Interactable[];
  markets: Market[];
}

export const worldStore = createStore<WorldState>({
  fleets: [],
  interactables: [],
  markets: [],
});
