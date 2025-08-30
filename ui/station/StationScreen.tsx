import React from 'react';
import { TradePanel } from './TradePanel';
import { BarPanel } from './BarPanel';

export function StationScreen() {
  return (
    <div>
      <div>Tabs: Trade | Refuel/Repair | Bar</div>
      <TradePanel />
      <BarPanel />
    </div>
  );
}
