import React from 'react';
import { genFirstDelivery, acceptContract } from '../../campaign-sim/Contracts';
import { worldStore } from '../../campaign-sim/WorldState';

let offered = false;
let contractId: string | null = null;

export function BarPanel() {
  const world = worldStore.get();
  if (!offered) {
    const c = genFirstDelivery(world);
    contractId = c.id;
    offered = true;
  }
  return (
    <div>
      <div>Delivery available</div>
      <button onClick={() => contractId && acceptContract(contractId)}>accept</button>
    </div>
  );
}
