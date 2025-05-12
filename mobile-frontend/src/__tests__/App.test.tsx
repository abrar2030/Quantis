import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import App from '../App';
import rootReducer from '../store/rootReducer';
import { ErrorBoundary } from 'react-error-boundary';

const createTestStore = () => {
  return configureStore({
    reducer: rootReducer,
    preloadedState: {
      auth: {
        isAuthenticated: false,
        user: null,
        loading: false,
        error: null
      },
      predictions: {
        data: [],
        loading: false,
        error: null
      }
    }
  });
};

describe('Mobile App Component', () => {
  let store;

  beforeEach(() => {
    store = createTestStore();
  });

  it('renders login screen when not authenticated', () => {
    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );
    expect(getByText('Sign In')).toBeTruthy();
  });

  it('renders home screen when authenticated', () => {
    store = configureStore({
      reducer: rootReducer,
      preloadedState: {
        auth: {
          isAuthenticated: true,
          user: { id: 1, email: 'test@example.com' },
          loading: false,
          error: null
        },
        predictions: {
          data: [],
          loading: false,
          error: null
        }
      }
    });

    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );
    expect(getByText('Home')).toBeTruthy();
  });

  it('handles login form submission', async () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Sign In'));

    await waitFor(() => {
      expect(store.getState().auth.loading).toBe(true);
    });
  });

  it('displays error message on failed login', async () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'invalid@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'wrongpassword');
    fireEvent.press(getByText('Sign In'));

    await waitFor(() => {
      expect(getByText('Invalid credentials')).toBeTruthy();
    });
  });

  it('handles navigation between screens', async () => {
    store = configureStore({
      reducer: rootReducer,
      preloadedState: {
        auth: {
          isAuthenticated: true,
          user: { id: 1, email: 'test@example.com' },
          loading: false,
          error: null
        },
        predictions: {
          data: [],
          loading: false,
          error: null
        }
      }
    });

    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    fireEvent.press(getByText('Profile'));
    expect(getByText('User Profile')).toBeTruthy();

    fireEvent.press(getByText('Predictions'));
    expect(getByText('Your Predictions')).toBeTruthy();
  });

  it('validates form inputs', async () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    // Try to submit without filling required fields
    fireEvent.press(getByText('Sign In'));

    await waitFor(() => {
      expect(getByText('Email is required')).toBeTruthy();
      expect(getByText('Password is required')).toBeTruthy();
    });

    // Try invalid email format
    fireEvent.changeText(getByPlaceholderText('Email'), 'invalid-email');
    fireEvent.press(getByText('Sign In'));

    await waitFor(() => {
      expect(getByText('Invalid email format')).toBeTruthy();
    });
  });

  it('shows loading state during authentication', async () => {
    const { getByPlaceholderText, getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Sign In'));

    expect(getByText('Loading')).toBeTruthy();
    expect(getByText('Sign In')).toBeDisabled();
  });

  it('handles error boundary', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    const { getByText } = render(
      <Provider store={store}>
        <ErrorBoundary fallback={<div>Error occurred</div>}>
          <ThrowError />
        </ErrorBoundary>
      </Provider>
    );

    expect(getByText('Error occurred')).toBeTruthy();
  });

  it('handles offline mode', async () => {
    // Mock network status
    const mockNetInfo = {
      isConnected: false,
      isInternetReachable: false
    };
    jest.mock('@react-native-community/netinfo', () => ({
      useNetInfo: () => mockNetInfo
    }));

    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    expect(getByText('You are offline')).toBeTruthy();
  });

  it('handles deep linking', async () => {
    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    // Simulate deep link
    act(() => {
      store.dispatch({
        type: 'HANDLE_DEEP_LINK',
        payload: { screen: 'Predictions', params: { id: 123 } }
      });
    });

    await waitFor(() => {
      expect(getByText('Your Predictions')).toBeTruthy();
    });
  });

  it('handles biometric authentication', async () => {
    const { getByText } = render(
      <Provider store={store}>
        <App />
      </Provider>
    );

    // Mock biometric authentication
    const mockBiometrics = {
      authenticate: jest.fn().mockResolvedValue({ success: true })
    };
    jest.mock('react-native-biometrics', () => mockBiometrics);

    fireEvent.press(getByText('Sign in with Biometrics'));

    await waitFor(() => {
      expect(mockBiometrics.authenticate).toHaveBeenCalled();
    });
  });
}); 