export type Listener<T> = (state: T) => void;

export interface Store<T> {
  get: () => T;
  set: (partial: Partial<T> | ((prev: T) => T)) => void;
  subscribe: (listener: Listener<T>) => () => void;
}

export function createStore<T>(initial: T): Store<T> {
  let state = initial;
  const listeners = new Set<Listener<T>>();

  const get = () => state;
  const set = (partial: Partial<T> | ((prev: T) => T)) => {
    state = typeof partial === 'function' ? (partial as any)(state) : { ...state, ...partial };
    listeners.forEach((l) => l(state));
  };
  const subscribe = (listener: Listener<T>) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };

  return { get, set, subscribe };
}
