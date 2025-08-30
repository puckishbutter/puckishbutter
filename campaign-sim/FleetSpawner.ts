import { Fleet, worldStore } from './WorldState';

export function spawnPatrol(systemId: string): Fleet {
  const patrol: Fleet = {
    id: `patrol-${Date.now()}`,
    name: 'Patrol',
    systemId,
    pos: { x: 0, y: 0 },
    transponderOn: true,
    suspicion: 0,
    cargo: {},
    route: [
      { x: 0, y: 0 },
      { x: 100, y: 0 }
    ],
    routeIndex: 0,
  };
  worldStore.set((w) => ({ ...w, fleets: [...w.fleets, patrol] }));
  return patrol;
}
