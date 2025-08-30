import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { start, stop, subscribeSnapshot } from '../engine';
import { MapScreen } from './map/MapScreen';
import { Toasts } from './Toasts';
import { IntelRail } from './IntelRail';
import { CourseWidget } from './hud/CourseWidget';
import { StatusCluster } from './hud/StatusCluster';

function Hud() {
  return (
    <div className="hud">
      <StatusCluster />
      <CourseWidget />
      <IntelRail />
      <Toasts />
    </div>
  );
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
        <Route path="/" element={<MapScreen />} />
      </Routes>
      <Hud />
    </BrowserRouter>
  );
}
