# Web Frontend Directory

## Overview

The `web-frontend` directory contains the comprehensive web application frontend for the Quantis platform. This React-based single-page application provides the user interface for interacting with the Quantis system, visualizing time series data, managing forecasting models, and accessing platform features. The frontend is designed with modern web development practices, emphasizing performance, responsiveness, and an intuitive user experience.

## Directory Structure

The web frontend is organized into the following key components:

- **public/**: Static assets and the HTML entry point for the application
  - **assets/**: Images, icons, and other static resources
  - **index.html**: Main HTML entry point for the React application
  - **manifest.json**: Progressive Web App manifest configuration

- **src/**: Source code for the React application
  - **components/**: Reusable UI components
  - **contexts/**: React context providers for state management
  - **hooks/**: Custom React hooks for shared functionality
  - **pages/**: Page-level components representing different routes
  - **services/**: API client and service integrations
  - **styles/**: Global styles and theming
  - **utils/**: Utility functions and helpers
  - **App.js**: Main application component
  - **index.js**: Application entry point

- **Dockerfile**: Configuration for building the frontend Docker container
- **jest.config.js**: Configuration for the Jest testing framework
- **nginx.conf**: Nginx web server configuration for serving the frontend application
- **package.json**: NPM package configuration, dependencies, and build scripts

## Technology Stack

The web frontend leverages a modern technology stack:

### Core Technologies
- **React 18**: Component-based UI library with hooks and concurrent rendering
- **React Router**: For client-side routing and navigation
- **Context API**: For state management across components
- **Material UI**: Component library for consistent design
- **Axios**: HTTP client for API communication
- **Chart.js & Nivo**: Data visualization libraries for time series charts
- **Formik & Yup**: Form handling and validation

### Development Tools
- **TypeScript**: For type safety and improved developer experience
- **Jest & Testing Library**: For unit and integration testing
- **ESLint & Prettier**: For code quality and formatting
- **Webpack**: For bundling and optimization (via React Scripts)

### Deployment & Infrastructure
- **Docker**: For containerization
- **Nginx**: For serving the static assets
- **CI/CD Integration**: For automated testing and deployment

## Key Components

### Application Structure

The application follows a modular architecture with clear separation of concerns:

1. **Component Layer**: Reusable UI components that accept props and render UI
2. **Page Layer**: Page-level components that compose multiple components
3. **Context Layer**: State management using React Context API
4. **Service Layer**: API clients and external service integrations
5. **Utility Layer**: Helper functions and shared logic

### State Management

The application uses React Context API for state management, with specialized contexts for:

- **AuthContext**: User authentication state and methods
- **ThemeContext**: Theme preferences and customization
- **NotificationContext**: System notifications and alerts
- **DataContext**: Shared data and caching

Example Context implementation:

```jsx
// src/contexts/AuthContext.js
import React, { createContext, useState, useEffect } from 'react';
import { loginUser, logoutUser, refreshToken } from '../services/authService';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check for existing session on load
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = await refreshToken(token);
          setUser(userData);
        }
      } catch (err) {
        setError(err.message);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const userData = await loginUser(credentials);
      setUser(userData);
      localStorage.setItem('token', userData.token);
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await logoutUser();
      setUser(null);
      localStorage.removeItem('token');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Routing

The application uses React Router for client-side routing with a structure that includes:

- Public routes accessible without authentication
- Protected routes requiring authentication
- Role-based route access control
- Nested routes for complex page hierarchies

Example routing configuration:

```jsx
// src/App.js
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Models from './pages/Models';
import Predictions from './pages/Predictions';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/models" element={
            <ProtectedRoute>
              <Models />
            </ProtectedRoute>
          } />
          
          <Route path="/predictions" element={
            <ProtectedRoute>
              <Predictions />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />
          
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

### API Integration

The frontend communicates with the Quantis backend API using a service-based approach:

```jsx
// src/services/apiClient.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
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

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token refresh on 401 errors
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, { refreshToken });
        const { token } = response.data;
        
        localStorage.setItem('token', token);
        
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login if refresh fails
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Data Visualization

The frontend includes sophisticated data visualization components for time series data:

```jsx
// src/components/TimeSeriesChart.jsx
import React, { useMemo } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { useTheme } from '../contexts/ThemeContext';

const TimeSeriesChart = ({ data, xAxisLabel, yAxisLabel, height = 400 }) => {
  const { theme } = useTheme();
  
  const formattedData = useMemo(() => {
    return data.map(series => ({
      id: series.name,
      data: series.values.map(point => ({
        x: new Date(point.timestamp),
        y: point.value
      }))
    }));
  }, [data]);
  
  const chartTheme = {
    axis: {
      ticks: {
        text: {
          fill: theme.palette.text.primary
        }
      },
      legend: {
        text: {
          fill: theme.palette.text.primary
        }
      }
    },
    grid: {
      line: {
        stroke: theme.palette.divider,
        strokeWidth: 1
      }
    },
    crosshair: {
      line: {
        stroke: theme.palette.primary.main,
        strokeWidth: 1,
        strokeOpacity: 0.35
      }
    },
    tooltip: {
      container: {
        background: theme.palette.background.paper,
        color: theme.palette.text.primary,
        boxShadow: theme.shadows[3]
      }
    }
  };
  
  return (
    <div style={{ height }}>
      <ResponsiveLine
        data={formattedData}
        margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
        xScale={{
          type: 'time',
          format: 'native',
          precision: 'minute'
        }}
        yScale={{
          type: 'linear',
          min: 'auto',
          max: 'auto',
          stacked: false
        }}
        axisBottom={{
          format: '%b %d, %Y',
          tickValues: 5,
          legend: xAxisLabel,
          legendOffset: 36,
          legendPosition: 'middle'
        }}
        axisLeft={{
          legend: yAxisLabel,
          legendOffset: -40,
          legendPosition: 'middle'
        }}
        pointSize={10}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor' }}
        pointLabelYOffset={-12}
        useMesh={true}
        legends={[
          {
            anchor: 'bottom-right',
            direction: 'column',
            justify: false,
            translateX: 100,
            translateY: 0,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 80,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
            effects: [
              {
                on: 'hover',
                style: {
                  itemBackground: 'rgba(0, 0, 0, .03)',
                  itemOpacity: 1
                }
              }
            ]
          }
        ]}
        theme={chartTheme}
      />
    </div>
  );
};

export default TimeSeriesChart;
```

## Development Workflow

### Environment Setup

To set up the development environment:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/quantis.git
   cd quantis/web-frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
   Create a `.env.local` file with the following variables:
   ```
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_VERSION=$npm_package_version
   REACT_APP_ENV=development
   ```

### Development Server

Start the development server with hot reloading:

```bash
npm start
```

This will start the application on `http://localhost:3000` with the following features:
- Hot module replacement for instant feedback
- Source maps for debugging
- ESLint integration for code quality
- Automatic browser reloading

### Building for Production

To create a production build:

```bash
npm run build
```

This creates an optimized build in the `build` directory with:
- Minified JavaScript bundles
- Optimized assets
- Source maps for production debugging
- Static file optimization

### Docker Deployment

The included Dockerfile enables containerized deployment:

```dockerfile
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

To build and run the Docker container:

```bash
docker build -t quantis-frontend .
docker run -p 80:80 quantis-frontend
```

The Nginx configuration (`nginx.conf`) is optimized for single-page applications:

```nginx
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

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://api.quantis.example.com;";
}
```

## Testing

The frontend includes a comprehensive testing strategy:

### Unit Testing

Unit tests focus on individual components and functions:

```jsx
// src/components/__tests__/Button.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../Button';

describe('Button Component', () => {
  test('renders correctly with default props', () => {
    render(<Button>Click Me</Button>);
    const button = screen.getByText('Click Me');
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    const button = screen.getByText('Click Me');
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('renders as disabled when disabled prop is true', () => {
    render(<Button disabled>Click Me</Button>);
    const button = screen.getByText('Click Me');
    expect(button).toBeDisabled();
  });

  test('applies variant styles correctly', () => {
    render(<Button variant="contained">Click Me</Button>);
    const button = screen.getByText('Click Me');
    expect(button).toHaveClass('contained');
  });
});
```

### Integration Testing

Integration tests verify interactions between components:

```jsx
// src/pages/__tests__/Login.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Login from '../Login';
import { loginUser } from '../../services/authService';

// Mock the auth service
jest.mock('../../services/authService');

describe('Login Page', () => {
  beforeEach(() => {
    // Reset mocks
    loginUser.mockReset();
  });

  test('submits the form with user credentials', async () => {
    // Mock successful login
    loginUser.mockResolvedValueOnce({ 
      id: '123', 
      username: 'testuser', 
      token: 'fake-token' 
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );

    // Fill out the form
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify login was called with correct credentials
    expect(loginUser).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123'
    });

    // Verify redirect after successful login
    await waitFor(() => {
      expect(window.location.pathname).toBe('/');
    });
  });

  test('displays error message on login failure', async () => {
    // Mock failed login
    loginUser.mockRejectedValueOnce(new Error('Invalid credentials'));

    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );

    // Fill out the form
    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'testuser' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
```

### Running Tests

Execute tests with the following commands:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Performance Optimization

The frontend implements several performance optimizations:

### Code Splitting

Code splitting reduces initial bundle size:

```jsx
import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import Loading from './components/Loading';

// Lazy-loaded components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Models = lazy(() => import('./pages/Models'));
const Predictions = lazy(() => import('./pages/Predictions'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/models" element={<Models />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### Memoization

Component memoization prevents unnecessary re-renders:

```jsx
import React, { useMemo } from 'react';

const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = useMemo(() => {
    return data.map(item => /* expensive calculation */);
  }, [data]);
  
  return (
    <div>
      {processedData.map(item => (
        <div key={item.id}>{item.value}</div>
      ))}
    </div>
  );
});
```

### Virtual Lists

Virtual lists optimize rendering of large datasets:

```jsx
import React from 'react';
import { FixedSizeList } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      {items[index].name}
    </div>
  );

  return (
    <FixedSizeList
      height={400}
      width="100%"
      itemCount={items.length}
      itemSize={35}
    >
      {Row}
    </FixedSizeList>
  );
};
```

## Accessibility

The frontend prioritizes accessibility with:

- Semantic HTML elements
- ARIA attributes for complex components
- Keyboard navigation support
- Color contrast compliance
- Screen reader compatibility

Example accessible component:

```jsx
import React from 'react';

const AccessibleTabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div role="tablist" aria-orientation="horizontal">
      {tabs.map((tab, index) => (
        <button
          key={tab.id}
          role="tab"
          id={`tab-${tab.id}`}
          aria-selected={activeTab === tab.id}
          aria-controls={`panel-${tab.id}`}
          tabIndex={activeTab === tab.id ? 0 : -1}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
      
      {tabs.map((tab) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== tab.id}
        >
          {tab.content}
        </div>
      ))}
    </div>
  );
};
```

## Security Considerations

The frontend implements several security measures:

### Authentication

- JWT-based authentication with secure storage
- Token refresh mechanism
- Automatic logout on inactivity
- Protection against CSRF attacks

### Data Protection

- HTTPS-only communication
- Input validation and sanitization
- Content Security Policy implementation
- Secure cookie handling

### Secure Development Practices

- Regular dependency updates
- Static code analysis
- Security-focused code reviews
- Vulnerability scanning

## Internationalization

The application supports multiple languages using i18next:

```jsx
import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { t, i18n } = useTranslation();
  
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };
  
  return (
    <div>
      <h2>{t('language.select')}</h2>
      <button onClick={() => changeLanguage('en')}>
        {t('language.english')}
      </button>
      <button onClick={() => changeLanguage('fr')}>
        {t('language.french')}
      </button>
      <button onClick={() => changeLanguage('de')}>
        {t('language.german')}
      </button>
    </div>
  );
};
```

## Troubleshooting

Common issues and solutions:

### API Connection Issues

**Symptoms**: API requests fail, network errors in console

**Solutions**:
1. Verify API URL in environment variables
2. Check CORS configuration on the backend
3. Verify network connectivity
4. Check authentication token validity

### Performance Problems

**Symptoms**: Slow rendering, UI freezes

**Solutions**:
1. Implement component memoization
2. Use virtualized lists for large datasets
3. Optimize expensive calculations
4. Implement code splitting

### Build Failures

**Symptoms**: npm build command fails

**Solutions**:
1. Check for TypeScript errors
2. Verify dependency compatibility
3. Clear node_modules and reinstall
4. Check for environment variable issues

## Roadmap

Future development plans include:

### Short-term Improvements

1. **Enhanced Data Visualization**:
   - Additional chart types
   - Interactive data exploration
   - Export capabilities

2. **Performance Optimizations**:
   - Bundle size reduction
   - Server-side rendering
   - Progressive loading

### Medium-term Goals

1. **Advanced User Features**:
   - Customizable dashboards
   - Saved views and reports
   - Collaborative annotations

2. **Integration Enhancements**:
   - External data source connections
   - Webhook configurations
   - API key management

### Long-term Vision

1. **AI-Assisted Interface**:
   - Natural language queries
   - Automated insights
   - Predictive user assistance

2. **Extended Platform Support**:
   - Native mobile applications
   - Offline capabilities
   - Desktop integration

## Contributing

Guidelines for contributing to the frontend:

### Development Standards

1. **Code Style**:
   - Follow ESLint configuration
   - Use Prettier for formatting
   - Maintain consistent naming conventions

2. **Component Structure**:
   - One component per file
   - Follow atomic design principles
   - Document component props with JSDoc

3. **Testing Requirements**:
   - Unit tests for all components
   - Integration tests for pages
   - Maintain >80% code coverage

### Pull Request Process

1. Create a feature branch from `develop`
2. Implement changes with tests
3. Ensure all tests pass
4. Submit PR with detailed description
5. Address review comments
6. Merge after approval

This comprehensive frontend provides a robust, performant, and user-friendly interface for the Quantis platform, enabling users to effectively interact with time series data and forecasting models.
