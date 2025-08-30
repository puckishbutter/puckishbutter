import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { start, stop, subscribeSnapshot } from '../engine';

function Hud() {
  return <div className="hud">HUD Placeholder</div>;
}

function MapView() {
  return <div className="map">Map Placeholder</div>;
}

export function App() {
  useEffect(() => {
    start();
    return () => stop();
  }, []);

  useEffect(() => {
    const unsub = subscribeSnapshot((snap) => {
      console.log('snapshot', snap);
    });
    return () => unsub();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MapView />} />
      </Routes>
      <Hud />
    </BrowserRouter>
  );
}
