import { worldStore, Fleet } from './WorldState';
import { shouldHail } from './ScanService';

const HAIL_RADIUS = 800;

export function tickWorld(dtDays: number) {
  const world = worldStore.get();
  const player = world.fleets.find((f) => f.id === 'player');
  if (!player) return { hailed: false };

  const updatedFleets = world.fleets.map((f) => {
    if (f.route && f.route.length > 1) {
      const nextIndex = f.routeIndex === 0 ? 1 : 0;
      f.pos = { ...f.route[nextIndex] };
      f.routeIndex = nextIndex;
    }
    return f;
  });

  let hailed = false;
  updatedFleets.forEach((f) => {
    if (f.id !== player.id && !f.hailed) {
      const dx = player.pos.x - f.pos.x;
      const dy = player.pos.y - f.pos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist <= HAIL_RADIUS && shouldHail(player, f)) {
        f.hailed = true;
        hailed = true;
      }
    }
  });

  worldStore.set({ ...world, fleets: updatedFleets });
  return { hailed };
}
