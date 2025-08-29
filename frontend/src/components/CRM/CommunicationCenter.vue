<template>
  <div class="communication-center">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Communication Center</h1>
        <p class="text-muted mb-0">Manage client communications and email accounts</p>
      </div>
      <div class="d-flex gap-2">
        <button 
          class="btn btn-outline-primary"
          @click="refreshData"
          :disabled="isRefreshing"
        >
          <i class="bi bi-arrow-clockwise" :class="{ 'spin': isRefreshing }"></i>
          <span class="ms-1">Refresh</span>
        </button>
        <button 
          class="btn btn-primary"
          @click="showComposeModal = true"
          :disabled="!hasEmailAccounts"
        >
          <i class="bi bi-plus-circle me-1"></i>
          Compose Email
        </button>
      </div>
    </div>

    <!-- Quick Stats Row -->
    <div class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-primary text-white">
                  <i class="bi bi-envelope"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ analytics.total_communications }}</span>
                <span class="d-block fs-6 text-muted">Total Communications</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-warning text-white">
                  <i class="bi bi-exclamation-triangle"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ analytics.unread_count }}</span>
                <span class="d-block fs-6 text-muted">Unread Messages</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-danger text-white">
                  <i class="bi bi-star-fill"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ analytics.high_priority_count }}</span>
                <span class="d-block fs-6 text-muted">High Priority</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-3 col-sm-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-success text-white">
                  <i class="bi bi-check-circle"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ analytics.read_percentage }}%</span>
                <span class="d-block fs-6 text-muted">Read Rate</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="row">
      <!-- Sidebar -->
      <div class="col-lg-3 col-md-4 mb-4">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-transparent border-bottom">
            <h6 class="card-title mb-0">Filters & Views</h6>
          </div>
          <div class="card-body p-0">
            <!-- Quick Filter Buttons -->
            <div class="list-group list-group-flush">
              <button 
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                :class="{ active: currentView === 'all' }"
                @click="setView('all')"
              >
                <span><i class="bi bi-inbox me-2"></i>All Messages</span>
                <span class="badge bg-secondary rounded-pill">{{ analytics.total_communications }}</span>
              </button>
              
              <button 
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                :class="{ active: currentView === 'unread' }"
                @click="setView('unread')"
              >
                <span><i class="bi bi-envelope me-2"></i>Unread</span>
                <span class="badge bg-warning rounded-pill">{{ analytics.unread_count }}</span>
              </button>
              
              <button 
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                :class="{ active: currentView === 'priority' }"
                @click="setView('priority')"
              >
                <span><i class="bi bi-star me-2"></i>High Priority</span>
                <span class="badge bg-danger rounded-pill">{{ analytics.high_priority_count }}</span>
              </button>
            </div>

            <!-- Sentiment Filters -->
            <div class="p-3 border-top">
              <h6 class="mb-2">Sentiment</h6>
              <div class="d-flex flex-wrap gap-1">
                <button 
                  v-for="sentiment in sentimentOptions" 
                  :key="sentiment.value"
                  class="btn btn-sm"
                  :class="filters.sentiment === sentiment.value ? sentiment.activeClass : sentiment.inactiveClass"
                  @click="toggleSentimentFilter(sentiment.value)"
                >
                  <i :class="sentiment.icon" class="me-1"></i>
                  {{ sentiment.label }}
                </button>
              </div>
            </div>

            <!-- Communication Type Filters -->
            <div class="p-3 border-top">
              <h6 class="mb-2">Type</h6>
              <div class="d-flex flex-wrap gap-1">
                <button 
                  v-for="type in typeOptions" 
                  :key="type.value"
                  class="btn btn-sm"
                  :class="filters.type === type.value ? 'btn-primary' : 'btn-outline-primary'"
                  @click="toggleTypeFilter(type.value)"
                >
                  <i :class="type.icon" class="me-1"></i>
                  {{ type.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Email Setup Section -->
        <div class="card border-0 shadow-sm mt-4" v-if="!hasEmailAccounts">
          <div class="card-body text-center">
            <div class="avatar avatar-lg avatar-circle bg-soft-primary text-primary mx-auto mb-3">
              <i class="bi bi-envelope-plus"></i>
            </div>
            <h6 class="mb-2">Setup Email Integration</h6>
            <p class="text-muted small mb-3">Connect your email accounts to start managing communications</p>
            <button 
              class="btn btn-primary btn-sm"
              @click="showEmailSetup = true"
            >
              <i class="bi bi-plus me-1"></i>
              Setup Email
            </button>
          </div>
        </div>

        <!-- Sync Status -->
        <div class="card border-0 shadow-sm mt-4" v-if="hasEmailAccounts">
          <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Email Sync Status</h6>
            <button 
              class="btn btn-sm btn-outline-primary"
              @click="triggerSync"
              :disabled="isSyncing"
            >
              <i class="bi bi-arrow-clockwise" :class="{ 'spin': isSyncing }"></i>
            </button>
          </div>
          <div class="card-body p-2">
            <div 
              v-for="account in emailAccounts" 
              :key="account.id"
              class="d-flex align-items-center justify-content-between py-2 px-2 rounded"
            >
              <div class="d-flex align-items-center">
                <i :class="getProviderIcon(account.provider)" class="me-2"></i>
                <small class="text-truncate">{{ account.email }}</small>
              </div>
              <div class="d-flex align-items-center">
                <span 
                  class="badge badge-soft-success"
                  v-if="account.is_active"
                >
                  Active
                </span>
                <span 
                  class="badge badge-soft-secondary"
                  v-else
                >
                  Inactive
                </span>
              </div>
            </div>
            
            <div class="text-center py-2" v-if="lastSyncTime">
              <small class="text-muted">
                Last sync: {{ formatLastSync(lastSyncTime) }}
              </small>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Communication List -->
      <div class="col-lg-9 col-md-8">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-transparent border-bottom">
            <div class="row align-items-center">
              <div class="col">
                <div class="d-flex align-items-center">
                  <h6 class="mb-0 me-3">Communications</h6>
                  <span class="badge bg-light text-dark" v-if="hasActiveFilters">
                    {{ activeFilterCount }} filter{{ activeFilterCount > 1 ? 's' : '' }} applied
                  </span>
                </div>
              </div>
              <div class="col-auto">
                <div class="d-flex align-items-center gap-2">
                  <!-- Search -->
                  <div class="input-group input-group-sm" style="width: 200px;">
                    <input 
                      v-model="searchQuery"
                      @input="onSearchInput"
                      type="text" 
                      class="form-control" 
                      placeholder="Search communications..."
                    >
                    <button class="btn btn-outline-secondary" type="button" @click="clearSearch" v-if="searchQuery">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>

                  <!-- Bulk Actions -->
                  <div class="dropdown" v-if="hasSelectedCommunications">
                    <button class="btn btn-sm btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                      Actions ({{ selectedCount }})
                    </button>
                    <ul class="dropdown-menu">
                      <li><button class="dropdown-item" @click="bulkMarkRead">Mark as Read</button></li>
                      <li><button class="dropdown-item" @click="bulkMarkUnread">Mark as Unread</button></li>
                      <li><hr class="dropdown-divider"></li>
                      <li><button class="dropdown-item text-danger" @click="bulkDelete">Delete Selected</button></li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Communication List Component -->
          <CommunicationList 
            :communications="communications"
            :loading="loading.communications"
            :selected-communications="selectedCommunications"
            @select-communication="selectCommunication"
            @deselect-communication="deselectCommunication"
            @toggle-read="toggleRead"
            @view-communication="viewCommunication"
            @delete-communication="deleteCommunication"
          />
        </div>

        <!-- Pagination -->
        <nav class="d-flex justify-content-between align-items-center mt-4" v-if="totalPages > 1">
          <div>
            <span class="text-muted">
              Showing {{ ((currentPage - 1) * pageSize) + 1 }} to {{ Math.min(currentPage * pageSize, totalCount) }} of {{ totalCount }} communications
            </span>
          </div>
          <div>
            <div class="btn-group">
              <button 
                class="btn btn-outline-primary btn-sm"
                @click="previousPage"
                :disabled="!hasPrevious"
              >
                <i class="bi bi-chevron-left"></i>
                Previous
              </button>
              <button 
                class="btn btn-outline-primary btn-sm"
                @click="nextPage"
                :disabled="!hasNext"
              >
                Next
                <i class="bi bi-chevron-right"></i>
              </button>
            </div>
          </div>
        </nav>
      </div>
    </div>

    <!-- Modals -->
    <EmailCompose 
      v-if="showComposeModal"
      @close="showComposeModal = false"
      @sent="onEmailSent"
    />

    <EmailSetup 
      v-if="showEmailSetup"
      @close="showEmailSetup = false"
      @account-added="onEmailAccountAdded"
    />

    <CommunicationDetail 
      v-if="showDetailModal"
      :communication-id="selectedCommunicationId"
      @close="showDetailModal = false"
      @updated="onCommunicationUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useCommunicationStore } from '@/stores/communicationStore'
import { useEmailStore } from '@/stores/emailStore'
import CommunicationList from './CommunicationList.vue'
import EmailCompose from './EmailCompose.vue'
import EmailSetup from './EmailSetup.vue'
import CommunicationDetail from './CommunicationDetail.vue'

// Stores
const communicationStore = useCommunicationStore()
const emailStore = useEmailStore()

// Component state
const showComposeModal = ref(false)
const showEmailSetup = ref(false)
const showDetailModal = ref(false)
const selectedCommunicationId = ref(null)
const currentView = ref('all')
const searchQuery = ref('')
const searchTimeout = ref(null)
const isRefreshing = ref(false)

// Store computed properties
const communications = computed(() => communicationStore.communications)
const analytics = computed(() => communicationStore.analytics)
const loading = computed(() => communicationStore.loading)
const filters = computed(() => communicationStore.filters)
const hasActiveFilters = computed(() => communicationStore.hasActiveFilters)
const activeFilterCount = computed(() => communicationStore.activeFilterCount)
const selectedCommunications = computed(() => communicationStore.selectedCommunications)
const hasSelectedCommunications = computed(() => communicationStore.hasSelectedCommunications)
const selectedCount = computed(() => communicationStore.selectedCount)
const totalCount = computed(() => communicationStore.totalCount)
const currentPage = computed(() => communicationStore.currentPage)
const pageSize = computed(() => communicationStore.pageSize)
const totalPages = computed(() => communicationStore.totalPages)
const hasNext = computed(() => communicationStore.hasNext)
const hasPrevious = computed(() => communicationStore.hasPrevious)

const emailAccounts = computed(() => emailStore.emailAccounts)
const hasEmailAccounts = computed(() => emailStore.hasEmailAccounts)
const isSyncing = computed(() => emailStore.loading.syncing)
const lastSyncTime = computed(() => emailStore.lastSyncTime)

// Filter options
const sentimentOptions = [
  { value: 'positive', label: 'Positive', icon: 'bi-emoji-smile', activeClass: 'btn-success', inactiveClass: 'btn-outline-success' },
  { value: 'negative', label: 'Negative', icon: 'bi-emoji-frown', activeClass: 'btn-danger', inactiveClass: 'btn-outline-danger' },
  { value: 'neutral', label: 'Neutral', icon: 'bi-emoji-neutral', activeClass: 'btn-secondary', inactiveClass: 'btn-outline-secondary' },
  { value: 'mixed', label: 'Mixed', icon: 'bi-emoji-expressionless', activeClass: 'btn-warning', inactiveClass: 'btn-outline-warning' }
]

const typeOptions = [
  { value: 'email', label: 'Email', icon: 'bi-envelope' },
  { value: 'sms', label: 'SMS', icon: 'bi-chat-dots' },
  { value: 'call', label: 'Call', icon: 'bi-telephone' },
  { value: 'meeting', label: 'Meeting', icon: 'bi-calendar' },
  { value: 'note', label: 'Note', icon: 'bi-sticky' }
]

// Methods
const refreshData = async () => {
  isRefreshing.value = true
  try {
    await Promise.all([
      communicationStore.fetchCommunications(),
      communicationStore.fetchAnalytics(),
      emailStore.fetchEmailAccounts(),
      emailStore.fetchSyncStatus()
    ])
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    isRefreshing.value = false
  }
}

const setView = async (view) => {
  currentView.value = view
  
  // Clear existing filters
  communicationStore.clearFilters()
  
  // Apply view-specific filters
  switch (view) {
    case 'unread':
      communicationStore.setFilter('is_read', false)
      break
    case 'priority':
      communicationStore.setFilter('priority_min', 0.7)
      break
    default:
      // 'all' - no additional filters
      break
  }
  
  await communicationStore.applyFilters()
}

const toggleSentimentFilter = async (sentiment) => {
  if (filters.value.sentiment === sentiment) {
    communicationStore.setFilter('sentiment', '')
  } else {
    communicationStore.setFilter('sentiment', sentiment)
  }
  await communicationStore.applyFilters()
}

const toggleTypeFilter = async (type) => {
  if (filters.value.type === type) {
    communicationStore.setFilter('type', '')
  } else {
    communicationStore.setFilter('type', type)
  }
  await communicationStore.applyFilters()
}

const onSearchInput = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(async () => {
    await communicationStore.searchCommunications(searchQuery.value)
  }, 300) // Debounce search
}

const clearSearch = async () => {
  searchQuery.value = ''
  await communicationStore.searchCommunications('')
}

const selectCommunication = (id) => {
  communicationStore.selectCommunication(id)
}

const deselectCommunication = (id) => {
  communicationStore.deselectCommunication(id)
}

const toggleRead = async (id) => {
  const communication = communicationStore.communicationById(id)
  if (communication.is_read) {
    await communicationStore.markAsUnread(id)
  } else {
    await communicationStore.markAsRead(id)
  }
}

const viewCommunication = (id) => {
  selectedCommunicationId.value = id
  showDetailModal.value = true
}

const deleteCommunication = async (id) => {
  if (confirm('Are you sure you want to delete this communication?')) {
    await communicationStore.deleteCommunication(id)
  }
}

const bulkMarkRead = async () => {
  await communicationStore.bulkMarkRead()
}

const bulkMarkUnread = async () => {
  await communicationStore.bulkMarkUnread()
}

const bulkDelete = async () => {
  if (confirm(`Are you sure you want to delete ${selectedCount.value} communications?`)) {
    await communicationStore.bulkDelete()
  }
}

const nextPage = async () => {
  await communicationStore.nextPage()
}

const previousPage = async () => {
  await communicationStore.previousPage()
}

const triggerSync = async () => {
  await emailStore.syncEmails()
}

const onEmailSent = () => {
  // Refresh communications list
  communicationStore.fetchCommunications()
}

const onEmailAccountAdded = () => {
  // Refresh email accounts
  emailStore.fetchEmailAccounts()
}

const onCommunicationUpdated = () => {
  // Refresh communications list
  communicationStore.fetchCommunications()
}

const getProviderIcon = (provider) => {
  switch (provider) {
    case 'gmail':
      return 'bi-google'
    case 'outlook':
      return 'bi-microsoft'
    default:
      return 'bi-envelope'
  }
}

const formatLastSync = (date) => {
  if (!date) return 'Never'
  
  const now = new Date()
  const syncDate = new Date(date)
  const diffMs = now - syncDate
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  
  // Start polling for real-time updates
  communicationStore.startPolling()
})

onUnmounted(() => {
  // Stop polling
  communicationStore.stopPolling()
  
  // Clear search timeout
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
})
</script>

<style scoped>
.communication-center {
  padding: 1rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  font-size: 1rem;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
  font-size: 0.875rem;
}

.avatar-lg {
  width: 3.5rem;
  height: 3.5rem;
  font-size: 1.5rem;
}

.badge-soft-success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.badge-soft-secondary {
  background-color: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.bg-soft-primary {
  background-color: rgba(13, 110, 253, 0.1);
}

.text-primary {
  color: #0d6efd !important;
}

.card {
  border-radius: 0.5rem;
}

.card-header {
  padding: 1rem 1.25rem;
  background-color: transparent;
  border-bottom: 1px solid #dee2e6;
}

.list-group-item-action:hover {
  background-color: #f8f9fa;
}

.list-group-item.active {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

@media (max-width: 768px) {
  .communication-center {
    padding: 0.5rem;
  }
  
  .col-md-3, .col-md-4 {
    margin-bottom: 1rem;
  }
  
  .d-flex.gap-2 {
    gap: 0.5rem !important;
  }
  
  .btn {
    font-size: 0.875rem;
  }
}
</style>