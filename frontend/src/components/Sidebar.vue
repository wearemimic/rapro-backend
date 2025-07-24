<template>
  <aside id="sidebar" class="sidebar" style="width:270px;">
    <div class="navbar-vertical-container">
      <div class="navbar-vertical-footer-offset">
        <!-- Logo -->

        <a class="navbar-brand" href="./index.html" aria-label="Front">
          
          <!-- <img class="navbar-brand-logo" src="./assets/svg/logos-light/logo.svg" alt="Logo" data-hs-theme-appearance="dark">
          <img class="navbar-brand-logo-mini" src="./assets/svg/logos/logo-short.svg" alt="Logo" data-hs-theme-appearance="default">
          <img class="navbar-brand-logo-mini" src="./assets/svg/logos-light/logo-short.svg" alt="Logo" data-hs-theme-appearance="dark"> -->
        </a>

        <!-- End Logo -->

        <!-- Navbar Vertical Toggle -->
        <button type="button" class="js-navbar-vertical-aside-toggle-invoker navbar-aside-toggler">
          <i class="bi-arrow-bar-left navbar-toggler-short-align" data-bs-template='<div class="tooltip d-none d-md-block" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>' data-bs-toggle="tooltip" data-bs-placement="right" title="Collapse"></i>
          <i class="bi-arrow-bar-right navbar-toggler-full-align" data-bs-template='<div class="tooltip d-none d-md-block" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>' data-bs-toggle="tooltip" data-bs-placement="right" title="Expand"></i>
        </button>

        <!-- End Navbar Vertical Toggle -->

        <!-- Content -->
        <div class="navbar-vertical-content">
          <div id="navbarVerticalMenu" class="nav nav-pills nav-vertical card-navbar-nav">
            <!-- Collapse -->
            <div class="nav-item">
              <a class="nav-link" href="/dashboard" role="button"  aria-expanded="true" aria-controls="navbarVerticalMenuDashboards">
                <i class="bi-people nav-icon"></i>
                <span class="nav-link-title">Dashboard</span>
              </a>

              
            </div>
            <!-- End Collapse -->
            <!-- Collapse -->
            <div class="navbar-nav nav-compact">

            </div>
            <div id="navbarVerticalMenuPagesMenu">
              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle " href="#navbarVerticalMenuPagesUsersMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuPagesUsersMenu" aria-expanded="false" aria-controls="navbarVerticalMenuPagesUsersMenu">
                  <i class="bi-people nav-icon"></i>
                  <span class="nav-link-title">Clients</span>
                </a>

                <div id="navbarVerticalMenuPagesUsersMenu" class="nav-collapse collapse " data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link " href="/clients">Overview</a>
                  <a class="nav-link " href="/clients/create">Add Client <span class="badge bg-info rounded-pill ms-1">Hot</span></a>
                </div>
              </div>
              <!-- End Collapse -->

              

              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle " href="#navbarVerticalMenuPagesAccountMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuPagesAccountMenu" aria-expanded="false" aria-controls="navbarVerticalMenuPagesAccountMenu">
                  <i class="bi-person-badge nav-icon"></i>
                  <span class="nav-link-title">Account</span>
                </a>

                <div id="navbarVerticalMenuPagesAccountMenu" class="nav-collapse collapse " data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link " href="./account-settings.html">Settings</a>
                  <a class="nav-link " href="./account-billing.html">Billing</a>
                  <a class="nav-link " href="./account-white-label.html">White Label</a>
                </div>
              </div>
              <!-- End Collapse -->

              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle" href="#navbarVerticalMenuIntegrationsMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuIntegrationsMenu" aria-expanded="false" aria-controls="navbarVerticalMenuIntegrationsMenu">
                  <i class="bi-plug nav-icon"></i>
                  <span class="nav-link-title">Integrations</span>
                </a>

                <div id="navbarVerticalMenuIntegrationsMenu" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">CRM</a>
                </div>
              </div>
              
              <!-- Client navigation section - only shown when in client context -->
              <div class="nav-item" v-if="isClientRoute">
                <a class="nav-link dropdown-toggle" href="#navbarVerticalMenuCurrentClient" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuCurrentClient" aria-expanded="true" aria-controls="navbarVerticalMenuCurrentClient">
                  <i class="bi-person nav-icon"></i>
                  <span class="nav-link-title">Current Client</span>
                  <span class="badge bg-primary rounded-pill ms-1">Active</span>
                </a>

                                  <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" :class="{ show: isClientRoute }" data-bs-parent="#navbarVerticalMenuPagesMenu">
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
      isClientRoute: false
    };
  },
  created() {
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
  
  methods: {
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
  width: 250px;
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-top: 1rem;
  border-right: 1px solid #e3e6f0;
}
</style>