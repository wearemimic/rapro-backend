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
    <!-- Stats -->
    <div class="row" style="margin-top:20px;">
    <div class="col-sm-6 col-lg-8 mb-3 mb-lg-5">
      <div class="card mb-3 mb-lg-5">
        <h2 class="card-title px-3 pt-3 mb-0">Recent Clients</h2>
      
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

    <div class="col-sm-6 col-lg-4 mb-3 mb-lg-5">
      <!-- Card -->
      <div class="card card-hover-shadow h-100">
        <div class="card-body">
          <h3 class="card-title text-inherit">Getting Started</h3>
          <ul class="list-unstyled">
            <li class="d-flex align-items-center mb-2" style="font-size: 1.1rem;">
              <i class="bi-check-circle-fill text-success me-2"></i>
              Complete the signup 
            </li>
            <li class="d-flex align-items-center mb-2" style="font-size: 1.1rem;">
              <i class="bi-circle me-2"></i>
              Set up your White Label
            </li>
            <li class="d-flex align-items-center mb-2" style="font-size: 1.1rem;">
              <i class="bi-circle me-2"></i>
              Connect to your CRM
            </li>
            <li class="d-flex align-items-center mb-2" style="font-size: 1.1rem;">
              <i class="bi-circle me-2"></i>
              Import your contacts
            </li>
            <li class="d-flex align-items-center mb-2" style="font-size: 1.1rem;">
              <i class="bi-check-circle-fill text-success me-2"></i>
              Enable tech integrations
            </li>
            <li class="d-flex align-items-center" style="font-size: 1.1rem;">
              <i class="bi-circle me-2"></i>
              Browse Help Center
            </li>
          </ul>
          <div class="progress mt-3" style="height: 5px;">
            <div class="progress-bar bg-primary" role="progressbar" style="width: 30%;" aria-valuenow="30" aria-valuemin="0" aria-valuemax="100"></div>
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

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
  name: 'ClientList',
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
    }
  },
  computed: {
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