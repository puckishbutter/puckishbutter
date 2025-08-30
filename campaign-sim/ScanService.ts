import { Cargo, Fleet } from './WorldState';

export function shouldHail(player: Fleet, patrol: Fleet): boolean {
  const dx = player.pos.x - patrol.pos.x;
  const dy = player.pos.y - patrol.pos.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist > 800) return false;
  return !player.transponderOn || player.suspicion > 0;
}

export function scanOutcome({
  playerCargo,
  suspicion,
  transponderOn,
}: {
  playerCargo: Cargo;
  suspicion: number;
  transponderOn: boolean;
}): 'clean' | 'warn' | 'fine' {
  if (suspicion > 0) return 'warn';
  if (!transponderOn) return 'warn';
  return 'clean';
}
