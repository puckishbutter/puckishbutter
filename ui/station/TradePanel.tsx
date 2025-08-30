import React from 'react';
import { getActiveContracts } from '../../campaign-sim/Contracts';

export function TradePanel() {
  const active = getActiveContracts()[0];
  function handleBuyHelper() {
    // stub helper
  }
  return (
    <div>
      {active && <button onClick={handleBuyHelper}>buy required cargo</button>}
      TradePanel
    </div>
  );
}
