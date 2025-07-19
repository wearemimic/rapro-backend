import { defineStore } from 'pinia';
import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
    isAuth0: false,
  }),
  persist: true,
  getters: {
    accessToken: (state) => state.token,
    isAuthenticated: (state) => !!state.token,
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
      axios.interceptors.response.use(
        response => response,
        async error => {
          const originalRequest = error.config;

          if (
            error.response &&
            error.response.status === 401 &&
            !originalRequest._retry &&
            localStorage.getItem('refresh_token')
          ) {
            originalRequest._retry = true;
            try {
              const res = await axios.post('http://localhost:8000/api/token/refresh/', {
                refresh: localStorage.getItem('refresh_token'),
              });

              const newToken = res.data.access;
              this.token = newToken;
              localStorage.setItem('token', newToken);
              axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
              originalRequest.headers['Authorization'] = `Bearer ${newToken}`;

              return axios(originalRequest);
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
              this.logout(); // Optional: force logout
            }
          }

          return Promise.reject(error);
        }
      );
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
      this.token = null;
      this.user = null;
      this.isAuth0 = false;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isAuth0');
      
      // Remove Authorization header
      delete axios.defaults.headers.common['Authorization'];
      
      // If Auth0 instance is provided, logout from Auth0 as well
      if (auth0) {
        auth0.logout({
          logoutParams: {
            returnTo: window.location.origin + '/login'
          }
        });
      }
    }
  }
});
