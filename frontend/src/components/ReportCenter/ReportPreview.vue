<template>
  <div class="modal fade" id="reportPreviewModal" tabindex="-1" aria-labelledby="reportPreviewModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header bg-dark text-white">
          <h5 class="modal-title" id="reportPreviewModalLabel">
            <i class="bi-eye me-2"></i>
            {{ previewType === 'template' ? 'Template Preview' : 'Report Preview' }}
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body p-0">
          <div class="preview-container h-100">
            <!-- Preview Toolbar -->
            <div class="preview-toolbar bg-light border-bottom">
              <div class="d-flex justify-content-between align-items-center px-3 py-2">
                <div class="d-flex align-items-center gap-3">
                  <!-- Item Info -->
                  <div v-if="previewItem">
                    <h6 class="mb-0">{{ previewItem.name }}</h6>
                    <small class="text-muted">
                      {{ previewType === 'template' ? 'Template' : 'Report' }} • 
                      {{ previewType === 'template' ? getTypeLabel(previewItem.template_type) : previewItem.status }}
                    </small>
                  </div>
                  
                  <!-- Preview Mode Toggle -->
                  <div class="btn-group" role="group">
                    <input 
                      type="radio" 
                      class="btn-check" 
                      name="previewMode" 
                      id="contentMode" 
                      value="content"
                      v-model="previewMode"
                    >
                    <label class="btn btn-outline-primary btn-sm" for="contentMode">
                      <i class="bi-file-text me-1"></i>Content
                    </label>
                    
                    <input 
                      type="radio" 
                      class="btn-check" 
                      name="previewMode" 
                      id="layoutMode" 
                      value="layout"
                      v-model="previewMode"
                    >
                    <label class="btn btn-outline-primary btn-sm" for="layoutMode">
                      <i class="bi-layout-text-sidebar me-1"></i>Layout
                    </label>
                    
                    <input 
                      type="radio" 
                      class="btn-check" 
                      name="previewMode" 
                      id="pdfMode" 
                      value="pdf"
                      v-model="previewMode"
                    >
                    <label class="btn btn-outline-primary btn-sm" for="pdfMode">
                      <i class="bi-file-pdf me-1"></i>PDF
                    </label>
                  </div>
                </div>

                <div class="d-flex align-items-center gap-2">
                  <!-- Zoom Controls -->
                  <div class="zoom-controls d-flex align-items-center gap-1">
                    <button class="btn btn-sm btn-outline-secondary" @click="zoomOut" :disabled="zoomLevel <= 0.5">
                      <i class="bi-zoom-out"></i>
                    </button>
                    <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
                    <button class="btn btn-sm btn-outline-secondary" @click="zoomIn" :disabled="zoomLevel >= 2">
                      <i class="bi-zoom-in"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" @click="resetZoom">
                      <i class="bi-arrows-angle-contract"></i>
                    </button>
                  </div>

                  <!-- Action Buttons -->
                  <div class="preview-actions">
                    <button 
                      v-if="previewType === 'template'"
                      class="btn btn-sm btn-primary"
                      @click="useTemplate"
                    >
                      <i class="bi-file-plus me-1"></i>Use Template
                    </button>
                    <button 
                      v-if="previewType === 'report' && previewItem?.status === 'completed'"
                      class="btn btn-sm btn-success"
                      @click="downloadReport"
                    >
                      <i class="bi-download me-1"></i>Download
                    </button>
                    <button 
                      v-if="previewType === 'report'"
                      class="btn btn-sm btn-outline-primary"
                      @click="editReport"
                    >
                      <i class="bi-pencil me-1"></i>Edit
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Preview Content -->
            <div class="preview-content" :style="{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }">
              <!-- Loading State -->
              <div v-if="previewLoading" class="preview-loading d-flex align-items-center justify-content-center h-100">
                <div class="text-center">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading preview...</span>
                  </div>
                  <p class="text-muted">Loading preview...</p>
                </div>
              </div>

              <!-- Error State -->
              <div v-else-if="previewError" class="preview-error d-flex align-items-center justify-content-center h-100">
                <div class="text-center">
                  <i class="bi-exclamation-triangle display-1 text-danger mb-3"></i>
                  <h5>Preview Error</h5>
                  <p class="text-muted">{{ previewError }}</p>
                  <button class="btn btn-primary" @click="retryPreview">
                    <i class="bi-arrow-clockwise me-2"></i>Retry
                  </button>
                </div>
              </div>

              <!-- Content Preview Mode -->
              <div v-else-if="previewMode === 'content'" class="content-preview">
                <div class="preview-document">
                  <!-- Cover Page -->
                  <div class="preview-page cover-page">
                    <div class="page-content">
                      <div class="text-center">
                        <h1 class="display-4 mb-4">{{ previewItem?.name || 'Report Title' }}</h1>
                        <div class="mb-4">
                          <img src="/images/logo-placeholder.png" alt="Logo" class="company-logo mb-3">
                        </div>
                        <div class="client-info">
                          <h3 v-if="previewItem?.client_name">{{ previewItem.client_name }}</h3>
                          <p class="text-muted">{{ formatDate(previewItem?.created_at || new Date()) }}</p>
                        </div>
                        <div class="report-type mt-4">
                          <span class="badge bg-primary fs-6">
                            {{ previewType === 'template' ? getTypeLabel(previewItem?.template_type) : 'Financial Report' }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Table of Contents -->
                  <div class="preview-page toc-page">
                    <div class="page-content">
                      <h2 class="page-title mb-4">Table of Contents</h2>
                      <div class="toc-list">
                        <div 
                          v-for="(section, index) in previewSections" 
                          :key="index"
                          class="toc-item d-flex justify-content-between align-items-center"
                        >
                          <div class="d-flex align-items-center">
                            <span class="section-number me-3">{{ index + 1 }}</span>
                            <span class="section-title">{{ section.title }}</span>
                          </div>
                          <span class="page-number">{{ section.pageNumber || index + 3 }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Content Sections -->
                  <div 
                    v-for="(section, index) in previewSections" 
                    :key="section.id || index"
                    class="preview-page content-page"
                  >
                    <div class="page-content">
                      <div class="page-header">
                        <h2 class="page-title">{{ section.title }}</h2>
                        <div class="page-subtitle text-muted">{{ section.description }}</div>
                      </div>
                      
                      <div class="section-content">
                        <!-- Sample content based on section type -->
                        <div v-if="section.type === 'executive_summary'" class="executive-summary">
                          <div class="summary-highlights mb-4">
                            <div class="row">
                              <div class="col-md-4 mb-3">
                                <div class="highlight-card">
                                  <div class="highlight-value">$1,250,000</div>
                                  <div class="highlight-label">Current Assets</div>
                                </div>
                              </div>
                              <div class="col-md-4 mb-3">
                                <div class="highlight-card">
                                  <div class="highlight-value">92%</div>
                                  <div class="highlight-label">Success Probability</div>
                                </div>
                              </div>
                              <div class="col-md-4 mb-3">
                                <div class="highlight-card">
                                  <div class="highlight-value">$85,000</div>
                                  <div class="highlight-label">Annual Income Goal</div>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div class="sample-text">
                            <p>This comprehensive analysis shows a strong foundation for retirement planning with several opportunities for optimization...</p>
                          </div>
                        </div>

                        <div v-else-if="section.type === 'financial_position'" class="financial-position">
                          <div class="chart-placeholder mb-4">
                            <div class="chart-container">
                              <canvas class="sample-chart"></canvas>
                            </div>
                          </div>
                          <div class="sample-text">
                            <p>Current financial position analysis indicates...</p>
                          </div>
                        </div>

                        <div v-else class="generic-section">
                          <div class="sample-text">
                            <p>{{ section.description || 'Section content will be generated based on your data and selected template.' }}</p>
                            <div class="content-placeholder">
                              <div class="placeholder-line long"></div>
                              <div class="placeholder-line medium"></div>
                              <div class="placeholder-line short"></div>
                              <div class="placeholder-line long"></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Layout Preview Mode -->
              <div v-else-if="previewMode === 'layout'" class="layout-preview">
                <div class="layout-grid">
                  <div class="layout-page" v-for="n in estimatedPages" :key="n">
                    <div class="page-wireframe">
                      <div class="wireframe-header"></div>
                      <div class="wireframe-content">
                        <div class="wireframe-block"></div>
                        <div class="wireframe-block small"></div>
                        <div class="wireframe-block medium"></div>
                      </div>
                    </div>
                    <div class="page-label">Page {{ n }}</div>
                  </div>
                </div>
              </div>

              <!-- PDF Preview Mode -->
              <div v-else-if="previewMode === 'pdf'" class="pdf-preview">
                <div class="pdf-viewer">
                  <div v-if="pdfUrl" class="pdf-embed">
                    <iframe :src="pdfUrl" width="100%" height="100%"></iframe>
                  </div>
                  <div v-else class="pdf-placeholder d-flex align-items-center justify-content-center h-100">
                    <div class="text-center">
                      <i class="bi-file-pdf display-1 text-muted mb-3"></i>
                      <h5>PDF Preview</h5>
                      <p class="text-muted">Generate report to view PDF preview</p>
                      <button v-if="previewType === 'report'" class="btn btn-primary" @click="generatePdfPreview">
                        <i class="bi-file-pdf me-2"></i>Generate PDF
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-light">
          <div class="d-flex justify-content-between w-100 align-items-center">
            <div class="preview-info">
              <small class="text-muted">
                {{ previewSections.length }} sections • {{ estimatedPages }} pages
                <span v-if="previewItem?.updated_at">
                  • Last updated {{ formatDate(previewItem.updated_at) }}
                </span>
              </small>
            </div>
            <div>
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'

export default {
  name: 'ReportPreview',
  props: {
    previewType: {
      type: String,
      default: 'report', // 'report' or 'template'
      validator: value => ['report', 'template'].includes(value)
    }
  },
  emits: ['template-selected', 'report-edit'],
  setup(props, { emit }) {
    const reportStore = useReportCenterStore()

    // Preview state
    const previewMode = ref('content')
    const zoomLevel = ref(1)
    const previewLoading = ref(false)
    const previewError = ref(null)
    const pdfUrl = ref(null)

    // Computed properties
    const previewItem = computed(() => {
      return props.previewType === 'template' 
        ? reportStore.selectedTemplate 
        : reportStore.selectedReport
    })

    const previewSections = computed(() => {
      if (!previewItem.value) return []
      
      if (props.previewType === 'template') {
        return previewItem.value.sections || getDefaultSections()
      } else {
        return previewItem.value.sections || getDefaultSections()
      }
    })

    const estimatedPages = computed(() => {
      const basePages = 2 // Cover + TOC
      const sectionPages = previewSections.value.length * 1.5
      return Math.ceil(basePages + sectionPages)
    })

    // Default sections for preview
    const getDefaultSections = () => [
      {
        title: 'Executive Summary',
        description: 'High-level overview of financial situation',
        type: 'executive_summary'
      },
      {
        title: 'Client Information',
        description: 'Basic client demographics and profile',
        type: 'client_info'
      },
      {
        title: 'Current Financial Position',
        description: 'Assets, liabilities, and cash flow',
        type: 'financial_position'
      },
      {
        title: 'Retirement Projections',
        description: 'Projected income and asset growth',
        type: 'retirement_projections'
      },
      {
        title: 'Recommendations',
        description: 'Strategic recommendations and next steps',
        type: 'recommendations'
      }
    ]

    // Methods
    const getTypeLabel = (type) => {
      const labels = {
        'comprehensive': 'Comprehensive Report',
        'retirement_analysis': 'Retirement Analysis',
        'tax_planning': 'Tax Planning Report',
        'estate_planning': 'Estate Planning Report',
        'investment_review': 'Investment Review',
        'monte_carlo': 'Monte Carlo Analysis'
      }
      return labels[type] || type
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const zoomIn = () => {
      if (zoomLevel.value < 2) {
        zoomLevel.value = Math.min(2, zoomLevel.value + 0.25)
      }
    }

    const zoomOut = () => {
      if (zoomLevel.value > 0.5) {
        zoomLevel.value = Math.max(0.5, zoomLevel.value - 0.25)
      }
    }

    const resetZoom = () => {
      zoomLevel.value = 1
    }

    const useTemplate = () => {
      if (previewItem.value) {
        emit('template-selected', previewItem.value)
        // Close modal
        const modal = document.getElementById('reportPreviewModal')
        const bsModal = window.bootstrap.Modal.getInstance(modal)
        bsModal?.hide()
      }
    }

    const editReport = () => {
      if (previewItem.value) {
        emit('report-edit', previewItem.value)
        // Close modal
        const modal = document.getElementById('reportPreviewModal')
        const bsModal = window.bootstrap.Modal.getInstance(modal)
        bsModal?.hide()
      }
    }

    const downloadReport = async () => {
      if (previewItem.value) {
        try {
          // This would trigger download in real implementation
          console.log('Download report:', previewItem.value.id)
        } catch (error) {
          console.error('Failed to download report:', error)
        }
      }
    }

    const generatePdfPreview = async () => {
      if (previewItem.value) {
        try {
          previewLoading.value = true
          // Generate PDF preview
          await reportStore.generateReport(previewItem.value.id, 'pdf')
          // Set PDF URL for preview (mock URL)
          pdfUrl.value = `/api/reports/${previewItem.value.id}/preview.pdf`
        } catch (error) {
          previewError.value = 'Failed to generate PDF preview'
          console.error('Failed to generate PDF preview:', error)
        } finally {
          previewLoading.value = false
        }
      }
    }

    const retryPreview = () => {
      previewError.value = null
      previewLoading.value = false
      pdfUrl.value = null
    }

    // Watch for item changes to reset preview state
    watch(previewItem, (newItem) => {
      if (newItem) {
        previewMode.value = 'content'
        zoomLevel.value = 1
        previewError.value = null
        pdfUrl.value = null
      }
    })

    // Modal management
    onMounted(() => {
      // Watch store state to show/hide modal
      watch(() => reportStore.showPreviewModal, (show) => {
        const modal = document.getElementById('reportPreviewModal')
        if (modal && show) {
          const bootstrapModal = new window.bootstrap.Modal(modal)
          bootstrapModal.show()
        }
      }, { immediate: true })

      // Reset store state when modal is hidden
      const modal = document.getElementById('reportPreviewModal')
      if (modal) {
        modal.addEventListener('hidden.bs.modal', () => {
          reportStore.hidePreviewModalAction()
        })
      }
    })

    return {
      // Data
      previewMode,
      zoomLevel,
      previewLoading,
      previewError,
      pdfUrl,

      // Computed
      previewItem,
      previewSections,
      estimatedPages,

      // Methods
      getTypeLabel,
      formatDate,
      zoomIn,
      zoomOut,
      resetZoom,
      useTemplate,
      editReport,
      downloadReport,
      generatePdfPreview,
      retryPreview
    }
  }
}
</script>

<style scoped>
/* Preview Container */
.preview-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.preview-toolbar {
  flex-shrink: 0;
  border-bottom: 2px solid #e9ecef;
}

.preview-content {
  flex-grow: 1;
  overflow: auto;
  background-color: #f8f9fa;
  position: relative;
}

/* Zoom Controls */
.zoom-level {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

/* Content Preview */
.content-preview {
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.preview-document {
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-width: 800px;
  width: 100%;
}

.preview-page {
  min-height: 11in;
  padding: 1in;
  border-bottom: 2px solid #e9ecef;
  page-break-after: always;
}

.preview-page:last-child {
  border-bottom: none;
}

/* Cover Page */
.cover-page {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.company-logo {
  max-height: 80px;
  width: auto;
}

/* Table of Contents */
.toc-page .page-title {
  border-bottom: 3px solid #0d6efd;
  padding-bottom: 0.5rem;
}

.toc-item {
  padding: 0.75rem 0;
  border-bottom: 1px dotted #dee2e6;
}

.toc-item:last-child {
  border-bottom: none;
}

.section-number {
  font-weight: bold;
  color: #0d6efd;
  min-width: 30px;
}

/* Content Pages */
.page-header {
  margin-bottom: 2rem;
}

.page-title {
  color: #2c3e50;
  border-bottom: 2px solid #0d6efd;
  padding-bottom: 0.5rem;
}

.page-subtitle {
  margin-top: 0.5rem;
  font-style: italic;
}

/* Executive Summary */
.highlight-card {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  text-align: center;
  border-left: 4px solid #0d6efd;
}

.highlight-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #0d6efd;
}

.highlight-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Chart Placeholder */
.chart-placeholder {
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container {
  text-align: center;
  color: #6c757d;
}

.sample-chart {
  width: 200px;
  height: 150px;
  background: linear-gradient(45deg, #0d6efd, #20c997);
  border-radius: 0.25rem;
}

/* Sample Text */
.sample-text {
  line-height: 1.6;
  color: #495057;
}

/* Content Placeholders */
.content-placeholder {
  margin-top: 1rem;
}

.placeholder-line {
  height: 1rem;
  background: #e9ecef;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.placeholder-line.long {
  width: 100%;
}

.placeholder-line.medium {
  width: 75%;
}

.placeholder-line.short {
  width: 50%;
}

/* Layout Preview */
.layout-preview {
  padding: 2rem;
}

.layout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.layout-page {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.page-wireframe {
  aspect-ratio: 8.5 / 11;
  padding: 1rem;
  background: white;
}

.wireframe-header {
  height: 20px;
  background: #dee2e6;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.wireframe-block {
  height: 40px;
  background: #e9ecef;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.wireframe-block.small {
  height: 20px;
  width: 60%;
}

.wireframe-block.medium {
  height: 60px;
  width: 80%;
}

.page-label {
  padding: 0.5rem;
  background: #f8f9fa;
  text-align: center;
  font-size: 0.75rem;
  color: #6c757d;
}

/* PDF Preview */
.pdf-preview {
  height: 100%;
}

.pdf-viewer {
  height: 100%;
  background: white;
}

.pdf-embed iframe {
  border: none;
  height: calc(100vh - 120px);
}

/* Loading and Error States */
.preview-loading,
.preview-error {
  background: white;
}

/* Responsive */
@media (max-width: 768px) {
  .preview-content {
    padding: 1rem;
  }
  
  .preview-page {
    padding: 0.5in;
  }
  
  .layout-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>