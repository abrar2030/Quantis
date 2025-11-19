import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider as CustomThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Predictions from './pages/Predictions';
import Models from './pages/Models';
import Datasets from './pages/Datasets';
import Login from './pages/Login';
import Register from './pages/Register';
import DatasetUpload from './pages/DatasetUpload';
import ModelManagement from './pages/ModelManagement';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>; // You can replace this with a proper loading component
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirects to dashboard if already authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return !isAuthenticated ? children : <Navigate to="/" replace />;
};

function AppContent() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/predictions" element={<Predictions />} />
                  <Route path="/models" element={<Models />} />
                  <Route path="/model-management" element={<ModelManagement />} />
                  <Route path="/datasets" element={<Datasets />} />
                  <Route path="/dataset-upload" element={<DatasetUpload />} />
                  {/* Redirect any unknown routes to dashboard */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <CustomThemeProvider>
        {(theme) => (
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppContent />
          </ThemeProvider>
        )}
      </CustomThemeProvider>
    </AuthProvider>
  );
}

export default App;
