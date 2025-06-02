// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserProfile from '@/views/UserProfile.vue'
import Signup from '@/views/Signup.vue'
import Login from '@/views/Login.vue'
import ClientList from '@/views/ClientList.vue'
import ClientsCreate from '@/views/ClientCreate.vue'


const routes = [
  { path: '/signup', name: 'Signup', component: Signup },
  { path: '/login', name: 'Login', component: Login },
  {
    path: '/',
    component: DefaultLayout,
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
      { path: 'profile', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true } },
      { path: 'clients', name: 'Clients', component: ClientList, meta: { requiresAuth: true } },
      { path: 'clients/create', name: 'ClientsCreate', component: ClientsCreate, meta: { requiresAuth: true } },
      { path: 'clients/:id', name: 'ClientDetail', component: () => import('@/views/ClientDetail.vue'), meta: { requiresAuth: true } }

    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { useAuthStore } from '@/stores/auth';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

const app = createApp({});
const pinia = createPinia();
app.use(pinia);

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // Check if route requires auth
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login');
  } else {
    next();
  }
});

export default router