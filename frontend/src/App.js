import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Dashboard from './pages/Dashboard';
import Predictions from './pages/Predictions';
import ModelMetrics from './pages/ModelMetrics';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="metrics" element={<ModelMetrics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
