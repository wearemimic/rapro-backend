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

              


              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link" :class="{ 'dropdown-toggle': !isCollapsed }" href="#navbarVerticalMenuIntegrationsMenu" role="button" 
                   :data-bs-toggle="isCollapsed ? '' : 'collapse'" :data-bs-target="isCollapsed ? '' : '#navbarVerticalMenuIntegrationsMenu'" 
                   :title="isCollapsed ? 'Integrations' : ''" aria-expanded="false" aria-controls="navbarVerticalMenuIntegrationsMenu">
                  <i class="bi-plug nav-icon"></i>
                  <span class="nav-link-title" v-show="!isCollapsed">Integrations</span>
                </a>

                <div id="navbarVerticalMenuIntegrationsMenu" class="nav-collapse collapse" v-show="!isCollapsed" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">CRM</a>
                </div>
              </div>
              
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
                    
                    <!-- For each scenario, create a collapsible section -->
                    <div v-for="scenario in clientScenarios" :key="scenario.id" class="nav-item">
                                          <!-- Non-clickable scenario name header -->
                    <a class="nav-link nav-link-title ps-3 dropdown-toggle" :href="'#scenario-' + scenario.id" role="button" 
                      data-bs-toggle="collapse" :data-bs-target="'#scenario-' + scenario.id" 
                      :aria-expanded="isCurrentScenario(scenario.id)" :aria-controls="'scenario-' + scenario.id">
                      <i class="bi-graph-up nav-icon me-2"></i>
                      <strong>{{ scenario.name.length > 12 ? scenario.name.slice(0, 12) + '' : scenario.name }}</strong>
                      <span v-if="isCurrentScenario(scenario.id)" class="badge bg-info rounded-pill ms-1">Current</span>
                    </a>
                    
                    <!-- Collapsible content for each scenario - only expanded for current scenario -->
                    <div :id="'scenario-' + scenario.id" class="nav-collapse collapse" :class="{ show: isCurrentScenario(scenario.id) }">
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'overview' }}">
                          Scenario Overview
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'financial' }}">
                          Financial Details
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'socialSecurity' }}">
                          Social Security Details
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'socialSecurity2' }}">
                          Social Security 2
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'medicare' }}">
                          Medicare Details
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'income' }}">
                          Income
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'rothConversion' }}">
                          Roth Conversion
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'worksheets' }}">
                          Social Security Worksheets
                        </router-link>
                        <router-link class="nav-link ps-4" 
                          :to="{ name: 'ScenarioDetail', params: { id: currentClientId, scenarioid: scenario.id }, query: { tab: 'nextSteps' }}">
                          Next Steps
                        </router-link>
                                            </div>
                    </div>
                  </div>
              </div>
              <!-- End Collapse -->
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
export default {
  name: 'Sidebar',
  data() {
    return {
      currentClientId: null,
      currentScenarioId: null,
      clientScenarios: [],
      isClientRoute: false,
      isCollapsed: false
    };
  },
  created() {
    // Restore collapsed state from localStorage
    const savedCollapsedState = localStorage.getItem('sidebarCollapsed');
    if (savedCollapsedState !== null) {
      this.isCollapsed = savedCollapsedState === 'true';
    }
    
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
      fetch(`http://localhost:8000/api/clients/${this.currentClientId}/`, { headers })
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