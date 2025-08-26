import { defineStore } from 'pinia';
import axios from 'axios';
import router from '@/router';
import { isTokenValid, isTokenExpiringSoon, getTokenExpirationInMinutes } from '@/utils/tokenUtils';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
    isAuth0: false,
    refreshAttempts: 0,
    maxRefreshAttempts: 3,
    isRefreshing: false,
    failedRequestsQueue: [],
  }),
  persist: true,
  getters: {
    accessToken: (state) => state.token,
    isAuthenticated: (state) => !!state.token,
    isTokenValidAndFresh: (state) => {
      if (!state.token) return false;
      return isTokenValid(state.token) && !isTokenExpiringSoon(state.token, 5);
    },
    tokenExpirationMinutes: (state) => {
      if (!state.token) return -1;
      return getTokenExpirationInMinutes(state.token);
    },
  },
  actions: {
    init() {
      const token = this.token || localStorage.getItem('token');
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        this.setupAxiosInterceptor();
      }
    },
    setupAxiosInterceptor() {
      // Request interceptor to add token
      axios.interceptors.request.use(
        config => {
          const token = this.token || localStorage.getItem('token');
          if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
          }
          return config;
        },
        error => Promise.reject(error)
      );

      // Response interceptor for token refresh and error handling
      axios.interceptors.response.use(
        response => response,
        async error => {
          const originalRequest = error.config;

          // Check for rate limiting (429 status)
          if (error.response && error.response.status === 429) {
            console.error('Rate limited - too many requests');
            // Clear tokens and redirect to login
            this.clearAuthData();
            router.push('/login');
            return Promise.reject(new Error('Rate limited. Please log in again.'));
          }

          // Skip refresh for certain endpoints
          const skipRefreshEndpoints = ['/api/token/refresh/', '/api/auth0/'];
          const shouldSkipRefresh = skipRefreshEndpoints.some(endpoint => 
            originalRequest.url.includes(endpoint)
          );

          if (shouldSkipRefresh && error.response?.status === 401) {
            // Refresh token is invalid, clear auth and redirect
            this.clearAuthData();
            router.push('/login');
            return Promise.reject(error);
          }

          // Handle 401 errors with token refresh
          if (
            error.response &&
            error.response.status === 401 &&
            !originalRequest._retry &&
            localStorage.getItem('refresh_token') &&
            this.refreshAttempts < this.maxRefreshAttempts
          ) {
            console.log(`401 error on ${originalRequest.url}, attempting token refresh (attempt ${this.refreshAttempts + 1}/${this.maxRefreshAttempts})`);
            originalRequest._retry = true;

            // If already refreshing, queue the request
            if (this.isRefreshing) {
              return new Promise((resolve, reject) => {
                this.failedRequestsQueue.push({ resolve, reject, originalRequest });
              });
            }

            this.isRefreshing = true;
            this.refreshAttempts++;

            try {
              // Add exponential backoff delay
              const delay = Math.min(1000 * Math.pow(2, this.refreshAttempts - 1), 10000);
              await new Promise(resolve => setTimeout(resolve, delay));

              const res = await axios.post('http://localhost:8000/api/token/refresh/', {
                refresh: localStorage.getItem('refresh_token'),
              });

              const newToken = res.data.access;
              this.token = newToken;
              localStorage.setItem('token', newToken);
              axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
              
              // Reset refresh attempts on success
              this.refreshAttempts = 0;
              this.isRefreshing = false;

              // Process queued requests
              this.processQueue(null, newToken);

              // Retry original request with new token
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
              return axios(originalRequest);
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
              this.isRefreshing = false;
              
              // Process queue with error
              this.processQueue(refreshError, null);
              
              // Clear auth and redirect to login
              this.clearAuthData();
              router.push('/login');
              
              return Promise.reject(refreshError);
            }
          }

          // For other errors or max attempts reached
          if (error.response?.status === 401 && this.refreshAttempts >= this.maxRefreshAttempts) {
            console.error('Max refresh attempts reached');
            this.clearAuthData();
            router.push('/login');
          }

          return Promise.reject(error);
        }
      );
    },

    processQueue(error, token = null) {
      this.failedRequestsQueue.forEach(promise => {
        if (error) {
          promise.reject(error);
        } else {
          promise.originalRequest.headers['Authorization'] = `Bearer ${token}`;
          promise.resolve(axios(promise.originalRequest));
        }
      });
      this.failedRequestsQueue = [];
    },

    async refreshTokenPreemptively() {
      if (this.isRefreshing) {
        console.log('Refresh already in progress, skipping preemptive refresh');
        return;
      }

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.warn('No refresh token available for preemptive refresh');
        throw new Error('No refresh token available');
      }

      this.isRefreshing = true;
      console.log('Starting preemptive token refresh');

      try {
        const res = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken,
        });

        const newToken = res.data.access;
        this.token = newToken;
        localStorage.setItem('token', newToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        
        // Reset refresh attempts on success
        this.refreshAttempts = 0;
        console.log('Preemptive token refresh successful');
        
        return newToken;
      } catch (error) {
        console.error('Preemptive token refresh failed:', error);
        throw error;
      } finally {
        this.isRefreshing = false;
      }
    },

    async ensureValidToken() {
      const token = this.token || localStorage.getItem('token');
      if (!token) {
        throw new Error('No token available');
      }

      // If token is valid and not expiring soon, we're good
      if (isTokenValid(token) && !isTokenExpiringSoon(token, 10)) {
        return token;
      }

      // Try to refresh the token
      try {
        console.log('Token expires soon, refreshing before operation');
        await this.refreshTokenPreemptively();
        return this.token;
      } catch (error) {
        console.error('Failed to ensure valid token:', error);
        throw error;
      }
    },

    clearAuthData() {
      this.token = null;
      this.user = null;
      this.isAuth0 = false;
      this.refreshAttempts = 0;
      this.isRefreshing = false;
      this.failedRequestsQueue = [];
      
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isAuth0');
      
      delete axios.defaults.headers.common['Authorization'];
    },
    async login(credentials) {
      // Deprecated: Use Auth0 login instead
      console.warn('Traditional login is deprecated. Use Auth0 authentication.');
      return this.loginWithAuth0(credentials.auth0Token);
    },
    
    async loginWithAuth0(auth0Token) {
      this.loading = true;
      this.error = null;
      try {
        console.log('Making request to backend with Auth0 token...');
        const response = await axios.post('http://localhost:8000/api/auth0/login/', {
          auth0Token: auth0Token
        });

        console.log('Backend response received:', response.status);

        this.token = response.data.access;
        localStorage.setItem('refresh_token', response.data.refresh);
        this.user = response.data.user;
        this.isAuth0 = true;

        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));
        localStorage.setItem('isAuth0', 'true');

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;

        console.log('Auth0 login successful, user:', this.user.email);
        return true;
      } catch (err) {
        console.error('Auth0 login error:', err);
        this.error = err.response?.data?.message || err.message || 'Auth0 login failed';
        
        // Log more details for debugging
        if (err.response) {
          console.error('Response status:', err.response.status);
          console.error('Response data:', err.response.data);
        }
        
        return false;
      } finally {
        this.loading = false;
      }
    },

    async register(credentials) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post('http://localhost:8000/api/auth0/signup/', credentials);
        this.token = response.data.access;
        this.user = response.data.user;
        this.isAuth0 = true;
        
        localStorage.setItem('token', this.token);
        localStorage.setItem('refresh_token', response.data.refresh);
        localStorage.setItem('user', JSON.stringify(this.user));
        localStorage.setItem('isAuth0', 'true');
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        return true;
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed';
        return false;
      } finally {
        this.loading = false;
      }
    },

    // User Management Functions
    async getUsers(params = {}) {
      try {
        const response = await axios.get('http://localhost:8000/api/users/', { params });
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Failed to fetch users');
      }
    },

    async getUserById(userId) {
      try {
        const response = await axios.get(`http://localhost:8000/api/users/${userId}/`);
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Failed to fetch user');
      }
    },

    async updateUser(userId, userData) {
      try {
        const response = await axios.put(`http://localhost:8000/api/users/${userId}/`, userData);
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Failed to update user');
      }
    },

    async deleteUser(userId) {
      try {
        await axios.delete(`http://localhost:8000/api/users/${userId}/`);
        return true;
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Failed to delete user');
      }
    },

    async resetUserPassword(userId) {
      try {
        const response = await axios.post(`http://localhost:8000/api/users/${userId}/reset-password/`);
        return response.data;
      } catch (error) {
        throw new Error(error.response?.data?.message || 'Failed to reset password');
      }
    },

    setUser(user) {
      this.user = user;
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        localStorage.removeItem('user');
      }
    },
    
    setTokens(tokens) {
      if (tokens && tokens.access) {
        this.token = tokens.access;
        localStorage.setItem('token', tokens.access);
        
        if (tokens.refresh) {
          localStorage.setItem('refresh_token', tokens.refresh);
        }
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;
      }
    },

    async fetchProfile() {
      if (!this.token) return;
      try {
        console.log('Fetching profile with token:', this.token);
        const response = await axios.get('http://localhost:8000/api/profile/', {
          headers: { Authorization: `Bearer ${this.token}` }
        });
        console.log('Profile response:', response.data);
        if (response.data && response.data.logo) {
          console.log('Logo from backend:', response.data.logo);
        }
        this.setUser(response.data);
        console.log('User after update:', this.user);
        console.log('LocalStorage after update:', JSON.parse(localStorage.getItem('user')));
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
      }
    },

    logout(auth0) {
      // Use the centralized clearAuthData method
      this.clearAuthData();
      
      // If Auth0 instance is provided, logout from Auth0 as well
      if (auth0) {
        auth0.logout({
          logoutParams: {
            returnTo: window.location.origin + '/login'
          }
        });
      } else {
        // If no Auth0 instance, just redirect to login
        router.push('/login');
      }
    }
  }
});
