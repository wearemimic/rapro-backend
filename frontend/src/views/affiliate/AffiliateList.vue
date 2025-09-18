<template>
  <div class="affiliate-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Affiliate Management</h1>
        <p class="text-muted">Manage your affiliate partners and track their performance</p>
      </div>
      <div>
        <a 
          href="/affiliate/portal/login"
          target="_blank"
          class="btn btn-outline-success me-2"
        >
          <i class="fas fa-sign-in-alt me-2"></i>
          Affiliate Portal
        </a>
        <router-link 
          to="/affiliate-dashboard"
          class="btn btn-outline-primary me-2"
        >
          <i class="fas fa-chart-line me-2"></i>
          View Analytics
        </router-link>
        <button 
          class="btn btn-primary"
          @click="showCreateModal = true"
        >
          <i class="fas fa-plus me-2"></i>
          Add New Affiliate
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="text-muted mb-2">Total Affiliates</h6>
            <h3 class="mb-0">{{ pagination.total }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="text-muted mb-2">Active</h6>
            <h3 class="mb-0 text-success">{{ activeCount }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="text-muted mb-2">Pending Approval</h6>
            <h3 class="mb-0 text-warning">{{ pendingCount }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h6 class="text-muted mb-2">Total Commissions</h6>
            <h3 class="mb-0">${{ totalCommissions }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Search</label>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search by name, email, or code..."
              @input="handleSearch"
            />
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select
              v-model="statusFilter"
              class="form-select"
              @change="handleFilterChange"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Sort By</label>
            <select v-model="sortBy" class="form-select" @change="handleSort">
              <option value="-created_at">Newest First</option>
              <option value="created_at">Oldest First</option>
              <option value="business_name">Name A-Z</option>
              <option value="-business_name">Name Z-A</option>
              <option value="-total_conversions">Most Conversions</option>
              <option value="-total_commissions_earned">Highest Earnings</option>
            </select>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button
              class="btn btn-outline-secondary w-100"
              @click="resetFilters"
            >
              <i class="fas fa-redo me-2"></i>
              Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Affiliates Table -->
    <div class="card">
      <div class="card-body p-0">
        <div v-if="loading" class="text-center p-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Loading affiliates...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger m-3">
          <i class="fas fa-exclamation-triangle me-2"></i>
          {{ error }}
        </div>

        <div v-else-if="affiliates.length === 0" class="text-center p-5">
          <i class="fas fa-users fa-3x text-muted mb-3"></i>
          <h5>No Affiliates Found</h5>
          <p class="text-muted">
            {{ searchQuery || statusFilter ? 'Try adjusting your filters' : 'Add your first affiliate to get started' }}
          </p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    class="form-check-input"
                    :checked="allSelected"
                    @change="toggleSelectAll"
                  />
                </th>
                <th>Affiliate</th>
                <th>Code</th>
                <th>Status</th>
                <th>Clicks</th>
                <th>Conversions</th>
                <th>Revenue</th>
                <th>Commissions</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="affiliate in affiliates"
                :key="affiliate.id"
                :class="{ 'table-warning': affiliate.status === 'pending' }"
              >
                <td>
                  <input
                    type="checkbox"
                    class="form-check-input"
                    :checked="selectedIds.includes(affiliate.id)"
                    @change="toggleSelect(affiliate.id)"
                  />
                </td>
                <td>
                  <div>
                    <strong>{{ affiliate.business_name }}</strong>
                    <br />
                    <small class="text-muted">{{ affiliate.email }}</small>
                  </div>
                </td>
                <td>
                  <code>{{ affiliate.affiliate_code }}</code>
                  <button
                    class="btn btn-sm btn-link p-0 ms-2"
                    @click="copyCode(affiliate.affiliate_code)"
                    title="Copy code"
                  >
                    <i class="fas fa-copy"></i>
                  </button>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="{
                      'bg-warning': affiliate.status === 'pending',
                      'bg-success': affiliate.status === 'active',
                      'bg-danger': affiliate.status === 'suspended',
                      'bg-secondary': affiliate.status === 'terminated'
                    }"
                  >
                    {{ affiliate.status }}
                  </span>
                </td>
                <td>{{ affiliate.total_clicks || 0 }}</td>
                <td>
                  {{ affiliate.total_conversions || 0 }}
                  <span v-if="affiliate.total_clicks > 0" class="text-muted">
                    ({{ ((affiliate.total_conversions / affiliate.total_clicks) * 100).toFixed(1) }}%)
                  </span>
                </td>
                <td>${{ formatNumber(affiliate.total_revenue_generated || 0) }}</td>
                <td>
                  <div>
                    <strong>${{ formatNumber(affiliate.total_commissions_earned || 0) }}</strong>
                    <br />
                    <small class="text-muted">
                      Pending: ${{ formatNumber(affiliate.pending_commission_balance || 0) }}
                    </small>
                  </div>
                </td>
                <td>{{ formatDate(affiliate.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button
                      class="btn btn-outline-primary"
                      @click="viewAffiliate(affiliate)"
                      title="View Details"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    <button
                      class="btn btn-outline-secondary"
                      @click="editAffiliate(affiliate)"
                      title="Edit"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <div class="btn-group btn-group-sm" role="group">
                      <button
                        type="button"
                        class="btn btn-outline-secondary dropdown-toggle"
                        data-bs-toggle="dropdown"
                      >
                        <i class="fas fa-ellipsis-v"></i>
                      </button>
                      <ul class="dropdown-menu">
                        <li v-if="affiliate.status === 'pending'">
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="approveAffiliate(affiliate)"
                          >
                            <i class="fas fa-check text-success me-2"></i>
                            Approve
                          </a>
                        </li>
                        <li v-if="affiliate.status === 'active'">
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="suspendAffiliate(affiliate)"
                          >
                            <i class="fas fa-pause text-warning me-2"></i>
                            Suspend
                          </a>
                        </li>
                        <li v-if="affiliate.status === 'suspended'">
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="reactivateAffiliate(affiliate)"
                          >
                            <i class="fas fa-play text-success me-2"></i>
                            Reactivate
                          </a>
                        </li>
                        <li>
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="viewDashboard(affiliate)"
                          >
                            <i class="fas fa-chart-line me-2"></i>
                            View Dashboard
                          </a>
                        </li>
                        <li>
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="viewLinks(affiliate)"
                          >
                            <i class="fas fa-link me-2"></i>
                            Manage Links
                          </a>
                        </li>
                        <li>
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="viewCommissions(affiliate)"
                          >
                            <i class="fas fa-dollar-sign me-2"></i>
                            View Commissions
                          </a>
                        </li>
                        <li>
                          <a
                            class="dropdown-item"
                            href="#"
                            @click.prevent="setupStripeConnect(affiliate)"
                          >
                            <i class="fas fa-credit-card me-2"></i>
                            Payment Setup
                          </a>
                        </li>
                        <li><hr class="dropdown-divider" /></li>
                        <li>
                          <a
                            class="dropdown-item text-danger"
                            href="#"
                            @click.prevent="deleteAffiliate(affiliate)"
                          >
                            <i class="fas fa-trash me-2"></i>
                            Delete
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="d-flex justify-content-between align-items-center p-3 border-top">
          <div class="text-muted">
            Showing {{ (currentPage - 1) * pageSize + 1 }} to
            {{ Math.min(currentPage * pageSize, pagination.total) }} of
            {{ pagination.total }} affiliates
          </div>
          <nav>
            <ul class="pagination mb-0">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a
                  class="page-link"
                  href="#"
                  @click.prevent="changePage(currentPage - 1)"
                >
                  Previous
                </a>
              </li>
              <li
                v-for="page in displayedPages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
              >
                <a
                  class="page-link"
                  href="#"
                  @click.prevent="changePage(page)"
                >
                  {{ page }}
                </a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a
                  class="page-link"
                  href="#"
                  @click.prevent="changePage(currentPage + 1)"
                >
                  Next
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Bulk Actions -->
    <div v-if="selectedIds.length > 0" class="position-fixed bottom-0 start-50 translate-middle-x mb-3">
      <div class="card shadow">
        <div class="card-body d-flex align-items-center">
          <span class="me-3">
            <strong>{{ selectedIds.length }}</strong> affiliate(s) selected
          </span>
          <button
            class="btn btn-sm btn-success me-2"
            @click="bulkApprove"
          >
            <i class="fas fa-check me-1"></i>
            Approve
          </button>
          <button
            class="btn btn-sm btn-warning me-2"
            @click="bulkSuspend"
          >
            <i class="fas fa-pause me-1"></i>
            Suspend
          </button>
          <button
            class="btn btn-sm btn-danger me-2"
            @click="bulkDelete"
          >
            <i class="fas fa-trash me-1"></i>
            Delete
          </button>
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="clearSelection"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal would go here -->
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAffiliateStore } from '@/stores/affiliateStore'
import affiliateService from '@/services/affiliateService'

export default {
  name: 'AffiliateList',
  setup() {
    const router = useRouter()
    const affiliateStore = useAffiliateStore()
    
    // Data
    const searchQuery = ref('')
    const statusFilter = ref('')
    const sortBy = ref('-created_at')
    const selectedIds = ref([])
    const showCreateModal = ref(false)
    
    // Computed
    const affiliates = computed(() => affiliateStore.affiliates)
    const loading = computed(() => affiliateStore.loading)
    const error = computed(() => affiliateStore.error)
    const pagination = computed(() => affiliateStore.pagination)
    const currentPage = computed(() => pagination.value.page)
    const pageSize = computed(() => pagination.value.pageSize)
    const totalPages = computed(() => pagination.value.totalPages)
    
    const activeCount = computed(() => 
      affiliates.value.filter(a => a.status === 'active').length
    )
    
    const pendingCount = computed(() => 
      affiliates.value.filter(a => a.status === 'pending').length
    )
    
    const totalCommissions = computed(() => 
      affiliates.value.reduce((sum, a) => sum + parseFloat(a.total_commissions_earned || 0), 0).toFixed(2)
    )
    
    const allSelected = computed(() => 
      affiliates.value.length > 0 && affiliates.value.every(a => selectedIds.value.includes(a.id))
    )
    
    const displayedPages = computed(() => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 3) {
          for (let i = 1; i <= 5; i++) {
            pages.push(i)
          }
          pages.push('...', total)
        } else if (current >= total - 2) {
          pages.push(1, '...')
          for (let i = total - 4; i <= total; i++) {
            pages.push(i)
          }
        } else {
          pages.push(1, '...')
          for (let i = current - 1; i <= current + 1; i++) {
            pages.push(i)
          }
          pages.push('...', total)
        }
      }
      
      return pages
    })
    
    // Methods
    const loadAffiliates = async () => {
      await affiliateStore.fetchAffiliates({
        search: searchQuery.value,
        status: statusFilter.value,
        ordering: sortBy.value
      })
    }
    
    const handleSearch = () => {
      affiliateStore.setSearchQuery(searchQuery.value)
      affiliateStore.setPagination(1)
      loadAffiliates()
    }
    
    const handleFilterChange = () => {
      affiliateStore.setFilters({ status: statusFilter.value })
      affiliateStore.setPagination(1)
      loadAffiliates()
    }
    
    const handleSort = () => {
      loadAffiliates()
    }
    
    const resetFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      sortBy.value = '-created_at'
      affiliateStore.setSearchQuery('')
      affiliateStore.setFilters({ status: '' })
      affiliateStore.setPagination(1)
      loadAffiliates()
    }
    
    const changePage = (page) => {
      if (page < 1 || page > totalPages.value || page === '...') return
      affiliateStore.setPagination(page)
      loadAffiliates()
    }
    
    const toggleSelectAll = () => {
      if (allSelected.value) {
        selectedIds.value = []
      } else {
        selectedIds.value = affiliates.value.map(a => a.id)
      }
    }
    
    const toggleSelect = (id) => {
      const index = selectedIds.value.indexOf(id)
      if (index > -1) {
        selectedIds.value.splice(index, 1)
      } else {
        selectedIds.value.push(id)
      }
    }
    
    const clearSelection = () => {
      selectedIds.value = []
    }
    
    const viewAffiliate = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}`)
    }
    
    const editAffiliate = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}/edit`)
    }
    
    const viewDashboard = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}/dashboard`)
    }
    
    const viewLinks = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}/links`)
    }
    
    const viewCommissions = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}/commissions`)
    }
    
    const setupStripeConnect = (affiliate) => {
      router.push(`/affiliates/${affiliate.id}/stripe-connect`)
    }
    
    const approveAffiliate = async (affiliate) => {
      if (confirm(`Approve ${affiliate.business_name} as an affiliate?`)) {
        try {
          await affiliateStore.approveAffiliate(affiliate.id)
          alert('Affiliate approved successfully!')
        } catch (error) {
          alert('Failed to approve affiliate: ' + error.message)
        }
      }
    }
    
    const suspendAffiliate = async (affiliate) => {
      if (confirm(`Suspend ${affiliate.business_name}? This will deactivate all their tracking links.`)) {
        try {
          await affiliateStore.suspendAffiliate(affiliate.id)
          alert('Affiliate suspended successfully!')
        } catch (error) {
          alert('Failed to suspend affiliate: ' + error.message)
        }
      }
    }
    
    const reactivateAffiliate = async (affiliate) => {
      try {
        await affiliateStore.updateAffiliate(affiliate.id, { status: 'active' })
        await loadAffiliates()
        alert('Affiliate reactivated successfully!')
      } catch (error) {
        alert('Failed to reactivate affiliate: ' + error.message)
      }
    }
    
    const deleteAffiliate = async (affiliate) => {
      if (confirm(`Delete ${affiliate.business_name}? This action cannot be undone.`)) {
        try {
          await affiliateStore.deleteAffiliate(affiliate.id)
          alert('Affiliate deleted successfully!')
        } catch (error) {
          alert('Failed to delete affiliate: ' + error.message)
        }
      }
    }
    
    const bulkApprove = async () => {
      if (confirm(`Approve ${selectedIds.value.length} affiliate(s)?`)) {
        try {
          await affiliateService.bulkApproveAffiliates(selectedIds.value)
          clearSelection()
          await loadAffiliates()
          alert('Affiliates approved successfully!')
        } catch (error) {
          alert('Failed to approve affiliates: ' + error.message)
        }
      }
    }
    
    const bulkSuspend = async () => {
      if (confirm(`Suspend ${selectedIds.value.length} affiliate(s)?`)) {
        try {
          await affiliateService.bulkSuspendAffiliates(selectedIds.value)
          clearSelection()
          await loadAffiliates()
          alert('Affiliates suspended successfully!')
        } catch (error) {
          alert('Failed to suspend affiliates: ' + error.message)
        }
      }
    }
    
    const bulkDelete = async () => {
      if (confirm(`Delete ${selectedIds.value.length} affiliate(s)? This action cannot be undone.`)) {
        try {
          for (const id of selectedIds.value) {
            await affiliateStore.deleteAffiliate(id)
          }
          clearSelection()
          await loadAffiliates()
          alert('Affiliates deleted successfully!')
        } catch (error) {
          alert('Failed to delete affiliates: ' + error.message)
        }
      }
    }
    
    const copyCode = async (code) => {
      try {
        await navigator.clipboard.writeText(code)
        alert('Affiliate code copied to clipboard!')
      } catch (error) {
        alert('Failed to copy code: ' + error.message)
      }
    }
    
    const formatNumber = (num) => {
      return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }
    
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    // Lifecycle
    onMounted(() => {
      loadAffiliates()
    })
    
    return {
      // Data
      searchQuery,
      statusFilter,
      sortBy,
      selectedIds,
      showCreateModal,
      
      // Computed
      affiliates,
      loading,
      error,
      pagination,
      currentPage,
      pageSize,
      totalPages,
      activeCount,
      pendingCount,
      totalCommissions,
      allSelected,
      displayedPages,
      
      // Methods
      handleSearch,
      handleFilterChange,
      handleSort,
      resetFilters,
      changePage,
      toggleSelectAll,
      toggleSelect,
      clearSelection,
      viewAffiliate,
      editAffiliate,
      viewDashboard,
      viewLinks,
      viewCommissions,
      setupStripeConnect,
      approveAffiliate,
      suspendAffiliate,
      reactivateAffiliate,
      deleteAffiliate,
      bulkApprove,
      bulkSuspend,
      bulkDelete,
      copyCode,
      formatNumber,
      formatDate
    }
  }
}
</script>

<style scoped>
.affiliate-list {
  padding: 20px;
  margin-top: 60px; /* Add space for fixed header */
}

.table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

code {
  padding: 2px 6px;
  background-color: #f5f5f5;
  border-radius: 3px;
}
</style>