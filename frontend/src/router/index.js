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

// Client Portal Components
import ClientPortalHome from '@/views/ClientPortal/ClientPortalHome.vue'
import ClientDashboard from '@/views/ClientPortal/ClientDashboard.vue'
import ClientPortalDocuments from '@/views/ClientPortal/ClientPortalDocuments.vue'
import ClientPortalMessages from '@/views/ClientPortal/ClientPortalMessages.vue'
import ClientPortalAppointments from '@/views/ClientPortal/ClientPortalAppointments.vue'
import ClientPortalScenarios from '@/views/ClientPortal/ClientPortalScenarios.vue'


const routes = [
  { path: '/register', name: 'Register', component: Register },
  { path: '/login', name: 'Login', component: Login },
  { path: '/auth/callback', name: 'Auth0Callback', component: Auth0Callback },
  
  // Client Portal Login (separate from advisor login)
  { 
    path: '/portal/login', 
    name: 'ClientPortalLogin', 
    component: () => import('@/views/ClientPortalLogin.vue')
  },
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
      { path: 'communication-center', name: 'CommunicationCenter', component: () => import('@/components/CRM/CommunicationCenter.vue'), meta: { requiresAuth: true } },
      { path: 'tasks', name: 'TaskManagement', component: () => import('@/components/TaskDashboard.vue'), meta: { requiresAuth: true } },
      { path: 'calendar', name: 'Calendar', component: () => import('@/components/CRM/CalendarView.vue'), meta: { requiresAuth: true } },
      { path: 'integrations', name: 'Integrations', component: () => import('@/views/Integrations.vue'), meta: { requiresAuth: true } },
      { path: 'users', name: 'UserManagement', component: UserManagement, meta: { requiresAuth: true } },
      { path: 'documents', name: 'DocumentCenter', component: () => import('@/components/DocumentCenter.vue'), meta: { requiresAuth: true } },
    ]
  },
  // Client Portal Routes
  {
    path: '/portal',
    component: ClientPortalHome,
    meta: { requiresAuth: true, isClientPortal: true },
    redirect: '/portal/dashboard',
    children: [
      { 
        path: 'dashboard', 
        name: 'client-portal-dashboard', 
        component: () => import('@/views/ClientPortalDashboard.vue'), 
        meta: { requiresAuth: true, isClientPortal: true } 
      },
      { 
        path: 'documents', 
        name: 'client-portal-documents', 
        component: ClientPortalDocuments, 
        meta: { requiresAuth: true, isClientPortal: true } 
      },
      { 
        path: 'messages', 
        name: 'client-portal-messages', 
        component: ClientPortalMessages, 
        meta: { requiresAuth: true, isClientPortal: true } 
      },
      { 
        path: 'appointments', 
        name: 'client-portal-appointments', 
        component: ClientPortalAppointments, 
        meta: { requiresAuth: true, isClientPortal: true } 
      },
      { 
        path: 'scenarios', 
        name: 'client-portal-scenarios', 
        component: ClientPortalScenarios, 
        meta: { requiresAuth: true, isClientPortal: true } 
      }
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
  
  console.log('🔍 Router navigation to:', to.path);
  console.log('🔍 Router query params:', to.query);
  
  // Special handling for Auth0 callback
  if (to.path === '/auth/callback') {
    console.log('🎯 Auth0 callback route detected!');
    console.log('🎯 Full URL:', window.location.href);
    // Don't interfere with the callback
    next();
    return;
  }

  // Check if route requires auth
  if (to.meta.requiresAuth && !authStore.token) {
    console.log('⚠️ Route requires auth but no token, redirecting to login');
    next('/login');
  } else {
    next();
  }
});

export default router