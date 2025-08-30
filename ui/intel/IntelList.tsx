import React from 'react';
import { getActiveContracts } from '../../campaign-sim/Contracts';
import { dispatch } from '../../shared/events';

export function IntelList() {
  const active = getActiveContracts();
  return (
    <div>
      {active.map((c) => (
        <div key={c.id}>
          Delivery to {c.to}
          <button onClick={() => dispatch({ type: 'SET_COURSE', dest: { x: 0, y: 0, systemId: c.to } })}>
            set course
          </button>
        </div>
      ))}
    </div>
  );
}
