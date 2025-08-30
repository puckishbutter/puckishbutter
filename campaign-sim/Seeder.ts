import fs from 'fs';
import { worldStore, Fleet, Interactable, Market } from './WorldState';

export function seedTutorialWorld(seed: number) {
  const fleets: Fleet[] = JSON.parse(fs.readFileSync('content/fleets.json', 'utf-8'));
  const interactables: Interactable[] = JSON.parse(fs.readFileSync('content/interactables.json', 'utf-8'));
  const markets: Market[] = JSON.parse(fs.readFileSync('content/markets.json', 'utf-8'));
  worldStore.set({ fleets, interactables, markets });
}
