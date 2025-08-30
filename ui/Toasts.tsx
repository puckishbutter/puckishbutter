import React, { useEffect, useState } from 'react';
import { subscribe } from '../shared/events';

export function Toasts() {
  const [messages, setMessages] = useState<string[]>([]);
  useEffect(() => {
    return subscribe((e) => {
      if (e.type === 'TOAST') {
        setMessages((m) => [...m, e.message]);
        setTimeout(() => {
          setMessages((m) => m.slice(1));
        }, 2000);
      }
    });
  }, []);
  return (
    <div className="toasts">
      {messages.map((m, i) => (
        <div key={i}>{m}</div>
      ))}
    </div>
  );
}
