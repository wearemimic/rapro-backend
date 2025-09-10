<template>
  <div class="commission-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Commission Management</h1>
        <p class="text-muted">Review and approve affiliate commissions</p>
      </div>
      <div class="d-flex gap-2">
        <button @click="calculateMonthlyCommissions" class="btn btn-outline-primary" :disabled="calculating">
          <div v-if="calculating" class="spinner-border spinner-border-sm me-2" role="status">
            <span class="visually-hidden">Calculating...</span>
          </div>
          <i v-else class="bi bi-calculator me-2"></i>
          Calculate Monthly
        </button>
        <button @click="showPayoutModal = true" class="btn btn-success" :disabled="selectedCommissions.length === 0">
          <i class="bi bi-cash-stack me-2"></i>
          Create Payout Batch ({{ selectedCommissions.length }})
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-2">Pending Approval</h6>
            <h3 class="mb-0 text-warning">${{ formatNumber(pendingTotal) }}</h3>
            <small class="text-muted">{{ pendingCount }} commissions</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-2">Approved</h6>
            <h3 class="mb-0 text-info">${{ formatNumber(approvedTotal) }}</h3>
            <small class="text-muted">Ready for payout</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-2">Paid Out</h6>
            <h3 class="mb-0 text-success">${{ formatNumber(paidTotal) }}</h3>
            <small class="text-muted">This period</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="text-muted mb-2">Total Commissions</h6>
            <h3 class="mb-0">${{ formatNumber(totalCommissions) }}</h3>
            <small class="text-muted">All time</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="filters.status" class="form-select">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="paid">Paid</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Affiliate</label>
            <select v-model="filters.affiliate" class="form-select">
              <option value="">All Affiliates</option>
              <option v-for="affiliate in affiliates" :key="affiliate.id" :value="affiliate.id">
                {{ affiliate.business_name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Date Range</label>
            <select v-model="filters.dateRange" class="form-select">
              <option value="30">Last 30 Days</option>
              <option value="60">Last 60 Days</option>
              <option value="90">Last 90 Days</option>
              <option value="365">Last Year</option>
              <option value="">All Time</option>
            </select>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <button @click="applyFilters" class="btn btn-primary w-100">
              <i class="bi bi-funnel me-2"></i>
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Commission Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    class="form-check-input"
                    @change="toggleAllCommissions"
                    :checked="allSelected"
                  >
                </th>
                <th>Date</th>
                <th>Affiliate</th>
                <th>Customer</th>
                <th>Type</th>
                <th>Base Amount</th>
                <th>Rate</th>
                <th>Commission</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="10" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="commissions.length === 0">
                <td colspan="10" class="text-center py-4 text-muted">
                  No commissions found
                </td>
              </tr>
              <tr v-for="commission in commissions" :key="commission.id">
                <td>
                  <input
                    v-if="commission.status === 'pending' || commission.status === 'approved'"
                    type="checkbox"
                    class="form-check-input"
                    :value="commission.id"
                    v-model="selectedCommissions"
                  >
                </td>
                <td>{{ formatDate(commission.created_at) }}</td>
                <td>
                  <strong>{{ commission.affiliate_name }}</strong>
                  <br>
                  <small class="text-muted">{{ commission.affiliate_code }}</small>
                </td>
                <td>{{ commission.customer_email }}</td>
                <td>
                  <span class="badge bg-secondary">
                    {{ commission.commission_type }}
                  </span>
                </td>
                <td>${{ commission.base_amount }}</td>
                <td>{{ commission.commission_rate ? (commission.commission_rate * 100).toFixed(1) + '%' : 'Flat' }}</td>
                <td class="fw-bold">${{ commission.commission_amount }}</td>
                <td>
                  <span :class="getStatusBadgeClass(commission.status)">
                    {{ commission.status }}
                  </span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button
                      v-if="commission.status === 'pending'"
                      @click="approveCommission(commission.id)"
                      class="btn btn-outline-success"
                      title="Approve"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <button
                      v-if="commission.status === 'pending'"
                      @click="rejectCommission(commission.id)"
                      class="btn btn-outline-danger"
                      title="Reject"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                    <button
                      @click="viewDetails(commission)"
                      class="btn btn-outline-primary"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="d-flex justify-content-between align-items-center mt-3">
          <div>
            Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalCommissions) }} of {{ totalCommissions }}
          </div>
          <nav>
            <ul class="pagination mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" @click="currentPage--" href="#">Previous</a>
              </li>
              <li
                v-for="page in totalPages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
              >
                <a class="page-link" @click="currentPage = page" href="#">{{ page }}</a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" @click="currentPage++" href="#">Next</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Payout Modal -->
    <div v-if="showPayoutModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Payout Batch</h5>
            <button type="button" class="btn-close" @click="showPayoutModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              You are about to create a payout batch for {{ selectedCommissions.length }} commissions totaling 
              <strong>${{ calculateSelectedTotal() }}</strong>
            </div>

            <h6 class="mb-3">Payout Summary by Affiliate</h6>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Affiliate</th>
                    <th>Commissions</th>
                    <th>Total Amount</th>
                    <th>Payment Method</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="summary in payoutSummary" :key="summary.affiliate_id">
                    <td>{{ summary.affiliate_name }}</td>
                    <td>{{ summary.count }}</td>
                    <td>${{ summary.total }}</td>
                    <td>
                      <span class="badge bg-secondary">
                        {{ summary.payment_method }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="mt-3">
              <label class="form-label">Payout Notes (Optional)</label>
              <textarea
                v-model="payoutNotes"
                class="form-control"
                rows="3"
                placeholder="Add any notes about this payout batch..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showPayoutModal = false">
              Cancel
            </button>
            <button type="button" class="btn btn-success" @click="createPayoutBatch">
              <i class="bi bi-check-circle me-2"></i>
              Create Payout Batch
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Commission Details Modal -->
    <div v-if="showDetailsModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Commission Details</h5>
            <button type="button" class="btn-close" @click="showDetailsModal = false"></button>
          </div>
          <div class="modal-body" v-if="selectedCommission">
            <dl class="row">
              <dt class="col-sm-4">Commission ID</dt>
              <dd class="col-sm-8">{{ selectedCommission.id }}</dd>

              <dt class="col-sm-4">Affiliate</dt>
              <dd class="col-sm-8">
                {{ selectedCommission.affiliate_name }}
                <br>
                <small class="text-muted">{{ selectedCommission.affiliate_code }}</small>
              </dd>

              <dt class="col-sm-4">Customer</dt>
              <dd class="col-sm-8">{{ selectedCommission.customer_email }}</dd>

              <dt class="col-sm-4">Subscription</dt>
              <dd class="col-sm-8">{{ selectedCommission.subscription_id }}</dd>

              <dt class="col-sm-4">Period</dt>
              <dd class="col-sm-8">
                {{ formatDate(selectedCommission.period_start) }} - 
                {{ formatDate(selectedCommission.period_end) }}
              </dd>

              <dt class="col-sm-4">Base Amount</dt>
              <dd class="col-sm-8">${{ selectedCommission.base_amount }}</dd>

              <dt class="col-sm-4">Commission Rate</dt>
              <dd class="col-sm-8">
                {{ selectedCommission.commission_rate ? (selectedCommission.commission_rate * 100).toFixed(1) + '%' : 'Flat Rate' }}
              </dd>

              <dt class="col-sm-4">Commission Amount</dt>
              <dd class="col-sm-8 fw-bold text-success">
                ${{ selectedCommission.commission_amount }}
              </dd>

              <dt class="col-sm-4">Status</dt>
              <dd class="col-sm-8">
                <span :class="getStatusBadgeClass(selectedCommission.status)">
                  {{ selectedCommission.status }}
                </span>
              </dd>

              <dt class="col-sm-4">Created</dt>
              <dd class="col-sm-8">{{ formatDate(selectedCommission.created_at) }}</dd>

              <dt class="col-sm-4" v-if="selectedCommission.approved_at">Approved</dt>
              <dd class="col-sm-8" v-if="selectedCommission.approved_at">
                {{ formatDate(selectedCommission.approved_at) }}
              </dd>

              <dt class="col-sm-4" v-if="selectedCommission.payout">Payout</dt>
              <dd class="col-sm-8" v-if="selectedCommission.payout">
                {{ selectedCommission.payout.reference }}
              </dd>
            </dl>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDetailsModal = false">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAffiliateStore } from '@/stores/affiliateStore'
import axios from 'axios'

const affiliateStore = useAffiliateStore()

// State
const loading = ref(false)
const calculating = ref(false)
const commissions = ref([])
const affiliates = ref([])
const selectedCommissions = ref([])
const showPayoutModal = ref(false)
const showDetailsModal = ref(false)
const selectedCommission = ref(null)
const payoutNotes = ref('')

// Filters
const filters = reactive({
  status: 'pending',
  affiliate: '',
  dateRange: '30'
})

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalCommissions = ref(0)

// Computed
const totalPages = computed(() => Math.ceil(totalCommissions.value / pageSize.value))

const allSelected = computed(() => {
  if (commissions.value.length === 0) return false
  const selectableCommissions = commissions.value.filter(c => 
    c.status === 'pending' || c.status === 'approved'
  )
  return selectableCommissions.length > 0 && 
    selectableCommissions.every(c => selectedCommissions.value.includes(c.id))
})

const pendingCount = computed(() => 
  commissions.value.filter(c => c.status === 'pending').length
)

const pendingTotal = computed(() => 
  commissions.value
    .filter(c => c.status === 'pending')
    .reduce((sum, c) => sum + parseFloat(c.commission_amount), 0)
)

const approvedTotal = computed(() => 
  commissions.value
    .filter(c => c.status === 'approved')
    .reduce((sum, c) => sum + parseFloat(c.commission_amount), 0)
)

const paidTotal = computed(() => 
  commissions.value
    .filter(c => c.status === 'paid')
    .reduce((sum, c) => sum + parseFloat(c.commission_amount), 0)
)

const payoutSummary = computed(() => {
  const summary = {}
  const selected = commissions.value.filter(c => 
    selectedCommissions.value.includes(c.id)
  )
  
  selected.forEach(commission => {
    if (!summary[commission.affiliate_id]) {
      summary[commission.affiliate_id] = {
        affiliate_id: commission.affiliate_id,
        affiliate_name: commission.affiliate_name,
        payment_method: commission.payment_method || 'stripe_connect',
        count: 0,
        total: 0
      }
    }
    summary[commission.affiliate_id].count++
    summary[commission.affiliate_id].total += parseFloat(commission.commission_amount)
  })
  
  return Object.values(summary)
})

// Methods
const loadCommissions = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    
    if (filters.status) params.append('status', filters.status)
    if (filters.affiliate) params.append('affiliate_id', filters.affiliate)
    if (filters.dateRange) {
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - parseInt(filters.dateRange))
      params.append('start_date', startDate.toISOString().split('T')[0])
      params.append('end_date', endDate.toISOString().split('T')[0])
    }
    
    params.append('page', currentPage.value)
    params.append('page_size', pageSize.value)
    
    const response = await axios.get(`/api/commissions/?${params}`)
    commissions.value = response.data.results || response.data || []
    totalCommissions.value = response.data.count || commissions.value.length
  } catch (error) {
    console.error('Failed to load commissions:', error)
  } finally {
    loading.value = false
  }
}

const loadAffiliates = async () => {
  try {
    await affiliateStore.fetchAffiliates()
    affiliates.value = affiliateStore.affiliates
  } catch (error) {
    console.error('Failed to load affiliates:', error)
  }
}

const applyFilters = () => {
  currentPage.value = 1
  loadCommissions()
}

const toggleAllCommissions = (event) => {
  const selectableCommissions = commissions.value.filter(c => 
    c.status === 'pending' || c.status === 'approved'
  )
  
  if (event.target.checked) {
    selectedCommissions.value = selectableCommissions.map(c => c.id)
  } else {
    selectedCommissions.value = []
  }
}

const approveCommission = async (id) => {
  try {
    await axios.post(`/api/commissions/${id}/approve/`)
    await loadCommissions()
    alert('Commission approved successfully')
  } catch (error) {
    console.error('Failed to approve commission:', error)
    alert('Failed to approve commission')
  }
}

const rejectCommission = async (id) => {
  if (!confirm('Are you sure you want to reject this commission?')) return
  
  try {
    await axios.post(`/api/commissions/${id}/reject/`)
    await loadCommissions()
    alert('Commission rejected')
  } catch (error) {
    console.error('Failed to reject commission:', error)
    alert('Failed to reject commission')
  }
}

const calculateMonthlyCommissions = async () => {
  if (!confirm('Calculate commissions for the previous month?')) return
  
  calculating.value = true
  try {
    const response = await axios.post('/api/commissions/calculate_monthly/')
    alert(`Created ${response.data.commissions_created} new commissions`)
    await loadCommissions()
  } catch (error) {
    console.error('Failed to calculate commissions:', error)
    alert('Failed to calculate monthly commissions')
  } finally {
    calculating.value = false
  }
}

const calculateSelectedTotal = () => {
  const selected = commissions.value.filter(c => 
    selectedCommissions.value.includes(c.id)
  )
  return selected.reduce((sum, c) => sum + parseFloat(c.commission_amount), 0).toFixed(2)
}

const createPayoutBatch = async () => {
  try {
    const response = await axios.post('/api/payouts/create_batch/', {
      commission_ids: selectedCommissions.value,
      notes: payoutNotes.value
    })
    
    alert(`Payout batch created: ${response.data.payouts_created} payouts`)
    showPayoutModal.value = false
    selectedCommissions.value = []
    payoutNotes.value = ''
    await loadCommissions()
  } catch (error) {
    console.error('Failed to create payout batch:', error)
    alert('Failed to create payout batch')
  }
}

const viewDetails = (commission) => {
  selectedCommission.value = commission
  showDetailsModal.value = true
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
    year: 'numeric'
  })
}

// Load data on mount
onMounted(() => {
  loadCommissions()
  loadAffiliates()
})
</script>

<style scoped>
.commission-management {
  padding: 20px;
}

.card {
  border-radius: 10px;
}

.table th {
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
}

.modal {
  display: block;
}

.badge {
  font-size: 0.875em;
  padding: 0.35em 0.65em;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>