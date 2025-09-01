<template>
  <div class="mobile-admin-layout" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Mobile Header -->
    <header class="mobile-header">
      <div class="mobile-header-content">
        <button 
          @click="toggleSidebar" 
          class="mobile-menu-btn"
          :aria-label="sidebarOpen ? 'Close menu' : 'Open menu'"
        >
          <svg class="icon" viewBox="0 0 24 24">
            <path v-if="!sidebarOpen" d="M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2Z"/>
            <path v-else d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"/>
          </svg>
        </button>
        
        <div class="mobile-header-title">
          <h1>{{ pageTitle }}</h1>
          <span class="mobile-breadcrumb">{{ breadcrumb }}</span>
        </div>
        
        <div class="mobile-header-actions">
          <!-- Notifications -->
          <button 
            @click="showNotifications = !showNotifications" 
            class="mobile-action-btn"
            :class="{ 'has-notifications': unreadNotifications > 0 }"
          >
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>
            <span v-if="unreadNotifications > 0" class="notification-badge">
              {{ unreadNotifications > 99 ? '99+' : unreadNotifications }}
            </span>
          </button>
          
          <!-- User Menu -->
          <button 
            @click="showUserMenu = !showUserMenu" 
            class="mobile-user-btn"
          >
            <img 
              :src="user.avatar || '/assets/img/default-avatar.png'" 
              :alt="user.name"
              class="user-avatar"
            >
          </button>
        </div>
      </div>
    </header>

    <!-- Mobile Sidebar -->
    <aside class="mobile-sidebar" :class="{ 'open': sidebarOpen }">
      <div class="mobile-sidebar-content">
        <!-- Logo -->
        <div class="mobile-logo">
          <img src="/assets/img/logo.png" alt="RetirementAdvisorPro" />
          <span>Admin</span>
        </div>

        <!-- Navigation -->
        <nav class="mobile-nav">
          <div class="mobile-nav-section">
            <h3>Dashboard</h3>
            <ul>
              <li>
                <router-link 
                  to="/admin/dashboard" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z"/>
                  </svg>
                  Overview
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/admin/analytics" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M22,21H2V3H4V19H6V10H10V19H12V6H16V19H18V14H22V21Z"/>
                  </svg>
                  Analytics
                </router-link>
              </li>
            </ul>
          </div>

          <div class="mobile-nav-section">
            <h3>Management</h3>
            <ul>
              <li>
                <router-link 
                  to="/admin/users" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M16,4C18.21,4 20,5.79 20,8C20,10.21 18.21,12 16,12C13.79,12 12,10.21 12,8C12,5.79 13.79,4 16,4M16,14C20.42,14 24,15.79 24,18V20H8V18C8,15.79 11.58,14 16,14M6,6H2V4H6V6M6,8H2V10H6V8M6,12H2V14H6V12Z"/>
                  </svg>
                  Users
                  <span v-if="pendingUsers > 0" class="nav-badge">{{ pendingUsers }}</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/admin/support" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2M6,9V7H18V9H6M14,11V13H6V11H14M16,15V17H6V15H16Z"/>
                  </svg>
                  Support
                  <span v-if="openTickets > 0" class="nav-badge urgent">{{ openTickets }}</span>
                </router-link>
              </li>
              <li>
                <router-link 
                  to="/admin/monitoring" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M3,3V21H21V19H5V3H3M18,17H20V10H18V17M14,17H16V7H14V17M10,17H12V13H10V17M6,17H8V15H6V17Z"/>
                  </svg>
                  Monitoring
                  <span v-if="systemAlerts > 0" class="nav-badge alert">{{ systemAlerts }}</span>
                </router-link>
              </li>
            </ul>
          </div>

          <div class="mobile-nav-section">
            <h3>Configuration</h3>
            <ul>
              <li>
                <router-link 
                  to="/admin/configuration" 
                  class="mobile-nav-link"
                  @click="closeSidebar"
                >
                  <svg class="icon" viewBox="0 0 24 24">
                    <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.97 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.95C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.95L19.05,18.95C19.27,19.04 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
                  </svg>
                  Settings
                </router-link>
              </li>
            </ul>
          </div>
        </nav>

        <!-- User Profile in Sidebar -->
        <div class="mobile-user-profile">
          <div class="user-info">
            <img 
              :src="user.avatar || '/assets/img/default-avatar.png'" 
              :alt="user.name"
              class="user-avatar-large"
            >
            <div class="user-details">
              <span class="user-name">{{ user.name }}</span>
              <span class="user-role">{{ user.role }}</span>
            </div>
          </div>
          <button @click="logout" class="logout-btn">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z"/>
            </svg>
            Logout
          </button>
        </div>
      </div>
    </aside>

    <!-- Sidebar Overlay -->
    <div 
      v-if="sidebarOpen" 
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>

    <!-- Main Content -->
    <main class="mobile-main-content">
      <!-- Quick Actions Bar -->
      <div v-if="showQuickActions" class="mobile-quick-actions">
        <button 
          v-for="action in quickActions" 
          :key="action.id"
          @click="executeQuickAction(action)"
          class="quick-action-btn"
          :class="action.class"
        >
          <svg class="icon" viewBox="0 0 24 24">
            <path :d="action.icon"/>
          </svg>
          <span>{{ action.label }}</span>
        </button>
      </div>

      <!-- Page Content -->
      <div class="mobile-page-content">
        <slot />
      </div>
    </main>

    <!-- Bottom Navigation (Alternative layout) -->
    <nav v-if="useBottomNav" class="mobile-bottom-nav">
      <router-link 
        v-for="item in bottomNavItems"
        :key="item.path"
        :to="item.path"
        class="bottom-nav-item"
        :class="{ 'active': $route.path === item.path }"
      >
        <svg class="icon" viewBox="0 0 24 24">
          <path :d="item.icon"/>
        </svg>
        <span>{{ item.label }}</span>
        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
      </router-link>
    </nav>

    <!-- Notification Panel -->
    <transition name="slide-right">
      <div v-if="showNotifications" class="notification-panel">
        <div class="notification-header">
          <h3>Notifications</h3>
          <button @click="showNotifications = false" class="close-btn">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
            </svg>
          </button>
        </div>
        
        <div class="notification-list">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.read }"
          >
            <div class="notification-icon" :class="notification.type">
              <svg class="icon" viewBox="0 0 24 24">
                <path :d="getNotificationIcon(notification.type)"/>
              </svg>
            </div>
            <div class="notification-content">
              <h4>{{ notification.title }}</h4>
              <p>{{ notification.message }}</p>
              <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Toast Notifications -->
    <transition-group name="toast" class="toast-container">
      <div 
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <div class="toast-content">
          <svg class="toast-icon" viewBox="0 0 24 24">
            <path :d="getToastIcon(toast.type)"/>
          </svg>
          <div class="toast-message">
            <h4 v-if="toast.title">{{ toast.title }}</h4>
            <p>{{ toast.message }}</p>
          </div>
        </div>
        <button @click="dismissToast(toast.id)" class="toast-close">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
          </svg>
        </button>
      </div>
    </transition-group>

    <!-- Offline Indicator -->
    <div v-if="!isOnline" class="offline-indicator">
      <svg class="icon" viewBox="0 0 24 24">
        <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H14A7,7 0 0,1 21,14H19A5,5 0 0,0 14,9H13V10.27C13.6,10.61 14,11.26 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10C12.74,10 13.39,10.4 13.73,11H14A3,3 0 0,0 11,8H10V6.73C9.4,6.39 9,5.74 9,5A2,2 0 0,1 11,3H12M7,9V10H5V12H7V13H9V11H7V9M10,2H14V4H10V2Z"/>
      </svg>
      <span>You're offline</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'MobileAdminLayout',
  props: {
    pageTitle: {
      type: String,
      default: 'Dashboard'
    },
    breadcrumb: {
      type: String,
      default: ''
    },
    showQuickActions: {
      type: Boolean,
      default: false
    },
    useBottomNav: {
      type: Boolean,
      default: false
    }
  },
  
  setup(props) {
    const router = useRouter();
    const route = useRoute();
    const authStore = useAuthStore();
    
    // Reactive state
    const sidebarOpen = ref(false);
    const showNotifications = ref(false);
    const showUserMenu = ref(false);
    const isOnline = ref(navigator.onLine);
    
    // Notification data
    const unreadNotifications = ref(5);
    const notifications = reactive([
      {
        id: 1,
        type: 'warning',
        title: 'System Alert',
        message: 'High server load detected',
        created_at: new Date(),
        read: false
      },
      {
        id: 2,
        type: 'info',
        title: 'New User Registration',
        message: '3 new users registered today',
        created_at: new Date(Date.now() - 3600000),
        read: false
      }
    ]);
    
    // Toast notifications
    const toasts = reactive([]);
    
    // Quick actions
    const quickActions = reactive([
      {
        id: 'add-user',
        label: 'Add User',
        icon: 'M15,14C12.33,14 7,15.33 7,18V20H23V18C23,15.33 17.67,14 15,14M6,10V7H4V10H1V12H4V15H6V12H9V10M15,12A4,4 0 0,0 19,8A4,4 0 0,0 15,4A4,4 0 0,0 11,8A4,4 0 0,0 15,12Z',
        class: 'primary'
      },
      {
        id: 'create-report',
        label: 'Report',
        icon: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z',
        class: 'secondary'
      }
    ]);
    
    // Bottom navigation items
    const bottomNavItems = reactive([
      {
        path: '/admin/dashboard',
        label: 'Dashboard',
        icon: 'M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z'
      },
      {
        path: '/admin/users',
        label: 'Users',
        icon: 'M16,4C18.21,4 20,5.79 20,8C20,10.21 18.21,12 16,12C13.79,12 12,10.21 12,8C12,5.79 13.79,4 16,4M16,14C20.42,14 24,15.79 24,18V20H8V18C8,15.79 11.58,14 16,14Z',
        badge: 3
      },
      {
        path: '/admin/support',
        label: 'Support',
        icon: 'M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C22,2.89 21.1,2 20,2Z',
        badge: 7
      },
      {
        path: '/admin/analytics',
        label: 'Analytics',
        icon: 'M22,21H2V3H4V19H6V10H10V19H12V6H16V19H18V14H22V21Z'
      }
    ]);
    
    // Computed properties
    const user = computed(() => authStore.user);
    const pendingUsers = ref(3);
    const openTickets = ref(7);
    const systemAlerts = ref(2);
    
    // Methods
    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value;
    };
    
    const closeSidebar = () => {
      sidebarOpen.value = false;
    };
    
    const executeQuickAction = (action) => {
      // Handle quick actions
      switch (action.id) {
        case 'add-user':
          router.push('/admin/users/create');
          break;
        case 'create-report':
          router.push('/admin/reports/create');
          break;
      }
    };
    
    const logout = () => {
      authStore.logout();
      router.push('/login');
    };
    
    const formatTime = (date) => {
      return new Date(date).toLocaleTimeString();
    };
    
    const getNotificationIcon = (type) => {
      const icons = {
        warning: 'M12,2L13.09,8.26L22,9L17,14L18.18,22L12,19.27L5.82,22L7,14L2,9L10.91,8.26L12,2Z',
        info: 'M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z',
        error: 'M12,2C17.53,2 22,6.47 22,12C22,17.53 17.53,22 12,22C6.47,22 2,17.53 2,12C2,6.47 6.47,2 12,2M15.59,7L12,10.59L8.41,7L7,8.41L10.59,12L7,15.59L8.41,17L12,13.41L15.59,17L17,15.59L13.41,12L17,8.41L15.59,7Z',
        success: 'M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M11,16.5L18,9.5L16.59,8.09L11,13.67L7.41,10.09L6,11.5L11,16.5Z'
      };
      return icons[type] || icons.info;
    };
    
    const getToastIcon = (type) => {
      return getNotificationIcon(type);
    };
    
    const showToast = (message, type = 'info', title = null) => {
      const toast = {
        id: Date.now(),
        message,
        type,
        title
      };
      toasts.push(toast);
      
      // Auto dismiss after 5 seconds
      setTimeout(() => {
        dismissToast(toast.id);
      }, 5000);
    };
    
    const dismissToast = (id) => {
      const index = toasts.findIndex(t => t.id === id);
      if (index > -1) {
        toasts.splice(index, 1);
      }
    };
    
    // Lifecycle
    onMounted(() => {
      // Register service worker
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
          .then(registration => {
            console.log('SW registered: ', registration);
          })
          .catch(registrationError => {
            console.log('SW registration failed: ', registrationError);
          });
      }
      
      // Online/offline listeners
      window.addEventListener('online', () => {
        isOnline.value = true;
        showToast('Connection restored', 'success');
      });
      
      window.addEventListener('offline', () => {
        isOnline.value = false;
        showToast('You are now offline', 'warning');
      });
      
      // Close sidebar on route change
      router.afterEach(() => {
        closeSidebar();
      });
    });
    
    onUnmounted(() => {
      window.removeEventListener('online', () => isOnline.value = true);
      window.removeEventListener('offline', () => isOnline.value = false);
    });
    
    return {
      sidebarOpen,
      showNotifications,
      showUserMenu,
      isOnline,
      unreadNotifications,
      notifications,
      toasts,
      quickActions,
      bottomNavItems,
      user,
      pendingUsers,
      openTickets,
      systemAlerts,
      toggleSidebar,
      closeSidebar,
      executeQuickAction,
      logout,
      formatTime,
      getNotificationIcon,
      getToastIcon,
      showToast,
      dismissToast
    };
  }
};
</script>

<style scoped>
/* Mobile-First Admin Layout Styles */
.mobile-admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/* Mobile Header */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #1e293b;
  color: white;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mobile-header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
}

.mobile-menu-btn {
  background: none;
  border: none;
  color: white;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  margin-right: 16px;
}

.mobile-menu-btn:hover {
  background: rgba(255,255,255,0.1);
}

.mobile-header-title {
  flex: 1;
  min-width: 0;
}

.mobile-header-title h1 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mobile-breadcrumb {
  font-size: 12px;
  opacity: 0.7;
}

.mobile-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-action-btn, .mobile-user-btn {
  background: none;
  border: none;
  color: white;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
}

.mobile-action-btn:hover, .mobile-user-btn:hover {
  background: rgba(255,255,255,0.1);
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ef4444;
  color: white;
  border-radius: 12px;
  padding: 2px 6px;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

/* Mobile Sidebar */
.mobile-sidebar {
  position: fixed;
  top: 0;
  left: -300px;
  width: 300px;
  height: 100%;
  background: #0f172a;
  color: white;
  z-index: 1100;
  transition: left 0.3s ease;
  overflow-y: auto;
}

.mobile-sidebar.open {
  left: 0;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 1050;
}

.mobile-sidebar-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #334155;
}

.mobile-logo img {
  width: 32px;
  height: 32px;
}

.mobile-logo span {
  font-size: 18px;
  font-weight: 600;
}

/* Mobile Navigation */
.mobile-nav-section {
  margin-bottom: 24px;
}

.mobile-nav-section h3 {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748b;
  margin: 0 0 12px 0;
}

.mobile-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  position: relative;
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  background: #1e293b;
  color: #3b82f6;
}

.mobile-nav-link .icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
  flex-shrink: 0;
}

.nav-badge {
  background: #ef4444;
  color: white;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 10px;
  margin-left: auto;
}

.nav-badge.urgent {
  background: #dc2626;
  animation: pulse 2s infinite;
}

.nav-badge.alert {
  background: #f59e0b;
}

/* User Profile in Sidebar */
.mobile-user-profile {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #334155;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-avatar-large {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  display: block;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  display: block;
  font-size: 12px;
  color: #64748b;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  background: none;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #334155;
}

/* Main Content */
.mobile-main-content {
  flex: 1;
  margin-top: 60px;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}

/* Quick Actions */
.mobile-quick-actions {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  min-width: 80px;
  flex-shrink: 0;
}

.quick-action-btn.primary {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.quick-action-btn.secondary {
  background: #6b7280;
  color: white;
  border-color: #6b7280;
}

.quick-action-btn .icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.quick-action-btn span {
  font-size: 12px;
}

/* Page Content */
.mobile-page-content {
  padding: 16px;
  min-height: calc(100vh - 120px);
}

/* Bottom Navigation */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #1e293b;
  display: flex;
  z-index: 1000;
  border-top: 1px solid #334155;
}

.bottom-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  text-decoration: none;
  position: relative;
  padding: 8px;
}

.bottom-nav-item.active {
  color: #3b82f6;
}

.bottom-nav-item .icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
  margin-bottom: 4px;
}

.bottom-nav-item span {
  font-size: 10px;
}

/* Notification Panel */
.notification-panel {
  position: fixed;
  top: 60px;
  right: 0;
  width: 320px;
  max-width: 100vw;
  height: calc(100vh - 60px);
  background: white;
  box-shadow: -2px 0 8px rgba(0,0,0,0.1);
  z-index: 1200;
  overflow-y: auto;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.notification-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
}

.close-btn:hover {
  background: #f1f5f9;
}

.notification-list {
  padding: 0;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.notification-item.unread {
  background: #f8fafc;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.warning {
  background: #fef3c7;
  color: #d97706;
}

.notification-icon.info {
  background: #dbeafe;
  color: #2563eb;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
}

.notification-content p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.notification-time {
  font-size: 11px;
  color: #9ca3af;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 80px;
  right: 16px;
  z-index: 2000;
  pointer-events: none;
}

.toast {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  margin-bottom: 8px;
  max-width: 320px;
  pointer-events: auto;
}

.toast.success {
  border-left: 4px solid #10b981;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast.warning {
  border-left: 4px solid #f59e0b;
}

.toast.info {
  border-left: 4px solid #3b82f6;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  padding-right: 40px;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.toast.success .toast-icon { fill: #10b981; }
.toast.error .toast-icon { fill: #ef4444; }
.toast.warning .toast-icon { fill: #f59e0b; }
.toast.info .toast-icon { fill: #3b82f6; }

.toast-message h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
}

.toast-message p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.toast-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.toast-close:hover {
  background: #f1f5f9;
}

/* Offline Indicator */
.offline-indicator {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  background: #f59e0b;
  color: white;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  z-index: 1500;
}

.offline-indicator .icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

/* Animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.slide-right-enter-active, .slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-leave-to {
  transform: translateX(100%);
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Common icon styles */
.icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .mobile-sidebar {
    width: 280px;
    left: -280px;
  }
  
  .notification-panel {
    width: 100vw;
  }
  
  .mobile-header-title h1 {
    font-size: 16px;
  }
  
  .mobile-page-content {
    padding: 12px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .mobile-admin-layout {
    background: #0f172a;
    color: white;
  }
  
  .notification-panel {
    background: #1e293b;
    color: white;
  }
  
  .toast {
    background: #1e293b;
    color: white;
  }
  
  .quick-action-btn {
    background: #1e293b;
    color: white;
    border-color: #334155;
  }
}
</style>