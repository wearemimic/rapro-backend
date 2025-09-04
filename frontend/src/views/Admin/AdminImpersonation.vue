<template>
  <div class="admin-impersonation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="row align-items-center">
        <div class="col">
          <h1 class="page-header-title">
            <i class="bi-person-check me-2"></i>
            User Impersonation Logs
          </h1>
          <p class="page-header-text">Monitor and audit all user impersonation sessions</p>
        </div>
        <div class="col-auto">
          <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Summary Statistics -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon bg-success">
            <i class="bi-activity"></i>
          </div>
          <div class="stats-content">
            <div class="stats-number">{{ summaryStats.active_sessions || 0 }}</div>
            <div class="stats-label">Active Sessions</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon bg-warning">
            <i class="bi-flag"></i>
          </div>
          <div class="stats-content">
            <div class="stats-number">{{ summaryStats.flagged_sessions || 0 }}</div>
            <div class="stats-label">Flagged for Review</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon bg-info">
            <i class="bi-calendar-day"></i>
          </div>
          <div class="stats-content">
            <div class="stats-number">{{ summaryStats.sessions_today || 0 }}</div>
            <div class="stats-label">Sessions Today</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="stats-card">
          <div class="stats-icon bg-secondary">
            <i class="bi-clock"></i>
          </div>
          <div class="stats-content">
            <div class="stats-number">{{ summaryStats.avg_duration_minutes || 0 }}m</div>
            <div class="stats-label">Avg Duration</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Sessions Alert -->
    <div v-if="activeSessions.length > 0" class="alert alert-warning mb-4">
      <div class="d-flex align-items-center">
        <i class="bi-exclamation-triangle-fill me-2"></i>
        <div>
          <strong>{{ activeSessions.length }} Active Impersonation Session(s)</strong>
          <div class="mt-1">
            <span v-for="(session, index) in activeSessions" :key="session.id" class="badge bg-warning text-dark me-2">
              {{ session.target_user.email }} ({{ session.duration_minutes }}m)
              <button @click="endSession(session.id)" class="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
            </span>
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
              v-model="searchTerm"
              @input="debounceSearch"
              type="text"
              class="form-control"
              placeholder="Search emails, reasons..."
            />
          </div>
          <div class="col-md-2">
            <label class="form-label">Status</label>
            <select v-model="filters.is_active" @change="applyFilters" class="form-select">
              <option value="">All Sessions</option>
              <option value="true">Active</option>
              <option value="false">Completed</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Date From</label>
            <input
              v-model="filters.date_from"
              @change="applyFilters"
              type="date"
              class="form-control"
            />
          </div>
          <div class="col-md-2">
            <label class="form-label">Date To</label>
            <input
              v-model="filters.date_to"
              @change="applyFilters"
              type="date"
              class="form-control"
            />
          </div>
          <div class="col-md-2">
            <div class="form-check mt-4">
              <input
                v-model="filters.flagged_only"
                @change="applyFilters"
                class="form-check-input"
                type="checkbox"
                id="flaggedOnly"
              />
              <label class="form-check-label" for="flaggedOnly">
                Flagged Only
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sessions Table -->
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">
          <i class="bi-list-ul me-2"></i>
          Impersonation Sessions
        </h5>
        <div class="d-flex align-items-center">
          <span class="text-muted me-3">
            {{ pagination.total_count }} total sessions
          </span>
          <select v-model="pagination.per_page" @change="applyFilters" class="form-select form-select-sm" style="width: auto;">
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="sessions.length > 0" class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Status</th>
                <th>Admin User</th>
                <th>Target User</th>
                <th>Start Time</th>
                <th>Duration</th>
                <th>Risk Score</th>
                <th>Actions</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="session in sessions" :key="session.id" :class="{ 'table-warning': session.flagged_for_review }">
                <td>
                  <span class="badge" :class="{
                    'bg-success': session.is_active,
                    'bg-secondary': !session.is_active,
                    'bg-danger': session.flagged_for_review
                  }">
                    {{ session.is_active ? 'ACTIVE' : 'COMPLETED' }}
                    <i v-if="session.flagged_for_review" class="bi-flag-fill ms-1"></i>
                  </span>
                </td>
                <td>
                  <div class="user-info">
                    <strong>{{ session.admin_user.name || session.admin_user.email }}</strong>
                    <div class="text-muted small">{{ session.admin_user.email }}</div>
                  </div>
                </td>
                <td>
                  <div class="user-info">
                    <strong>{{ session.target_user.name || session.target_user.email }}</strong>
                    <div class="text-muted small">{{ session.target_user.email }}</div>
                  </div>
                </td>
                <td>
                  <div>{{ formatDateTime(session.start_timestamp) }}</div>
                  <div v-if="session.end_timestamp" class="text-muted small">
                    Ended: {{ formatDateTime(session.end_timestamp) }}
                  </div>
                </td>
                <td>
                  <span v-if="session.duration_minutes !== null">
                    {{ session.duration_minutes }}m
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <div class="risk-score">
                    <span class="badge" :class="{
                      'bg-success': session.risk_score <= 30,
                      'bg-warning': session.risk_score > 30 && session.risk_score <= 70,
                      'bg-danger': session.risk_score > 70
                    }">
                      {{ session.risk_score }}%
                    </span>
                  </div>
                </td>
                <td>
                  <div class="action-counts">
                    <span class="badge bg-info me-1">
                      <i class="bi-gear"></i> {{ session.actions_count }}
                    </span>
                    <span class="badge bg-secondary">
                      <i class="bi-file-text"></i> {{ session.pages_count }}
                    </span>
                  </div>
                </td>
                <td>
                  <div class="btn-group" role="group">
                    <button
                      @click="viewSessionDetail(session.id)"
                      class="btn btn-sm btn-outline-primary"
                      title="View Details"
                    >
                      <i class="bi-eye"></i>
                    </button>
                    <button
                      v-if="session.is_active"
                      @click="endSession(session.id)"
                      class="btn btn-sm btn-outline-danger"
                      title="End Session"
                    >
                      <i class="bi-stop-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-5">
          <i class="bi-inbox display-1 text-muted"></i>
          <h5 class="mt-3">No Impersonation Sessions</h5>
          <p class="text-muted">No sessions match your current filters.</p>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.total_pages > 1" class="card-footer">
        <nav aria-label="Sessions pagination">
          <ul class="pagination pagination-sm justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: !pagination.has_previous }">
              <button @click="changePage(pagination.current_page - 1)" class="page-link" :disabled="!pagination.has_previous">
                Previous
              </button>
            </li>
            <li
              v-for="page in paginationRange"
              :key="page"
              class="page-item"
              :class="{ active: page === pagination.current_page }"
            >
              <button @click="changePage(page)" class="page-link">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <button @click="changePage(pagination.current_page + 1)" class="page-link" :disabled="!pagination.has_next">
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Session Detail Modal -->
    <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-dialog modal-lg" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Session Details</h5>
            <button type="button" class="btn-close" @click="closeDetailModal">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="selectedSession" class="row">
              <!-- Session Overview -->
              <div class="col-12 mb-4">
                <h6>Session Overview</h6>
                <div class="row">
                  <div class="col-md-6">
                    <strong>Session ID:</strong> {{ selectedSession.id }}<br>
                    <strong>Status:</strong> 
                    <span class="badge" :class="{ 'bg-success': selectedSession.is_active, 'bg-secondary': !selectedSession.is_active }">
                      {{ selectedSession.is_active ? 'ACTIVE' : 'COMPLETED' }}
                    </span><br>
                    <strong>Risk Score:</strong> 
                    <span class="badge" :class="{
                      'bg-success': selectedSession.risk_score <= 30,
                      'bg-warning': selectedSession.risk_score > 30 && selectedSession.risk_score <= 70,
                      'bg-danger': selectedSession.risk_score > 70
                    }">{{ selectedSession.risk_score }}%</span>
                  </div>
                  <div class="col-md-6">
                    <strong>Duration:</strong> {{ selectedSession.duration_minutes || 0 }} minutes<br>
                    <strong>IP Address:</strong> {{ selectedSession.ip_address }}<br>
                    <strong>Flagged:</strong> {{ selectedSession.flagged_for_review ? 'Yes' : 'No' }}
                  </div>
                </div>
              </div>

              <!-- Users -->
              <div class="col-12 mb-4">
                <h6>Participants</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div class="user-card">
                      <strong>Admin User</strong>
                      <div>{{ selectedSession.admin_user.name || selectedSession.admin_user.email }}</div>
                      <div class="text-muted small">{{ selectedSession.admin_user.email }}</div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="user-card">
                      <strong>Target User</strong>
                      <div>{{ selectedSession.target_user.name || selectedSession.target_user.email }}</div>
                      <div class="text-muted small">{{ selectedSession.target_user.email }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reason -->
              <div class="col-12 mb-4">
                <h6>Justification</h6>
                <p class="bg-light p-3 rounded">{{ selectedSession.reason }}</p>
              </div>

              <!-- Actions Performed -->
              <div v-if="selectedSession.actions_performed && selectedSession.actions_performed.length > 0" class="col-12 mb-4">
                <h6>Actions Performed ({{ selectedSession.actions_performed.length }})</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Action</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(action, index) in selectedSession.actions_performed" :key="index">
                        <td>{{ formatDateTime(action.timestamp) }}</td>
                        <td>{{ action.action_type }}</td>
                        <td>{{ action.details || '-' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Pages Accessed -->
              <div v-if="selectedSession.pages_accessed && selectedSession.pages_accessed.length > 0" class="col-12 mb-4">
                <h6>Pages Accessed ({{ selectedSession.pages_accessed.length }})</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Page</th>
                        <th>URL</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(page, index) in selectedSession.pages_accessed" :key="index">
                        <td>{{ formatDateTime(page.timestamp) }}</td>
                        <td>{{ page.page_name }}</td>
                        <td class="text-truncate" style="max-width: 300px;">{{ page.url }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Technical Details -->
              <div class="col-12 mb-4">
                <h6>Technical Details</h6>
                <div class="row">
                  <div class="col-md-6">
                    <strong>Session Key:</strong> {{ selectedSession.session_key }}<br>
                    <strong>Start Time:</strong> {{ formatDateTime(selectedSession.start_timestamp) }}<br>
                    <strong>End Time:</strong> {{ selectedSession.end_timestamp ? formatDateTime(selectedSession.end_timestamp) : 'Still Active' }}
                  </div>
                  <div class="col-md-6">
                    <strong>User Agent:</strong><br>
                    <small class="text-muted">{{ selectedSession.user_agent }}</small>
                  </div>
                </div>
              </div>

              <!-- Review Information -->
              <div v-if="selectedSession.reviewed_by || selectedSession.review_notes" class="col-12">
                <h6>Review Information</h6>
                <div v-if="selectedSession.reviewed_by">
                  <strong>Reviewed By:</strong> {{ selectedSession.reviewed_by.name || selectedSession.reviewed_by.email }}<br>
                </div>
                <div v-if="selectedSession.review_notes">
                  <strong>Review Notes:</strong><br>
                  <p class="bg-light p-2 rounded">{{ selectedSession.review_notes }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeDetailModal">Close</button>
            <button
              v-if="selectedSession && selectedSession.is_active"
              @click="endSession(selectedSession.id)"
              class="btn btn-danger"
            >
              End Session
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '@/config'

// Reactive data
const loading = ref(false)
const sessions = ref([])
const activeSessions = ref([])
const selectedSession = ref(null)
const showDetailModal = ref(false)
const searchTerm = ref('')
const searchDebounceTimer = ref(null)

// Pagination and filters
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  per_page: 25,
  has_next: false,
  has_previous: false
})

const filters = ref({
  is_active: '',
  date_from: '',
  date_to: '',
  flagged_only: false
})

const summaryStats = ref({
  active_sessions: 0,
  flagged_sessions: 0,
  sessions_today: 0,
  avg_duration_minutes: 0
})

// Computed
const paginationRange = computed(() => {
  const range = []
  const total = pagination.value.total_pages
  const current = pagination.value.current_page
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      range.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) range.push(i)
      range.push('...')
      range.push(total)
    } else if (current >= total - 3) {
      range.push(1)
      range.push('...')
      for (let i = total - 4; i <= total; i++) range.push(i)
    } else {
      range.push(1)
      range.push('...')
      for (let i = current - 1; i <= current + 1; i++) range.push(i)
      range.push('...')
      range.push(total)
    }
  }
  
  return range.filter(item => item !== '...' || range.indexOf(item) === range.lastIndexOf(item))
})

// Methods
const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchSessions = async (page = 1) => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: pagination.value.per_page.toString()
    })

    // Add filters
    if (filters.value.is_active) params.append('is_active', filters.value.is_active)
    if (filters.value.date_from) params.append('date_from', filters.value.date_from)
    if (filters.value.date_to) params.append('date_to', filters.value.date_to)
    if (filters.value.flagged_only) params.append('flagged_only', 'true')
    if (searchTerm.value.trim()) params.append('search', searchTerm.value.trim())

    const response = await axios.get(`${API_CONFIG.API_URL}/admin/impersonation/logs/?${params}`)
    const data = response.data

    sessions.value = data.sessions
    pagination.value = data.pagination
    summaryStats.value = data.summary_stats

  } catch (error) {
    console.error('Failed to fetch sessions:', error)
    // Handle error - maybe show a toast
  } finally {
    loading.value = false
  }
}

const fetchActiveSessions = async () => {
  try {
    const response = await axios.get('${API_CONFIG.API_URL}/admin/impersonation/active/')
    activeSessions.value = response.data.active_sessions
  } catch (error) {
    console.error('Failed to fetch active sessions:', error)
  }
}

const viewSessionDetail = async (sessionId) => {
  try {
    const response = await axios.get(`${API_CONFIG.API_URL}/admin/impersonation/logs/${sessionId}/`)
    selectedSession.value = response.data
    showDetailModal.value = true
  } catch (error) {
    console.error('Failed to fetch session details:', error)
    alert('Failed to load session details')
  }
}

const endSession = async (sessionId) => {
  if (!confirm('Are you sure you want to end this impersonation session?')) return

  try {
    await axios.post(`${API_CONFIG.API_URL}/admin/impersonation/${sessionId}/end/`)
    alert('Session ended successfully')
    await refreshData()
    if (showDetailModal.value && selectedSession.value?.id === sessionId) {
      closeDetailModal()
    }
  } catch (error) {
    console.error('Failed to end session:', error)
    alert('Failed to end session')
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedSession.value = null
}

const applyFilters = () => {
  fetchSessions(1)
}

const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchSessions(page)
  }
}

const debounceSearch = () => {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }
  searchDebounceTimer.value = setTimeout(() => {
    applyFilters()
  }, 500)
}

const refreshData = async () => {
  await Promise.all([
    fetchSessions(pagination.value.current_page),
    fetchActiveSessions()
  ])
}

// Load initial data
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.admin-impersonation-page {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.page-header-title {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.page-header-text {
  color: #6c757d;
  margin-bottom: 0;
}

.stats-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid #dee2e6;
  margin-bottom: 1rem;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  color: white;
  font-size: 1.5rem;
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
}

.stats-label {
  color: #6c757d;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.user-info strong {
  display: block;
}

.user-card {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
}

.risk-score .badge {
  font-size: 0.75rem;
}

.action-counts .badge {
  font-size: 0.7rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-dialog {
  max-width: 900px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #000;
  opacity: 0.5;
}

.btn-close:hover {
  opacity: 1;
}

.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1);
}

.pagination {
  margin-bottom: 0;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid #dee2e6;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}
</style>