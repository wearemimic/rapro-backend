<template>
  <div class="client-portal-scenarios">
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-0">My Retirement Scenarios</h5>
          <small class="text-muted">View your retirement planning scenarios and projections</small>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading scenarios...</span>
      </div>
      <p class="text-muted mt-2">Loading your scenarios...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="scenarios.length === 0" class="text-center py-5">
      <i class="bi bi-graph-up display-1 text-muted mb-3 opacity-50"></i>
      <h5 class="text-muted">No scenarios available</h5>
      <p class="text-muted mb-4">
        Your advisor hasn't shared any retirement scenarios with you yet.<br>
        Contact your advisor to discuss creating your retirement planning scenarios.
      </p>
      <button class="btn btn-primary" @click="contactAdvisor">
        <i class="bi bi-chat-dots me-2"></i>
        Contact Advisor
      </button>
    </div>

    <!-- Scenarios Grid -->
    <div v-else class="row">
      <div 
        v-for="scenario in scenarios" 
        :key="scenario.id"
        class="col-md-6 col-lg-4 mb-4"
      >
        <div class="scenario-card card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h6 class="card-title mb-0">{{ scenario.name }}</h6>
              <span 
                class="badge"
                :class="getScenarioStatusBadge(scenario.status)"
              >
                {{ scenario.status || 'Draft' }}
              </span>
            </div>
            
            <p v-if="scenario.description" class="card-text text-muted small mb-3">
              {{ scenario.description }}
            </p>
            
            <!-- Key Metrics -->
            <div class="scenario-metrics mb-3">
              <div class="metric-item d-flex justify-content-between align-items-center mb-2">
                <span class="metric-label small text-muted">Retirement Age:</span>
                <span class="metric-value fw-medium">{{ scenario.retirement_age || 'N/A' }}</span>
              </div>
              
              <div v-if="scenario.total_assets" class="metric-item d-flex justify-content-between align-items-center mb-2">
                <span class="metric-label small text-muted">Total Assets:</span>
                <span class="metric-value fw-medium">${{ formatCurrency(scenario.total_assets) }}</span>
              </div>
              
              <div v-if="scenario.annual_income" class="metric-item d-flex justify-content-between align-items-center mb-2">
                <span class="metric-label small text-muted">Annual Income:</span>
                <span class="metric-value fw-medium">${{ formatCurrency(scenario.annual_income) }}</span>
              </div>
              
              <div class="metric-item d-flex justify-content-between align-items-center mb-2">
                <span class="metric-label small text-muted">Last Updated:</span>
                <span class="metric-value small">{{ formatDate(scenario.updated_at) }}</span>
              </div>
            </div>
            
            <!-- Success Probability (if available) -->
            <div v-if="scenario.success_probability !== null" class="success-probability mb-3">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="small text-muted">Success Probability</span>
                <span class="fw-medium">{{ Math.round(scenario.success_probability || 0) }}%</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div 
                  class="progress-bar"
                  :class="{
                    'bg-success': scenario.success_probability >= 80,
                    'bg-warning': scenario.success_probability >= 60 && scenario.success_probability < 80,
                    'bg-danger': scenario.success_probability < 60
                  }"
                  :style="{ width: (scenario.success_probability || 0) + '%' }"
                ></div>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="scenario-actions">
              <div class="btn-group w-100">
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="viewScenario(scenario)"
                >
                  <i class="bi bi-eye me-1"></i>
                  View Details
                </button>
                <button 
                  class="btn btn-outline-secondary btn-sm"
                  @click="downloadScenarioReport(scenario)"
                >
                  <i class="bi bi-download me-1"></i>
                  Report
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenario Detail Modal -->
    <Teleport to="body">
      <div v-if="viewingScenario" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-graph-up me-2"></i>
                  {{ viewingScenario.name }}
                </h5>
                <button type="button" class="btn-close" @click="viewingScenario = null"></button>
              </div>
              <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                <div class="scenario-details">
                  <!-- Summary -->
                  <div class="row mb-4">
                    <div class="col-md-6">
                      <div class="card bg-light">
                        <div class="card-body">
                          <h6 class="card-title">Scenario Overview</h6>
                          <div class="detail-item mb-2">
                            <strong>Status:</strong>
                            <span 
                              class="badge ms-2"
                              :class="getScenarioStatusBadge(viewingScenario.status)"
                            >
                              {{ viewingScenario.status || 'Draft' }}
                            </span>
                          </div>
                          <div class="detail-item mb-2">
                            <strong>Retirement Age:</strong>
                            {{ viewingScenario.retirement_age || 'Not set' }}
                          </div>
                          <div class="detail-item mb-2">
                            <strong>Planning Horizon:</strong>
                            {{ viewingScenario.planning_horizon || 'Not set' }} years
                          </div>
                          <div class="detail-item mb-2">
                            <strong>Last Updated:</strong>
                            {{ formatDateTime(viewingScenario.updated_at) }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="card bg-light">
                        <div class="card-body">
                          <h6 class="card-title">Key Metrics</h6>
                          <div v-if="viewingScenario.success_probability !== null" class="detail-item mb-3">
                            <strong>Success Probability:</strong>
                            <div class="mt-1">
                              <div class="progress" style="height: 8px;">
                                <div 
                                  class="progress-bar"
                                  :class="{
                                    'bg-success': viewingScenario.success_probability >= 80,
                                    'bg-warning': viewingScenario.success_probability >= 60 && viewingScenario.success_probability < 80,
                                    'bg-danger': viewingScenario.success_probability < 60
                                  }"
                                  :style="{ width: (viewingScenario.success_probability || 0) + '%' }"
                                ></div>
                              </div>
                              <small class="text-muted">{{ Math.round(viewingScenario.success_probability || 0) }}% chance of success</small>
                            </div>
                          </div>
                          <div v-if="viewingScenario.total_assets" class="detail-item mb-2">
                            <strong>Total Assets:</strong>
                            ${{ formatCurrency(viewingScenario.total_assets) }}
                          </div>
                          <div v-if="viewingScenario.annual_income" class="detail-item mb-2">
                            <strong>Projected Annual Income:</strong>
                            ${{ formatCurrency(viewingScenario.annual_income) }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Description -->
                  <div v-if="viewingScenario.description" class="mb-4">
                    <h6>Description</h6>
                    <div class="card bg-light">
                      <div class="card-body">
                        <p class="mb-0">{{ viewingScenario.description }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Assumptions & Notes -->
                  <div v-if="viewingScenario.assumptions || viewingScenario.notes" class="mb-4">
                    <h6>Assumptions & Notes</h6>
                    <div class="card bg-light">
                      <div class="card-body">
                        <div v-if="viewingScenario.assumptions" class="mb-3">
                          <strong>Assumptions:</strong>
                          <p class="mb-0 mt-1">{{ viewingScenario.assumptions }}</p>
                        </div>
                        <div v-if="viewingScenario.notes">
                          <strong>Notes:</strong>
                          <p class="mb-0 mt-1">{{ viewingScenario.notes }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Placeholder for Charts -->
                  <div class="chart-placeholder bg-light rounded p-5 text-center mb-4">
                    <i class="bi bi-bar-chart display-4 text-muted mb-3"></i>
                    <h6 class="text-muted">Scenario Projections</h6>
                    <p class="text-muted">
                      Interactive charts and projections would be displayed here.<br>
                      This would include asset growth, income projections, and Monte Carlo results.
                    </p>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="viewingScenario = null">
                  Close
                </button>
                <button 
                  type="button" 
                  class="btn btn-primary"
                  @click="downloadScenarioReport(viewingScenario)"
                >
                  <i class="bi bi-download me-2"></i>
                  Download Report
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="viewingScenario = null"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useClientStore } from '@/stores/clientStore.js'

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const clientStore = useClientStore()

// State
const scenarios = ref([])
const viewingScenario = ref(null)
const loading = ref(false)

// Methods
const loadScenarios = async () => {
  loading.value = true
  try {
    const response = await clientStore.getClientScenarios(props.client.id)
    scenarios.value = response.results || []
  } catch (error) {
    console.error('Failed to load scenarios:', error)
    scenarios.value = []
  } finally {
    loading.value = false
  }
}

const viewScenario = (scenario) => {
  viewingScenario.value = scenario
}

const downloadScenarioReport = async (scenario) => {
  try {
    // This would trigger a PDF download
    alert(`Report download for "${scenario.name}" will be implemented soon.`)
  } catch (error) {
    console.error('Failed to download report:', error)
    alert('Failed to download report. Please try again.')
  }
}

const contactAdvisor = () => {
  router.push({ name: 'client-portal-messages' })
}

const formatCurrency = (amount) => {
  if (!amount) return '0'
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const getScenarioStatusBadge = (status) => {
  const statusMap = {
    'active': 'bg-success',
    'draft': 'bg-warning text-dark',
    'archived': 'bg-secondary',
    'shared': 'bg-info',
    'completed': 'bg-primary'
  }
  return statusMap[status?.toLowerCase()] || 'bg-warning text-dark'
}

// Lifecycle
onMounted(() => {
  loadScenarios()
})
</script>

<style scoped>
.client-portal-scenarios {
  padding: 0;
}

.page-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.scenario-card {
  transition: all 0.2s ease;
  border: 1px solid #dee2e6;
}

.scenario-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.scenario-metrics {
  border-top: 1px solid #f8f9fa;
  border-bottom: 1px solid #f8f9fa;
  padding: 0.75rem 0;
}

.metric-item {
  font-size: 0.875rem;
}

.metric-label {
  flex-shrink: 0;
}

.metric-value {
  text-align: right;
  min-width: 0;
}

.success-probability .progress {
  border-radius: 3px;
}

.scenario-actions .btn-group .btn {
  flex: 1;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.detail-item strong {
  min-width: 140px;
  flex-shrink: 0;
}

.chart-placeholder {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.modal-overlay .modal {
  position: relative;
  z-index: 10001;
}

.modal-overlay .modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10000;
}
</style>