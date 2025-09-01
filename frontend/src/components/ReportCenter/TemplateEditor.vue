<template>
  <div class="template-editor">
    <!-- Header -->
    <div class="editor-header bg-white border-bottom p-3 mb-4">
      <div class="row align-items-center">
        <div class="col-md-6">
          <h4 class="mb-1">{{ isEditing ? 'Edit Template' : 'Create New Template' }}</h4>
          <small class="text-muted">Design and customize your report template</small>
        </div>
        <div class="col-md-6 text-end">
          <button @click="handlePreview" class="btn btn-outline-primary me-2">
            <i class="fas fa-eye me-1"></i>Preview
          </button>
          <button @click="handleSave" class="btn btn-success me-2" :disabled="!isValid || isSaving">
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="fas fa-save me-1"></i>
            {{ isSaving ? 'Saving...' : 'Save Template' }}
          </button>
          <button @click="handleCancel" class="btn btn-outline-secondary">
            <i class="fas fa-times me-1"></i>Cancel
          </button>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Template Properties Panel -->
      <div class="col-lg-3">
        <div class="card h-100">
          <div class="card-header">
            <h6 class="mb-0">Template Properties</h6>
          </div>
          <div class="card-body">
            <!-- Basic Information -->
            <div class="mb-3">
              <label class="form-label">Template Name *</label>
              <input 
                v-model="template.name" 
                type="text" 
                class="form-control"
                placeholder="Enter template name"
                :class="{ 'is-invalid': !template.name && showValidation }"
              >
            </div>

            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea 
                v-model="template.description" 
                class="form-control" 
                rows="3"
                placeholder="Template description..."
              ></textarea>
            </div>

            <div class="mb-3">
              <label class="form-label">Category</label>
              <select v-model="template.category" class="form-select">
                <option value="comprehensive">Comprehensive</option>
                <option value="summary">Summary</option>
                <option value="analysis">Analysis</option>
                <option value="comparison">Comparison</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <!-- Template Settings -->
            <hr>
            <h6 class="mb-3">Template Settings</h6>

            <div class="mb-3">
              <div class="form-check">
                <input 
                  id="isPublic" 
                  v-model="template.is_public" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="isPublic" class="form-check-label">Make template public</label>
              </div>
            </div>

            <div class="mb-3">
              <div class="form-check">
                <input 
                  id="isDefault" 
                  v-model="template.is_default" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="isDefault" class="form-check-label">Set as default template</label>
              </div>
            </div>

            <!-- Page Settings -->
            <hr>
            <h6 class="mb-3">Page Settings</h6>

            <div class="mb-3">
              <label class="form-label">Page Size</label>
              <select v-model="template.page_size" class="form-select">
                <option value="letter">Letter (8.5" × 11")</option>
                <option value="a4">A4 (8.27" × 11.7")</option>
                <option value="legal">Legal (8.5" × 14")</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Orientation</label>
              <select v-model="template.orientation" class="form-select">
                <option value="portrait">Portrait</option>
                <option value="landscape">Landscape</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Margins (inches)</label>
              <div class="row g-2">
                <div class="col-6">
                  <input 
                    v-model.number="template.margins.top" 
                    type="number" 
                    class="form-control form-control-sm"
                    placeholder="Top"
                    step="0.1"
                    min="0.5"
                    max="2"
                  >
                </div>
                <div class="col-6">
                  <input 
                    v-model.number="template.margins.bottom" 
                    type="number" 
                    class="form-control form-control-sm"
                    placeholder="Bottom"
                    step="0.1"
                    min="0.5"
                    max="2"
                  >
                </div>
                <div class="col-6">
                  <input 
                    v-model.number="template.margins.left" 
                    type="number" 
                    class="form-control form-control-sm"
                    placeholder="Left"
                    step="0.1"
                    min="0.5"
                    max="2"
                  >
                </div>
                <div class="col-6">
                  <input 
                    v-model.number="template.margins.right" 
                    type="number" 
                    class="form-control form-control-sm"
                    placeholder="Right"
                    step="0.1"
                    min="0.5"
                    max="2"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Library -->
      <div class="col-lg-3">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Available Sections</h6>
            <button @click="showCustomSectionModal = true" class="btn btn-sm btn-outline-primary">
              <i class="fas fa-plus me-1"></i>Custom
            </button>
          </div>
          <div class="card-body p-0">
            <div class="section-library">
              <!-- Search -->
              <div class="p-3 border-bottom">
                <input 
                  v-model="sectionSearch" 
                  type="text" 
                  class="form-control form-control-sm"
                  placeholder="Search sections..."
                >
              </div>

              <!-- Section Categories -->
              <div class="accordion" id="sectionAccordion">
                <div 
                  v-for="(categoryData, category) in filteredSectionLibrary" 
                  :key="category"
                  class="accordion-item border-0"
                >
                  <h2 class="accordion-header">
                    <button 
                      class="accordion-button py-2 px-3"
                      type="button"
                      :data-bs-target="`#collapse-${category}`"
                      :aria-expanded="expandedCategories[category]"
                      @click="toggleCategory(category)"
                    >
                      <small class="fw-medium text-capitalize">{{ category }}</small>
                    </button>
                  </h2>
                  <div 
                    :id="`collapse-${category}`"
                    class="accordion-collapse collapse"
                    :class="{ show: expandedCategories[category] }"
                  >
                    <div class="accordion-body p-0">
                      <div 
                        v-for="section in categoryData.sections" 
                        :key="section.type"
                        class="section-item p-2 border-bottom"
                        draggable="true"
                        @dragstart="handleSectionDragStart($event, section)"
                      >
                        <div class="d-flex align-items-center">
                          <i :class="section.icon" class="me-2 text-muted"></i>
                          <div class="flex-grow-1">
                            <div class="fw-medium small">{{ section.title }}</div>
                            <div class="text-muted" style="font-size: 0.75rem;">{{ section.description }}</div>
                          </div>
                          <button 
                            @click="addSection(section)"
                            class="btn btn-sm btn-outline-primary ms-2"
                            title="Add to template"
                          >
                            <i class="fas fa-plus"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Template Canvas -->
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Template Structure</h6>
            <div class="btn-group btn-group-sm">
              <button 
                @click="canvasView = 'structure'"
                class="btn"
                :class="canvasView === 'structure' ? 'btn-primary' : 'btn-outline-primary'"
              >
                Structure
              </button>
              <button 
                @click="canvasView = 'preview'"
                class="btn"
                :class="canvasView === 'preview' ? 'btn-primary' : 'btn-outline-primary'"
              >
                Preview
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <!-- Structure View -->
            <div v-if="canvasView === 'structure'" class="template-canvas">
              <div 
                ref="sectionsContainer"
                class="sections-container p-3"
                @dragover.prevent
                @drop="handleSectionDrop"
              >
                <div v-if="template.sections.length === 0" class="empty-canvas text-center py-5">
                  <i class="fas fa-plus-circle fa-3x text-muted mb-3"></i>
                  <h6 class="text-muted">No sections added yet</h6>
                  <p class="text-muted small">Drag sections from the library or click the + button to add sections</p>
                </div>

                <div v-else class="sections-list">
                  <div 
                    v-for="(section, index) in template.sections" 
                    :key="section.uid"
                    class="section-block mb-3"
                    :class="{ 'selected': selectedSectionIndex === index }"
                    @click="selectSection(index)"
                  >
                    <div class="section-header d-flex align-items-center p-3 bg-light rounded">
                      <div class="drag-handle me-3 text-muted cursor-move">
                        <i class="fas fa-grip-vertical"></i>
                      </div>
                      <i :class="getSectionIcon(section.type)" class="me-2"></i>
                      <div class="flex-grow-1">
                        <div class="fw-medium">{{ section.title }}</div>
                        <small class="text-muted">{{ getSectionTypeLabel(section.type) }}</small>
                      </div>
                      <div class="section-actions">
                        <button 
                          @click.stop="duplicateSection(index)"
                          class="btn btn-sm btn-outline-secondary me-1"
                          title="Duplicate section"
                        >
                          <i class="fas fa-copy"></i>
                        </button>
                        <button 
                          @click.stop="removeSection(index)"
                          class="btn btn-sm btn-outline-danger"
                          title="Remove section"
                        >
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>

                    <!-- Section Configuration Preview -->
                    <div v-if="selectedSectionIndex === index" class="section-config mt-2 p-3 border rounded">
                      <SectionConfiguration 
                        :section="section"
                        :available-data-sources="availableDataSources"
                        @update-section="updateSection(index, $event)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Preview View -->
            <div v-if="canvasView === 'preview'" class="template-preview">
              <div class="preview-container p-3">
                <ReportPreviewRenderer 
                  :sections="template.sections"
                  :data="sampleData"
                  :settings="template"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Section Modal -->
    <div 
      v-if="showCustomSectionModal" 
      class="modal d-block"
      style="background: rgba(0,0,0,0.5);"
      @click.self="showCustomSectionModal = false"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Custom Section</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showCustomSectionModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Section Title</label>
              <input 
                v-model="customSection.title" 
                type="text" 
                class="form-control"
                placeholder="Enter section title"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Section Type</label>
              <select v-model="customSection.type" class="form-select">
                <option value="text">Text Block</option>
                <option value="html">HTML Content</option>
                <option value="image">Image</option>
                <option value="table">Data Table</option>
                <option value="chart">Chart</option>
                <option value="spacer">Spacer</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Content</label>
              <textarea 
                v-model="customSection.content" 
                class="form-control" 
                rows="4"
                placeholder="Enter section content or configuration..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showCustomSectionModal = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="addCustomSection"
              :disabled="!customSection.title || !customSection.type"
            >
              Add Section
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import Sortable from 'sortablejs'
import { useReportCenterStore } from '@/stores/reportCenterStore'
import SectionConfiguration from './SectionConfiguration.vue'
import ReportPreviewRenderer from './ReportPreviewRenderer.vue'

export default {
  name: 'TemplateEditor',
  components: {
    SectionConfiguration,
    ReportPreviewRenderer
  },
  props: {
    templateId: {
      type: [String, Number],
      default: null
    }
  },
  setup(props) {
    const router = useRouter()
    const reportStore = useReportCenterStore()

    // Reactive data
    const template = ref({
      id: null,
      name: '',
      description: '',
      category: 'custom',
      is_public: false,
      is_default: false,
      page_size: 'letter',
      orientation: 'portrait',
      margins: { top: 1, bottom: 1, left: 1, right: 1 },
      sections: []
    })

    const selectedSectionIndex = ref(null)
    const canvasView = ref('structure')
    const sectionSearch = ref('')
    const showCustomSectionModal = ref(false)
    const isSaving = ref(false)
    const showValidation = ref(false)

    const customSection = ref({
      title: '',
      type: 'text',
      content: ''
    })

    const expandedCategories = ref({
      basic: true,
      financial: false,
      analysis: false,
      layout: false
    })

    // Computed properties
    const isEditing = computed(() => !!props.templateId)

    const isValid = computed(() => {
      return template.value.name && template.value.name.trim().length > 0
    })

    const sectionLibrary = computed(() => ({
      basic: {
        sections: [
          {
            type: 'cover_page',
            title: 'Cover Page',
            description: 'Title page with client info',
            icon: 'fas fa-file-alt'
          },
          {
            type: 'table_of_contents',
            title: 'Table of Contents',
            description: 'Automatic TOC generation',
            icon: 'fas fa-list-ul'
          },
          {
            type: 'executive_summary',
            title: 'Executive Summary',
            description: 'High-level overview',
            icon: 'fas fa-clipboard-list'
          },
          {
            type: 'text_block',
            title: 'Text Block',
            description: 'Formatted text content',
            icon: 'fas fa-align-left'
          }
        ]
      },
      financial: {
        sections: [
          {
            type: 'scenario_overview',
            title: 'Scenario Overview',
            description: 'Current scenario details',
            icon: 'fas fa-chart-line'
          },
          {
            type: 'financial_timeline',
            title: 'Financial Timeline',
            description: 'Year-by-year projections',
            icon: 'fas fa-calendar-alt'
          },
          {
            type: 'asset_allocation',
            title: 'Asset Allocation',
            description: 'Investment breakdown',
            icon: 'fas fa-pie-chart'
          },
          {
            type: 'income_sources',
            title: 'Income Sources',
            description: 'Retirement income streams',
            icon: 'fas fa-money-bill-wave'
          },
          {
            type: 'tax_analysis',
            title: 'Tax Analysis',
            description: 'Tax projections and strategies',
            icon: 'fas fa-calculator'
          }
        ]
      },
      analysis: {
        sections: [
          {
            type: 'monte_carlo',
            title: 'Monte Carlo Analysis',
            description: 'Success probability charts',
            icon: 'fas fa-dice'
          },
          {
            type: 'sensitivity_analysis',
            title: 'Sensitivity Analysis',
            description: 'Variable impact assessment',
            icon: 'fas fa-sliders-h'
          },
          {
            type: 'scenario_comparison',
            title: 'Scenario Comparison',
            description: 'Side-by-side comparisons',
            icon: 'fas fa-columns'
          },
          {
            type: 'irmaa_analysis',
            title: 'IRMAA Analysis',
            description: 'Medicare premium impact',
            icon: 'fas fa-heartbeat'
          }
        ]
      },
      layout: {
        sections: [
          {
            type: 'page_break',
            title: 'Page Break',
            description: 'Force new page',
            icon: 'fas fa-file-export'
          },
          {
            type: 'spacer',
            title: 'Spacer',
            description: 'Vertical spacing',
            icon: 'fas fa-arrows-alt-v'
          },
          {
            type: 'divider',
            title: 'Divider',
            description: 'Visual separator',
            icon: 'fas fa-minus'
          }
        ]
      }
    }))

    const filteredSectionLibrary = computed(() => {
      if (!sectionSearch.value) return sectionLibrary.value

      const filtered = {}
      const searchTerm = sectionSearch.value.toLowerCase()

      Object.keys(sectionLibrary.value).forEach(category => {
        const sections = sectionLibrary.value[category].sections.filter(section =>
          section.title.toLowerCase().includes(searchTerm) ||
          section.description.toLowerCase().includes(searchTerm)
        )
        
        if (sections.length > 0) {
          filtered[category] = { sections }
        }
      })

      return filtered
    })

    const availableDataSources = computed(() => [
      'client_info',
      'scenario_results',
      'financial_timeline',
      'asset_data',
      'income_data',
      'tax_data',
      'monte_carlo_results'
    ])

    const sampleData = computed(() => ({
      client: {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com'
      },
      scenario: {
        name: 'Retirement Plan 2024',
        retirement_age: 65,
        current_age: 45
      }
    }))

    // Methods
    const loadTemplate = async () => {
      if (!props.templateId) return

      try {
        const templateData = await reportStore.getTemplate(props.templateId)
        Object.assign(template.value, templateData)
      } catch (error) {
        console.error('Error loading template:', error)
        // Handle error - maybe show notification
      }
    }

    const toggleCategory = (category) => {
      expandedCategories.value[category] = !expandedCategories.value[category]
    }

    const selectSection = (index) => {
      selectedSectionIndex.value = selectedSectionIndex.value === index ? null : index
    }

    const addSection = (sectionData) => {
      const newSection = {
        uid: `section_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: sectionData.type,
        title: sectionData.title,
        description: sectionData.description,
        config: getDefaultSectionConfig(sectionData.type)
      }

      template.value.sections.push(newSection)
    }

    const getDefaultSectionConfig = (sectionType) => {
      const defaults = {
        text_block: { content: '', font_size: 12, alignment: 'left' },
        chart: { chart_type: 'line', data_source: 'scenario_results' },
        table: { data_source: 'financial_timeline', columns: [] },
        image: { src: '', width: '100%', alignment: 'center' },
        spacer: { height: 50 },
        page_break: { type: 'always' }
      }
      return defaults[sectionType] || {}
    }

    const updateSection = (index, updatedSection) => {
      template.value.sections[index] = { ...updatedSection }
    }

    const removeSection = (index) => {
      template.value.sections.splice(index, 1)
      if (selectedSectionIndex.value === index) {
        selectedSectionIndex.value = null
      } else if (selectedSectionIndex.value > index) {
        selectedSectionIndex.value--
      }
    }

    const duplicateSection = (index) => {
      const original = template.value.sections[index]
      const duplicate = {
        ...original,
        uid: `section_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: `${original.title} (Copy)`
      }
      template.value.sections.splice(index + 1, 0, duplicate)
    }

    const addCustomSection = () => {
      const newSection = {
        uid: `section_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: customSection.value.type,
        title: customSection.value.title,
        description: 'Custom section',
        config: {
          content: customSection.value.content,
          ...getDefaultSectionConfig(customSection.value.type)
        }
      }

      template.value.sections.push(newSection)
      showCustomSectionModal.value = false
      
      // Reset custom section form
      customSection.value = { title: '', type: 'text', content: '' }
    }

    const handleSectionDragStart = (event, section) => {
      event.dataTransfer.setData('text/plain', JSON.stringify(section))
    }

    const handleSectionDrop = (event) => {
      event.preventDefault()
      try {
        const sectionData = JSON.parse(event.dataTransfer.getData('text/plain'))
        addSection(sectionData)
      } catch (error) {
        console.error('Error handling section drop:', error)
      }
    }

    const getSectionIcon = (sectionType) => {
      const icons = {
        cover_page: 'fas fa-file-alt',
        table_of_contents: 'fas fa-list-ul',
        executive_summary: 'fas fa-clipboard-list',
        text_block: 'fas fa-align-left',
        scenario_overview: 'fas fa-chart-line',
        financial_timeline: 'fas fa-calendar-alt',
        asset_allocation: 'fas fa-pie-chart',
        income_sources: 'fas fa-money-bill-wave',
        tax_analysis: 'fas fa-calculator',
        monte_carlo: 'fas fa-dice',
        sensitivity_analysis: 'fas fa-sliders-h',
        scenario_comparison: 'fas fa-columns',
        irmaa_analysis: 'fas fa-heartbeat',
        page_break: 'fas fa-file-export',
        spacer: 'fas fa-arrows-alt-v',
        divider: 'fas fa-minus'
      }
      return icons[sectionType] || 'fas fa-square'
    }

    const getSectionTypeLabel = (sectionType) => {
      return sectionType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const handleSave = async () => {
      showValidation.value = true
      
      if (!isValid.value) {
        return
      }

      isSaving.value = true
      
      try {
        if (isEditing.value) {
          await reportStore.updateTemplate(props.templateId, template.value)
        } else {
          await reportStore.createTemplate(template.value)
        }
        
        // Navigate back to dashboard
        router.push('/report-center')
      } catch (error) {
        console.error('Error saving template:', error)
        // Handle error - show notification
      } finally {
        isSaving.value = false
      }
    }

    const handlePreview = () => {
      canvasView.value = 'preview'
    }

    const handleCancel = () => {
      router.push('/report-center')
    }

    // Lifecycle
    onMounted(async () => {
      await loadTemplate()
      
      // Initialize sortable for sections
      await nextTick()
      const sectionsContainer = document.querySelector('.sections-list')
      if (sectionsContainer) {
        new Sortable(sectionsContainer, {
          handle: '.drag-handle',
          animation: 150,
          ghostClass: 'sortable-ghost',
          onEnd: (evt) => {
            const item = template.value.sections.splice(evt.oldIndex, 1)[0]
            template.value.sections.splice(evt.newIndex, 0, item)
          }
        })
      }
    })

    return {
      // Data
      template,
      selectedSectionIndex,
      canvasView,
      sectionSearch,
      showCustomSectionModal,
      isSaving,
      showValidation,
      customSection,
      expandedCategories,
      
      // Computed
      isEditing,
      isValid,
      filteredSectionLibrary,
      availableDataSources,
      sampleData,
      
      // Methods
      toggleCategory,
      selectSection,
      addSection,
      updateSection,
      removeSection,
      duplicateSection,
      addCustomSection,
      handleSectionDragStart,
      handleSectionDrop,
      getSectionIcon,
      getSectionTypeLabel,
      handleSave,
      handlePreview,
      handleCancel
    }
  }
}
</script>

<style scoped>
.template-editor {
  min-height: 100vh;
}

.editor-header {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-library {
  max-height: 600px;
  overflow-y: auto;
}

.section-item {
  cursor: grab;
  transition: background-color 0.2s;
}

.section-item:hover {
  background-color: #f8f9fa;
}

.section-item:active {
  cursor: grabbing;
}

.template-canvas {
  min-height: 500px;
}

.sections-container {
  min-height: 400px;
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
  transition: border-color 0.2s;
}

.sections-container:hover {
  border-color: #adb5bd;
}

.empty-canvas {
  color: #6c757d;
}

.section-block {
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  transition: all 0.2s;
  cursor: pointer;
}

.section-block:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.15);
}

.section-block.selected {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,0.25);
}

.drag-handle {
  cursor: move;
}

.section-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.section-block:hover .section-actions {
  opacity: 1;
}

.preview-container {
  max-height: 600px;
  overflow-y: auto;
  background: #f8f9fa;
}

.sortable-ghost {
  opacity: 0.5;
  background: #e9ecef;
}

.cursor-move {
  cursor: move;
}

/* Accordion customization */
.accordion-button:not(.collapsed) {
  background-color: #f8f9fa;
  color: #212529;
}

.accordion-button:focus {
  box-shadow: none;
}

/* Modal styling */
.modal {
  z-index: 1060;
}

.modal-content {
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
}
</style>