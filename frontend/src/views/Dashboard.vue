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
                    <canvas class="js-chart" data-hs-chartjs-options='{
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

                  <!-- Legend Indicators -->
                  <div class="row justify-content-center">
                    <div class="col-auto mb-3 mb-sm-0">
                      <span class="card-title h4">$2,332.00</span>
                      <span class="legend-indicator bg-primary"></span> Marketing
                    </div>

                    <div class="col-auto mb-3 mb-sm-0">
                      <span class="card-title h4">$10,452.00</span>
                      <span class="legend-indicator bg-info"></span> Bills
                    </div>

                    <div class="col-auto">
                      <span class="card-title h4">$56,856.00</span>
                      <span class="legend-indicator"></span> Others
                    </div>
                  </div>
                  <!-- End Legend Indicators -->
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
              <h6 class="card-subtitle">Sessions</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <h2 class="card-title text-inherit">29.4%</h2>
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
                                  "data": [21,20,24,20,18,17,15,17,30,30,35,25,18,30,31,35,35,90,90,90,85,100,120,120,120,100,90,75,75,75,90],
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
              <h6 class="card-subtitle">Avg. Click Rate</h6>

              <div class="row align-items-center gx-2 mb-1">
                <div class="col-6">
                  <h2 class="card-title text-inherit">56.8%</h2>
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
                                  "data": [25,18,30,31,35,35,60,60,60,75,21,20,24,20,18,17,15,17,30,120,120,120,100,90,75,90,90,90,75,70,60],
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

              <span class="badge bg-soft-danger text-danger">
                <i class="bi-graph-down"></i> 4.4%
              </span>
              <span class="text-body fs-6 ms-1">from 61.2%</span>
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
        <table v-if="clients.length && !isLoading" class="table table-borderless table-thead-bordered table-nowrap table-align-middle card-table">
          <!-- <table  class="table table-hover"> -->
          <thead class="thead-light">
            <tr>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Email</th>
              <th>Birthdate</th>
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
              <td>{{ client.birthdate }}</td>
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
        <div class="card-footer">
          <!-- Pagination -->
          <div class="row justify-content-center justify-content-sm-between align-items-sm-center">
            <div class="col-sm mb-2 mb-sm-0">
              <div class="d-flex justify-content-center justify-content-sm-start align-items-center">
                <span class="me-2">Showing:</span>

                <!-- Select -->
                <div class="tom-select-custom">
                  <select id="datatableEntries" class="js-select form-select form-select-borderless w-auto" autocomplete="off" data-hs-tom-select-options='{
                            "searchInDropdown": false,
                            "hideSearch": true
                          }'>
                    <option value="4">4</option>
                    <option value="6">6</option>
                    <option value="8" selected>8</option>
                    <option value="12">12</option>
                  </select>
                </div>
                <!-- End Select -->

                <span class="text-secondary me-2">of</span>

                <!-- Pagination Quantity -->
                <span id="datatableWithPaginationInfoTotalQty"></span>
              </div>
            </div>
            <!-- End Col -->

            <div class="col-sm-auto">
              <div class="d-flex justify-content-center justify-content-sm-end">
                <!-- Pagination -->
                <nav id="datatablePagination" aria-label="Activity pagination"></nav>
              </div>
            </div>
            <!-- End Col -->
          </div>
          <!-- End Pagination -->
        </div>
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
    }
  },
  computed: {
    filteredClients() {
      const query = this.searchQuery.toLowerCase()
      return this.clients.filter(c =>
        c.first_name.toLowerCase().includes(query) ||
        c.last_name.toLowerCase().includes(query)
      )
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
    currentPage() {
      this.fetchClients()
    },
    searchQuery() {
      this.currentPage = 1
      this.fetchClients()
    }
  }
}
</script>