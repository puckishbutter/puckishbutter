import { createStore } from '../shared/store';
import { nowDay } from '../shared/time';

export interface Snapshot {
  time: number;
}

const store = createStore<Snapshot>({ time: nowDay() });

let interval: ReturnType<typeof setInterval> | undefined;
const snapshotListeners = new Set<(s: Snapshot) => void>();

function tick() {
  store.set({ time: nowDay() });
  const snap = store.get();
  snapshotListeners.forEach((cb) => cb(snap));
}

export function start() {
  if (interval) return;
  interval = setInterval(tick, 100); // ~10Hz
}

export function stop() {
  if (interval) {
    clearInterval(interval);
    interval = undefined;
  }
}

export function subscribeSnapshot(cb: (s: Snapshot) => void) {
  snapshotListeners.add(cb);
  return () => snapshotListeners.delete(cb);
}
