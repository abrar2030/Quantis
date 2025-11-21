# Frontend Documentation

This document provides comprehensive information about the frontend application of the Quantis time series forecasting platform, including its architecture, components, and development guidelines.

## Overview

The Quantis frontend is a modern, responsive web application built with React. It provides an intuitive user interface for interacting with the time series forecasting platform, visualizing data and predictions, and managing models.

## Architecture

### Technology Stack

The frontend application is built using the following technologies:

- **React**: A JavaScript library for building user interfaces
- **Context API**: For state management across components
- **React Router**: For navigation and routing
- **Chart.js**: For data visualization
- **Axios**: For API communication
- **CSS Modules**: For component-scoped styling

### Directory Structure

The frontend codebase follows a structured organization:

```
frontend/
├── public/             # Static assets and HTML template
│   ├── assets/         # Images, icons, and other static files
│   ├── index.html      # HTML template
│   └── manifest.json   # Web app manifest
├── src/                # Source code
│   ├── components/     # Reusable UI components
│   │   ├── charts/     # Chart components
│   │   └── ...         # Other component categories
│   ├── context/        # React context providers
│   ├── hooks/          # Custom React hooks
│   ├── pages/          # Application pages
│   ├── services/       # API service integrations
│   ├── styles/         # Global styles and themes
│   ├── utils/          # Utility functions
│   ├── App.js          # Main application component
│   └── index.js        # Application entry point
├── .env                # Environment variables
├── package.json        # Dependencies and scripts
└── nginx.conf          # Nginx configuration for production
```

### Component Architecture

The frontend follows a component-based architecture:

1. **Pages**: Top-level components representing entire screens
2. **Layout Components**: Structure the overall page layout
3. **Feature Components**: Implement specific features or sections
4. **Base Components**: Reusable UI elements like buttons, inputs, etc.

### State Management

State management is handled through:

1. **React Context**: For global state shared across components
2. **Component State**: For local state within components
3. **Custom Hooks**: For reusable stateful logic

## Key Components

### Layout Components

#### Header

The Header component provides navigation and user account functions:

```jsx
// Header.js
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import styles from './Header.module.css';

const Header = () => {
  const { theme, toggleTheme } = useContext(ThemeContext);

  return (
    <header className={`${styles.header} ${styles[theme]}`}>
      <div className={styles.logo}>
        <Link to="/">Quantis</Link>
      </div>
      <nav className={styles.navigation}>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/predictions">Predictions</Link>
        <Link to="/model-metrics">Model Metrics</Link>
        <Link to="/settings">Settings</Link>
      </nav>
      <div className={styles.userControls}>
        <button onClick={toggleTheme}>
          {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
        </button>
        <div className={styles.userProfile}>
          <span>User Name</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
```

#### Sidebar

The Sidebar provides secondary navigation and context-specific options:

```jsx
// Sidebar.js
import React from 'react';
import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

const Sidebar = ({ items }) => {
  return (
    <aside className={styles.sidebar}>
      <nav className={styles.sidebarNav}>
        {items.map((item, index) => (
          <NavLink
            key={index}
            to={item.path}
            className={({ isActive }) =>
              isActive ? styles.activeLink : styles.link
            }
          >
            {item.icon && <span className={styles.icon}>{item.icon}</span>}
            <span className={styles.label}>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
```

### Page Components

#### Dashboard

The Dashboard page displays an overview of forecasting projects and key metrics:

```jsx
// Dashboard.js
import React, { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';
import { fetchDashboardData } from '../services/api';
import styles from './Dashboard.module.css';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchDashboardData();
        setDashboardData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error loading dashboard: {error}</div>;

  return (
    <Layout title="Dashboard">
      <div className={styles.statsContainer}>
        <StatCard
          title="Active Models"
          value={dashboardData.activeModels}
          trend={dashboardData.modelTrend}
        />
        <StatCard
          title="Predictions Today"
          value={dashboardData.predictionsToday}
          trend={dashboardData.predictionsTrend}
        />
        <StatCard
          title="Avg. Accuracy"
          value={`${dashboardData.avgAccuracy}%`}
          trend={dashboardData.accuracyTrend}
        />
        <StatCard
          title="Data Points"
          value={dashboardData.dataPoints}
          trend={dashboardData.dataPointsTrend}
        />
      </div>

      <div className={styles.chartsContainer}>
        <div className={styles.chartCard}>
          <h3>Recent Forecast Performance</h3>
          <LineChart data={dashboardData.forecastPerformance} />
        </div>
        <div className={styles.chartCard}>
          <h3>Model Accuracy Comparison</h3>
          <BarChart data={dashboardData.modelComparison} />
        </div>
      </div>

      <div className={styles.recentActivity}>
        <h3>Recent Activity</h3>
        <ul className={styles.activityList}>
          {dashboardData.recentActivity.map((activity, index) => (
            <li key={index} className={styles.activityItem}>
              <span className={styles.activityTime}>{activity.time}</span>
              <span className={styles.activityDescription}>
                {activity.description}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </Layout>
  );
};

export default Dashboard;
```

#### Predictions

The Predictions page allows users to create and manage forecasts:

```jsx
// Predictions.js
import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { fetchPredictions, createPrediction } from '../services/api';
import styles from './Predictions.module.css';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    datasetId: '',
    forecastHorizon: 7,
    modelId: 'default',
  });

  useEffect(() => {
    const loadPredictions = async () => {
      try {
        const data = await fetchPredictions();
        setPredictions(data);
        setLoading(false);
      } catch (error) {
        console.error('Error loading predictions:', error);
        setLoading(false);
      }
    };

    loadPredictions();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const newPrediction = await createPrediction(formData);
      setPredictions([newPrediction, ...predictions]);
    } catch (error) {
      console.error('Error creating prediction:', error);
    }
  };

  return (
    <Layout title="Predictions">
      <div className={styles.container}>
        <div className={styles.formContainer}>
          <h2>Create New Prediction</h2>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label htmlFor="datasetId">Dataset</label>
              <select
                id="datasetId"
                name="datasetId"
                value={formData.datasetId}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a dataset</option>
                <option value="1">Sales Data</option>
                <option value="2">Website Traffic</option>
                <option value="3">Energy Consumption</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="forecastHorizon">Forecast Horizon (Days)</label>
              <input
                type="number"
                id="forecastHorizon"
                name="forecastHorizon"
                min="1"
                max="365"
                value={formData.forecastHorizon}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="modelId">Model</label>
              <select
                id="modelId"
                name="modelId"
                value={formData.modelId}
                onChange={handleInputChange}
                required
              >
                <option value="default">Default (TFT)</option>
                <option value="prophet">Prophet</option>
                <option value="arima">ARIMA</option>
                <option value="xgboost">XGBoost</option>
              </select>
            </div>

            <button type="submit" className={styles.submitButton}>
              Generate Forecast
            </button>
          </form>
        </div>

        <div className={styles.predictionsContainer}>
          <h2>Recent Predictions</h2>
          {loading ? (
            <p>Loading predictions...</p>
          ) : predictions.length > 0 ? (
            <ul className={styles.predictionsList}>
              {predictions.map((prediction) => (
                <li key={prediction.id} className={styles.predictionItem}>
                  <div className={styles.predictionHeader}>
                    <h3>{prediction.datasetName}</h3>
                    <span className={styles.predictionDate}>
                      {new Date(prediction.createdAt).toLocaleString()}
                    </span>
                  </div>
                  <div className={styles.predictionDetails}>
                    <p>Model: {prediction.modelName}</p>
                    <p>Horizon: {prediction.forecastHorizon} days</p>
                    <p>Accuracy: {prediction.accuracy}%</p>
                  </div>
                  <div className={styles.predictionActions}>
                    <button className={styles.viewButton}>View Details</button>
                    <button className={styles.exportButton}>Export</button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p>No predictions found. Create your first prediction!</p>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Predictions;
```

### Chart Components

#### LineChart

The LineChart component visualizes time series data:

```jsx
// LineChart.js
import React, { useRef, useEffect } from 'react';
import Chart from 'chart.js/auto';
import styles from './LineChart.module.css';

const LineChart = ({ data, options = {} }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartRef.current && data) {
      // Destroy existing chart if it exists
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      // Create new chart
      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: data.datasets.map((dataset) => ({
            label: dataset.label,
            data: dataset.data,
            borderColor: dataset.color || '#4285F4',
            backgroundColor:
              dataset.backgroundColor || 'rgba(66, 133, 244, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: dataset.fill !== undefined ? dataset.fill : false,
          })),
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            },
          },
          scales: {
            x: {
              grid: {
                display: false,
              },
            },
            y: {
              grid: {
                borderDash: [2, 4],
                color: 'rgba(0, 0, 0, 0.1)',
              },
              beginAtZero: true,
            },
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false,
          },
          ...options,
        },
      });
    }

    // Cleanup function
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, options]);

  return (
    <div className={styles.chartContainer}>
      <canvas ref={chartRef} />
    </div>
  );
};

export default LineChart;
```

## State Management

### Theme Context

The ThemeContext provides theme switching functionality:

```jsx
// ThemeContext.js
import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Get theme from localStorage or default to 'light'
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'light';
  });

  // Update localStorage when theme changes
  useEffect(() => {
    localStorage.setItem('theme', theme);
    // Apply theme class to body
    document.body.className = `theme-${theme}`;
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

## API Integration

### API Service

The API service handles communication with the backend:

```jsx
// api.js
import axios from 'axios';

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API functions
export const login = async (credentials) => {
  const response = await apiClient.post('/users/token', credentials);
  return response.data;
};

export const fetchDashboardData = async () => {
  const response = await apiClient.get('/dashboard');
  return response.data;
};

export const fetchPredictions = async () => {
  const response = await apiClient.get('/predictions/');
  return response.data.predictions;
};

export const createPrediction = async (predictionData) => {
  const response = await apiClient.post('/predictions/', predictionData);
  return response.data;
};

export const fetchModelMetrics = async (modelId) => {
  const response = await apiClient.get(`/models/${modelId}/metrics`);
  return response.data;
};

export const updateUserSettings = async (settings) => {
  const response = await apiClient.put('/users/settings', settings);
  return response.data;
};
```

## Styling

### CSS Architecture

The frontend uses CSS Modules for component-scoped styling:

```css
/* index.css - Global styles */
:root {
  /* Color variables */
  --primary-color: #4285f4;
  --secondary-color: #34a853;
  --accent-color: #fbbc05;
  --error-color: #ea4335;
  --text-primary: #202124;
  --text-secondary: #5f6368;
  --background-light: #ffffff;
  --background-dark: #202124;
  --border-color: #dadce0;

  /* Spacing variables */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;

  /* Font variables */
  --font-family: 'Roboto', sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;

  /* Border radius */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 16px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Base styles */
body {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  color: var(--text-primary);
  background-color: var(--background-light);
  margin: 0;
  padding: 0;
  line-height: 1.5;
}

/* Theme classes */
body.theme-dark {
  --text-primary: #e8eaed;
  --text-secondary: #9aa0a6;
  --background-light: #202124;
  --background-dark: #303134;
  --border-color: #5f6368;
}

/* Typography */
h1,
h2,
h3,
h4,
h5,
h6 {
  margin-top: 0;
  font-weight: 500;
}

h1 {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-lg);
}

h2 {
  font-size: calc(var(--font-size-xl) - 2px);
  margin-bottom: var(--spacing-md);
}

h3 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-md);
}

/* Links */
a {
  color: var(--primary-color);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Buttons */
button {
  cursor: pointer;
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
  background-color: transparent;
  transition: all 0.2s ease;
}

button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

button:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.4);
}

/* Form elements */
input,
select,
textarea {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background-color: var(--background-light);
  color: var(--text-primary);
  width: 100%;
  box-sizing: border-box;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(66, 133, 244, 0.2);
}

/* Utility classes */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.card {
  background-color: var(--background-light);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.justify-between {
  justify-content: space-between;
}

.align-center {
  align-items: center;
}

.text-center {
  text-align: center;
}

.mt-sm {
  margin-top: var(--spacing-sm);
}
.mt-md {
  margin-top: var(--spacing-md);
}
.mt-lg {
  margin-top: var(--spacing-lg);
}
.mb-sm {
  margin-bottom: var(--spacing-sm);
}
.mb-md {
  margin-bottom: var(--spacing-md);
}
.mb-lg {
  margin-bottom: var(--spacing-lg);
}
```

## Responsive Design

The frontend is designed to be responsive across different screen sizes:

```css
/* Responsive breakpoints */
@media (max-width: 1200px) {
  .container {
    max-width: 960px;
  }
}

@media (max-width: 992px) {
  .container {
    max-width: 720px;
  }

  /* Adjust layout for tablets */
  .statsContainer {
    grid-template-columns: repeat(2, 1fr);
  }

  .chartsContainer {
    flex-direction: column;
  }

  .chartCard {
    width: 100%;
    margin-right: 0;
    margin-bottom: var(--spacing-lg);
  }
}

@media (max-width: 768px) {
  .container {
    max-width: 540px;
  }

  /* Adjust layout for mobile */
  .header {
    flex-direction: column;
    padding: var(--spacing-md);
  }

  .navigation {
    margin: var(--spacing-md) 0;
  }

  .sidebar {
    width: 100%;
    position: static;
    height: auto;
  }

  .mainContent {
    margin-left: 0;
  }

  .statsContainer {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 576px) {
  .container {
    max-width: 100%;
    padding: 0 var(--spacing-sm);
  }

  /* Further adjustments for small mobile */
  .navigation a {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: var(--font-size-sm);
  }

  h1 {
    font-size: var(--font-size-lg);
  }

  h2 {
    font-size: var(--font-size-md);
  }
}
```

## Performance Optimization

### Code Splitting

The application uses React's lazy loading for code splitting:

```jsx
// App.js
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';

// Eagerly loaded components
import Layout from './components/Layout';

// Lazily loaded components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Predictions = lazy(() => import('./pages/Predictions'));
const ModelMetrics = lazy(() => import('./pages/ModelMetrics'));
const Settings = lazy(() => import('./pages/Settings'));
const NotFound = lazy(() => import('./pages/NotFound'));

const App = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/model-metrics" element={<ModelMetrics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
```

### Memoization

Components use React.memo and useMemo for performance optimization:

```jsx
// StatCard.js
import React, { useMemo } from 'react';
import styles from './StatCard.module.css';

const StatCard = React.memo(({ title, value, trend }) => {
  const trendClass = useMemo(() => {
    if (trend > 0) return styles.positive;
    if (trend < 0) return styles.negative;
    return styles.neutral;
  }, [trend]);

  const trendIcon = useMemo(() => {
    if (trend > 0) return '↑';
    if (trend < 0) return '↓';
    return '→';
  }, [trend]);

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>{title}</h3>
      <div className={styles.value}>{value}</div>
      <div className={`${styles.trend} ${trendClass}`}>
        {trendIcon} {Math.abs(trend)}%
      </div>
    </div>
  );
});

export default StatCard;
```

## Build and Deployment

### Development Build

For local development:

```bash
# Install dependencies
npm install

# Start development server
npm start
```

### Production Build

For production deployment:

```bash
# Create optimized production build
npm run build

# The build artifacts will be in the build/ directory
```

### Docker Deployment

The frontend is containerized using Docker:

```dockerfile
# Dockerfile.frontend
# Build stage
FROM node:14-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

The Nginx configuration ensures proper routing for the SPA:

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }

    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Testing

### Unit Testing

Unit tests are written using Jest and React Testing Library:

```jsx
// Header.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import Header from './Header';

const renderWithContext = (
  ui,
  { theme = 'light', toggleTheme = jest.fn() } = {}
) => {
  return render(
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <BrowserRouter>{ui}</BrowserRouter>
    </ThemeContext.Provider>
  );
};

describe('Header Component', () => {
  test('renders correctly', () => {
    renderWithContext(<Header />);

    expect(screen.getByText('Quantis')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Predictions')).toBeInTheDocument();
    expect(screen.getByText('Model Metrics')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  test('toggles theme when button is clicked', () => {
    const toggleTheme = jest.fn();
    renderWithContext(<Header />, { toggleTheme });

    const themeButton = screen.getByText('Dark Mode');
    fireEvent.click(themeButton);

    expect(toggleTheme).toHaveBeenCalledTimes(1);
  });

  test('displays correct theme button text based on current theme', () => {
    renderWithContext(<Header />, { theme: 'light' });
    expect(screen.getByText('Dark Mode')).toBeInTheDocument();

    renderWithContext(<Header />, { theme: 'dark' });
    expect(screen.getByText('Light Mode')).toBeInTheDocument();
  });
});
```

### Integration Testing

Integration tests verify component interactions:

```jsx
// Dashboard.test.js
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeContext } from '../context/ThemeContext';
import Dashboard from '../pages/Dashboard';
import { fetchDashboardData } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  fetchDashboardData: jest.fn(),
}));

const mockDashboardData = {
  activeModels: 5,
  modelTrend: 20,
  predictionsToday: 120,
  predictionsTrend: 15,
  avgAccuracy: 92.5,
  accuracyTrend: -2,
  dataPoints: 15000,
  dataPointsTrend: 5,
  forecastPerformance: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        label: 'Actual',
        data: [10, 15, 12, 18, 20],
        color: '#4285F4',
      },
      {
        label: 'Predicted',
        data: [11, 14, 13, 17, 21],
        color: '#34A853',
      },
    ],
  },
  modelComparison: {
    labels: ['TFT', 'Prophet', 'ARIMA', 'XGBoost'],
    datasets: [
      {
        label: 'Accuracy',
        data: [92, 88, 85, 90],
        backgroundColor: '#4285F4',
      },
    ],
  },
  recentActivity: [
    { time: '10:30 AM', description: 'New prediction created for Sales Data' },
    { time: '09:15 AM', description: 'Model TFT-v2 training completed' },
    { time: 'Yesterday', description: 'New dataset uploaded: Website Traffic' },
  ],
};

const renderWithProviders = (ui) => {
  return render(
    <ThemeContext.Provider value={{ theme: 'light', toggleTheme: jest.fn() }}>
      <BrowserRouter>{ui}</BrowserRouter>
    </ThemeContext.Provider>
  );
};

describe('Dashboard Page', () => {
  beforeEach(() => {
    fetchDashboardData.mockResolvedValue(mockDashboardData);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('displays loading state initially', () => {
    renderWithProviders(<Dashboard />);
    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  test('fetches and displays dashboard data', async () => {
    renderWithProviders(<Dashboard />);

    await waitFor(() => {
      expect(fetchDashboardData).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByText('Active Models')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();

    expect(screen.getByText('Predictions Today')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();

    expect(screen.getByText('Avg. Accuracy')).toBeInTheDocument();
    expect(screen.getByText('92.5%')).toBeInTheDocument();

    expect(screen.getByText('Recent Forecast Performance')).toBeInTheDocument();
    expect(screen.getByText('Model Accuracy Comparison')).toBeInTheDocument();

    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    expect(
      screen.getByText('New prediction created for Sales Data')
    ).toBeInTheDocument();
  });

  test('displays error message when API call fails', async () => {
    fetchDashboardData.mockRejectedValue(new Error('Failed to fetch data'));

    renderWithProviders(<Dashboard />);

    await waitFor(() => {
      expect(fetchDashboardData).toHaveBeenCalledTimes(1);
    });

    expect(
      screen.getByText('Error loading dashboard: Failed to fetch data')
    ).toBeInTheDocument();
  });
});
```

## Accessibility

The frontend follows accessibility best practices:

1. **Semantic HTML**: Using appropriate HTML elements
2. **ARIA Attributes**: Adding aria-\* attributes where needed
3. **Keyboard Navigation**: Ensuring all interactive elements are keyboard accessible
4. **Focus Management**: Proper focus handling for modals and dynamic content
5. **Color Contrast**: Meeting WCAG AA standards for text contrast

Example of accessible component:

```jsx
// AccessibleButton.js
import React from 'react';
import styles from './AccessibleButton.module.css';

const AccessibleButton = ({
  children,
  onClick,
  disabled = false,
  ariaLabel,
  type = 'button',
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  className = '',
}) => {
  const buttonClasses = [
    styles.button,
    styles[variant],
    styles[size],
    fullWidth ? styles.fullWidth : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel || undefined}
    >
      {children}
    </button>
  );
};

export default AccessibleButton;
```

## Browser Compatibility

The frontend is designed to work across modern browsers:

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

Polyfills are included for older browsers when necessary.

## Development Guidelines

### Coding Standards

1. **Naming Conventions**:
   - Components: PascalCase (e.g., `Header.js`)
   - Functions and variables: camelCase (e.g., `handleSubmit`)
   - Constants: UPPER_SNAKE_CASE (e.g., `MAX_ITEMS`)

2. **File Organization**:
   - One component per file
   - Related components in subdirectories
   - Shared utilities in the utils directory

3. **Code Style**:
   - Use functional components with hooks
   - Prefer destructuring for props
   - Use named exports for utility functions
   - Use default exports for components

### Best Practices

1. **Performance**:
   - Memoize expensive calculations with useMemo
   - Prevent unnecessary re-renders with React.memo
   - Use useCallback for event handlers passed to child components

2. **State Management**:
   - Use local state for component-specific state
   - Use context for shared state across components
   - Keep state as close as possible to where it's used

3. **Error Handling**:
   - Implement error boundaries for component errors
   - Handle API errors gracefully with user-friendly messages
   - Log errors for debugging

4. **Security**:
   - Sanitize user inputs
   - Implement proper authentication and authorization
   - Use HTTPS for all API requests

## Troubleshooting

### Common Issues

#### API Connection Problems

If the frontend cannot connect to the API:

1. Check that the API is running
2. Verify the API URL in the environment variables
3. Check for CORS issues in the browser console
4. Ensure the API is accessible from the frontend's network

#### Rendering Issues

If components are not rendering correctly:

1. Check the browser console for errors
2. Verify that data is being fetched correctly
3. Check component props and state
4. Use React DevTools to inspect component hierarchy

#### Performance Problems

If the application is slow:

1. Use React DevTools Profiler to identify slow components
2. Check for unnecessary re-renders
3. Optimize expensive calculations with memoization
4. Implement code splitting for large components

## References

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Create React App Documentation](https://create-react-app.dev/docs/getting-started)
- [React Router Documentation](https://reactrouter.com/web/guides/quick-start)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Axios Documentation](https://axios-http.com/docs/intro)
