<template>
  <div class="container mt-12">
    <div class="row" style="margin-top:60px;">
      <div class="col-sm-6 col-lg-2 mb-3 mb-lg-5">
        <!-- Card -->
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-subtitle mb-2 text-center">Total Clients</h5>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ totalClients }}</span>
              </div>
              <!-- End Col -->
            </div>
            <!-- End Row -->
          </div>
        </div>
        <!-- End Card -->
      </div>

      <div class="col-sm-6 col-lg-2 mb-3 mb-lg-5">
        <!-- Card -->
        <div class="col-auto" style="margin-top:50px;">
          <a class="btn btn-primary" href="/clients/create">
            <i class="bi-person-plus-fill me-1"></i> Create Client
          </a>
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
                  <label for="statusFilter" class="form-label me-2">Filter by Status:</label>
                  <select v-model="statusFilter" class="form-select w-auto d-inline" id="statusFilter">
                    <option value="">All</option>
                    <option value="Draft">Draft</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Reviewed">Reviewed</option>
                    <option value="Archived">Archived</option>
                  </select>
                </div>
              </div>
              <div class="mb-2 text-muted" style="margin-top:40px;">Total clients retrieved: {{ clients.length }}</div>

              <table v-if="clients.length && !isLoading" class="table table-hover">
                <thead class="thead-light">
                  <tr>
                    <th>Members</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th># of Scenarios</th>
                    <th>Tax Status</th>
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
                    <td>{{ client.first_name }}</td>
                    <td>{{ client.last_name }}</td>
                    <td>{{ client.scenarios?.length || 0 }}</td>
                    <td>{{ client.tax_status }}</td>
                    <td>{{ client.status }}</td>
                    <td>
                      <button class="btn btn-sm btn-outline-primary me-2" @click.stop="viewClient(client.id)">View</button>
                      <button class="btn btn-sm btn-outline-secondary" style="border-color: #6c757d;" @click.stop="editClient(client.id)">Edit</button>
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
    },
    totalClients() {
      return this.clients.length;
    }
  },
  methods: {
    async fetchClients() {
        this.isLoading = true
        this.error = null
        try {
            const response = await axios.get('http://localhost:8000/api/clients/', { headers })
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
    createNewClient() {
      this.$router.push('/clients/create');
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

<style scoped>
.icon-container {
  display: flex;
  align-items: center;
}
.single-icon {
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  color: #333;
  position: absolute;
  border: 1px solid #ccc;
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