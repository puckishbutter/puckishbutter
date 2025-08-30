import React, { useEffect, useState } from 'react';
import { worldStore } from '../../campaign-sim/WorldState';

export function StatusCluster() {
  const [credits, setCredits] = useState(0);
  const [fuel, setFuel] = useState(0);
  const [supplies, setSupplies] = useState(0);
  useEffect(() => {
    return worldStore.subscribe((w) => {
      const player = w.fleets.find((f) => f.id === 'player');
      if (player) {
        setCredits(player.credits || 0);
        setFuel(player.cargo['fuel'] || 0);
        setSupplies(player.cargo['supplies'] || 0);
      }
    });
  }, []);
  return (
    <div className="status-cluster">
      credits {credits} | fuel {fuel} | supplies {supplies}
    </div>
  );
}
