import React from 'react';
import { dispatch } from '../shared/events';

export function IntelRail() {
  return (
    <div className="intel-rail" onClick={() => dispatch({ type: 'OPEN_INTEL' })}>
      Intel
    </div>
  );
}
