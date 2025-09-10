<template>
  <div class="affiliate-portal-dashboard">
    <!-- Header -->
    <div class="bg-success text-white p-4 mb-4">
      <div class="container-fluid">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h2 class="mb-1">Welcome back, {{ affiliateData?.name || 'Partner' }}!</h2>
            <p class="mb-0 opacity-75">Affiliate Code: {{ affiliateData?.affiliate_code }}</p>
          </div>
          <button @click="handleLogout" class="btn btn-outline-light">
            <i class="bi bi-box-arrow-right me-2"></i>
            Logout
          </button>
        </div>
      </div>
    </div>

    <div class="container-fluid">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-success" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading your dashboard...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      <!-- Dashboard Content -->
      <div v-else>
        <!-- Performance Metrics Cards -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Total Clicks</h6>
                    <h3 class="mb-0">{{ metrics.total_clicks || 0 }}</h3>
                    <small class="text-muted">Last 30 days</small>
                  </div>
                  <div class="text-primary fs-1">
                    <i class="bi bi-cursor-fill"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Conversions</h6>
                    <h3 class="mb-0">{{ metrics.total_conversions || 0 }}</h3>
                    <small class="text-success">
                      {{ metrics.conversion_rate || 0 }}% rate
                    </small>
                  </div>
                  <div class="text-success fs-1">
                    <i class="bi bi-graph-up-arrow"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Pending Commission</h6>
                    <h3 class="mb-0">${{ formatNumber(metrics.pending_commission || 0) }}</h3>
                    <small class="text-muted">Awaiting payout</small>
                  </div>
                  <div class="text-warning fs-1">
                    <i class="bi bi-hourglass-split"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-3">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="text-muted mb-1">Total Earned</h6>
                    <h3 class="mb-0">${{ formatNumber(metrics.total_commission || 0) }}</h3>
                    <small class="text-muted">Last 30 days</small>
                  </div>
                  <div class="text-info fs-1">
                    <i class="bi bi-cash-stack"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Chart -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-0 pt-3">
                <h5 class="mb-0">Performance Trend</h5>
              </div>
              <div class="card-body">
                <Graph
                  :data="performanceChartData"
                  :options="chartOptions"
                  :height="300"
                  type="line"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <!-- Active Links -->
          <div class="col-md-6 mb-4">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-0 d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Your Active Links</h5>
                <button @click="showCreateLinkModal = true" class="btn btn-sm btn-success">
                  <i class="bi bi-plus-circle me-1"></i>
                  Create Link
                </button>
              </div>
              <div class="card-body">
                <div v-if="links.length === 0" class="text-center py-3 text-muted">
                  <i class="bi bi-link-45deg fs-1"></i>
                  <p>No active links yet</p>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Campaign</th>
                        <th>Clicks</th>
                        <th>Conversions</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="link in links" :key="link.id">
                        <td>
                          <div>
                            <strong>{{ link.campaign_name }}</strong>
                            <br>
                            <small class="text-muted">{{ link.tracking_code }}</small>
                          </div>
                        </td>
                        <td>{{ link.click_count || 0 }}</td>
                        <td>{{ link.conversion_count || 0 }}</td>
                        <td>
                          <button
                            @click="copyLink(link)"
                            class="btn btn-sm btn-outline-secondary"
                            title="Copy link"
                          >
                            <i class="bi bi-clipboard"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="col-md-6 mb-4">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-0">
                <h5 class="mb-0">Recent Activity</h5>
              </div>
              <div class="card-body">
                <div v-if="!recentActivity.clicks?.length && !recentActivity.conversions?.length" 
                     class="text-center py-3 text-muted">
                  <i class="bi bi-activity fs-1"></i>
                  <p>No recent activity</p>
                </div>
                <div v-else>
                  <!-- Recent Conversions -->
                  <div v-if="recentActivity.conversions?.length" class="mb-3">
                    <h6 class="text-success mb-2">
                      <i class="bi bi-check-circle me-1"></i>
                      Recent Conversions
                    </h6>
                    <div v-for="conversion in recentActivity.conversions" :key="conversion.id" 
                         class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                      <div>
                        <small class="text-muted">
                          {{ formatDate(conversion.converted_at) }}
                        </small>
                      </div>
                      <div>
                        <span class="badge bg-success">
                          ${{ conversion.conversion_value }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Recent Clicks -->
                  <div v-if="recentActivity.clicks?.length">
                    <h6 class="text-primary mb-2">
                      <i class="bi bi-cursor me-1"></i>
                      Recent Clicks
                    </h6>
                    <div v-for="click in recentActivity.clicks.slice(0, 5)" :key="click.id" 
                         class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                      <div>
                        <small class="text-muted">
                          {{ formatDate(click.clicked_at) }}
                        </small>
                        <br>
                        <small>{{ click.source || 'Direct' }}</small>
                      </div>
                      <div>
                        <small class="text-muted">{{ click.ip_address }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Commission History -->
        <div class="row">
          <div class="col-12">
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-0">
                <h5 class="mb-0">Commission History</h5>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Amount</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="!commissions || commissions.length === 0">
                        <td colspan="4" class="text-center text-muted py-3">
                          No commission history yet
                        </td>
                      </tr>
                      <tr v-for="commission in commissions" :key="commission.id">
                        <td>{{ formatDate(commission.created_at) }}</td>
                        <td>{{ commission.description }}</td>
                        <td>${{ commission.commission_amount }}</td>
                        <td>
                          <span :class="getStatusBadgeClass(commission.status)">
                            {{ commission.status }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Link Modal -->
    <div v-if="showCreateLinkModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Tracking Link</h5>
            <button type="button" class="btn-close" @click="showCreateLinkModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Campaign Name</label>
              <input
                v-model="newLink.campaign_name"
                type="text"
                class="form-control"
                placeholder="e.g., Facebook Ads Q4"
                required
              >
            </div>
            <div class="mb-3">
              <label class="form-label">UTM Source</label>
              <input
                v-model="newLink.utm_source"
                type="text"
                class="form-control"
                placeholder="e.g., facebook"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">UTM Medium</label>
              <input
                v-model="newLink.utm_medium"
                type="text"
                class="form-control"
                placeholder="e.g., cpc"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">UTM Campaign</label>
              <input
                v-model="newLink.utm_campaign"
                type="text"
                class="form-control"
                placeholder="e.g., retirement_planning"
              >
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateLinkModal = false">
              Cancel
            </button>
            <button type="button" class="btn btn-success" @click="createLink">
              Create Link
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import Graph from '@/components/Graph.vue'

const router = useRouter()

// State
const loading = ref(true)
const error = ref('')
const affiliateData = ref(null)
const metrics = ref({})
const links = ref([])
const recentActivity = ref({})
const commissions = ref([])
const showCreateLinkModal = ref(false)

// New link form
const newLink = reactive({
  campaign_name: '',
  utm_source: '',
  utm_medium: '',
  utm_campaign: ''
})

// Chart data
const performanceChartData = computed(() => {
  // Generate sample data for the last 30 days
  const labels = []
  const clicksData = []
  const conversionsData = []
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
    
    // Generate sample data
    clicksData.push(Math.floor(Math.random() * 50) + 10)
    conversionsData.push(Math.floor(Math.random() * 5))
  }
  
  return {
    labels,
    datasets: [
      {
        label: 'Clicks',
        data: clicksData,
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        tension: 0.3
      },
      {
        label: 'Conversions',
        data: conversionsData,
        borderColor: '#28a745',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        tension: 0.3
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Methods
const loadDashboardData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // Get affiliate data from localStorage
    const storedData = localStorage.getItem('affiliate_portal_data')
    if (storedData) {
      affiliateData.value = JSON.parse(storedData)
    }
    
    // Get dashboard data from API
    const token = localStorage.getItem('affiliate_portal_token')
    const response = await axios.get(
      `http://localhost:8000/api/affiliates/portal_dashboard/?affiliate_id=${affiliateData.value.affiliate_id}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    
    if (response.data) {
      metrics.value = response.data.metrics || {}
      links.value = response.data.links || []
      recentActivity.value = response.data.recent_activity || {}
      
      // Load commission history separately if needed
      await loadCommissions()
    }
  } catch (err) {
    console.error('Dashboard load error:', err)
    error.value = 'Failed to load dashboard data. Please try again.'
    
    // If unauthorized, redirect to login
    if (err.response?.status === 401) {
      router.push('/affiliate/portal/login')
    }
  } finally {
    loading.value = false
  }
}

const loadCommissions = async () => {
  try {
    const token = localStorage.getItem('affiliate_portal_token')
    const response = await axios.get(
      `http://localhost:8000/api/affiliates/${affiliateData.value.affiliate_id}/commissions/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    commissions.value = response.data || []
  } catch (err) {
    console.error('Failed to load commissions:', err)
  }
}

const createLink = async () => {
  try {
    const token = localStorage.getItem('affiliate_portal_token')
    const response = await axios.post(
      `http://localhost:8000/api/affiliates/${affiliateData.value.affiliate_id}/generate_link/`,
      newLink,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    
    if (response.data) {
      links.value.unshift(response.data)
      showCreateLinkModal.value = false
      
      // Reset form
      newLink.campaign_name = ''
      newLink.utm_source = ''
      newLink.utm_medium = ''
      newLink.utm_campaign = ''
      
      // Show success message
      alert('Link created successfully!')
    }
  } catch (err) {
    console.error('Failed to create link:', err)
    alert('Failed to create link. Please try again.')
  }
}

const copyLink = (link) => {
  const url = `http://localhost:8000/api/track/${link.tracking_code}`
  navigator.clipboard.writeText(url)
  alert('Link copied to clipboard!')
}

const handleLogout = () => {
  localStorage.removeItem('affiliate_portal_token')
  localStorage.removeItem('affiliate_portal_refresh')
  localStorage.removeItem('affiliate_portal_data')
  router.push('/affiliate/portal/login')
}

const formatNumber = (num) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'badge bg-warning',
    approved: 'badge bg-info',
    paid: 'badge bg-success',
    rejected: 'badge bg-danger'
  }
  return classes[status] || 'badge bg-secondary'
}

// Check authentication on mount
onMounted(() => {
  const token = localStorage.getItem('affiliate_portal_token')
  if (!token) {
    router.push('/affiliate/portal/login')
  } else {
    loadDashboardData()
  }
})
</script>

<style scoped>
.affiliate-portal-dashboard {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.card {
  border-radius: 10px;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.table td {
  vertical-align: middle;
}

.modal {
  display: block;
}

.badge {
  font-size: 0.85em;
  padding: 0.35em 0.65em;
}
</style>