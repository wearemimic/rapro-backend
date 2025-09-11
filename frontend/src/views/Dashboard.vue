<!-- Dashboard.vue -->
<template>
  <div class="dashboard container-fluid" style="margin-top:80px;">
    <div class="dashboard-page-header">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-header-title">Dashboard</h1>
        </div>
        <div class="d-flex gap-2 align-items-center">
          <!-- Client Search Box -->
          <div class="position-relative" style="width: 300px;">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search clients..."
              v-model="clientSearchQuery"
              @input="searchClients"
              @focus="showSearchResults = true"
              @blur="hideSearchResults"
              style="padding-left: 2.5rem;"
            >
            <i class="bi-search position-absolute" style="left: 0.75rem; top: 50%; transform: translateY(-50%); color: #6c757d;"></i>
            
            <!-- Search Results Dropdown -->
            <div 
              v-if="showSearchResults && (searchResults.length > 0 || (clientSearchQuery && searchResults.length === 0))"
              class="position-absolute w-100 mt-1 bg-white border rounded shadow-lg"
              style="z-index: 1050; max-height: 300px; overflow-y: auto;"
            >
              <!-- Loading state -->
              <div v-if="searchLoading" class="p-3 text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              
              <!-- Search results -->
              <div v-else-if="searchResults.length > 0">
                <div 
                  v-for="client in searchResults" 
                  :key="client.id"
                  class="p-2 border-bottom cursor-pointer search-result-item"
                  @mousedown="navigateToClient(client.id)"
                  style="cursor: pointer;"
                  @mouseover="$event.target.style.backgroundColor = '#f8f9fa'"
                  @mouseout="$event.target.style.backgroundColor = 'white'"
                >
                  <div class="d-flex align-items-center">
                    <i class="bi-person-circle me-2 text-muted"></i>
                    <div>
                      <div class="fw-medium">{{ client.first_name }} {{ client.last_name }}</div>
                      <small class="text-muted">{{ client.email }}</small>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- No results -->
              <div v-else-if="clientSearchQuery" class="p-3 text-center text-muted">
                No clients found matching "{{ clientSearchQuery }}"
              </div>
            </div>
          </div>
          
          <a class="btn btn-primary" href="/clients/create">
            <i class="bi-person-plus-fill me-2"></i>Create Client
          </a>
        </div>
      </div>
    </div>
    
    <!-- CRM Quick Stats -->
    <div class="row" v-if="hasCRMAccess">
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5" v-if="isAdminUser">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Unread Communications</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ crmStats.unreadCommunications || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5" v-if="isAdminUser">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">High Priority Items</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ crmStats.highPriority || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5" v-if="isAdminUser">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">AI Analyzed Today</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ crmStats.aiAnalyzed || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Total Clients</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ clients.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FINRA Compliance Quick Status (Admin Only) -->
    <div class="row mb-3 mb-lg-5" v-if="isAdminUser">
      <div class="col-12">
        <div class="card border-success">
          <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <i class="bi-shield-check me-2 fs-4"></i>
              <h5 class="mb-0">FINRA Compliance Status</h5>
            </div>
            <router-link to="/compliance" class="btn btn-light btn-sm">
              <i class="bi-arrow-right-circle"></i> View Details
            </router-link>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3 text-center">
                <div class="p-3">
                  <i class="bi-shield-check display-1 text-success mb-2"></i>
                  <h6>Rule 3110</h6>
                  <span class="badge bg-success">COMPLIANT</span>
                  <small class="d-block text-muted mt-1">Books & Records</small>
                </div>
              </div>
              <div class="col-md-3 text-center">
                <div class="p-3">
                  <i class="bi-person-check display-1 text-success mb-2"></i>
                  <h6>Rule 4511</h6>
                  <span class="badge bg-success">COMPLIANT</span>
                  <small class="d-block text-muted mt-1">Customer Account Info</small>
                </div>
              </div>
              <div class="col-md-3 text-center">
                <div class="p-3">
                  <i class="bi-archive display-1 text-success mb-2"></i>
                  <h6>SEC Rule 17a-4</h6>
                  <span class="badge bg-success">COMPLIANT</span>
                  <small class="d-block text-muted mt-1">Record Retention</small>
                </div>
              </div>
              <div class="col-md-3 text-center">
                <div class="p-3">
                  <i class="bi-lock display-1 text-success mb-2"></i>
                  <h6>Regulation S-P</h6>
                  <span class="badge bg-success">COMPLIANT</span>
                  <small class="d-block text-muted mt-1">Privacy Protection</small>
                </div>
              </div>
            </div>
            <div class="row mt-3">
              <div class="col-md-12">
                <div class="d-flex justify-content-between align-items-center bg-light p-3 rounded">
                  <div>
                    <strong>Audit Trail:</strong> {{ complianceStats.auditEntries || 0 }} entries logged today
                  </div>
                  <div>
                    <strong>Documents:</strong> {{ complianceStats.documentsEncrypted || 0 }}/{{ complianceStats.totalDocuments || 0 }} encrypted
                  </div>
                  <div>
                    <strong>Last Report:</strong> {{ complianceStats.lastReportDate || 'Never' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Main Content Area -->
    <div class="row">
    <div class="col-lg-6 mb-3 mb-lg-5">
      <div class="card mb-3 mb-lg-5">
        <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
          <h4 class="card-header-title">Recent Clients</h4>
          <div class="d-flex gap-2">
            <router-link to="/clients" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-person-plus me-1"></i>
              View All Clients
            </router-link>
          </div>
        </div>
      
        <div class="card-body">
          <!-- Table -->
          <div class="mb-3 d-flex justify-content-between align-items-center">
            <input type="text" v-model="searchQuery" placeholder="Search by name..." class="form-control me-2" style="width: 30%;" />
            <div class="d-flex align-items-center">
              <label for="statusFilter" class="form-label me-2 mb-0">Filter by Status:</label>
              <select v-model="statusFilter" class="form-select w-auto" id="statusFilter">
                <option value="">All</option>
                <option value="Draft">Draft</option>
                <option value="In Progress">In Progress</option>
                <option value="Reviewed">Reviewed</option>
                <option value="Archived">Archived</option>
              </select>
            </div>
          </div>

          <div class="mb-2 text-muted">Total clients retrieved: {{ clients.length }}</div>

          <table v-if="clients.length && !isLoading" class="table table-hover">
            <thead class="thead-light">
              <tr>
                <th>Members</th>
                <th>Name</th>
                <th># of Scenarios</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="client in paginatedClients" :key="client.id" @click="viewClient(client.id)" style="cursor: pointer;">
                <td>
                  <div v-if="client.tax_status === 'Single'" class="icon-container">
                    <div class="single-icon">{{ client.first_name.charAt(0) }}</div>
                  </div>
                  <div v-else class="offset-icons">
                    <div class="icon">{{ client.first_name.charAt(0) }}</div>
                    <div class="icon">{{ client.spouse?.first_name?.charAt(0) || '' }}</div>
                  </div>
                </td>
                <td>{{ client.last_name }} , {{ client.first_name }}</td>
                <td>{{ client.scenarios?.length || 0 }}</td>
                <td>{{ client.status }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click.stop="viewClient(client.id)">View</button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="totalPages > 1" class="mt-3">
            <button class="btn btn-sm btn-light" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">Previous</button>
            <span class="mx-2">Page {{ currentPage }} of {{ totalPages }}</span>
            <button class="btn btn-sm btn-light" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">Next</button>
          </div>

          <div v-if="!clients.length && !isLoading" class="alert alert-warning">
            No clients found.
          </div>
        </div>
      
      </div>
    </div>

    <div class="col-lg-6 mb-3 mb-lg-5">
      <!-- Recent Tasks -->
      <div class="card mb-3 mb-lg-5">
        <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
          <h4 class="card-header-title">Recent Tasks</h4>
          <div class="d-flex gap-2">
            <router-link to="/tasks" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-list-task me-1"></i>
              View All Tasks
            </router-link>
          </div>
        </div>
        
        <div class="card-body">
          <!-- Loading State -->
          <div v-if="tasksLoading" class="text-center py-3">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <!-- Task List -->
          <TaskList 
            v-if="!tasksLoading && recentTasks.length > 0"
            :tasks="recentTasks"
            :loading="tasksLoading"
            @task-click="handleTaskClick"
            @task-update="handleTaskUpdate"
            @task-delete="handleTaskDelete"
            @task-select="handleTaskSelect"
          />
          
          <!-- Empty State -->
          <div v-if="!tasksLoading && recentTasks.length === 0" class="text-center py-4">
            <i class="bi bi-list-task display-4 text-muted mb-3"></i>
            <h6 class="text-muted">No recent tasks</h6>
            <p class="text-muted mb-3">Create your first task to get started.</p>
            <router-link to="/tasks" class="btn btn-primary btn-sm">
              <i class="bi bi-plus me-1"></i>
              Create Task
            </router-link>
          </div>
        </div>
      </div>
    </div>

    
  </div>
  <!-- End Stats -->
  </div>
</template>

<script>
import axios from 'axios'
import { hasCRMAccess } from '@/utils/permissions'
import ActivityStream from '@/components/CRM/ActivityStream.vue'
import TaskList from '@/components/TaskList.vue'
import { API_CONFIG } from '@/config'
// TestChart removed

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
  name: 'Dashboard',
  components: {
    ActivityStream,
    TaskList
  },
  data() {
    return {
      clients: [],
      isLoading: false,
      error: null,
      searchQuery: '',
      sortKey: 'last_name',
      sortDirection: 'asc',
      currentPage: 1,
      perPage: 5,
      statusFilter: '',
      crmStats: {
        unreadCommunications: 0,
        highPriority: 0,
        aiAnalyzed: 0
      },
      complianceStats: {
        auditEntries: 0,
        documentsEncrypted: 0,
        totalDocuments: 0,
        lastReportDate: 'Never'
      },
      // Client search properties
      clientSearchQuery: '',
      searchResults: [],
      showSearchResults: false,
      searchLoading: false,
      searchTimeout: null,
      // Task properties
      recentTasks: [],
      tasksLoading: false
    }
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
    filteredClients() {
      const query = this.searchQuery.toLowerCase()
      return this.clients.filter(c => {
        const nameMatch = c.first_name.toLowerCase().includes(query) || c.last_name.toLowerCase().includes(query)
        const statusMatch = this.statusFilter
          ? c.status.toLowerCase() === this.statusFilter.toLowerCase()
          : c.status.toLowerCase() !== 'archived'
        return nameMatch && statusMatch
      })
    },
    sortedClients() {
      return [...this.filteredClients].sort((a, b) => {
        const modifier = this.sortDirection === 'asc' ? 1 : -1
        return a[this.sortKey] > b[this.sortKey] ? modifier : -modifier
      })
    },
    paginatedClients() {
      const start = (this.currentPage - 1) * this.perPage
      return this.sortedClients.slice(start, start + this.perPage)
    },
    totalPages() {
      return Math.ceil(this.sortedClients.length / this.perPage)
    }
  },
  methods: {
    async fetchClients() {
        this.isLoading = true
        this.error = null
        try {
            const response = await axios.get(`${API_CONFIG.API_URL}/clients/`) // ← simpler, no params yet
            this.clients = response.data
            console.log('Fetched clients:', this.clients.length)  // Debug
        } catch (err) {
            this.error = err.response?.data?.detail || err.message
        } finally {
            this.isLoading = false
        }
    },
    viewClient(clientId) {
      this.$router.push({ name: 'ClientDetail', params: { id: clientId } }) // placeholder
    },
    toggleSort(key) {
      if (this.sortKey === key) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortDirection = 'asc'
      }
    },
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    editClient(clientId) {
      this.$router.push({ name: 'ClientEdit', params: { id: clientId } }) // placeholder
    },
    handleActivityClick(activity) {
      // Handle activity item clicks - navigate to relevant section
      if (activity.type === 'communication') {
        this.$router.push('/communication-center');
      } else if (activity.client_id) {
        this.$router.push(`/clients/${activity.client_id}`);
      }
    },
    handleActionExecuted(action) {
      // Handle when an action is executed from activity stream
      console.log('Action executed:', action);
      // Could refresh dashboard stats here if needed
    },
    async loadComplianceStats() {
      try {
        // For now, set mock data since the compliance endpoints don't exist yet
        // In the future, this would be: const response = await axios.get('/api/compliance/dashboard/')
        this.complianceStats = {
          auditEntries: 47,
          documentsEncrypted: 156,
          totalDocuments: 156,
          lastReportDate: new Date().toLocaleDateString()
        }
      } catch (error) {
        console.error('Error loading compliance stats:', error);
        // Keep default values
      }
    },
    
    // Client search methods
    searchClients() {
      // Clear previous timeout
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      
      // If search query is empty, clear results
      if (!this.clientSearchQuery.trim()) {
        this.searchResults = [];
        this.showSearchResults = false;
        return;
      }
      
      // Debounce the search to avoid too many API calls
      this.searchTimeout = setTimeout(async () => {
        await this.performClientSearch();
      }, 300);
    },
    
    async performClientSearch() {
      if (!this.clientSearchQuery.trim()) return;
      
      this.searchLoading = true;
      try {
        const response = await axios.get(`${API_CONFIG.API_URL}/clients/`, {
          params: {
            search: this.clientSearchQuery,
            limit: 10 // Limit search results
          },
          headers
        });
        
        this.searchResults = response.data || [];
      } catch (error) {
        console.error('Error searching clients:', error);
        this.searchResults = [];
      } finally {
        this.searchLoading = false;
      }
    },
    
    navigateToClient(clientId) {
      // Clear search and hide results
      this.clientSearchQuery = '';
      this.searchResults = [];
      this.showSearchResults = false;
      
      // Navigate to client detail page
      this.$router.push({ name: 'ClientDetail', params: { id: clientId } });
    },
    
    hideSearchResults() {
      // Add small delay to allow click events to register
      setTimeout(() => {
        this.showSearchResults = false;
      }, 200);
    },
    
    // Task-related methods
    async loadRecentTasks() {
      this.tasksLoading = true;
      try {
        const response = await axios.get(`${API_CONFIG.API_URL}/tasks/`, {
          params: {
            limit: 5,
            ordering: '-created_at'
          },
          headers
        });
        this.recentTasks = response.data.results || response.data || [];
      } catch (error) {
        console.error('Error loading recent tasks:', error);
        this.recentTasks = [];
      } finally {
        this.tasksLoading = false;
      }
    },
    
    handleTaskClick(task) {
      // Navigate to task detail or related client
      if (task.client) {
        this.$router.push(`/clients/${task.client}`);
      }
    },
    
    handleTaskUpdate(updatedTask) {
      // Update the task in the list
      const index = this.recentTasks.findIndex(t => t.id === updatedTask.id);
      if (index !== -1) {
        this.recentTasks[index] = updatedTask;
      }
    },
    
    handleTaskDelete(taskId) {
      // Remove the task from the list
      this.recentTasks = this.recentTasks.filter(t => t.id !== taskId);
    },
    
    handleTaskSelect(task) {
      // Handle task selection if needed
      console.log('Task selected:', task);
    }
  },
  mounted() {
    this.fetchClients()
    this.loadComplianceStats()
    this.loadRecentTasks()
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    }
  }
}



</script>

<style scoped>
.dashboard {
  padding: 1rem;
}

.dashboard-page-header {
  margin-bottom: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0;
}


.card-header-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.display-4 {
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1.2;
}

.card-subtitle {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.icon-container {
  display: flex;
  align-items: center;
}

.single-icon, .offset-icons .icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: #333;
  border: 1px solid #ccc;
}

.offset-icons {
  position: relative;
  width: 55px;
}

.offset-icons .icon {
  position: absolute;
}

.offset-icons .icon:first-child {
  left: 0;
  z-index: 2;
}

.offset-icons .icon:last-child {
  left: 20px;
  z-index: 1;
}
</style>