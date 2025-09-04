<template>
  <aside id="sidebar" class="sidebar js-navbar-vertical-aside" :class="{ 'sidebar-collapsed': isCollapsed }" :style="{ width: isCollapsed ? '60px' : '270px' }">
    <div class="navbar-vertical-container">
      <div class="navbar-vertical-footer-offset">
        <!-- Content -->
        <div class="navbar-vertical-content">
          <div id="navbarVerticalMenu" class="nav nav-pills nav-vertical card-navbar-nav">
            <!-- Collapse -->
            <div class="nav-item">
              <a class="nav-link" href="/dashboard" role="button" :title="isCollapsed ? 'Dashboard' : ''" aria-expanded="true" aria-controls="navbarVerticalMenuDashboards">
                <i class="bi-people nav-icon"></i>
                <span class="nav-link-title" v-show="!isCollapsed">Dashboard</span>
              </a>
            </div>
            <!-- End Collapse -->
            <!-- Collapse -->
            <div class="navbar-nav nav-compact">

            </div>
            <div id="navbarVerticalMenuPagesMenu">
              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link" :class="{ 'dropdown-toggle': !isCollapsed }" href="#navbarVerticalMenuPagesUsersMenu" role="button" 
                   :data-bs-toggle="isCollapsed ? '' : 'collapse'" :data-bs-target="isCollapsed ? '' : '#navbarVerticalMenuPagesUsersMenu'" 
                   :title="isCollapsed ? 'Clients' : ''" aria-expanded="false" aria-controls="navbarVerticalMenuPagesUsersMenu">
                  <i class="bi-people nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Clients</span>
                </a>

                <div id="navbarVerticalMenuPagesUsersMenu" class="nav-collapse collapse" v-show="!isCollapsed" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link " href="/clients">Overview</a>
                  <a class="nav-link " href="/clients/create">Add Client <span class="badge bg-info rounded-pill ms-1">Hot</span></a>
                </div>
              </div>
              <!-- End Collapse -->

              <!-- Communication Center -->
              <div class="nav-item">
                <router-link class="nav-link" to="/communication-center" :title="isCollapsed ? 'Communication Center' : ''" role="button">
                  <i class="bi-inbox nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Communication Center</span>
                  <span v-if="totalUnreadCommunications > 0" class="badge bg-primary rounded-pill ms-1" v-show="!isCollapsed">{{ totalUnreadCommunications }}</span>
                </router-link>
              </div>
              <!-- End Communication Center -->

              <!-- Task Management -->
              <div class="nav-item">
                <router-link class="nav-link" to="/tasks" :title="isCollapsed ? 'Task Management' : ''" role="button">
                  <i class="bi-check-square nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Task Management</span>
                  <span v-if="pendingTasksCount > 0" class="badge bg-warning rounded-pill ms-1" v-show="!isCollapsed">{{ pendingTasksCount }}</span>
                </router-link>
              </div>
              <!-- End Task Management -->

              <!-- Calendar -->
              <div class="nav-item">
                <router-link class="nav-link" to="/calendar" :title="isCollapsed ? 'Calendar' : ''" role="button">
                  <i class="bi-calendar-event nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Calendar</span>
                  <span v-if="todayEventsCount > 0" class="badge bg-info rounded-pill ms-1" v-show="!isCollapsed">{{ todayEventsCount }}</span>
                </router-link>
              </div>
              <!-- End Calendar -->

              <!-- Document Management -->
              <div class="nav-item">
                <a class="nav-link" href="/documents" :title="isCollapsed ? 'Documents' : ''" role="button">
                  <i class="bi-files nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Documents</span>
                  <span class="badge bg-info rounded-pill ms-1" v-show="!isCollapsed">New</span>
                </a>
              </div>
              <!-- End Document Management -->

              <!-- Report Center -->
              <div class="nav-item">
                <router-link class="nav-link" to="/report-center" :title="isCollapsed ? 'Report Center' : ''" role="button">
                  <i class="bi-file-earmark-slides nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Report Center</span>
                  <span class="badge bg-primary rounded-pill ms-1" v-show="!isCollapsed">AI</span>
                </router-link>
              </div>
              <!-- End Report Center -->

              <!-- Compliance Section -->
              <div class="nav-item">
                <a class="nav-link" :class="{ 'dropdown-toggle': !isCollapsed }" href="#navbarVerticalMenuComplianceMenu" role="button" 
                   :data-bs-toggle="isCollapsed ? '' : 'collapse'" :data-bs-target="isCollapsed ? '' : '#navbarVerticalMenuComplianceMenu'" 
                   :title="isCollapsed ? 'FINRA Compliance' : ''" aria-expanded="false" aria-controls="navbarVerticalMenuComplianceMenu">
                  <i class="bi-shield-check nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">FINRA Compliance</span>
                  <span class="badge bg-success rounded-pill ms-1" v-show="!isCollapsed">✓</span>
                </a>

                <div id="navbarVerticalMenuComplianceMenu" class="nav-collapse collapse" v-show="!isCollapsed" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <router-link class="nav-link" to="/compliance">
                    <i class="bi-speedometer2 nav-icon me-2"></i>Compliance Dashboard
                  </router-link>
                  <router-link class="nav-link" to="/compliance/audit-trail">
                    <i class="bi-list-check nav-icon me-2"></i>Audit Trail
                    <span v-if="complianceAlerts > 0" class="badge bg-warning rounded-pill ms-1">{{ complianceAlerts }}</span>
                  </router-link>
                  <router-link class="nav-link" to="/compliance/retention">
                    <i class="bi-clock-history nav-icon me-2"></i>Document Retention
                  </router-link>
                  <router-link class="nav-link" to="/compliance/reports">
                    <i class="bi-file-earmark-text nav-icon me-2"></i>Compliance Reports
                  </router-link>
                </div>
              </div>
              <!-- End Compliance Section -->

              
              <!-- Client navigation section - only shown when in client context -->
              <div class="nav-item" v-if="isClientRoute">
                <a class="nav-link" :class="{ 'dropdown-toggle': !isCollapsed }" href="#navbarVerticalMenuCurrentClient" role="button" 
                   :data-bs-toggle="isCollapsed ? '' : 'collapse'" :data-bs-target="isCollapsed ? '' : '#navbarVerticalMenuCurrentClient'" 
                   :title="isCollapsed ? 'Current Client' : ''" aria-expanded="true" aria-controls="navbarVerticalMenuCurrentClient">
                  <i class="bi-person nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Current Client</span>
                  <span class="badge bg-primary rounded-pill ms-1" v-show="!isCollapsed">Active</span>
                </a>

                                  <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" :class="{ show: isClientRoute && !isCollapsed }" v-show="!isCollapsed" data-bs-parent="#navbarVerticalMenuPagesMenu">
                    <router-link class="nav-link" :to="{ name: 'ClientDetail', params: { id: currentClientId }}">
                      <i class="bi-person-badge nav-icon me-2"></i>Client Detail
                    </router-link>
                    
                    <router-link class="nav-link" :to="{ name: 'ComparisonReport', params: { id: currentClientId }}">
                      <i class="bi-bar-chart nav-icon me-2"></i>Comparison Report
                    </router-link>
                    
                    <!-- For each scenario, create a simple link -->
                    <div v-for="scenario in clientScenarios" :key="scenario.id" class="nav-item">
                      <router-link class="nav-link ps-3" 
                        :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'overview' }}">
                        <i class="bi-graph-up nav-icon me-2"></i>
                        <strong>{{ scenario.name.length > 12 ? scenario.name.slice(0, 12) + '' : scenario.name }}</strong>
                        <span v-if="isCurrentScenario(scenario.id)" class="badge bg-info rounded-pill ms-1">Current</span>
                      </router-link>
                    </div>
                  </div>
              </div>
              <!-- End Collapse -->
              
              <!-- Admin Section -->
              <div class="nav-item" v-if="isAdminUser">
                <a class="nav-link" :class="{ 'dropdown-toggle': !isCollapsed }" href="#navbarVerticalMenuAdminMenu" role="button" 
                   :data-bs-toggle="isCollapsed ? '' : 'collapse'" :data-bs-target="isCollapsed ? '' : '#navbarVerticalMenuAdminMenu'" 
                   :title="isCollapsed ? 'Admin Panel' : ''" aria-expanded="false" aria-controls="navbarVerticalMenuAdminMenu">
                  <i class="bi-gear nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Admin Panel</span>
                  <span v-if="adminRole === 'super_admin'" class="badge bg-danger rounded-pill ms-1" v-show="!isCollapsed">Super</span>
                </a>

                <div id="navbarVerticalMenuAdminMenu" class="nav-collapse collapse" v-show="!isCollapsed" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <router-link class="nav-link" to="/admin/dashboard">
                    <i class="bi-speedometer2 nav-icon me-2"></i>Dashboard
                  </router-link>
                  <router-link v-if="canAccessSection('user_management')" class="nav-link" to="/admin/users">
                    <i class="bi-people nav-icon me-2"></i>User Management
                  </router-link>
                  <router-link v-if="canAccessSection('user_management')" class="nav-link" to="/admin/impersonation">
                    <i class="bi-person-check nav-icon me-2"></i>Impersonation Logs
                  </router-link>
                  <router-link v-if="canAccessSection('analytics')" class="nav-link" to="/admin/analytics">
                    <i class="bi-bar-chart nav-icon me-2"></i>Analytics
                  </router-link>
                  <router-link v-if="canAccessSection('billing')" class="nav-link" to="/admin/billing">
                    <i class="bi-credit-card nav-icon me-2"></i>Billing
                  </router-link>
                  <router-link v-if="canAccessSection('system_monitoring')" class="nav-link" to="/admin/monitoring">
                    <i class="bi-cpu nav-icon me-2"></i>System Monitoring
                  </router-link>
                  <router-link v-if="canAccessSection('system_monitoring')" class="nav-link" to="/admin/performance">
                    <i class="bi-speedometer2 nav-icon me-2"></i>Performance
                  </router-link>
                  <router-link v-if="canAccessSection('system_monitoring')" class="nav-link" to="/admin/alerts">
                    <i class="bi-bell nav-icon me-2"></i>Alert Management
                  </router-link>
                  <router-link v-if="canAccessSection('support_tools')" class="nav-link" to="/admin/support">
                    <i class="bi-life-preserver nav-icon me-2"></i>Support Tools
                  </router-link>
                  <router-link v-if="canAccessSection('support_tools')" class="nav-link" to="/admin/support/tickets">
                    <i class="bi-ticket nav-icon me-2"></i>Support Tickets
                  </router-link>
                </div>
              </div>
              <!-- End Admin Section -->
            </div>
            <!-- End Collapse -->


          

          </div>

        </div>
        <!-- End Content -->
      </div>
    </div>
    
    <!-- Navbar Vertical Toggle - positioned on right side -->
    <button type="button" class="navbar-aside-toggler-right" @click="toggleSidebar">
      <i v-if="!isCollapsed" class="bi-chevron-left" title="Collapse"></i>
      <i v-else class="bi-chevron-right" title="Expand"></i>
    </button>
    <!-- End Navbar Vertical Toggle -->
  </aside>
</template>

<script>
import { useCommunicationStore } from '@/stores/communicationStore';
import { useTaskStore } from '@/stores/taskStore';
import { useCalendarStore } from '@/stores/calendarStore';
import { hasCRMAccess } from '@/utils/permissions';
import { API_CONFIG } from '@/config';

export default {
  name: 'Sidebar',
  data() {
    return {
      currentClientId: null,
      currentScenarioId: null,
      clientScenarios: [],
      isClientRoute: false,
      isCollapsed: false,
      totalUnreadCommunications: 0,
      pendingTasksCount: 0,
      todayEventsCount: 0,
      complianceAlerts: 0,
      communicationStore: null,
      taskStore: null,
      calendarStore: null
    };
  },
  computed: {
    hasCRMAccess() {
      // Use auth store if available, otherwise fall back to localStorage
      try {
        const { useAuthStore } = require('@/stores/auth');
        const authStore = useAuthStore();
        return hasCRMAccess(authStore.user);
      } catch (error) {
        // Fallback to direct function call which will check localStorage
        return hasCRMAccess(null);
      }
    },
    
    // Admin-related computed properties
    isAdminUser() {
      try {
        const { useAuthStore } = require('@/stores/auth');
        const authStore = useAuthStore();
        return authStore.user?.is_admin_user || false;
      } catch (error) {
        // Fallback to localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        return user.is_admin_user || false;
      }
    },
    
    adminRole() {
      try {
        const { useAuthStore } = require('@/stores/auth');
        const authStore = useAuthStore();
        return authStore.user?.admin_role || '';
      } catch (error) {
        // Fallback to localStorage
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        return user.admin_role || '';
      }
    }
  },
  async created() {
    // Initialize stores
    this.communicationStore = useCommunicationStore();
    this.taskStore = useTaskStore();
    this.calendarStore = useCalendarStore();
    
    // Restore collapsed state from localStorage
    const savedCollapsedState = localStorage.getItem('sidebarCollapsed');
    if (savedCollapsedState !== null) {
      this.isCollapsed = savedCollapsedState === 'true';
    }
    
    // Load counts for badges
    await Promise.all([
      this.loadUnreadCount(),
      this.loadPendingTasksCount(),
      this.loadTodayEventsCount()
    ]);
    
    // Create handler for scenario deletion events
    this.handleScenarioDeleted = (event) => {
      console.log('🔄 Sidebar: Scenario deleted event received:', event.detail);
      console.log('🔍 Current client ID:', this.currentClientId);
      console.log('🔍 Event client ID:', event.detail?.clientId);
      
      // Refresh the scenarios list
      if (event.detail && event.detail.clientId == this.currentClientId) {
        console.log('✅ Client IDs match, refreshing scenarios...');
        this.fetchClientScenarios();
      } else {
        console.log('❌ Client IDs do not match, skipping refresh');
      }
    };
    
    // Listen for scenario deletion events
    window.addEventListener('scenario-deleted', this.handleScenarioDeleted);
    
    // Check the initial route
    this.checkIfClientRoute(this.$route);
    
    // Listen for route changes to update state
    this.$router.beforeEach((to, from, next) => {
      // Check if this is a client-related route
      this.checkIfClientRoute(to);
      
      // If we have client and scenario IDs in the route
      if (to.params.id && to.params.scenarioid) {
        this.currentClientId = to.params.id;
        this.currentScenarioId = to.params.scenarioid;
        
        // Store current values in localStorage for persistence
        localStorage.setItem('currentClientId', this.currentClientId);
        localStorage.setItem('currentScenarioId', this.currentScenarioId);
        
        // Fetch scenarios for this client
        this.fetchClientScenarios();
      }
      next();
    });
    
    // Initialize client info from route or localStorage
    if (this.$route.params.id) {
      this.currentClientId = this.$route.params.id;
      
      if (this.$route.params.scenarioid) {
        this.currentScenarioId = this.$route.params.scenarioid;
      }
      
      // Fetch client scenarios
      this.fetchClientScenarios();
    } 
    // Try from localStorage if not in route
    else if (!this.isClientRoute) {
      const storedClientId = localStorage.getItem('currentClientId');
      const storedScenarioId = localStorage.getItem('currentScenarioId');
      
      // Only use stored values if we're not on a client page
      // This prevents showing the client nav on non-client pages
      if (storedClientId && !this.isClientRoute) {
        this.currentClientId = storedClientId;
        this.currentScenarioId = storedScenarioId;
        this.fetchClientScenarios();
      }
    }
  },
  
  destroyed() {
    // Clean up event listener to prevent memory leaks
    if (this.handleScenarioDeleted) {
      window.removeEventListener('scenario-deleted', this.handleScenarioDeleted);
    }
  },
  
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
      // Save state to localStorage
      localStorage.setItem('sidebarCollapsed', this.isCollapsed.toString());
      // Emit event to parent if needed for layout adjustments
      this.$emit('sidebar-toggle', this.isCollapsed);
    },
    
    // Check if a scenario is the currently selected one
    isCurrentScenario(scenarioId) {
      // First check if we have a current scenario ID and we're viewing a scenario
      if (!this.currentScenarioId || !this.$route.params.scenarioid) {
        return false;
      }
      
      // Compare as integers to ensure accurate comparison
      return parseInt(scenarioId) === parseInt(this.currentScenarioId);
    },
    
    // Check if current route is client-related
    checkIfClientRoute(route) {
      // Reset client status if it's a different client
      if (route.params && route.params.id && this.currentClientId && route.params.id !== this.currentClientId) {
        console.log('Different client detected, resetting state');
        this.currentScenarioId = null;
      }
      
      // Consider these routes as client context routes
      const clientRoutes = ['ClientDetail', 'ScenarioDetail'];
      
      // Check if route name matches client routes
      if (route.name && clientRoutes.includes(route.name)) {
        this.isClientRoute = true;
        
        // If we're on a client detail page but not scenario, reset scenario context
        if (route.name === 'ClientDetail' && !route.params.scenarioid) {
          this.currentScenarioId = null;
        }
        
        return;
      }
      
      // Also check if the path includes client or scenario identifiers
      if (route.params && (route.params.id || route.params.clientId)) {
        this.isClientRoute = true;
        
        // No scenario context if we're just on a client page
        if (!route.params.scenarioid) {
          this.currentScenarioId = null;
        }
        
        return;
      }
      
      // Also check path structure
      const path = route.path || '';
      if (path.includes('/clients/') && path.split('/').length > 3) {
        this.isClientRoute = true;
        
        // Reset scenario context if not in URL
        if (!path.includes('/scenario/')) {
          this.currentScenarioId = null;
        }
        
        return;
      }
      
      // Not a client route
      this.isClientRoute = false;
      
      // When leaving client routes, reset scenario context
      this.currentScenarioId = null;
    },
    
    fetchClientScenarios() {
      if (!this.currentClientId) return;
      
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const headers = { Authorization: `Bearer ${token}` };
      
      // Fetch client data which includes scenarios
      fetch(`${API_CONFIG.API_URL}/clients/${this.currentClientId}/`, { headers })
        .then(response => response.json())
        .then(data => {
          if (data && data.scenarios) {
            this.clientScenarios = data.scenarios;
            console.log('Loaded scenarios for client:', this.clientScenarios);
          }
        })
        .catch(error => {
          console.error('Error loading client scenarios:', error);
        });
    },
    
    async loadUnreadCount() {
      try {
        // Get total unread communications count
        await this.communicationStore.fetchCommunications({
          is_read: false,
          limit: 1
        });
        
        this.totalUnreadCommunications = this.communicationStore.totalCount || 0;
      } catch (error) {
        console.error('Error loading unread count:', error);
        this.totalUnreadCommunications = 0;
      }
    },
    
    async loadPendingTasksCount() {
      try {
        // Get pending tasks count (not completed)
        await this.taskStore.fetchTasks({
          status: 'pending',
          limit: 1
        });
        
        this.pendingTasksCount = this.taskStore.totalCount || 0;
      } catch (error) {
        console.error('Error loading pending tasks count:', error);
        this.pendingTasksCount = 0;
      }
    },
    
    async loadTodayEventsCount() {
      try {
        // Get today's events count
        const today = new Date().toISOString().split('T')[0];
        await this.calendarStore.fetchCalendarEvents({
          start_date: today,
          end_date: today,
          limit: 1
        });
        
        this.todayEventsCount = this.calendarStore.todayEvents?.length || 0;
      } catch (error) {
        console.error('Error loading today events count:', error);
        this.todayEventsCount = 0;
      }
    },
    
    // Admin access method
    canAccessSection(section) {
      // Super admin can access everything
      if (this.adminRole === 'super_admin') {
        return true;
      }
      
      // Define section permissions mapping
      const sectionPermissions = {
        'user_management': ['admin', 'support'],
        'billing': ['admin', 'billing'], 
        'analytics': ['admin', 'analyst'],
        'system_monitoring': ['admin'],
        'support_tools': ['admin', 'support'],
      };
      
      const allowedRoles = sectionPermissions[section] || [];
      return allowedRoles.includes(this.adminRole);
    }
  }
};
</script>

<style scoped>
/* You can move real styles from dist/assets/css or define here */
.sidebar {
  position: relative;
  width: 250px;
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-top: 1rem;
  border-right: 1px solid #e3e6f0;
}

/* Fix for scrolling when content overflows */
.navbar-vertical-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar-vertical-footer-offset {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding-bottom: 0 !important; /* Remove footer offset space */
}

.navbar-vertical-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 2rem;
  padding-top: 2.5rem;
}

/* Ensure the dropdown menu items are visible within scroll container */
#navbarVerticalMenuCurrentClient {
  max-height: calc(100vh - 400px); /* Adjust based on other nav items */
  overflow-y: auto;
}

/* Optional: Add subtle scrollbar styling */
.navbar-vertical-content::-webkit-scrollbar,
#navbarVerticalMenuCurrentClient::-webkit-scrollbar {
  width: 6px;
}

.navbar-vertical-content::-webkit-scrollbar-track,
#navbarVerticalMenuCurrentClient::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.navbar-vertical-content::-webkit-scrollbar-thumb,
#navbarVerticalMenuCurrentClient::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.navbar-vertical-content::-webkit-scrollbar-thumb:hover,
#navbarVerticalMenuCurrentClient::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Collapsed sidebar styles */
.sidebar-collapsed .nav-link {
  justify-content: center;
  padding: 0.75rem 0.5rem;
}

.sidebar-collapsed .nav-icon {
  margin-right: 0 !important;
  font-size: 1.2rem;
}

.sidebar-collapsed .navbar-aside-toggler {
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Hide badges and text when collapsed */
.sidebar-collapsed .nav-link-title,
.sidebar-collapsed .badge {
  display: none !important;
}

/* Center the icons in collapsed mode */
.sidebar-collapsed .nav-link {
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Smooth transition */
.sidebar {
  transition: width 0.3s ease;
}

/* Tooltip styles for collapsed mode */
.sidebar-collapsed .nav-link:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* Remove dropdown arrows in collapsed mode */
.sidebar-collapsed .dropdown-toggle::after {
  display: none;
}

/* Toggle button styling - positioned on right side */
.navbar-aside-toggler-right {
  position: absolute;
  top: 50%;
  right: -15px;
  transform: translateY(-50%);
  background: #ffffff;
  border: 1px solid #e3e6f0;
  color: #6c757d;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  width: 30px;
  height: 30px;
}

.navbar-aside-toggler-right:hover {
  background-color: #f8f9fa;
  color: #495057;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.navbar-aside-toggler-right i {
  font-size: 0.9rem;
}

/* Reduce spacing for first navigation item */
#navbarVerticalMenu .nav-item:first-child {
  margin-top: 0;
}

#navbarVerticalMenu .nav-item:first-child .nav-link {
  margin-top: 0;
}

</style>