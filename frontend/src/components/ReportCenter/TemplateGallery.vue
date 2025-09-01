<template>
  <div class="modal fade" id="templateGalleryModal" tabindex="-1" aria-labelledby="templateGalleryModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="templateGalleryModalLabel">
            <i class="bi-collection me-2"></i>Template Gallery
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body">
          <!-- Search and Filter Bar -->
          <div class="row mb-4">
            <div class="col-md-8">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi-search"></i>
                </span>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search templates..."
                  v-model="searchQuery"
                >
              </div>
            </div>
            <div class="col-md-4">
              <select class="form-select" v-model="selectedType">
                <option value="">All Types</option>
                <option value="comprehensive">Comprehensive Report</option>
                <option value="retirement_analysis">Retirement Analysis</option>
                <option value="tax_planning">Tax Planning</option>
                <option value="estate_planning">Estate Planning</option>
                <option value="investment_review">Investment Review</option>
                <option value="monte_carlo">Monte Carlo Analysis</option>
              </select>
            </div>
          </div>

          <!-- Filter Tabs -->
          <ul class="nav nav-tabs mb-4" role="tablist">
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'all' }"
                @click="activeTab = 'all'"
                type="button"
              >
                All Templates ({{ filteredTemplates.length }})
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'public' }"
                @click="activeTab = 'public'"
                type="button"
              >
                Public Templates ({{ publicTemplates.length }})
              </button>
            </li>
            <li class="nav-item" role="presentation">
              <button 
                class="nav-link" 
                :class="{ active: activeTab === 'my' }"
                @click="activeTab = 'my'"
                type="button"
              >
                My Templates ({{ myTemplates.length }})
              </button>
            </li>
          </ul>

          <!-- Loading State -->
          <div v-if="templateLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading templates...</span>
            </div>
            <p class="text-muted mt-2">Loading templates...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="templateError" class="alert alert-danger" role="alert">
            <i class="bi-exclamation-triangle me-2"></i>
            <strong>Error:</strong> {{ templateError }}
            <button class="btn btn-sm btn-outline-danger ms-2" @click="retryLoad">
              <i class="bi-arrow-clockwise me-1"></i>Retry
            </button>
          </div>

          <!-- Templates Grid -->
          <div v-else-if="displayedTemplates.length > 0" class="row">
            <div 
              v-for="template in displayedTemplates" 
              :key="template.id"
              class="col-md-6 col-lg-4 mb-4"
            >
              <div class="card template-card h-100" :class="{ 'border-primary': selectedTemplate?.id === template.id }">
                <!-- Template Preview -->
                <div class="template-preview">
                  <img 
                    :src="template.preview_image || '/images/template-placeholder.png'" 
                    class="card-img-top"
                    :alt="template.name"
                    @error="handleImageError"
                  >
                  <div class="template-overlay">
                    <button 
                      class="btn btn-primary btn-sm"
                      @click="previewTemplate(template)"
                      title="Preview Template"
                    >
                      <i class="bi-eye"></i>
                    </button>
                  </div>
                </div>

                <div class="card-body d-flex flex-column">
                  <!-- Template Header -->
                  <div class="mb-2">
                    <h6 class="card-title mb-1">{{ template.name }}</h6>
                    <div class="d-flex align-items-center gap-2 mb-2">
                      <span class="badge" :class="{
                        'bg-success': template.template_type === 'comprehensive',
                        'bg-info': template.template_type === 'retirement_analysis',
                        'bg-warning': template.template_type === 'tax_planning',
                        'bg-primary': template.template_type === 'estate_planning',
                        'bg-secondary': template.template_type === 'investment_review',
                        'bg-danger': template.template_type === 'monte_carlo'
                      }">
                        {{ getTypeLabel(template.template_type) }}
                      </span>
                      <span v-if="template.is_public" class="badge bg-light text-dark">
                        <i class="bi-globe2 me-1"></i>Public
                      </span>
                      <span v-else class="badge bg-dark">
                        <i class="bi-lock me-1"></i>Private
                      </span>
                    </div>
                  </div>

                  <!-- Template Description -->
                  <p class="card-text text-muted small flex-grow-1">
                    {{ template.description || 'No description available.' }}
                  </p>

                  <!-- Template Stats -->
                  <div class="template-stats mb-3">
                    <div class="row text-center">
                      <div class="col-4">
                        <small class="text-muted d-block">Sections</small>
                        <strong>{{ template.sections?.length || 0 }}</strong>
                      </div>
                      <div class="col-4">
                        <small class="text-muted d-block">Pages</small>
                        <strong>{{ template.estimated_pages || 'N/A' }}</strong>
                      </div>
                      <div class="col-4">
                        <small class="text-muted d-block">Uses</small>
                        <strong>{{ template.usage_count || 0 }}</strong>
                      </div>
                    </div>
                  </div>

                  <!-- Template Actions -->
                  <div class="template-actions mt-auto">
                    <div class="d-grid gap-2">
                      <button 
                        class="btn btn-primary"
                        @click="selectAndUseTemplate(template)"
                      >
                        <i class="bi-file-plus me-2"></i>Use Template
                      </button>
                      <div class="btn-group">
                        <button 
                          class="btn btn-outline-secondary btn-sm"
                          @click="previewTemplate(template)"
                          title="Preview"
                        >
                          <i class="bi-eye"></i>
                        </button>
                        <button 
                          class="btn btn-outline-secondary btn-sm"
                          @click="duplicateTemplate(template)"
                          title="Duplicate"
                        >
                          <i class="bi-files"></i>
                        </button>
                        <button 
                          v-if="canEditTemplate(template)"
                          class="btn btn-outline-secondary btn-sm"
                          @click="editTemplate(template)"
                          title="Edit"
                        >
                          <i class="bi-pencil"></i>
                        </button>
                        <button 
                          v-if="canDeleteTemplate(template)"
                          class="btn btn-outline-danger btn-sm"
                          @click="deleteTemplate(template)"
                          title="Delete"
                        >
                          <i class="bi-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-5">
            <i class="bi-collection display-1 text-muted mb-3"></i>
            <h5>No Templates Found</h5>
            <p class="text-muted">
              {{ searchQuery || selectedType ? 'Try adjusting your search criteria.' : 'No templates available yet.' }}
            </p>
            <button v-if="searchQuery || selectedType" class="btn btn-primary" @click="clearFilters">
              <i class="bi-x-circle me-2"></i>Clear Filters
            </button>
          </div>

          <!-- Pagination -->
          <nav v-if="templatesPagination.total > templatesPagination.pageSize" aria-label="Template pagination">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: !templatesPagination.hasPrevious }">
                <button class="page-link" @click="previousPage" :disabled="!templatesPagination.hasPrevious">
                  <i class="bi-chevron-left"></i>
                </button>
              </li>
              <li class="page-item active">
                <span class="page-link">
                  {{ templatesPagination.page }} of {{ Math.ceil(templatesPagination.total / templatesPagination.pageSize) }}
                </span>
              </li>
              <li class="page-item" :class="{ disabled: !templatesPagination.hasNext }">
                <button class="page-link" @click="nextPage" :disabled="!templatesPagination.hasNext">
                  <i class="bi-chevron-right"></i>
                </button>
              </li>
            </ul>
          </nav>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="bi-x-circle me-2"></i>Close
          </button>
          <button 
            v-if="selectedTemplate"
            type="button" 
            class="btn btn-primary"
            @click="useSelectedTemplate"
          >
            <i class="bi-check-circle me-2"></i>Use Selected Template
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch, onMounted } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'TemplateGallery',
  emits: ['template-selected', 'template-preview'],
  setup(_, { emit }) {
    const reportStore = useReportCenterStore()
    const authStore = useAuthStore()

    // Reactive data
    const searchQuery = ref('')
    const selectedType = ref('')
    const activeTab = ref('all')

    // Computed properties from store
    const templates = computed(() => reportStore.templates)
    const templateLoading = computed(() => reportStore.templateLoading)
    const templateError = computed(() => reportStore.templateError)
    const templatesPagination = computed(() => reportStore.templatesPagination)
    const selectedTemplate = computed(() => reportStore.selectedTemplate)
    const publicTemplates = computed(() => reportStore.publicTemplates)
    const myTemplates = computed(() => reportStore.myTemplates)

    // Filter templates based on search and type
    const filteredTemplates = computed(() => {
      let filtered = templates.value

      // Apply tab filter
      if (activeTab.value === 'public') {
        filtered = publicTemplates.value
      } else if (activeTab.value === 'my') {
        filtered = myTemplates.value
      }

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(template => 
          template.name.toLowerCase().includes(query) ||
          template.description?.toLowerCase().includes(query) ||
          template.template_type.toLowerCase().includes(query)
        )
      }

      // Apply type filter
      if (selectedType.value) {
        filtered = filtered.filter(template => template.template_type === selectedType.value)
      }

      return filtered
    })

    const displayedTemplates = computed(() => filteredTemplates.value)

    // Methods
    const getTypeLabel = (type) => {
      const labels = {
        'comprehensive': 'Comprehensive',
        'retirement_analysis': 'Retirement',
        'tax_planning': 'Tax Planning',
        'estate_planning': 'Estate',
        'investment_review': 'Investment',
        'monte_carlo': 'Monte Carlo'
      }
      return labels[type] || type
    }

    const canEditTemplate = (template) => {
      return template.created_by === authStore.user?.id || authStore.isAdminUser
    }

    const canDeleteTemplate = (template) => {
      return template.created_by === authStore.user?.id || authStore.isAdminUser
    }

    const handleImageError = (event) => {
      event.target.src = '/images/template-placeholder.png'
    }

    const selectAndUseTemplate = (template) => {
      reportStore.selectTemplate(template)
      emit('template-selected', template)
      // Close modal
      const modal = document.getElementById('templateGalleryModal')
      const bsModal = window.bootstrap.Modal.getInstance(modal)
      bsModal?.hide()
    }

    const useSelectedTemplate = () => {
      if (selectedTemplate.value) {
        emit('template-selected', selectedTemplate.value)
        // Close modal
        const modal = document.getElementById('templateGalleryModal')
        const bsModal = window.bootstrap.Modal.getInstance(modal)
        bsModal?.hide()
      }
    }

    const previewTemplate = (template) => {
      reportStore.selectTemplate(template)
      emit('template-preview', template)
    }

    const duplicateTemplate = async (template) => {
      try {
        await reportStore.duplicateTemplate(template.id)
      } catch (error) {
        console.error('Failed to duplicate template:', error)
      }
    }

    const editTemplate = (template) => {
      reportStore.selectTemplate(template)
      // Emit edit event or navigate to edit page
      console.log('Edit template:', template.id)
    }

    const deleteTemplate = async (template) => {
      if (confirm(`Are you sure you want to delete "${template.name}"?`)) {
        try {
          await reportStore.deleteTemplate(template.id)
        } catch (error) {
          console.error('Failed to delete template:', error)
        }
      }
    }

    const retryLoad = async () => {
      try {
        await reportStore.fetchTemplates()
      } catch (error) {
        console.error('Failed to retry load:', error)
      }
    }

    const clearFilters = () => {
      searchQuery.value = ''
      selectedType.value = ''
      activeTab.value = 'all'
    }

    const previousPage = () => {
      if (templatesPagination.value.hasPrevious) {
        reportStore.setTemplatesPage(templatesPagination.value.page - 1)
      }
    }

    const nextPage = () => {
      if (templatesPagination.value.hasNext) {
        reportStore.setTemplatesPage(templatesPagination.value.page + 1)
      }
    }

    // Watch for changes in filters to reset pagination
    watch([searchQuery, selectedType, activeTab], () => {
      reportStore.setTemplatesPage(1)
    })

    // Modal management
    onMounted(() => {
      // Watch store state to show/hide modal
      watch(() => reportStore.showTemplateGallery, (show) => {
        const modal = document.getElementById('templateGalleryModal')
        if (modal && show) {
          const bootstrapModal = new window.bootstrap.Modal(modal)
          bootstrapModal.show()
        }
      }, { immediate: true })

      // Reset store state when modal is hidden
      const modal = document.getElementById('templateGalleryModal')
      if (modal) {
        modal.addEventListener('hidden.bs.modal', () => {
          reportStore.hideTemplateGalleryModal()
          clearFilters()
        })
      }
    })

    return {
      // Data
      searchQuery,
      selectedType,
      activeTab,

      // Computed
      templates,
      templateLoading,
      templateError,
      templatesPagination,
      selectedTemplate,
      publicTemplates,
      myTemplates,
      filteredTemplates,
      displayedTemplates,

      // Methods
      getTypeLabel,
      canEditTemplate,
      canDeleteTemplate,
      handleImageError,
      selectAndUseTemplate,
      useSelectedTemplate,
      previewTemplate,
      duplicateTemplate,
      editTemplate,
      deleteTemplate,
      retryLoad,
      clearFilters,
      previousPage,
      nextPage
    }
  }
}
</script>

<style scoped>
.template-card {
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.template-preview {
  position: relative;
  overflow: hidden;
}

.template-preview img {
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s;
}

.template-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.template-preview:hover .template-overlay {
  opacity: 1;
}

.template-preview:hover img {
  transform: scale(1.05);
}

.template-stats {
  border-top: 1px solid #e9ecef;
  border-bottom: 1px solid #e9ecef;
  padding: 0.5rem 0;
}

.template-actions {
  padding-top: 0.5rem;
}

.modal-xl {
  max-width: 1200px;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-color: #0d6efd;
}

.badge {
  font-size: 0.7rem;
}
</style>