// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserProfile from '@/views/UserProfile.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import ClientList from '@/views/ClientList.vue'
import ClientsCreate from '@/views/ClientCreate.vue'
import ScenarioDetail from '@/views/ScenarioDetail.vue'
import Auth0Callback from '@/views/Auth0Callback.vue'
import UserManagement from '@/views/UserManagement.vue'
import ComparisonReport from '@/views/ComparisonReport.vue'


const routes = [
  { path: '/register', name: 'Register', component: Register },
  { path: '/login', name: 'Login', component: Login },
  { path: '/auth/callback', name: 'Auth0Callback', component: Auth0Callback },
  {
    path: '/',
    component: DefaultLayout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
      { path: 'profile', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true } },
      { path: 'clients', name: 'Clients', component: ClientList, meta: { requiresAuth: true } },
      { path: 'clients/create', name: 'ClientsCreate', component: ClientsCreate, meta: { requiresAuth: true } },
      { path: 'clients/:id', name: 'ClientDetail', component: () => import('@/views/ClientDetail.vue'), meta: { requiresAuth: true } },
      { path: 'clients/:id/edit', name: 'ClientEdit', component: () => import('@/views/ClientEdit.vue'), meta: { requiresAuth: true } },
      { path: 'clients/:id/comparison-report', name: 'ComparisonReport', component: ComparisonReport, meta: { requiresAuth: true } },
      { path: 'clients/:id/scenarios/new', name: 'ScenarioCreate', component: () => import('@/views/ScenarioCreate.vue'), meta: { requiresAuth: true }, props: true },
      { path: 'clients/:id/scenarios/detail/:scenarioid', name: 'ScenarioDetail', component: ScenarioDetail, meta: { requiresAuth: true } },
      { path: 'integrations', name: 'Integrations', component: () => import('@/views/Integrations.vue'), meta: { requiresAuth: true } },
      { path: 'users', name: 'UserManagement', component: UserManagement, meta: { requiresAuth: true } },
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

router.beforeEach((to, _, next) => {
  const authStore = useAuthStore();

  // Check if route requires auth
  if (to.meta.requiresAuth && !authStore.token) {
    next('/login');
  } else {
    next();
  }
});

export default router