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
    }
  },
  
});
