<template>
  <div class="report-center container-fluid" style="margin-top:80px;">
    <div class="dashboard-page-header">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-header-title">Report Center</h1>
          <p class="text-muted">Create, manage, and generate professional reports for your clients</p>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary" @click="showTemplateGallery">
            <i class="bi-collection me-2"></i>Browse Templates
          </button>
          <button class="btn btn-primary" @click="showReportBuilder">
            <i class="bi-file-plus me-2"></i>Create Report
          </button>
        </div>
      </div>
    </div>

    <!-- Report Generation Stats -->
    <div class="row mb-4">
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Total Reports</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ reports.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Pending Generation</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-warning">{{ pendingReports.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Templates Available</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-info">{{ templates.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <span class="card-subtitle mb-2 text-center d-block text-muted" style="font-size: 0.75rem; font-weight: 500;">Recent Generations</span>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-success">{{ recentReports.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi-lightning-charge me-2"></i>Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-4 mb-3">
                <div class="d-grid">
                  <button class="btn btn-outline-primary btn-lg" @click="showTemplateGallery">
                    <i class="bi-collection-fill mb-2 d-block fs-1"></i>
                    Browse Template Gallery
                  </button>
                </div>
              </div>
              <div class="col-md-4 mb-3">
                <div class="d-grid">
                  <button class="btn btn-outline-success btn-lg" @click="showReportBuilder">
                    <i class="bi-file-plus-fill mb-2 d-block fs-1"></i>
                    Create New Report
                  </button>
                </div>
              </div>
              <div class="col-md-4 mb-3">
                <div class="d-grid">
                  <button class="btn btn-outline-info btn-lg" @click="refreshData">
                    <i class="bi-arrow-clockwise mb-2 d-block fs-1"></i>
                    Refresh Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Reports -->
    <div class="row mb-4" v-if="recentReports.length > 0">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi-clock-history me-2"></i>Recent Reports
            </h5>
            <router-link to="/reports" class="btn btn-sm btn-outline-primary">
              View All Reports
            </router-link>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Report Name</th>
                    <th>Client</th>
                    <th>Template</th>
                    <th>Created</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="report in recentReports" :key="report.id">
                    <td>
                      <strong>{{ report.name }}</strong>
                      <br>
                      <small class="text-muted">{{ report.description }}</small>
                    </td>
                    <td>{{ report.client_name || 'N/A' }}</td>
                    <td>{{ report.template_name || 'Custom' }}</td>
                    <td>{{ formatDate(report.created_at) }}</td>
                    <td>
                      <span class="badge" :class="{
                        'bg-success': report.status === 'completed',
                        'bg-warning': report.status === 'generating',
                        'bg-danger': report.status === 'failed',
                        'bg-secondary': report.status === 'draft'
                      }">
                        {{ report.status }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="selectReport(report)"
                          title="Preview Report"
                        >
                          <i class="bi-eye"></i>
                        </button>
                        <div 
                          v-if="report.status === 'completed'"
                          class="btn-group btn-group-sm"
                        >
                          <button 
                            class="btn btn-outline-success"
                            @click="downloadReport(report, 'pdf')"
                            title="Download PDF"
                          >
                            <i class="bi-file-earmark-pdf"></i> PDF
                          </button>
                          <button 
                            class="btn btn-outline-info"
                            @click="downloadReport(report, 'pptx')"
                            title="Download PowerPoint"
                          >
                            <i class="bi-file-earmark-ppt"></i> PPTX
                          </button>
                        </div>
                        <button 
                          class="btn btn-outline-secondary"
                          @click="editReport(report)"
                          title="Edit Report"
                        >
                          <i class="bi-pencil"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Generation Tasks -->
    <div class="row mb-4" v-if="Object.keys(generationTasks).length > 0">
      <div class="col-12">
        <div class="card border-warning">
          <div class="card-header bg-warning text-dark">
            <h5 class="card-title mb-0">
              <i class="bi-gear-fill me-2"></i>Active Generation Tasks
            </h5>
          </div>
          <div class="card-body">
            <div v-for="(task, reportId) in generationTasks" :key="reportId" class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <strong>Report ID: {{ reportId }}</strong>
                <br>
                <small class="text-muted">
                  Format: {{ task.format }} | Started: {{ formatDate(task.started_at) }}
                </small>
              </div>
              <div>
                <div class="spinner-border spinner-border-sm text-warning me-2" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <span class="badge bg-warning">{{ task.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div class="row" v-if="reports.length === 0 && !reportLoading">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="bi-file-text display-1 text-muted mb-3"></i>
            <h4>Welcome to Report Center</h4>
            <p class="text-muted">Get started by creating your first report or browsing our template gallery.</p>
            <div class="d-flex justify-content-center gap-2">
              <button class="btn btn-primary" @click="showReportBuilder">
                <i class="bi-file-plus me-2"></i>Create First Report
              </button>
              <button class="btn btn-outline-primary" @click="showTemplateGallery">
                <i class="bi-collection me-2"></i>Browse Templates
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div class="row" v-if="reportLoading || templateLoading">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mt-3">Loading report center data...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div class="row" v-if="reportError || templateError">
      <div class="col-12">
        <div class="alert alert-danger" role="alert">
          <i class="bi-exclamation-triangle me-2"></i>
          <strong>Error:</strong> {{ reportError || templateError }}
          <button class="btn btn-sm btn-outline-danger ms-2" @click="clearErrors">
            <i class="bi-x-circle me-1"></i>Clear
          </button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <TemplateGallery 
      @template-selected="onTemplateSelected"
      @template-preview="onTemplatePreview"
    />
    
    <ReportBuilder 
      @report-created="onReportCreated"
    />
    
    <ReportPreview 
      :preview-type="previewType"
      @template-selected="onTemplateSelected"
      @report-edit="onReportEdit"
    />
  </div>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'
import TemplateGallery from '@/components/ReportCenter/TemplateGallery.vue'
import ReportBuilder from '@/components/ReportCenter/ReportBuilder.vue'
import ReportPreview from '@/components/ReportCenter/ReportPreview.vue'

export default {
  name: 'ReportCenterDashboard',
  components: {
    TemplateGallery,
    ReportBuilder,
    ReportPreview
  },
  setup() {
    const reportStore = useReportCenterStore()

    // Local state for modal management
    const previewType = ref('report')
    
    // Status polling for generating reports
    const pollingInterval = ref(null)

    // Computed properties from store
    const templates = computed(() => reportStore.templates)
    const reports = computed(() => reportStore.reports)
    const reportLoading = computed(() => reportStore.reportLoading)
    const templateLoading = computed(() => reportStore.templateLoading)
    const reportError = computed(() => reportStore.reportError)
    const templateError = computed(() => reportStore.templateError)
    const generationTasks = computed(() => reportStore.generationTasks)
    const recentReports = computed(() => reportStore.recentReports)
    const pendingReports = computed(() => reportStore.pendingReports)

    // Methods
    const showTemplateGallery = () => {
      reportStore.showTemplateGalleryModal()
    }

    const showReportBuilder = () => {
      reportStore.showReportBuilderModal()
    }

    const selectReport = (report) => {
      reportStore.selectReport(report)
      reportStore.showPreviewModalAction()
    }

    const downloadReport = async (report, format = 'pdf') => {
      try {
        console.log(`Downloading report: ${report.id} in ${format} format`)
        await reportStore.downloadReport(report.id, format)
        console.log('Download completed successfully')
      } catch (error) {
        console.error('Download failed:', error)
        alert(`Failed to download ${format.toUpperCase()} report. Please try again.`)
      }
    }

    const editReport = (report) => {
      reportStore.selectReport(report)
      reportStore.showReportBuilderModal()
    }

    const refreshData = async () => {
      try {
        await reportStore.refreshData()
      } catch (error) {
        console.error('Failed to refresh data:', error)
      }
    }

    const clearErrors = () => {
      reportStore.clearErrors()
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

    // Status polling functions
    const startStatusPolling = () => {
      if (pollingInterval.value) return // Already polling
      
      pollingInterval.value = setInterval(async () => {
        // Get all reports with generating status
        const generatingReports = reports.value.filter(report => 
          report.status === 'generating' || 
          Object.keys(generationTasks.value).includes(report.id?.toString())
        )
        
        // Check status for each generating report
        for (const report of generatingReports) {
          try {
            await reportStore.checkReportStatus(report.id)
          } catch (error) {
            console.error(`Failed to check status for report ${report.id}:`, error)
          }
        }
        
        // Stop polling if no reports are generating
        if (generatingReports.length === 0 && Object.keys(generationTasks.value).length === 0) {
          stopStatusPolling()
        }
      }, 3000) // Check every 3 seconds
    }
    
    const stopStatusPolling = () => {
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value)
        pollingInterval.value = null
      }
    }

    // Event handlers for modals
    const onTemplateSelected = (template) => {
      reportStore.selectTemplate(template)
      reportStore.showReportBuilderModal()
    }

    const onTemplatePreview = (template) => {
      reportStore.selectTemplate(template)
      previewType.value = 'template'
      reportStore.showPreviewModalAction()
    }

    const onReportCreated = (report) => {
      console.log('Report created:', report)
      // Refresh data to show new report
      refreshData()
      
      // Start status polling if report is generating
      if (report.status === 'generating' || Object.keys(generationTasks.value).length > 0) {
        startStatusPolling()
      }
    }

    const onReportEdit = (report) => {
      reportStore.selectReport(report)
      reportStore.showReportBuilderModal()
    }

    // Lifecycle
    onMounted(async () => {
      try {
        await reportStore.refreshData()
        
        // Start status polling if there are any generating reports
        const hasGeneratingReports = reports.value.some(report => 
          report.status === 'generating') || 
          Object.keys(generationTasks.value).length > 0
        
        if (hasGeneratingReports) {
          startStatusPolling()
        }
      } catch (error) {
        console.error('Failed to load initial data:', error)
      }
    })
    
    onUnmounted(() => {
      stopStatusPolling()
    })

    return {
      // Data
      templates,
      reports,
      reportLoading,
      templateLoading,
      reportError,
      templateError,
      generationTasks,
      recentReports,
      pendingReports,
      previewType,

      // Methods
      showTemplateGallery,
      showReportBuilder,
      selectReport,
      downloadReport,
      editReport,
      refreshData,
      clearErrors,
      formatDate,
      startStatusPolling,
      stopStatusPolling,
      onTemplateSelected,
      onTemplatePreview,
      onReportCreated,
      onReportEdit
    }
  }
}
</script>

<style scoped>
.report-center {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.dashboard-page-header {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-header-title {
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 0;
}

.card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: none;
  border-radius: 0.5rem;
}

.card-header {
  background-color: #fff;
  border-bottom: 1px solid #e9ecef;
  border-radius: 0.5rem 0.5rem 0 0 !important;
}

.btn-lg i {
  font-size: 2rem;
}

.table-hover tbody tr:hover {
  background-color: rgba(0,123,255,0.05);
}

.js-counter {
  font-weight: 700;
}

.badge {
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
}
</style>