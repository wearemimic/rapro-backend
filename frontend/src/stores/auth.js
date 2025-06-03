import { defineStore } from 'pinia';
import axios from 'axios';



export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
  }),
  persist: true,
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
      this.loading = true;
      this.error = null;
      try {
        //ZAPHOD - GET RID OF HARD CODED URL
        const response = await axios.post('http://localhost:8000/api/login/', {
          email: credentials.email,
          password: credentials.password
        });

        this.token = response.data.access;
        localStorage.setItem('refresh_token', response.data.refresh);
        this.user = response.data.user; // <-- this may throw if `user` is undefined

        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));

        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;

        return true;
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed';
      } finally {
        this.loading = false;
      }
    },

    register: async function (credentials) {
      try {
        const response = await axios.post('http://localhost:8000/api/login/', credentials);
        this.token = response.data.access;
        this.user = response.data.user;
        localStorage.setItem('token', this.token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
        console.log("✅ Registered and token set:", this.token);
        return true;
      } catch (error) {
        console.error("❌ Registration failed:", error);
        return false;
      }
    },

    

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('refresh_token');
    }
  },
  
});
