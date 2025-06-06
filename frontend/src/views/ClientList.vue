<template>
  <div class="container mt-12">
      <div class="row" style="margin-top:60px;">
        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <div class="card h-100">
            <div class="card-body">
              <h6 class="card-subtitle mb-2">Total Clients</h6>

              <div class="row align-items-center gx-2">
                <div class="col">
                  <span class="js-counter display-4 text-dark">24</span>
                  <span class="text-body fs-5 ms-1">from 22</span>
                </div>
                <!-- End Col -->

                <div class="col-auto">
                  <span class="badge bg-soft-success text-success p-1">
                    <i class="bi-graph-up"></i> 5.0%
                  </span>
                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <div class="card h-100">
            <div class="card-body">
              <h6 class="card-subtitle mb-2">Clients In Process</h6>

              <div class="row align-items-center gx-2">
                <div class="col">
                  <span class="js-counter display-4 text-dark">12</span>
                  <span class="text-body fs-5 ms-1">from 11</span>
                </div>

                <div class="col-auto">
                  <span class="badge bg-soft-success text-success p-1">
                    <i class="bi-graph-up"></i> 1.2%
                  </span>
                </div>
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <div class="card h-100">
            <div class="card-body">
              <h6 class="card-subtitle mb-2">Clients in Draft</h6>

              <div class="row align-items-center gx-2">
                <div class="col">
                  <span class="js-counter display-4 text-dark">56</span>
                  <span class="display-4 text-dark">%</span>
                  <span class="text-body fs-5 ms-1">from 48.7</span>
                </div>

                <div class="col-auto">
                  <span class="badge bg-soft-danger text-danger p-1">
                    <i class="bi-graph-down"></i> 2.8%
                  </span>
                </div>
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <div class="card h-100">
            <div class="card-body">
              <h6 class="card-subtitle mb-2">Active members</h6>

              <div class="row align-items-center gx-2">
                <div class="col">
                  <span class="js-counter display-4 text-dark">28.6</span>
                  <span class="display-4 text-dark">%</span>
                  <span class="text-body fs-5 ms-1">from 28.6%</span>
                </div>

                <div class="col-auto">
                  <span class="badge bg-soft-secondary text-secondary p-1">0.0%</span>
                </div>
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>
      </div>
    <div class="row">
        <div class="mb-lg-12">
          <!-- Card -->
          
          

          <div v-if="isLoading" class="alert alert-info">Loading clients...</div>
          <div v-if="error" class="alert alert-danger">Error: {{ error }}</div>
          <div class="card h-100">
            <div class="card-body">
              <div class="mb-3 d-flex justify-content-between">
                <input type="text" v-model="searchQuery" placeholder="Search by name..." class="form-control w-50" />
                <div>
                  <button class="btn btn-sm btn-outline-secondary" @click="toggleSort('last_name')">Sort by Last Name</button>
                  <button class="btn btn-sm btn-outline-secondary" @click="toggleSort('created_at')">Sort by Created</button>
                </div>
              </div>

              <div class="mb-3">
                <label for="statusFilter" class="form-label me-2">Filter by Status:</label>
                <select v-model="statusFilter" class="form-select w-auto d-inline" id="statusFilter">
                  <option value="">All</option>
                  <option value="Draft">Draft</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Reviewed">Reviewed</option>
                  <option value="Archived">Archived</option>
                </select>
              </div>

              <div class="mb-2 text-muted">Total clients retrieved: {{ clients.length }}</div>

              <table v-if="clients.length && !isLoading" class="table table-hover">
                <thead class="thead-light">
                  <tr>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Email</th>
                    <th>Tax Status</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="client in paginatedClients" :key="client.id">
                    <td>{{ client.first_name }}</td>
                    <td>{{ client.last_name }}</td>
                    <td>{{ client.email }}</td>
                    <td>{{ client.tax_status }}</td>
                    <td>{{ client.status }}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary" @click="viewClient(client.id)">View</button>
                      <button class="btn btn-sm btn-outline-secondary" @click="editClient(client.id)">Edit</button>
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
      </div>
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
    // currentPage() {
    //   this.fetchClients()
    // },
    searchQuery() {
      this.currentPage = 1
      //this.fetchClients()
    }
  }
}
</script>