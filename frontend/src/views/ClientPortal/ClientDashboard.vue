<template>
  <div class="client-dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section mb-4">
      <div class="card bg-gradient-primary text-white">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h5 class="card-title mb-1">Welcome back, {{ clientName }}!</h5>
              <p class="card-text mb-0">
                Here's your retirement planning overview
              </p>
            </div>
            <div class="col-md-4 text-end">
              <i class="bi bi-graph-up display-4 opacity-75"></i>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <div class="metric-icon text-success mb-2">
              <i class="bi bi-piggy-bank display-4"></i>
            </div>
            <h6 class="card-title text-muted">Total Assets</h6>
            <h4 class="text-success mb-0">${{ formatCurrency(totalAssets) }}</h4>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <div class="metric-icon text-info mb-2">
              <i class="bi bi-calendar-check display-4"></i>
            </div>
            <h6 class="card-title text-muted">Retirement Age</h6>
            <h4 class="text-info mb-0">{{ retirementAge }}</h4>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <div class="metric-icon text-warning mb-2">
              <i class="bi bi-file-text display-4"></i>
            </div>
            <h6 class="card-title text-muted">Scenarios</h6>
            <h4 class="text-warning mb-0">{{ scenarioCount }}</h4>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <div class="metric-icon text-primary mb-2">
              <i class="bi bi-folder display-4"></i>
            </div>
            <h6 class="card-title text-muted">Documents</h6>
            <h4 class="text-primary mb-0">{{ documentCount }}</h4>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity & Quick Actions -->
    <div class="row">
      <div class="col-md-8">
        <!-- Recent Scenarios -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-graph-up me-2"></i>
              Recent Scenarios
            </h6>
            <router-link 
              :to="{ name: 'client-portal-scenarios' }"
              class="btn btn-sm btn-outline-primary"
            >
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="recentScenarios.length === 0" class="text-center py-3 text-muted">
              <i class="bi bi-graph-up display-4 mb-2 opacity-50"></i>
              <p>No scenarios created yet</p>
            </div>
            <div v-else>
              <div 
                v-for="scenario in recentScenarios.slice(0, 3)" 
                :key="scenario.id"
                class="scenario-item d-flex justify-content-between align-items-center py-2 border-bottom"
              >
                <div>
                  <h6 class="mb-1">{{ scenario.name }}</h6>
                  <small class="text-muted">
                    Created {{ formatDate(scenario.created_at) }}
                  </small>
                </div>
                <div>
                  <span class="badge bg-light text-dark me-2">
                    {{ scenario.status || 'Draft' }}
                  </span>
                  <router-link 
                    :to="{ name: 'scenario-detail', params: { clientId: client.id, id: scenario.id } }"
                    class="btn btn-sm btn-outline-primary"
                  >
                    View
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Documents -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-folder me-2"></i>
              Recent Documents
            </h6>
            <router-link 
              :to="{ name: 'client-portal-documents' }"
              class="btn btn-sm btn-outline-primary"
            >
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="recentDocuments.length === 0" class="text-center py-3 text-muted">
              <i class="bi bi-folder display-4 mb-2 opacity-50"></i>
              <p>No documents uploaded yet</p>
            </div>
            <div v-else>
              <div 
                v-for="doc in recentDocuments.slice(0, 3)" 
                :key="doc.id"
                class="document-item d-flex justify-content-between align-items-center py-2 border-bottom"
              >
                <div class="d-flex align-items-center">
                  <i :class="getFileIcon(doc.content_type) + ' me-2'"></i>
                  <div>
                    <h6 class="mb-1">{{ doc.title || doc.original_filename }}</h6>
                    <small class="text-muted">
                      {{ formatFileSize(doc.file_size) }} • {{ formatDate(doc.uploaded_at) }}
                    </small>
                  </div>
                </div>
                <button 
                  class="btn btn-sm btn-outline-success"
                  @click="downloadDocument(doc)"
                >
                  <i class="bi bi-download"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions Sidebar -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-lightning me-2"></i>
              Quick Actions
            </h6>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <router-link 
                :to="{ name: 'client-portal-messages' }"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              >
                <div>
                  <i class="bi bi-chat-dots me-2"></i>
                  Send Message
                </div>
                <i class="bi bi-chevron-right"></i>
              </router-link>
              
              <router-link 
                :to="{ name: 'client-portal-appointments' }"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              >
                <div>
                  <i class="bi bi-calendar-plus me-2"></i>
                  Book Appointment
                </div>
                <i class="bi bi-chevron-right"></i>
              </router-link>
              
              <router-link 
                :to="{ name: 'client-portal-documents' }"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              >
                <div>
                  <i class="bi bi-cloud-upload me-2"></i>
                  Upload Document
                </div>
                <i class="bi bi-chevron-right"></i>
              </router-link>
              
              <router-link 
                :to="{ name: 'client-portal-scenarios' }"
                class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              >
                <div>
                  <i class="bi bi-graph-up me-2"></i>
                  View Scenarios
                </div>
                <i class="bi bi-chevron-right"></i>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card mt-4">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-calendar-event me-2"></i>
              Upcoming Appointments
            </h6>
          </div>
          <div class="card-body">
            <div v-if="upcomingAppointments.length === 0" class="text-center py-3 text-muted">
              <i class="bi bi-calendar display-4 mb-2 opacity-50"></i>
              <p class="small">No upcoming appointments</p>
              <router-link 
                :to="{ name: 'client-portal-appointments' }"
                class="btn btn-sm btn-primary"
              >
                Schedule One
              </router-link>
            </div>
            <div v-else>
              <div 
                v-for="appointment in upcomingAppointments.slice(0, 2)" 
                :key="appointment.id"
                class="appointment-item py-2 border-bottom"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">{{ appointment.title }}</h6>
                    <small class="text-muted">
                      <i class="bi bi-clock me-1"></i>
                      {{ formatDateTime(appointment.scheduled_time) }}
                    </small>
                  </div>
                  <span class="badge bg-primary">{{ appointment.type }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/documentStore.js'
import { useClientStore } from '@/stores/clientStore.js'

const props = defineProps({
  client: {
    type: Object,
    required: true
  },
  documentCount: {
    type: Number,
    default: 0
  }
})

const documentStore = useDocumentStore()
const clientStore = useClientStore()

// State
const loading = ref(false)
const recentScenarios = ref([])
const recentDocuments = ref([])
const upcomingAppointments = ref([])

// Computed
const clientName = computed(() => {
  if (!props.client) return 'Client'
  return `${props.client.first_name} ${props.client.last_name}`
})

const totalAssets = computed(() => {
  // Calculate total assets from client data
  if (!props.client) return 0
  // This would come from the client's scenario data
  return 500000 // Placeholder
})

const retirementAge = computed(() => {
  return props.client?.retirement_age || 67
})

const scenarioCount = computed(() => {
  return recentScenarios.value.length
})

// Methods
const loadDashboardData = async () => {
  if (!props.client) return
  
  loading.value = true
  try {
    // Load recent scenarios
    const scenariosResponse = await clientStore.getClientScenarios(props.client.id)
    recentScenarios.value = scenariosResponse.results || []
    
    // Load recent documents
    const documentsResponse = await documentStore.getClientDocuments(props.client.id)
    recentDocuments.value = (documentsResponse.results || [])
      .sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at))
    
    // Load upcoming appointments (placeholder for now)
    upcomingAppointments.value = []
    
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(amount || 0)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (contentType) => {
  const iconMap = {
    'application/pdf': 'bi-file-pdf-fill text-danger',
    'application/msword': 'bi-file-word-fill text-primary',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-word-fill text-primary',
    'application/vnd.ms-excel': 'bi-file-excel-fill text-success',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'bi-file-excel-fill text-success',
    'text/plain': 'bi-file-text-fill text-secondary',
    'text/csv': 'bi-file-spreadsheet-fill text-info',
    'image/jpeg': 'bi-file-image-fill text-warning',
    'image/png': 'bi-file-image-fill text-warning',
    'image/tiff': 'bi-file-image-fill text-warning'
  }
  return iconMap[contentType] || 'bi-file-fill text-muted'
}

const downloadDocument = async (doc) => {
  try {
    await documentStore.downloadDocument(doc.id, doc.original_filename)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.client-dashboard {
  padding: 0;
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.metric-icon {
  opacity: 0.8;
}

.card {
  border: 1px solid rgba(0,0,0,0.125);
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
}

.card:hover {
  box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
  transition: box-shadow 0.15s ease-in-out;
}

.scenario-item:last-child,
.document-item:last-child,
.appointment-item:last-child {
  border-bottom: none !important;
}

.list-group-item-action:hover {
  background-color: #f8f9fa;
}

.badge {
  font-size: 0.7rem;
}
</style>