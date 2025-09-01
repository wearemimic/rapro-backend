<template>
  <div class="bulk-export-manager">
    <!-- Bulk Export Modal -->
    <div 
      v-if="showBulkExportModal" 
      class="modal d-block"
      style="background: rgba(0,0,0,0.5);"
      @click.self="showBulkExportModal = false"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-download me-2"></i>Bulk Export Reports
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showBulkExportModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <!-- Export Configuration Form -->
            <div class="export-config-form">
              <!-- Selection Type -->
              <div class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label">Export Target</label>
                  <div class="btn-group w-100" role="group">
                    <input 
                      id="selectionClients" 
                      v-model="exportConfig.selectionType" 
                      type="radio" 
                      class="btn-check" 
                      value="clients"
                    >
                    <label for="selectionClients" class="btn btn-outline-primary">Clients</label>
                    
                    <input 
                      id="selectionScenarios" 
                      v-model="exportConfig.selectionType" 
                      type="radio" 
                      class="btn-check" 
                      value="scenarios"
                    >
                    <label for="selectionScenarios" class="btn btn-outline-primary">Scenarios</label>
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Export Format</label>
                  <select v-model="exportConfig.format" class="form-select">
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                    <option value="powerpoint">PowerPoint</option>
                  </select>
                </div>
              </div>

              <!-- Client Selection -->
              <div v-if="exportConfig.selectionType === 'clients'" class="mb-4">
                <label class="form-label">Select Clients</label>
                <div class="selection-controls mb-3">
                  <button 
                    @click="selectAllClients" 
                    class="btn btn-sm btn-outline-primary me-2"
                    type="button"
                  >
                    Select All
                  </button>
                  <button 
                    @click="clearClientSelection" 
                    class="btn btn-sm btn-outline-secondary me-2"
                    type="button"
                  >
                    Clear All
                  </button>
                  <input 
                    v-model="clientSearchTerm" 
                    type="text" 
                    class="form-control d-inline-block w-auto"
                    placeholder="Search clients..."
                    style="width: 200px !important"
                  >
                </div>
                <div class="client-selection-list border rounded p-3" style="max-height: 300px; overflow-y: auto;">
                  <div 
                    v-for="client in filteredClients" 
                    :key="client.id"
                    class="form-check mb-2"
                  >
                    <input 
                      :id="`client-${client.id}`"
                      v-model="exportConfig.selectedClients" 
                      type="checkbox" 
                      class="form-check-input"
                      :value="client.id"
                    >
                    <label :for="`client-${client.id}`" class="form-check-label">
                      {{ client.first_name }} {{ client.last_name }}
                      <small class="text-muted d-block">{{ client.email }}</small>
                    </label>
                  </div>
                  <div v-if="filteredClients.length === 0" class="text-muted text-center py-3">
                    No clients match your search
                  </div>
                </div>
                <small class="text-muted">{{ exportConfig.selectedClients.length }} clients selected</small>
              </div>

              <!-- Scenario Selection -->
              <div v-if="exportConfig.selectionType === 'scenarios'" class="mb-4">
                <label class="form-label">Select Scenarios</label>
                <div class="selection-controls mb-3">
                  <button 
                    @click="selectAllScenarios" 
                    class="btn btn-sm btn-outline-primary me-2"
                    type="button"
                  >
                    Select All
                  </button>
                  <button 
                    @click="clearScenarioSelection" 
                    class="btn btn-sm btn-outline-secondary me-2"
                    type="button"
                  >
                    Clear All
                  </button>
                  <input 
                    v-model="scenarioSearchTerm" 
                    type="text" 
                    class="form-control d-inline-block w-auto"
                    placeholder="Search scenarios..."
                    style="width: 200px !important"
                  >
                </div>
                <div class="scenario-selection-list border rounded p-3" style="max-height: 300px; overflow-y: auto;">
                  <div 
                    v-for="scenario in filteredScenarios" 
                    :key="scenario.id"
                    class="form-check mb-2"
                  >
                    <input 
                      :id="`scenario-${scenario.id}`"
                      v-model="exportConfig.selectedScenarios" 
                      type="checkbox" 
                      class="form-check-input"
                      :value="scenario.id"
                    >
                    <label :for="`scenario-${scenario.id}`" class="form-check-label">
                      {{ scenario.name }}
                      <small class="text-muted d-block">
                        Client: {{ scenario.client_name }} | 
                        Updated: {{ formatDate(scenario.updated_at) }}
                      </small>
                    </label>
                  </div>
                  <div v-if="filteredScenarios.length === 0" class="text-muted text-center py-3">
                    No scenarios match your search
                  </div>
                </div>
                <small class="text-muted">{{ exportConfig.selectedScenarios.length }} scenarios selected</small>
              </div>

              <!-- Template Selection -->
              <div class="mb-4">
                <label class="form-label">Select Templates</label>
                <div class="template-selection">
                  <div class="row">
                    <div 
                      v-for="template in availableTemplates" 
                      :key="template.id"
                      class="col-md-6 mb-3"
                    >
                      <div class="card template-card h-100" :class="{ 'selected': exportConfig.selectedTemplates.includes(template.id) }">
                        <div class="card-body">
                          <div class="form-check">
                            <input 
                              :id="`template-${template.id}`"
                              v-model="exportConfig.selectedTemplates" 
                              type="checkbox" 
                              class="form-check-input"
                              :value="template.id"
                            >
                            <label :for="`template-${template.id}`" class="form-check-label">
                              <h6 class="card-title mb-1">{{ template.name }}</h6>
                              <p class="card-text small text-muted">{{ template.description }}</p>
                              <span class="badge bg-secondary">{{ template.category }}</span>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <small class="text-muted">{{ exportConfig.selectedTemplates.length }} templates selected</small>
              </div>

              <!-- Export Options -->
              <div class="mb-4">
                <h6>Export Options</h6>
                <div class="row">
                  <div class="col-md-6">
                    <div class="form-check mb-2">
                      <input 
                        id="includeCharts" 
                        v-model="exportConfig.options.includeCharts" 
                        type="checkbox" 
                        class="form-check-input"
                      >
                      <label for="includeCharts" class="form-check-label">Include Charts</label>
                    </div>
                    <div class="form-check mb-2">
                      <input 
                        id="includeDataTables" 
                        v-model="exportConfig.options.includeDataTables" 
                        type="checkbox" 
                        class="form-check-input"
                      >
                      <label for="includeDataTables" class="form-check-label">Include Data Tables</label>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="form-check mb-2">
                      <input 
                        id="includeComments" 
                        v-model="exportConfig.options.includeComments" 
                        type="checkbox" 
                        class="form-check-input"
                      >
                      <label for="includeComments" class="form-check-label">Include Comments</label>
                    </div>
                    <div class="form-check mb-2">
                      <input 
                        id="organizeByClient" 
                        v-model="exportConfig.options.organizeByClient" 
                        type="checkbox" 
                        class="form-check-input"
                      >
                      <label for="organizeByClient" class="form-check-label">Organize by Client</label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- PDF Options (conditional) -->
              <div v-if="exportConfig.format === 'pdf'" class="mb-4">
                <h6>PDF Options</h6>
                <div class="row">
                  <div class="col-md-6">
                    <label class="form-label">Page Size</label>
                    <select v-model="exportConfig.pdfOptions.pageSize" class="form-select">
                      <option value="letter">Letter</option>
                      <option value="a4">A4</option>
                      <option value="legal">Legal</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Orientation</label>
                    <select v-model="exportConfig.pdfOptions.orientation" class="form-select">
                      <option value="portrait">Portrait</option>
                      <option value="landscape">Landscape</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Summary -->
              <div class="export-summary bg-light p-3 rounded">
                <h6>Export Summary</h6>
                <div class="row">
                  <div class="col-md-3">
                    <strong>{{ getTotalItems() }}</strong><br>
                    <small class="text-muted">Total Items</small>
                  </div>
                  <div class="col-md-3">
                    <strong>{{ exportConfig.selectedTemplates.length }}</strong><br>
                    <small class="text-muted">Templates</small>
                  </div>
                  <div class="col-md-3">
                    <strong>{{ exportConfig.format.toUpperCase() }}</strong><br>
                    <small class="text-muted">Format</small>
                  </div>
                  <div class="col-md-3">
                    <strong>{{ getEstimatedTime() }}</strong><br>
                    <small class="text-muted">Est. Time</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showBulkExportModal = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="startBulkExport"
              :disabled="!canStartExport"
            >
              <i class="fas fa-play me-1"></i>Start Export
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Jobs List -->
    <div class="export-jobs-section">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5>
          <i class="fas fa-tasks me-2"></i>Export Jobs
        </h5>
        <button 
          @click="showBulkExportModal = true" 
          class="btn btn-primary"
        >
          <i class="fas fa-plus me-1"></i>New Bulk Export
        </button>
      </div>

      <!-- Jobs Filter -->
      <div class="jobs-filter mb-3">
        <div class="row">
          <div class="col-md-4">
            <select v-model="jobsFilter.status" class="form-select" @change="loadExportJobs">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="completed_with_errors">Completed with Errors</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-4">
            <button @click="loadExportJobs" class="btn btn-outline-secondary">
              <i class="fas fa-sync me-1"></i>Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Export Jobs Table -->
      <div class="export-jobs-table">
        <div v-if="isLoadingJobs" class="text-center py-4">
          <div class="spinner-border text-primary" role="status"></div>
          <div class="mt-2">Loading export jobs...</div>
        </div>

        <div v-else-if="exportJobs.length === 0" class="text-center py-5">
          <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
          <h6 class="text-muted">No export jobs found</h6>
          <p class="text-muted">Start your first bulk export to see jobs here</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Items</th>
                <th>Format</th>
                <th>Started</th>
                <th>Duration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in exportJobs" :key="job.id">
                <td>
                  <span class="font-monospace">#{{ job.id }}</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(job.status)">
                    {{ getStatusLabel(job.status) }}
                  </span>
                </td>
                <td>
                  <div class="progress" style="height: 20px;">
                    <div 
                      class="progress-bar" 
                      :class="getProgressBarClass(job.status)"
                      role="progressbar" 
                      :style="`width: ${job.progress}%`"
                    >
                      {{ job.progress }}%
                    </div>
                  </div>
                </td>
                <td>
                  <div class="text-nowrap">
                    <small class="text-success">{{ job.successful_exports || 0 }} success</small><br>
                    <small class="text-danger">{{ job.failed_exports || 0 }} failed</small>
                  </div>
                </td>
                <td>
                  <span class="badge bg-info">{{ job.export_config.format?.toUpperCase() || 'PDF' }}</span>
                </td>
                <td>
                  <small>{{ formatDate(job.started_at) }}</small>
                </td>
                <td>
                  <small>{{ formatDuration(job.duration) }}</small>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      v-if="job.status === 'completed' || job.status === 'completed_with_errors'"
                      @click="downloadExport(job.id)"
                      class="btn btn-outline-success"
                      title="Download"
                    >
                      <i class="fas fa-download"></i>
                    </button>
                    <button 
                      v-if="job.status === 'pending' || job.status === 'processing'"
                      @click="cancelExport(job.id)"
                      class="btn btn-outline-warning"
                      title="Cancel"
                    >
                      <i class="fas fa-stop"></i>
                    </button>
                    <button 
                      v-if="job.is_completed"
                      @click="deleteExport(job.id)"
                      class="btn btn-outline-danger"
                      title="Delete"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <nav v-if="pagination.total_pages > 1" class="mt-4">
          <ul class="pagination justify-content-center">
            <li class="page-item" :class="{ disabled: !pagination.has_previous }">
              <button 
                class="page-link" 
                @click="changePage(pagination.page - 1)"
                :disabled="!pagination.has_previous"
              >
                Previous
              </button>
            </li>
            <li 
              v-for="page in getVisiblePages()" 
              :key="page"
              class="page-item" 
              :class="{ active: page === pagination.page }"
            >
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <button 
                class="page-link" 
                @click="changePage(pagination.page + 1)"
                :disabled="!pagination.has_next"
              >
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'
import api from '@/services/api'

export default {
  name: 'BulkExportManager',
  setup() {
    const reportStore = useReportCenterStore()

    // Reactive data
    const showBulkExportModal = ref(false)
    const isLoadingJobs = ref(false)
    const exportJobs = ref([])
    const clients = ref([])
    const scenarios = ref([])
    const availableTemplates = ref([])
    
    const clientSearchTerm = ref('')
    const scenarioSearchTerm = ref('')
    
    const exportConfig = ref({
      selectionType: 'clients',
      format: 'pdf',
      selectedClients: [],
      selectedScenarios: [],
      selectedTemplates: [],
      options: {
        includeCharts: true,
        includeDataTables: true,
        includeComments: false,
        organizeByClient: true
      },
      pdfOptions: {
        pageSize: 'letter',
        orientation: 'portrait'
      }
    })
    
    const jobsFilter = ref({
      status: '',
      page: 1
    })
    
    const pagination = ref({
      page: 1,
      page_size: 20,
      total_count: 0,
      total_pages: 0,
      has_next: false,
      has_previous: false
    })

    // Computed properties
    const filteredClients = computed(() => {
      if (!clientSearchTerm.value) return clients.value
      
      const searchTerm = clientSearchTerm.value.toLowerCase()
      return clients.value.filter(client => 
        `${client.first_name} ${client.last_name}`.toLowerCase().includes(searchTerm) ||
        client.email.toLowerCase().includes(searchTerm)
      )
    })

    const filteredScenarios = computed(() => {
      if (!scenarioSearchTerm.value) return scenarios.value
      
      const searchTerm = scenarioSearchTerm.value.toLowerCase()
      return scenarios.value.filter(scenario => 
        scenario.name.toLowerCase().includes(searchTerm) ||
        scenario.client_name.toLowerCase().includes(searchTerm)
      )
    })

    const canStartExport = computed(() => {
      const hasSelection = 
        (exportConfig.value.selectionType === 'clients' && exportConfig.value.selectedClients.length > 0) ||
        (exportConfig.value.selectionType === 'scenarios' && exportConfig.value.selectedScenarios.length > 0)
      
      const hasTemplates = exportConfig.value.selectedTemplates.length > 0
      
      return hasSelection && hasTemplates
    })

    // Methods
    const loadInitialData = async () => {
      try {
        // Load clients
        const clientsResponse = await api.get('/api/clients/')
        clients.value = clientsResponse.data.results || clientsResponse.data

        // Load scenarios with client names
        const scenariosResponse = await api.get('/api/scenarios/')
        scenarios.value = (scenariosResponse.data.results || scenariosResponse.data).map(scenario => ({
          ...scenario,
          client_name: `${scenario.client.first_name} ${scenario.client.last_name}`
        }))

        // Load templates
        const templatesResponse = await reportStore.getTemplates()
        availableTemplates.value = templatesResponse

        // Load export jobs
        await loadExportJobs()
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    const selectAllClients = () => {
      exportConfig.value.selectedClients = filteredClients.value.map(client => client.id)
    }

    const clearClientSelection = () => {
      exportConfig.value.selectedClients = []
    }

    const selectAllScenarios = () => {
      exportConfig.value.selectedScenarios = filteredScenarios.value.map(scenario => scenario.id)
    }

    const clearScenarioSelection = () => {
      exportConfig.value.selectedScenarios = []
    }

    const getTotalItems = () => {
      const selectedCount = exportConfig.value.selectionType === 'clients' 
        ? exportConfig.value.selectedClients.length 
        : exportConfig.value.selectedScenarios.length
      
      return selectedCount * exportConfig.value.selectedTemplates.length
    }

    const getEstimatedTime = () => {
      const totalItems = getTotalItems()
      const estimatedMinutes = Math.ceil(totalItems * 0.5) // 30 seconds per item
      return estimatedMinutes > 60 
        ? `${Math.ceil(estimatedMinutes / 60)}h ${estimatedMinutes % 60}m`
        : `${estimatedMinutes}m`
    }

    const startBulkExport = async () => {
      try {
        const payload = {
          export_config: {
            format: exportConfig.value.format,
            ...exportConfig.value.options,
            pdf_options: exportConfig.value.format === 'pdf' ? exportConfig.value.pdfOptions : undefined
          },
          selection_type: exportConfig.value.selectionType,
          client_ids: exportConfig.value.selectionType === 'clients' ? exportConfig.value.selectedClients : undefined,
          scenario_ids: exportConfig.value.selectionType === 'scenarios' ? exportConfig.value.selectedScenarios : undefined,
          template_ids: exportConfig.value.selectedTemplates
        }

        const response = await api.post('/api/report-center/bulk-export/initiate/', payload)
        
        // Close modal and refresh jobs list
        showBulkExportModal.value = false
        await loadExportJobs()
        
        // Reset form
        exportConfig.value.selectedClients = []
        exportConfig.value.selectedScenarios = []
        exportConfig.value.selectedTemplates = []
        
        // Show success message
        console.log('Bulk export started:', response.data)
      } catch (error) {
        console.error('Error starting bulk export:', error)
      }
    }

    const loadExportJobs = async () => {
      try {
        isLoadingJobs.value = true
        
        const params = {
          page: pagination.value.page,
          page_size: pagination.value.page_size
        }
        
        if (jobsFilter.value.status) {
          params.status = jobsFilter.value.status
        }

        const response = await api.get('/api/report-center/bulk-export/jobs/', { params })
        
        exportJobs.value = response.data.jobs
        pagination.value = response.data.pagination
      } catch (error) {
        console.error('Error loading export jobs:', error)
      } finally {
        isLoadingJobs.value = false
      }
    }

    const changePage = (page) => {
      pagination.value.page = page
      loadExportJobs()
    }

    const getVisiblePages = () => {
      const current = pagination.value.page
      const total = pagination.value.total_pages
      const visible = []
      
      const start = Math.max(1, current - 2)
      const end = Math.min(total, current + 2)
      
      for (let i = start; i <= end; i++) {
        visible.push(i)
      }
      
      return visible
    }

    const downloadExport = async (jobId) => {
      try {
        const response = await api.get(`/api/report-center/bulk-export/${jobId}/download/`)
        
        // Create download link
        const downloadUrl = response.data.download_url
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `bulk_export_${jobId}.zip`
        link.click()
      } catch (error) {
        console.error('Error downloading export:', error)
      }
    }

    const cancelExport = async (jobId) => {
      try {
        await api.post(`/api/report-center/bulk-export/${jobId}/cancel/`)
        await loadExportJobs()
      } catch (error) {
        console.error('Error cancelling export:', error)
      }
    }

    const deleteExport = async (jobId) => {
      if (!confirm('Are you sure you want to delete this export job? This action cannot be undone.')) {
        return
      }
      
      try {
        await api.delete(`/api/report-center/bulk-export/${jobId}/`)
        await loadExportJobs()
      } catch (error) {
        console.error('Error deleting export:', error)
      }
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        pending: 'bg-warning text-dark',
        processing: 'bg-info',
        completed: 'bg-success',
        completed_with_errors: 'bg-warning text-dark',
        failed: 'bg-danger',
        cancelled: 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
    }

    const getStatusLabel = (status) => {
      const labels = {
        pending: 'Pending',
        processing: 'Processing',
        completed: 'Completed',
        completed_with_errors: 'Completed with Errors',
        failed: 'Failed',
        cancelled: 'Cancelled'
      }
      return labels[status] || status
    }

    const getProgressBarClass = (status) => {
      const classes = {
        pending: '',
        processing: 'bg-info',
        completed: 'bg-success',
        completed_with_errors: 'bg-warning',
        failed: 'bg-danger',
        cancelled: 'bg-secondary'
      }
      return classes[status] || ''
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatDuration = (seconds) => {
      if (!seconds) return '-'
      
      if (seconds < 60) {
        return `${Math.round(seconds)}s`
      } else if (seconds < 3600) {
        return `${Math.round(seconds / 60)}m`
      } else {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.round((seconds % 3600) / 60)
        return `${hours}h ${minutes}m`
      }
    }

    // Auto-refresh active jobs
    const refreshInterval = ref(null)
    
    const startAutoRefresh = () => {
      refreshInterval.value = setInterval(() => {
        const hasActiveJobs = exportJobs.value.some(job => 
          job.status === 'pending' || job.status === 'processing'
        )
        
        if (hasActiveJobs) {
          loadExportJobs()
        }
      }, 5000) // Refresh every 5 seconds
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    // Lifecycle
    onMounted(() => {
      loadInitialData()
      startAutoRefresh()
    })

    // Watch for selection type changes
    watch(() => exportConfig.value.selectionType, () => {
      exportConfig.value.selectedClients = []
      exportConfig.value.selectedScenarios = []
    })

    return {
      // Data
      showBulkExportModal,
      isLoadingJobs,
      exportJobs,
      clients,
      scenarios,
      availableTemplates,
      clientSearchTerm,
      scenarioSearchTerm,
      exportConfig,
      jobsFilter,
      pagination,
      
      // Computed
      filteredClients,
      filteredScenarios,
      canStartExport,
      
      // Methods
      selectAllClients,
      clearClientSelection,
      selectAllScenarios,
      clearScenarioSelection,
      getTotalItems,
      getEstimatedTime,
      startBulkExport,
      loadExportJobs,
      changePage,
      getVisiblePages,
      downloadExport,
      cancelExport,
      deleteExport,
      getStatusBadgeClass,
      getStatusLabel,
      getProgressBarClass,
      formatDate,
      formatDuration
    }
  }
}
</script>

<style scoped>
.bulk-export-manager {
  padding: 2rem 0;
}

.modal {
  z-index: 1060;
}

.selection-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.client-selection-list,
.scenario-selection-list {
  background: #fafafa;
}

.template-card {
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.template-card:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.15);
}

.template-card.selected {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.template-card .form-check-input {
  margin-top: 0.25rem;
}

.export-summary {
  border: 1px solid #dee2e6;
}

.export-jobs-table {
  min-height: 400px;
}

.progress {
  margin-bottom: 0;
}

.btn-group-sm > .btn {
  font-size: 0.75rem;
}

.page-link {
  color: #007bff;
}

.page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

/* Auto-refresh indicator */
.export-jobs-section {
  position: relative;
}

.auto-refresh-indicator {
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: #6c757d;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 1rem;
  }
  
  .selection-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .selection-controls input[type="text"] {
    width: 100% !important;
    margin-top: 0.5rem;
  }
}
</style>