<template>
  <div class="client-portal-dashboard">
    <div class="container-fluid py-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm bg-primary text-white">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h2 class="mb-1">Welcome, {{ client?.first_name }}!</h2>
                  <p class="mb-0 opacity-75">
                    Your financial advisor: {{ advisor?.first_name }} {{ advisor?.last_name }}
                  </p>
                </div>
                <div class="text-end">
                  <button @click="logout" class="btn btn-outline-light">
                    <i class="bi bi-box-arrow-right me-2"></i>
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-primary mb-3">
                <i class="bi bi-graph-up display-4"></i>
              </div>
              <h3 class="text-primary">{{ stats?.shared_scenarios_count || 0 }}</h3>
              <p class="text-muted mb-0">Retirement Scenarios</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-success mb-3">
                <i class="bi bi-folder display-4"></i>
              </div>
              <h3 class="text-success">{{ stats?.shared_documents_count || 0 }}</h3>
              <p class="text-muted mb-0">Shared Documents</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-info mb-3">
                <i class="bi bi-clock display-4"></i>
              </div>
              <p class="text-info mb-1">Last Login</p>
              <small class="text-muted">{{ formatDate(last_login) }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Content Sections -->
      <div class="row">
        <!-- Retirement Scenarios -->
        <div class="col-lg-6 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-bottom-0 pb-0">
              <h5 class="card-title mb-0">
                <i class="bi bi-graph-up me-2 text-primary"></i>
                Your Retirement Scenarios
              </h5>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              
              <div v-else-if="shared_scenarios?.length > 0">
                <div 
                  v-for="scenario in shared_scenarios.slice(0, 3)" 
                  :key="scenario.id"
                  class="scenario-item p-3 border rounded mb-2 hover-shadow"
                  style="cursor: pointer"
                  @click="viewScenario(scenario.id)"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <h6 class="mb-1">{{ scenario.description || 'Retirement Scenario' }}</h6>
                      <small class="text-muted">Updated: {{ formatDate(scenario.updated_at) }}</small>
                    </div>
                    <div>
                      <i class="bi bi-chevron-right text-muted"></i>
                    </div>
                  </div>
                </div>
                
                <div v-if="shared_scenarios.length > 3" class="text-center mt-3">
                  <button @click="viewAllScenarios" class="btn btn-outline-primary btn-sm">
                    View All {{ shared_scenarios.length }} Scenarios
                  </button>
                </div>
              </div>
              
              <div v-else class="text-center text-muted py-4">
                <i class="bi bi-graph-up display-4 opacity-25 mb-3"></i>
                <p>No retirement scenarios shared yet.</p>
                <small>Your advisor will share scenarios with you when available.</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Documents -->
        <div class="col-lg-6 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-transparent border-bottom-0 pb-0">
              <h5 class="card-title mb-0">
                <i class="bi bi-folder me-2 text-success"></i>
                Shared Documents
              </h5>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <div class="spinner-border text-success" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              
              <div v-else-if="shared_documents?.length > 0">
                <div 
                  v-for="document in shared_documents.slice(0, 3)" 
                  :key="document.id"
                  class="document-item p-3 border rounded mb-2 hover-shadow"
                  style="cursor: pointer"
                  @click="viewDocument(document.id)"
                >
                  <div class="d-flex align-items-center">
                    <div class="me-3">
                      <i :class="getFileIcon(document.content_type)"></i>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-1">{{ document.title || document.file_name }}</h6>
                      <small class="text-muted">
                        {{ formatFileSize(document.file_size) }} • {{ formatDate(document.uploaded_at) }}
                      </small>
                    </div>
                    <div>
                      <i class="bi bi-chevron-right text-muted"></i>
                    </div>
                  </div>
                </div>
                
                <div v-if="shared_documents.length > 3" class="text-center mt-3">
                  <button @click="viewAllDocuments" class="btn btn-outline-success btn-sm">
                    View All {{ shared_documents.length }} Documents
                  </button>
                </div>
              </div>
              
              <div v-else class="text-center text-muted py-4">
                <i class="bi bi-folder display-4 opacity-25 mb-3"></i>
                <p>No documents shared yet.</p>
                <small>Your advisor will share documents with you when available.</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-transparent">
              <h5 class="card-title mb-0">
                <i class="bi bi-lightning me-2 text-warning"></i>
                Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 mb-2">
                  <button @click="viewAllScenarios" class="btn btn-outline-primary w-100">
                    <i class="bi bi-graph-up me-2"></i>
                    All Scenarios
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button @click="viewAllDocuments" class="btn btn-outline-success w-100">
                    <i class="bi bi-folder me-2"></i>
                    All Documents
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button @click="contactAdvisor" class="btn btn-outline-info w-100">
                    <i class="bi bi-envelope me-2"></i>
                    Contact Advisor
                  </button>
                </div>
                <div class="col-md-3 mb-2">
                  <button @click="logout" class="btn btn-outline-secondary w-100">
                    <i class="bi bi-box-arrow-right me-2"></i>
                    Logout
                  </button>
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// State
const loading = ref(true)
const client = ref(null)
const advisor = ref(null)
const stats = ref(null)
const shared_scenarios = ref([])
const shared_documents = ref([])
const last_login = ref(null)

// Methods
const loadDashboardData = async () => {
  loading.value = true
  
  try {
    const token = localStorage.getItem('client_portal_token')
    if (!token) {
      router.push('/portal/login')
      return
    }

    const response = await axios.get('http://localhost:8000/api/client-portal/dashboard/', {
      headers: {
        'Authorization': `Token ${token}`
      }
    })

    client.value = response.data.client
    advisor.value = response.data.advisor
    stats.value = response.data.stats
    shared_scenarios.value = response.data.shared_scenarios
    shared_documents.value = response.data.shared_documents
    last_login.value = response.data.last_login

  } catch (error) {
    console.error('Error loading dashboard data:', error)
    if (error.response?.status === 401) {
      logout()
    }
  } finally {
    loading.value = false
  }
}

const logout = async () => {
  try {
    const token = localStorage.getItem('client_portal_token')
    if (token) {
      await axios.post('http://localhost:8000/api/client-portal/auth/logout/', {}, {
        headers: {
          'Authorization': `Token ${token}`
        }
      })
    }
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // Clear local storage
    localStorage.removeItem('client_portal_token')
    localStorage.removeItem('client_portal_user')
    localStorage.removeItem('client_portal_client')
    
    // Redirect to login
    router.push('/portal/login')
  }
}

const viewScenario = (scenarioId) => {
  router.push(`/portal/scenarios/${scenarioId}`)
}

const viewAllScenarios = () => {
  router.push('/portal/scenarios')
}

const viewDocument = (documentId) => {
  router.push(`/portal/documents/${documentId}`)
}

const viewAllDocuments = () => {
  router.push('/portal/documents')
}

const contactAdvisor = () => {
  if (advisor.value?.email) {
    window.location.href = `mailto:${advisor.value.email}?subject=Client Portal Inquiry`
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
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
    'image/jpeg': 'bi-file-image-fill text-warning',
    'image/png': 'bi-file-image-fill text-warning'
  }
  return iconMap[contentType] || 'bi-file-fill text-muted'
}

// Initialize
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.hover-shadow {
  transition: all 0.2s ease;
}

.hover-shadow:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.scenario-item, .document-item {
  transition: all 0.2s ease;
}

.scenario-item:hover, .document-item:hover {
  background-color: #f8f9fa;
}

.bg-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.card {
  border-radius: 12px;
}

.btn {
  border-radius: 8px;
}
</style>