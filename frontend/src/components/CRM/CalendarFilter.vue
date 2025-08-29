<template>
  <div class="calendar-filter">
    <div class="filter-header">
      <h6 class="mb-0">
        <i class="fas fa-filter me-2"></i>
        Calendar Filters
      </h6>
      <button
        v-if="hasActiveFilters"
        class="btn btn-link btn-sm p-0"
        @click="clearAllFilters"
      >
        <i class="fas fa-times me-1"></i>
        Clear All
      </button>
    </div>

    <div class="filter-content">
      <div class="row">
        <!-- Calendar Accounts Filter -->
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Calendar Accounts</label>
            <div class="filter-options">
              <div
                v-for="account in calendarAccounts"
                :key="account.id"
                class="form-check"
              >
                <input
                  class="form-check-input"
                  type="checkbox"
                  :id="`account-${account.id}`"
                  :value="account.id"
                  v-model="localFilters.accounts"
                  @change="updateFilters"
                >
                <label class="form-check-label" :for="`account-${account.id}`">
                  <i :class="getProviderIcon(account.provider)" class="me-2"></i>
                  {{ account.display_name }}
                </label>
              </div>
              <div v-if="calendarAccounts.length === 0" class="text-muted small">
                No calendar accounts connected
              </div>
            </div>
          </div>
        </div>

        <!-- Event Types Filter -->
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Event Types</label>
            <div class="filter-options">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="showMeetings"
                  v-model="localFilters.showMeetings"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="showMeetings">
                  <i class="fas fa-video me-2 text-primary"></i>
                  Meetings
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="showEvents"
                  v-model="localFilters.showEvents"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="showEvents">
                  <i class="fas fa-calendar me-2 text-info"></i>
                  Events
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="showTasks"
                  v-model="localFilters.showTasks"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="showTasks">
                  <i class="fas fa-tasks me-2 text-warning"></i>
                  Tasks
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Status Filter -->
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Status</label>
            <div class="filter-options">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="statusConfirmed"
                  value="confirmed"
                  v-model="localFilters.statuses"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="statusConfirmed">
                  <span class="badge bg-success me-2">●</span>
                  Confirmed
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="statusTentative"
                  value="tentative"
                  v-model="localFilters.statuses"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="statusTentative">
                  <span class="badge bg-warning me-2">●</span>
                  Tentative
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="statusCancelled"
                  value="cancelled"
                  v-model="localFilters.statuses"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="statusCancelled">
                  <span class="badge bg-danger me-2">●</span>
                  Cancelled
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Privacy Filter -->
        <div class="col-lg-3 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Privacy</label>
            <div class="filter-options">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="privacyPublic"
                  value="public"
                  v-model="localFilters.privacy"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="privacyPublic">
                  <i class="fas fa-globe me-2 text-info"></i>
                  Public
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="privacyPrivate"
                  value="private"
                  v-model="localFilters.privacy"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="privacyPrivate">
                  <i class="fas fa-lock me-2 text-secondary"></i>
                  Private
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="privacyConfidential"
                  value="confidential"
                  v-model="localFilters.privacy"
                  @change="updateFilters"
                >
                <label class="form-check-label" for="privacyConfidential">
                  <i class="fas fa-shield-alt me-2 text-danger"></i>
                  Confidential
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Advanced Filters Row -->
      <div v-show="showAdvancedFilters" class="row">
        <!-- Clients Filter -->
        <div class="col-lg-4 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Clients</label>
            <div class="client-selector">
              <div class="search-input mb-2">
                <input
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Search clients..."
                  v-model="clientSearch"
                  @input="filterClients"
                >
              </div>
              <div class="client-options" style="max-height: 150px; overflow-y: auto;">
                <div
                  v-for="client in filteredClients.slice(0, 10)"
                  :key="client.id"
                  class="form-check"
                >
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="`client-${client.id}`"
                    :value="client.id"
                    v-model="localFilters.clients"
                    @change="updateFilters"
                  >
                  <label class="form-check-label" :for="`client-${client.id}`">
                    <i class="fas fa-user me-2 text-primary"></i>
                    {{ client.name }}
                  </label>
                </div>
                <div v-if="filteredClients.length === 0 && clientSearch" class="text-muted small">
                  No clients found
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Leads Filter -->
        <div class="col-lg-4 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Leads</label>
            <div class="lead-selector">
              <div class="search-input mb-2">
                <input
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Search leads..."
                  v-model="leadSearch"
                  @input="filterLeads"
                >
              </div>
              <div class="lead-options" style="max-height: 150px; overflow-y: auto;">
                <div
                  v-for="lead in filteredLeads.slice(0, 10)"
                  :key="lead.id"
                  class="form-check"
                >
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="`lead-${lead.id}`"
                    :value="lead.id"
                    v-model="localFilters.leads"
                    @change="updateFilters"
                  >
                  <label class="form-check-label" :for="`lead-${lead.id}`">
                    <i class="fas fa-user-plus me-2 text-warning"></i>
                    {{ lead.name }}
                  </label>
                </div>
                <div v-if="filteredLeads.length === 0 && leadSearch" class="text-muted small">
                  No leads found
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Date Range Filter -->
        <div class="col-lg-4 col-md-6 mb-3">
          <div class="filter-section">
            <label class="form-label">Date Range</label>
            <div class="date-range-selector">
              <div class="quick-ranges mb-2">
                <div class="btn-group-sm" role="group">
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    :class="{ active: dateRange === 'today' }"
                    @click="setDateRange('today')"
                  >
                    Today
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    :class="{ active: dateRange === 'week' }"
                    @click="setDateRange('week')"
                  >
                    This Week
                  </button>
                  <button
                    type="button"
                    class="btn btn-outline-secondary btn-sm"
                    :class="{ active: dateRange === 'month' }"
                    @click="setDateRange('month')"
                  >
                    This Month
                  </button>
                </div>
              </div>
              <div class="custom-range">
                <div class="row g-1">
                  <div class="col-6">
                    <input
                      type="date"
                      class="form-control form-control-sm"
                      v-model="customDateStart"
                      @change="setCustomDateRange"
                    >
                  </div>
                  <div class="col-6">
                    <input
                      type="date"
                      class="form-control form-control-sm"
                      v-model="customDateEnd"
                      @change="setCustomDateRange"
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filter Actions -->
      <div class="filter-actions">
        <div class="d-flex justify-content-between align-items-center">
          <button
            class="btn btn-link btn-sm"
            @click="showAdvancedFilters = !showAdvancedFilters"
          >
            <i :class="showAdvancedFilters ? 'fas fa-chevron-up' : 'fas fa-chevron-down'" class="me-1"></i>
            {{ showAdvancedFilters ? 'Hide' : 'Show' }} Advanced Filters
          </button>
          
          <div class="active-filters">
            <span class="text-muted small me-2">Active Filters:</span>
            <span class="badge bg-primary me-1" v-if="localFilters.accounts.length > 0">
              {{ localFilters.accounts.length }} Calendar{{ localFilters.accounts.length !== 1 ? 's' : '' }}
            </span>
            <span class="badge bg-info me-1" v-if="localFilters.clients.length > 0">
              {{ localFilters.clients.length }} Client{{ localFilters.clients.length !== 1 ? 's' : '' }}
            </span>
            <span class="badge bg-warning me-1" v-if="localFilters.leads.length > 0">
              {{ localFilters.leads.length }} Lead{{ localFilters.leads.length !== 1 ? 's' : '' }}
            </span>
            <span class="badge bg-secondary me-1" v-if="!localFilters.showTasks">
              No Tasks
            </span>
            <span class="badge bg-secondary me-1" v-if="!localFilters.showMeetings">
              No Meetings
            </span>
            <span class="badge bg-secondary me-1" v-if="!localFilters.showEvents">
              No Events
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useClientStore } from '@/stores/clientStore'
import { storeToRefs } from 'pinia'

const emit = defineEmits(['update:filters', 'clear-filters'])

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  calendarAccounts: {
    type: Array,
    default: () => []
  }
})

// Store
const clientStore = useClientStore()
const { clients } = storeToRefs(clientStore)

// Local state
const localFilters = ref({ ...props.filters })
const showAdvancedFilters = ref(false)
const clientSearch = ref('')
const leadSearch = ref('')
const dateRange = ref('')
const customDateStart = ref('')
const customDateEnd = ref('')

// Mock leads data (replace with actual leads store when available)
const leads = ref([
  { id: 1, name: 'John Smith - Prospect' },
  { id: 2, name: 'Sarah Johnson - Lead' },
  { id: 3, name: 'Mike Wilson - Warm Lead' }
])

// Computed
const filteredClients = computed(() => {
  if (!clientSearch.value) return clients.value
  
  const search = clientSearch.value.toLowerCase()
  return clients.value.filter(client =>
    client.name.toLowerCase().includes(search)
  )
})

const filteredLeads = computed(() => {
  if (!leadSearch.value) return leads.value
  
  const search = leadSearch.value.toLowerCase()
  return leads.value.filter(lead =>
    lead.name.toLowerCase().includes(search)
  )
})

const hasActiveFilters = computed(() => {
  return localFilters.value.accounts.length > 0 ||
    localFilters.value.clients.length > 0 ||
    localFilters.value.leads.length > 0 ||
    !localFilters.value.showTasks ||
    !localFilters.value.showMeetings ||
    !localFilters.value.showEvents ||
    localFilters.value.statuses.length !== 2 ||
    localFilters.value.privacy.length !== 2
})

// Methods
const updateFilters = () => {
  emit('update:filters', { ...localFilters.value })
}

const clearAllFilters = () => {
  localFilters.value = {
    accounts: [],
    statuses: ['confirmed', 'tentative'],
    privacy: ['public', 'private'],
    showTasks: true,
    showMeetings: true,
    showEvents: true,
    clients: [],
    leads: []
  }
  clientSearch.value = ''
  leadSearch.value = ''
  dateRange.value = ''
  customDateStart.value = ''
  customDateEnd.value = ''
  
  emit('clear-filters')
}

const filterClients = () => {
  // Debounced search could be implemented here
}

const filterLeads = () => {
  // Debounced search could be implemented here
}

const setDateRange = (range) => {
  dateRange.value = range
  const today = new Date()
  
  switch (range) {
    case 'today':
      customDateStart.value = today.toISOString().split('T')[0]
      customDateEnd.value = today.toISOString().split('T')[0]
      break
    case 'week':
      const startOfWeek = new Date(today)
      startOfWeek.setDate(today.getDate() - today.getDay())
      const endOfWeek = new Date(startOfWeek)
      endOfWeek.setDate(startOfWeek.getDate() + 6)
      
      customDateStart.value = startOfWeek.toISOString().split('T')[0]
      customDateEnd.value = endOfWeek.toISOString().split('T')[0]
      break
    case 'month':
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      
      customDateStart.value = startOfMonth.toISOString().split('T')[0]
      customDateEnd.value = endOfMonth.toISOString().split('T')[0]
      break
  }
  
  // Apply date range filter (this would need to be implemented in the calendar store)
  updateFilters()
}

const setCustomDateRange = () => {
  dateRange.value = 'custom'
  // Apply custom date range filter
  updateFilters()
}

const getProviderIcon = (provider) => {
  switch (provider) {
    case 'google':
      return 'fab fa-google text-danger'
    case 'outlook':
      return 'fab fa-microsoft text-primary'
    default:
      return 'fas fa-calendar text-info'
  }
}

// Watch for prop changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

// Lifecycle
onMounted(async () => {
  // Load clients if not already loaded
  if (clients.value.length === 0) {
    try {
      await clientStore.fetchClients()
    } catch (error) {
      console.error('Failed to load clients for filter:', error)
    }
  }
})
</script>

<style scoped>
.calendar-filter {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.filter-header h6 {
  color: #495057;
  font-weight: 600;
}

.filter-content {
  margin-bottom: 0;
}

.filter-section {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  height: 100%;
  border: 1px solid #e9ecef;
}

.filter-section .form-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-check {
  margin-bottom: 0;
}

.form-check-label {
  font-size: 0.875rem;
  color: #495057;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.form-check-input {
  margin-top: 0;
}

.search-input .form-control {
  border: 1px solid #ced4da;
  border-radius: 0.375rem;
}

.client-options,
.lead-options {
  max-height: 150px;
  overflow-y: auto;
}

.client-options .form-check,
.lead-options .form-check {
  padding: 0.25rem 0;
}

.date-range-selector .quick-ranges {
  margin-bottom: 0.75rem;
}

.date-range-selector .btn-group-sm .btn {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.date-range-selector .btn.active {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
}

.filter-actions {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
  margin-top: 1.5rem;
}

.active-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.active-filters .badge {
  font-size: 0.7rem;
}

/* Custom scrollbar for options */
.client-options::-webkit-scrollbar,
.lead-options::-webkit-scrollbar {
  width: 4px;
}

.client-options::-webkit-scrollbar-track,
.lead-options::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.client-options::-webkit-scrollbar-thumb,
.lead-options::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.client-options::-webkit-scrollbar-thumb:hover,
.lead-options::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .filter-content .row > div {
    margin-bottom: 1rem;
  }
  
  .filter-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .active-filters {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .calendar-filter {
    padding: 1rem;
  }
  
  .filter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .filter-section {
    padding: 0.75rem;
  }
  
  .date-range-selector .quick-ranges .btn-group-sm {
    width: 100%;
  }
  
  .date-range-selector .quick-ranges .btn {
    flex: 1;
  }
  
  .active-filters {
    font-size: 0.875rem;
  }
  
  .active-filters .text-muted {
    display: block;
    width: 100%;
    margin-bottom: 0.5rem;
  }
}

@media (max-width: 576px) {
  .filter-content .col-lg-3,
  .filter-content .col-lg-4 {
    margin-bottom: 1rem;
  }
  
  .filter-section .form-label {
    font-size: 0.8rem;
  }
  
  .form-check-label {
    font-size: 0.8rem;
  }
  
  .date-range-selector .quick-ranges {
    margin-bottom: 0.5rem;
  }
  
  .date-range-selector .btn {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
}

/* Accessibility improvements */
.form-check-input:focus {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn:focus,
.form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

/* Animation for advanced filters */
.filter-content .row:nth-child(2) {
  transition: all 0.3s ease;
}

/* Badge styles for better contrast */
.badge.bg-primary {
  background-color: #007bff !important;
}

.badge.bg-info {
  background-color: #17a2b8 !important;
}

.badge.bg-warning {
  background-color: #ffc107 !important;
  color: #212529 !important;
}

.badge.bg-secondary {
  background-color: #6c757d !important;
}
</style>