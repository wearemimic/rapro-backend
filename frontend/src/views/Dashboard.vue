<!-- Dashboard.vue -->
<template>
  <div class="container-fluid" style="margin-top:80px;">
    <div class="row align-items-center">
      <div>
        <!-- End Col -->
        <div class="col-auto">
          <a class="btn btn-primary" href="/clients/create">
            <i class="bi-person-plus-fill me-1"></i> Create Client
          </a>
        </div>
        <!-- End Col -->
      </div>
      <!-- End Row -->
    </div>
    <!-- End Page Header -->
    <!-- CRM Quick Stats -->
    <div class="row mb-4" style="margin-top:20px;" v-if="hasCRMAccess">
      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-primary text-white">
                  <i class="bi-envelope"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ crmStats.unreadCommunications || 0 }}</span>
                <span class="d-block fs-6 text-muted">Unread Communications</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-warning text-white">
                  <i class="bi-exclamation-triangle"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ crmStats.highPriority || 0 }}</span>
                <span class="d-block fs-6 text-muted">High Priority Items</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-info text-white">
                  <i class="bi-robot"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ crmStats.aiAnalyzed || 0 }}</span>
                <span class="d-block fs-6 text-muted">AI Analyzed Today</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-success text-white">
                  <i class="bi-people"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ clients.length || 0 }}</span>
                <span class="d-block fs-6 text-muted">Total Clients</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="row" style="margin-top:20px;">
    <div class="col-lg-8 mb-3 mb-lg-5">
      <div class="card mb-3 mb-lg-5">
        <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
          <h2 class="mb-0">Recent Clients</h2>
          <div class="d-flex gap-2">
            <router-link to="/communication-center" class="btn btn-outline-primary btn-sm">
              <i class="bi bi-envelope me-1"></i>
              Communication Center
            </router-link>
          </div>
        </div>
      
        <div class="card-body">
          <!-- Table -->
          <div class="mb-3 d-flex justify-content-between align-items-center" style="margin-top:10px;">
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

    <div class="col-lg-4 mb-3 mb-lg-5">
      <!-- CRM Activity Stream -->
      <div class="mb-4" v-if="hasCRMAccess">
        <ActivityStream 
          :max-items="8"
          :auto-refresh="true"
          :refresh-interval="60000"
          @activity-click="handleActivityClick"
          @action-executed="handleActionExecuted"
        />
      </div>

      <!-- Getting Started Card -->
      <div class="card card-hover-shadow h-100">
        <div class="card-body">
          <h6 class="card-title text-inherit mb-3">Getting Started</h6>
          <ul class="list-unstyled">
            <li class="d-flex align-items-center mb-2">
              <i class="bi-check-circle-fill text-success me-2"></i>
              <span>Complete the signup</span>
            </li>
            <li class="d-flex align-items-center mb-2">
              <i class="bi-circle me-2 text-muted"></i>
              <span>Set up your White Label</span>
            </li>
            <li class="d-flex align-items-center mb-2">
              <i class="bi-check-circle-fill text-success me-2"></i>
              <span>Connect to your CRM</span>
            </li>
            <li class="d-flex align-items-center mb-2">
              <i class="bi-circle me-2 text-muted"></i>
              <span>Import your contacts</span>
            </li>
            <li class="d-flex align-items-center mb-2">
              <i class="bi-check-circle-fill text-success me-2"></i>
              <span>Enable tech integrations</span>
            </li>
            <li class="d-flex align-items-center">
              <i class="bi-circle me-2 text-muted"></i>
              <span>Browse Help Center</span>
            </li>
          </ul>
          <div class="progress mt-3" style="height: 5px;">
            <div class="progress-bar bg-primary" role="progressbar" style="width: 50%;" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
          </div>
        </div>
      </div>
      <!-- End Card -->
    </div>

    
  </div>
  <!-- End Stats -->
  </div>
</template>

<script>
import axios from 'axios'
import { hasCRMAccess } from '@/utils/permissions'
import ActivityStream from '@/components/CRM/ActivityStream.vue'
// TestChart removed

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
  name: 'Dashboard',
  components: {
    ActivityStream
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
      }
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
            const response = await axios.get('http://localhost:8000/api/clients/') // ← simpler, no params yet
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
    }
  },
  mounted() {
    this.fetchClients()
  },
  watch: {
    searchQuery() {
      this.currentPage = 1
    }
  }
}



</script>

<style scoped>
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