import React from 'react';

export function HailDialog({ outcome, onClose }: { outcome: 'clean' | 'warn' | 'fine'; onClose: () => void }) {
  return (
    <div className="hail-dialog">
      <div>Scan result: {outcome}</div>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
