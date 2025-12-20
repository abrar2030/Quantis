import React from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
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
    return <div>Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return !isAuthenticated ? children : <Navigate to="/" replace />;
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
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
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/predictions"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Predictions />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/models"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Models />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/model-management"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ModelManagement />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/datasets"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Datasets />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dataset-upload"
              element={
                <ProtectedRoute>
                  <Layout>
                    <DatasetUpload />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
