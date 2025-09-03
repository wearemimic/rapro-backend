import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import Toast, { POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import axios from 'axios';
// Removed Auth0 Vue SDK - using Django server-side auth

const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Auth0 removed - using Django server-side authentication

import { useAuthStore } from './stores/auth';
const authStore = useAuthStore();
authStore.init(); // ✅ Ensure axios always has the token
authStore.restoreImpersonationState(); // ✅ Restore impersonation state if any

// Toast configuration (optional customization)
app.use(Toast, {
  position: POSITION.TOP_RIGHT,
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
});

app.mount('#app');