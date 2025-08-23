import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import Toast, { POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import axios from 'axios';
import { createAuth0 } from '@auth0/auth0-vue';
import { auth0Config } from './config/auth0';

const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Initialize Auth0 - TEMPORARILY DISABLED FOR DEBUGGING
// The Auth0 Vue plugin might be intercepting callbacks
// app.use(
//   createAuth0({
//     domain: auth0Config.domain,
//     clientId: auth0Config.clientId,
//     authorizationParams: {
//       redirect_uri: auth0Config.redirectUri,
//       audience: auth0Config.audience,
//     },
//   })
// );

import { useAuthStore } from './stores/auth';
const authStore = useAuthStore();
authStore.init(); // ✅ Ensure axios always has the token

// Toast configuration (optional customization)
app.use(Toast, {
  position: POSITION.TOP_RIGHT,
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
});

app.mount('#app');