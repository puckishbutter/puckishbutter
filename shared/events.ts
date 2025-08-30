export type Event =
  | { type: 'TOAST'; message: string }
  | { type: 'OPEN_INTEL' }
  | { type: 'SET_COURSE'; dest: { x: number; y: number; systemId: string } };

const listeners = new Set<(e: Event) => void>();

export function dispatch(e: Event) {
  listeners.forEach((l) => l(e));
}

export function subscribe(listener: (e: Event) => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
