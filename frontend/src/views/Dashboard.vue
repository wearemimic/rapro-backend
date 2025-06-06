<!-- Dashboard.vue -->
<template>
  <section>
    <h1>Dashboard</h1>
    <div class="row align-items-center">
      <div>
        <!-- <div class="col">
          <h1 class="page-header-title">Dashboard</h1>
        </div> -->
        <!-- End Col -->
        <div class="col-auto" style="margin-top:20px;">
          <a class="btn btn-primary" href="javascript:;" data-bs-toggle="modal" data-bs-target="#inviteUserModal">
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
        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <a class="card card-hover-shadow h-100" href="#">
            <div class="card-body">
              <h6 class="card-subtitle">Total Medicare Costs (cirlce that has red if over 75% is IRmaa, ornage is over 50% yellow if over 25% and green if below 25%)</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <!-- Pie Chart -->
                  <div class="chartjs-custom" style="height: 13rem;">
                    <canvas id="updatingDoughnutChart" data-hs-chartjs-options='{
                                    "type": "doughnut",
                                    "data": {
                                      "labels": ["USD", "USD", "USD"],
                                      "datasets": [{
                                        "data": [45, 25, 30],
                                        "backgroundColor": ["#377dff", "#00c9db", "#e7eaf3"],
                                        "borderWidth": 5,
                                        "hoverBorderColor": "#fff"
                                      }]
                                    },
                                    "options": {
                                      "cutout": "80%",
                                      "plugins": {
                                        "tooltip": {
                                          "postfix": "k",
                                          "hasIndicator": true,
                                          "mode": "index",
                                          "intersect": false
                                        }
                                      },
                                      "hover": {
                                        "mode": "nearest",
                                        "intersect": true
                                      }
                                    }
                                  }'>
                      </canvas>
                  </div>
                  <!-- End Pie Chart -->

                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->

            </div>
          </a>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <a class="card card-hover-shadow h-100" href="#">
            <div class="card-body">
              <h6 class="card-subtitle">Connect to Wealthbox</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <h2 class="card-title text-inherit">CLICK HERE</h2>
                </div> 
                <!-- End Col -->
              </div>
              <!-- End Row -->

              <span class="badge bg-soft-success text-success">
                <i class="bi-graph-up"></i> 1.7%
              </span>
              <span class="text-body fs-6 ms-1">from 29.1%</span>
            </div>
          </a>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <a class="card card-hover-shadow h-100" href="#">
            <div class="card-body">
              <h6 class="card-subtitle">White Label Set up</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <h2 class="card-title text-inherit">CLICK HERE</h2>
                </div> 
                <!-- End Col -->
              </div>
            </div>
          </a>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
          <!-- Card -->
          <a class="card card-hover-shadow h-100" href="#">
            <div class="card-body">
              <h6 class="card-subtitle">Pageviews</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <h2 class="card-title text-inherit">92,913</h2>
                </div>
                <!-- End Col -->

                <div class="col-6">
                  <!-- Chart -->
                  <div class="chartjs-custom" style="height: 3rem;">
                    <canvas class="js-chart" data-hs-chartjs-options='{
                              "type": "line",
                              "data": {
                                 "labels": ["1 May","2 May","3 May","4 May","5 May","6 May","7 May","8 May","9 May","10 May","11 May","12 May","13 May","14 May","15 May","16 May","17 May","18 May","19 May","20 May","21 May","22 May","23 May","24 May","25 May","26 May","27 May","28 May","29 May","30 May","31 May"],
                                 "datasets": [{
                                  "data": [21,20,24,15,17,30,30,35,35,35,40,60,12,90,90,85,70,75,43,75,90,22,120,120,90,85,100,92,92,92,92],
                                  "backgroundColor": ["rgba(55, 125, 255, 0)", "rgba(255, 255, 255, 0)"],
                                  "borderColor": "#377dff",
                                  "borderWidth": 2,
                                  "pointRadius": 0,
                                  "pointHoverRadius": 0
                                }]
                              },
                              "options": {
                                 "scales": {
                                   "y": {
                                     "display": false
                                   },
                                   "x": {
                                     "display": false
                                   }
                                 },
                                "hover": {
                                  "mode": "nearest",
                                  "intersect": false
                                },
                                "plugins": {
                                  "tooltip": {
                                    "postfix": "k",
                                    "hasIndicator": true,
                                    "intersect": false
                                  }
                                }
                              }
                            }'>
                    </canvas>
                  </div>
                  <!-- End Chart -->
                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->

              <span class="badge bg-soft-secondary text-body">0.0%</span>
              <span class="text-body fs-6 ms-1">from 2,913</span>
            </div>
          </a>
          <!-- End Card -->
        </div>
      </div>
      <!-- End Stats -->
    <!-- Card -->
      <div class="card mb-3 mb-lg-5">
        <!-- Table -->
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

       
        <!-- End Table -->

        <!-- Footer -->
        
        <!-- End Footer -->
      </div>
      <!-- End Card -->
  </section>
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