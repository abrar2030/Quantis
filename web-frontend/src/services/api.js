"""
API service for handling all backend communication
"""
import axios from 'axios';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    const apiKey = localStorage.getItem('apiKey');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else if (apiKey) {
      config.headers['X-API-Key'] = apiKey;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Clear authentication and redirect to login
      localStorage.removeItem('authToken');
      localStorage.removeItem('apiKey');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },
  
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },
  
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
  
  refreshToken: async () => {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// Users API
export const usersAPI = {
  getUsers: async (params = {}) => {
    const response = await apiClient.get('/users', { params });
    return response.data;
  },
  
  getUser: async (userId) => {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  },
  
  updateUser: async (userId, userData) => {
    const response = await apiClient.put(`/users/${userId}`, userData);
    return response.data;
  },
  
  deleteUser: async (userId) => {
    const response = await apiClient.delete(`/users/${userId}`);
    return response.data;
  },
  
  createApiKey: async (keyData) => {
    const response = await apiClient.post('/users/api-keys', keyData);
    return response.data;
  },
  
  getApiKeys: async () => {
    const response = await apiClient.get('/users/api-keys');
    return response.data;
  },
  
  revokeApiKey: async (keyId) => {
    const response = await apiClient.delete(`/users/api-keys/${keyId}`);
    return response.data;
  },
};

// Datasets API
export const datasetsAPI = {
  getDatasets: async (params = {}) => {
    const response = await apiClient.get('/datasets', { params });
    return response.data;
  },
  
  getDataset: async (datasetId) => {
    const response = await apiClient.get(`/datasets/${datasetId}`);
    return response.data;
  },
  
  uploadDataset: async (formData, onUploadProgress) => {
    const response = await apiClient.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },
  
  updateDataset: async (datasetId, datasetData) => {
    const response = await apiClient.put(`/datasets/${datasetId}`, datasetData);
    return response.data;
  },
  
  deleteDataset: async (datasetId) => {
    const response = await apiClient.delete(`/datasets/${datasetId}`);
    return response.data;
  },
  
  getDatasetPreview: async (datasetId, rows = 10) => {
    const response = await apiClient.get(`/datasets/${datasetId}/preview`, {
      params: { rows },
    });
    return response.data;
  },
};

// Models API
export const modelsAPI = {
  getModels: async (params = {}) => {
    const response = await apiClient.get('/models', { params });
    return response.data;
  },
  
  getModel: async (modelId) => {
    const response = await apiClient.get(`/models/${modelId}`);
    return response.data;
  },
  
  createModel: async (modelData) => {
    const response = await apiClient.post('/models', modelData);
    return response.data;
  },
  
  updateModel: async (modelId, modelData) => {
    const response = await apiClient.put(`/models/${modelId}`, modelData);
    return response.data;
  },
  
  deleteModel: async (modelId) => {
    const response = await apiClient.delete(`/models/${modelId}`);
    return response.data;
  },
  
  trainModel: async (modelId) => {
    const response = await apiClient.post(`/models/${modelId}/train`);
    return response.data;
  },
  
  getModelMetrics: async (modelId) => {
    const response = await apiClient.get(`/models/${modelId}/metrics`);
    return response.data;
  },
};

// Predictions API
export const predictionsAPI = {
  getPredictions: async (params = {}) => {
    const response = await apiClient.get('/predictions', { params });
    return response.data;
  },
  
  getPrediction: async (predictionId) => {
    const response = await apiClient.get(`/predictions/${predictionId}`);
    return response.data;
  },
  
  createPrediction: async (predictionData) => {
    const response = await apiClient.post('/predictions', predictionData);
    return response.data;
  },
  
  batchPredict: async (batchData) => {
    const response = await apiClient.post('/predictions/batch', batchData);
    return response.data;
  },
  
  getPredictionStats: async (params = {}) => {
    const response = await apiClient.get('/predictions/stats', { params });
    return response.data;
  },
};

// Monitoring API
export const monitoringAPI = {
  getHealthStatus: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
  
  getMetrics: async () => {
    const response = await apiClient.get('/metrics');
    return response.data;
  },
  
  getSystemMetrics: async () => {
    const response = await apiClient.get('/monitoring/system');
    return response.data;
  },
  
  getDatabaseMetrics: async () => {
    const response = await apiClient.get('/monitoring/database');
    return response.data;
  },
  
  getPerformanceSummary: async (hours = 24) => {
    const response = await apiClient.get('/monitoring/performance', {
      params: { hours },
    });
    return response.data;
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async (params = {}) => {
    const response = await apiClient.get('/notifications', { params });
    return response.data;
  },
  
  markAsRead: async (notificationId) => {
    const response = await apiClient.put(`/notifications/${notificationId}/read`);
    return response.data;
  },
  
  markAllAsRead: async () => {
    const response = await apiClient.put('/notifications/read-all');
    return response.data;
  },
  
  deleteNotification: async (notificationId) => {
    const response = await apiClient.delete(`/notifications/${notificationId}`);
    return response.data;
  },
  
  getNotificationStats: async () => {
    const response = await apiClient.get('/notifications/stats');
    return response.data;
  },
};

// Error handling utility
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    return {
      status,
      message: data.message || data.detail || 'An error occurred',
      details: data.details || null,
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      status: 0,
      message: 'Network error - please check your connection',
      details: null,
    };
  } else {
    // Something else happened
    return {
      status: 0,
      message: error.message || 'An unexpected error occurred',
      details: null,
    };
  }
};

// Utility functions
export const setAuthToken = (token) => {
  localStorage.setItem('authToken', token);
};

export const setApiKey = (apiKey) => {
  localStorage.setItem('apiKey', apiKey);
};

export const clearAuth = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('apiKey');
  localStorage.removeItem('user');
};

export const isAuthenticated = () => {
  return !!(localStorage.getItem('authToken') || localStorage.getItem('apiKey'));
};

export default apiClient;

