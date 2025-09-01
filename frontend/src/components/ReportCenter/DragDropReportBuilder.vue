<template>
  <div class="modal fade" id="dragDropReportBuilderModal" tabindex="-1" aria-labelledby="dragDropReportBuilderModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title" id="dragDropReportBuilderModalLabel">
            <i class="bi-magic me-2"></i>{{ isEditing ? 'Edit Report' : 'Build Your Report' }}
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body p-0">
          <div class="report-builder-container h-100">
            <!-- Builder Toolbar -->
            <div class="builder-toolbar bg-light border-bottom">
              <div class="d-flex justify-content-between align-items-center px-3 py-2">
                <div class="d-flex align-items-center gap-3">
                  <!-- Report Info -->
                  <div>
                    <h6 class="mb-0">{{ formData.name || 'New Report' }}</h6>
                    <small class="text-muted">
                      {{ selectedClient?.first_name }} {{ selectedClient?.last_name }}
                      {{ selectedTemplate?.name ? `• Template: ${selectedTemplate?.name}` : '' }}
                    </small>
                  </div>
                  
                  <!-- View Mode Toggle -->
                  <div class="btn-group" role="group">
                    <input 
                      type="radio" 
                      class="btn-check" 
                      name="viewMode" 
                      id="builderMode" 
                      value="builder"
                      v-model="viewMode"
                    >
                    <label class="btn btn-outline-secondary btn-sm" for="builderMode">
                      <i class="bi-grid-3x3-gap me-1"></i>Builder
                    </label>
                    
                    <input 
                      type="radio" 
                      class="btn-check" 
                      name="viewMode" 
                      id="previewMode" 
                      value="preview"
                      v-model="viewMode"
                    >
                    <label class="btn btn-outline-secondary btn-sm" for="previewMode">
                      <i class="bi-eye me-1"></i>Preview
                    </label>
                  </div>
                </div>

                <div class="d-flex align-items-center gap-2">
                  <!-- Actions -->
                  <button class="btn btn-sm btn-outline-primary" @click="saveAsDraft">
                    <i class="bi-save me-1"></i>Save Draft
                  </button>
                  <button class="btn btn-sm btn-success" @click="generateReport" :disabled="reportSections.length === 0">
                    <i class="bi-file-earmark-pdf me-1"></i>Generate PDF
                  </button>
                </div>
              </div>
            </div>

            <div class="builder-main d-flex h-100">
              <!-- Section Library Sidebar -->
              <div class="section-library bg-light border-end" style="width: 280px;">
                <div class="p-3">
                  <h6 class="mb-3">
                    <i class="bi-collection me-2"></i>Section Library
                  </h6>
                  
                  <!-- Search Sections -->
                  <div class="mb-3">
                    <div class="input-group input-group-sm">
                      <span class="input-group-text"><i class="bi-search"></i></span>
                      <input 
                        type="text" 
                        class="form-control" 
                        placeholder="Search sections..."
                        v-model="sectionSearchQuery"
                      >
                    </div>
                  </div>

                  <!-- Section Categories -->
                  <div class="section-categories">
                    <div v-for="category in availableCategories" :key="category.id" class="category-group mb-3">
                      <h6 class="category-title mb-2">
                        <i :class="category.icon" class="me-2"></i>{{ category.name }}
                      </h6>
                      
                      <div class="available-sections">
                        <div 
                          v-for="section in filteredSectionsByCategory(category.id)"
                          :key="section.id"
                          class="section-item draggable"
                          :data-section-id="section.id"
                          @dragstart="onDragStart($event, section)"
                          draggable="true"
                        >
                          <div class="section-preview">
                            <i :class="section.icon" class="section-icon"></i>
                            <div class="section-info">
                              <strong>{{ section.title }}</strong>
                              <small class="d-block text-muted">{{ section.description }}</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Main Builder Area -->
              <div class="builder-workspace flex-grow-1 d-flex flex-column">
                <!-- Builder Mode -->
                <div v-if="viewMode === 'builder'" class="builder-content flex-grow-1">
                  <div class="row h-100 g-0">
                    <!-- Report Canvas -->
                    <div class="col-md-8 border-end">
                      <div class="canvas-area h-100 p-3">
                        <div class="report-canvas">
                          <!-- Drop Zone Header -->
                          <div class="drop-zone-header text-center mb-4">
                            <div class="drop-zone-info">
                              <i class="bi-plus-circle display-1 text-muted mb-2"></i>
                              <h5 v-if="reportSections.length === 0">Start Building Your Report</h5>
                              <p class="text-muted mb-0" v-if="reportSections.length === 0">
                                Drag sections from the library to build your report
                              </p>
                            </div>
                          </div>

                          <!-- Report Sections -->
                          <div 
                            ref="reportCanvas" 
                            class="report-sections"
                            @dragover.prevent
                            @drop="onDrop"
                          >
                            <div 
                              v-for="(section, index) in reportSections" 
                              :key="section.uid"
                              class="report-section"
                              :class="{ 'selected': selectedSectionIndex === index }"
                              @click="selectSection(index)"
                            >
                              <!-- Section Header -->
                              <div class="section-header">
                                <div class="d-flex justify-content-between align-items-center">
                                  <div class="d-flex align-items-center">
                                    <i class="bi-grip-vertical drag-handle me-2 text-muted"></i>
                                    <i :class="section.icon" class="me-2"></i>
                                    <h6 class="mb-0">{{ section.title }}</h6>
                                  </div>
                                  <div class="section-actions">
                                    <button 
                                      class="btn btn-sm btn-outline-secondary me-1"
                                      @click.stop="duplicateSection(index)"
                                      title="Duplicate Section"
                                    >
                                      <i class="bi-files"></i>
                                    </button>
                                    <button 
                                      class="btn btn-sm btn-outline-danger"
                                      @click.stop="removeSection(index)"
                                      title="Remove Section"
                                    >
                                      <i class="bi-trash"></i>
                                    </button>
                                  </div>
                                </div>
                              </div>

                              <!-- Section Content Preview -->
                              <div class="section-content">
                                <SectionPreview 
                                  :section="section" 
                                  :data="sampleData"
                                  :compact="true"
                                />
                              </div>
                            </div>

                            <!-- Drop Zone for Empty Canvas -->
                            <div 
                              v-if="reportSections.length === 0"
                              class="empty-drop-zone"
                              @dragover.prevent
                              @drop="onDrop"
                            >
                              <div class="drop-zone-content">
                                <i class="bi-cloud-arrow-down display-3 text-muted mb-3"></i>
                                <p class="text-muted mb-0">Drop sections here to start building</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Properties Panel -->
                    <div class="col-md-4">
                      <div class="properties-panel h-100" :class="{ 'active': showPropertiesPanel && isMobile }">
                        <div class="panel-header bg-light p-3 border-bottom">
                          <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                              <i class="bi-sliders me-2"></i>Properties
                            </h6>
                            <button 
                              v-if="isMobile" 
                              @click="showPropertiesPanel = false"
                              class="btn btn-sm btn-outline-secondary"
                            >
                              <i class="bi-x"></i>
                            </button>
                          </div>
                        </div>
                        
                        <div class="panel-content p-3">
                          <!-- Report Properties (when no section selected) -->
                          <div v-if="selectedSectionIndex === null" class="report-properties">
                            <h6 class="mb-3">Report Settings</h6>
                            
                            <div class="mb-3">
                              <label class="form-label">Report Name</label>
                              <input 
                                type="text" 
                                class="form-control form-control-sm" 
                                v-model="formData.name"
                                placeholder="Enter report name"
                              >
                            </div>
                            
                            <div class="mb-3">
                              <label class="form-label">Description</label>
                              <textarea 
                                class="form-control form-control-sm" 
                                rows="3"
                                v-model="formData.description"
                                placeholder="Report description"
                              ></textarea>
                            </div>

                            <div class="mb-3">
                              <label class="form-label">Export Format</label>
                              <select class="form-select form-select-sm" v-model="formData.export_format">
                                <option value="pdf">PDF Document</option>
                                <option value="pptx">PowerPoint Presentation</option>
                                <option value="docx">Word Document</option>
                              </select>
                            </div>

                            <div class="report-stats">
                              <h6 class="mb-2">Report Statistics</h6>
                              <div class="stats-grid">
                                <div class="stat-item">
                                  <div class="stat-value">{{ reportSections.length }}</div>
                                  <div class="stat-label">Sections</div>
                                </div>
                                <div class="stat-item">
                                  <div class="stat-value">{{ estimatedPages }}</div>
                                  <div class="stat-label">Pages</div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <!-- Section Properties (when section selected) -->
                          <div v-else-if="selectedSection" class="section-properties">
                            <h6 class="mb-3">{{ selectedSection.title }} Settings</h6>
                            
                            <div class="mb-3">
                              <label class="form-label">Section Title</label>
                              <input 
                                type="text" 
                                class="form-control form-control-sm" 
                                v-model="selectedSection.title"
                                placeholder="Section title"
                              >
                            </div>
                            
                            <div class="mb-3">
                              <label class="form-label">Description</label>
                              <textarea 
                                class="form-control form-control-sm" 
                                rows="2"
                                v-model="selectedSection.description"
                                placeholder="Section description"
                              ></textarea>
                            </div>

                            <!-- Section-specific configuration -->
                            <div class="section-config">
                              <SectionConfiguration 
                                :section="selectedSection"
                                @update="updateSectionConfig"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Preview Mode -->
                <div v-else class="preview-content flex-grow-1">
                  <div class="preview-area p-4">
                    <div class="preview-document mx-auto">
                      <ReportPreviewRenderer 
                        :sections="reportSections"
                        :data="sampleData"
                        :settings="formData"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI Assistant -->
    <AIAssistant 
      :client-id="formData.client_id"
      :scenario-id="formData.scenario_id"
      :report-id="formData.id"
      @content-generated="handleAIContentGenerated"
      @recommendations-applied="handleAIRecommendations"
      @executive-summary-generated="handleExecutiveSummaryGenerated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'
import Sortable from 'sortablejs'
import SectionPreview from './SectionPreview.vue'
import SectionConfiguration from './SectionConfiguration.vue'
import ReportPreviewRenderer from './ReportPreviewRenderer.vue'
import AIAssistant from './AIAssistant.vue'

export default {
  name: 'DragDropReportBuilder',
  components: {
    SectionPreview,
    SectionConfiguration,
    ReportPreviewRenderer,
    AIAssistant
  },
  emits: ['report-created'],
  setup(_, { emit }) {
    const reportStore = useReportCenterStore()

    // State
    const viewMode = ref('builder')
    const selectedSectionIndex = ref(null)
    const sectionSearchQuery = ref('')
    const reportCanvas = ref(null)
    const draggedSection = ref(null)
    const isMobile = ref(window.innerWidth < 768)
    const showPropertiesPanel = ref(false)

    // Form data
    const formData = ref({
      name: 'New Report',
      description: '',
      client_id: '',
      scenario_id: '',
      template_id: null,
      export_format: 'pdf'
    })

    // Report sections (dragged into canvas)
    const reportSections = ref([])

    // Available section categories and types
    const availableCategories = ref([
      {
        id: 'content',
        name: 'Content',
        icon: 'bi-file-text'
      },
      {
        id: 'charts',
        name: 'Charts & Data',
        icon: 'bi-bar-chart'
      },
      {
        id: 'analysis',
        name: 'Analysis',
        icon: 'bi-graph-up'
      },
      {
        id: 'layout',
        name: 'Layout',
        icon: 'bi-layout-text-sidebar'
      }
    ])

    // Available sections library
    const availableSections = ref([
      // Content sections
      {
        id: 'cover',
        category: 'content',
        title: 'Cover Page',
        description: 'Professional cover page with branding',
        icon: 'bi-file-earmark-text',
        type: 'cover',
        config: {
          include_logo: true,
          include_date: true,
          include_client_name: true
        }
      },
      {
        id: 'executive_summary',
        category: 'content',
        title: 'Executive Summary',
        description: 'High-level overview and key findings',
        icon: 'bi-file-earmark-richtext',
        type: 'summary',
        config: {
          bullet_points: true,
          highlight_key_metrics: true
        }
      },
      {
        id: 'table_of_contents',
        category: 'content',
        title: 'Table of Contents',
        description: 'Navigational overview of report sections',
        icon: 'bi-list-ol',
        type: 'toc',
        config: {
          auto_generate: true,
          include_page_numbers: true
        }
      },
      {
        id: 'recommendations',
        category: 'content',
        title: 'Recommendations',
        description: 'Strategic recommendations and action items',
        icon: 'bi-lightbulb',
        type: 'recommendations',
        config: {
          priority_ranking: true,
          include_timeline: true
        }
      },

      // Charts & Data sections
      {
        id: 'asset_allocation_chart',
        category: 'charts',
        title: 'Asset Allocation',
        description: 'Pie chart showing asset distribution',
        icon: 'bi-pie-chart',
        type: 'chart',
        config: {
          chart_type: 'pie',
          data_source: 'assets',
          colors: 'professional'
        }
      },
      {
        id: 'income_projection_chart',
        category: 'charts',
        title: 'Income Projections',
        description: 'Timeline of projected retirement income',
        icon: 'bi-graph-up-arrow',
        type: 'chart',
        config: {
          chart_type: 'line',
          data_source: 'income_projections',
          years: 30
        }
      },
      {
        id: 'asset_timeline_chart',
        category: 'charts',
        title: 'Asset Timeline',
        description: 'Asset growth and depletion over time',
        icon: 'bi-activity',
        type: 'chart',
        config: {
          chart_type: 'area',
          data_source: 'asset_timeline',
          show_projections: true
        }
      },
      {
        id: 'data_table',
        category: 'charts',
        title: 'Financial Data Table',
        description: 'Detailed financial data in table format',
        icon: 'bi-table',
        type: 'data_table',
        config: {
          data_source: 'financial_summary',
          format_currency: true
        }
      },

      // Analysis sections
      {
        id: 'monte_carlo',
        category: 'analysis',
        title: 'Monte Carlo Analysis',
        description: 'Probability analysis of retirement success',
        icon: 'bi-dice-3',
        type: 'monte_carlo',
        config: {
          simulations: 10000,
          confidence_levels: [50, 75, 90]
        }
      },
      {
        id: 'irmaa_analysis',
        category: 'analysis',
        title: 'IRMAA Analysis',
        description: 'Medicare premium impact analysis',
        icon: 'bi-heart-pulse',
        type: 'irmaa',
        config: {
          show_brackets: true,
          projection_years: 20
        }
      },
      {
        id: 'roth_conversion',
        category: 'analysis',
        title: 'Roth Conversion Analysis',
        description: 'Roth conversion strategy and impact',
        icon: 'bi-arrow-repeat',
        type: 'roth',
        config: {
          conversion_years: 10,
          show_tax_impact: true
        }
      },
      {
        id: 'tax_strategy',
        category: 'analysis',
        title: 'Tax Strategy',
        description: 'Tax optimization analysis and recommendations',
        icon: 'bi-receipt',
        type: 'tax_strategy',
        config: {
          include_brackets: true,
          optimization_strategies: true
        }
      },

      // Layout sections
      {
        id: 'page_break',
        category: 'layout',
        title: 'Page Break',
        description: 'Force a new page in the report',
        icon: 'bi-arrow-down-square',
        type: 'page_break',
        config: {}
      },
      {
        id: 'spacer',
        category: 'layout',
        title: 'Spacer',
        description: 'Add white space between sections',
        icon: 'bi-distribute-vertical',
        type: 'spacer',
        config: {
          height: 'medium'
        }
      },
      {
        id: 'two_column',
        category: 'layout',
        title: 'Two Column Layout',
        description: 'Split content into two columns',
        icon: 'bi-columns-gap',
        type: 'layout',
        config: {
          column_ratio: '50-50'
        }
      }
    ])

    // Sample data for preview
    const sampleData = ref({
      client: {
        first_name: 'John',
        last_name: 'Doe',
        age: 58
      },
      assets: [
        { name: '401(k)', value: 450000, type: 'retirement' },
        { name: 'Roth IRA', value: 85000, type: 'retirement' },
        { name: 'Taxable Investments', value: 125000, type: 'taxable' }
      ],
      income_projections: [
        { year: 2024, amount: 75000 },
        { year: 2025, amount: 78000 },
        { year: 2026, amount: 81000 }
      ]
    })

    // Computed properties
    const isEditing = computed(() => !!reportStore.selectedReport)
    const selectedTemplate = computed(() => reportStore.selectedTemplate)
    const selectedClient = computed(() => {
      // Mock client data for now
      return { first_name: 'John', last_name: 'Doe' }
    })

    const selectedSection = computed(() => {
      if (selectedSectionIndex.value !== null) {
        return reportSections.value[selectedSectionIndex.value]
      }
      return null
    })

    const estimatedPages = computed(() => {
      const basePages = 1 // Cover page
      const sectionPages = reportSections.value.length * 0.75
      return Math.ceil(basePages + sectionPages)
    })

    // Methods
    const filteredSectionsByCategory = (categoryId) => {
      let sections = availableSections.value.filter(s => s.category === categoryId)
      
      if (sectionSearchQuery.value) {
        const query = sectionSearchQuery.value.toLowerCase()
        sections = sections.filter(s => 
          s.title.toLowerCase().includes(query) ||
          s.description.toLowerCase().includes(query)
        )
      }
      
      return sections
    }

    const onDragStart = (event, section) => {
      draggedSection.value = section
      event.dataTransfer.setData('text/plain', section.id)
      event.dataTransfer.effectAllowed = 'copy'
    }

    const onDrop = (event) => {
      event.preventDefault()
      
      if (draggedSection.value) {
        addSectionToReport(draggedSection.value)
        draggedSection.value = null
      }
    }

    const addSectionToReport = (sectionTemplate) => {
      const newSection = {
        ...sectionTemplate,
        uid: generateUID(), // Unique ID for this instance
        config: { ...sectionTemplate.config } // Deep copy config
      }
      
      reportSections.value.push(newSection)
      
      // Auto-select the new section
      selectedSectionIndex.value = reportSections.value.length - 1
    }

    const selectSection = (index) => {
      selectedSectionIndex.value = index
      // Show properties panel on mobile when a section is selected
      if (isMobile.value) {
        showPropertiesPanel.value = true
      }
    }

    const removeSection = (index) => {
      reportSections.value.splice(index, 1)
      
      // Adjust selection
      if (selectedSectionIndex.value === index) {
        selectedSectionIndex.value = null
      } else if (selectedSectionIndex.value > index) {
        selectedSectionIndex.value--
      }
    }

    const duplicateSection = (index) => {
      const originalSection = reportSections.value[index]
      const duplicatedSection = {
        ...originalSection,
        uid: generateUID(),
        title: `${originalSection.title} (Copy)`,
        config: { ...originalSection.config }
      }
      
      reportSections.value.splice(index + 1, 0, duplicatedSection)
    }

    const updateSectionConfig = (newConfig) => {
      if (selectedSection.value) {
        selectedSection.value.config = { ...selectedSection.value.config, ...newConfig }
      }
    }

    const generateUID = () => {
      return Math.random().toString(36).substr(2, 9)
    }

    const saveAsDraft = async () => {
      try {
        const reportData = {
          ...formData.value,
          sections: reportSections.value,
          status: 'draft'
        }
        
        const report = await reportStore.createReport(reportData)
        emit('report-created', report)
        
        // Show success message
        console.log('Report saved as draft')
      } catch (error) {
        console.error('Failed to save draft:', error)
      }
    }

    const generateReport = async () => {
      try {
        const reportData = {
          ...formData.value,
          sections: reportSections.value,
          status: 'generating'
        }
        
        const report = await reportStore.createReport(reportData)
        await reportStore.generateReport(report.id, formData.value.export_format)
        
        emit('report-created', report)
        
        // Show success message
        console.log('Report generation started')
      } catch (error) {
        console.error('Failed to generate report:', error)
      }
    }

    // AI Assistant Event Handlers
    const handleAIContentGenerated = (content) => {
      // Create a text section with the AI-generated content
      const newSection = {
        id: 'ai_generated_text',
        category: 'content',
        title: content.section_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        description: `AI-generated ${content.section_type} content`,
        icon: 'bi-robot',
        type: 'text',
        uid: generateUID(),
        config: {
          content: content.content,
          ai_generated: true,
          generated_at: content.generated_at,
          tone: content.tone
        }
      }
      
      addSectionToReport(newSection)
      console.log('AI content added to report')
    }

    const handleAIRecommendations = (recommendations) => {
      // Apply slide recommendations by adding sections in recommended order
      const sectionMapping = {
        'cover': availableSections.value.find(s => s.id === 'cover'),
        'executive_summary': availableSections.value.find(s => s.id === 'executive_summary'),
        'current_snapshot': availableSections.value.find(s => s.id === 'data_table'),
        'income_timeline': availableSections.value.find(s => s.id === 'income_projection_chart'),
        'asset_allocation': availableSections.value.find(s => s.id === 'asset_allocation_chart'),
        'monte_carlo': availableSections.value.find(s => s.id === 'monte_carlo'),
        'tax_strategy': availableSections.value.find(s => s.id === 'tax_strategy'),
        'irmaa_analysis': availableSections.value.find(s => s.id === 'irmaa_analysis'),
        'roth_conversion': availableSections.value.find(s => s.id === 'roth_conversion'),
        'recommendations': availableSections.value.find(s => s.id === 'recommendations'),
        'next_steps': availableSections.value.find(s => s.id === 'recommendations')
      }
      
      recommendations.forEach(rec => {
        const sectionTemplate = sectionMapping[rec.slide_type]
        if (sectionTemplate) {
          addSectionToReport(sectionTemplate)
        }
      })
      
      console.log(`Applied ${recommendations.length} AI recommendations`)
    }

    const handleExecutiveSummaryGenerated = (summary) => {
      // Find and update executive summary section or create new one
      const summaryIndex = reportSections.value.findIndex(s => s.id === 'executive_summary' || s.type === 'summary')
      
      if (summaryIndex > -1) {
        // Update existing summary section
        reportSections.value[summaryIndex].config = {
          ...reportSections.value[summaryIndex].config,
          ai_generated_content: summary.summary,
          ai_confidence: summary.confidence,
          generated_at: summary.generated_at
        }
      } else {
        // Create new executive summary section
        const summarySection = {
          ...availableSections.value.find(s => s.id === 'executive_summary'),
          uid: generateUID(),
          config: {
            ...availableSections.value.find(s => s.id === 'executive_summary').config,
            ai_generated_content: summary.summary,
            ai_confidence: summary.confidence,
            generated_at: summary.generated_at
          }
        }
        
        // Insert at the beginning (after cover if it exists)
        const coverIndex = reportSections.value.findIndex(s => s.type === 'cover')
        const insertIndex = coverIndex >= 0 ? coverIndex + 1 : 0
        reportSections.value.splice(insertIndex, 0, summarySection)
      }
      
      console.log('Executive summary generated and applied')
    }

    // Handle window resize for responsive behavior
    const handleResize = () => {
      isMobile.value = window.innerWidth < 768
    }

    // Setup drag-and-drop sorting for report sections
    onMounted(async () => {
      await nextTick()
      
      // Add resize listener
      window.addEventListener('resize', handleResize)
      
      if (reportCanvas.value) {
        new Sortable(reportCanvas.value, {
          handle: '.drag-handle',
          animation: 150,
          ghostClass: 'sortable-ghost',
          chosenClass: 'sortable-chosen',
          dragClass: 'sortable-drag',
          // Enable touch support
          forceFallback: 'ontouchstart' in window,
          fallbackTolerance: 3,
          touchStartThreshold: 3,
          onEnd: (evt) => {
            const { oldIndex, newIndex } = evt
            if (oldIndex !== newIndex) {
              const movedSection = reportSections.value.splice(oldIndex, 1)[0]
              reportSections.value.splice(newIndex, 0, movedSection)
              
              // Adjust selection
              if (selectedSectionIndex.value === oldIndex) {
                selectedSectionIndex.value = newIndex
              } else if (selectedSectionIndex.value > oldIndex && selectedSectionIndex.value <= newIndex) {
                selectedSectionIndex.value--
              } else if (selectedSectionIndex.value < oldIndex && selectedSectionIndex.value >= newIndex) {
                selectedSectionIndex.value++
              }
            }
          }
        })
      }
      
      // Cleanup on unmount
      return () => {
        window.removeEventListener('resize', handleResize)
      }
    })

    return {
      // Data
      viewMode,
      selectedSectionIndex,
      sectionSearchQuery,
      reportCanvas,
      formData,
      reportSections,
      availableCategories,
      availableSections,
      sampleData,
      isMobile,
      showPropertiesPanel,

      // Computed
      isEditing,
      selectedTemplate,
      selectedClient,
      selectedSection,
      estimatedPages,

      // Methods
      filteredSectionsByCategory,
      onDragStart,
      onDrop,
      addSectionToReport,
      selectSection,
      removeSection,
      duplicateSection,
      updateSectionConfig,
      saveAsDraft,
      generateReport,
      
      // AI Methods
      handleAIContentGenerated,
      handleAIRecommendations,
      handleExecutiveSummaryGenerated
    }
  }
}
</script>

<style scoped>
.report-builder-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.builder-toolbar {
  flex-shrink: 0;
  border-bottom: 2px solid #e9ecef;
}

.builder-main {
  flex-grow: 1;
  overflow: hidden;
}

.section-library {
  flex-shrink: 0;
  overflow-y: auto;
}

.section-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: grab;
  transition: all 0.2s;
}

.section-item:hover {
  border-color: #0d6efd;
  box-shadow: 0 2px 4px rgba(13, 110, 253, 0.1);
}

.section-item:active {
  cursor: grabbing;
}

.section-preview {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.section-icon {
  color: #6c757d;
  font-size: 1.1rem;
  margin-top: 2px;
}

.section-info {
  flex-grow: 1;
  min-width: 0;
}

.section-info strong {
  font-size: 0.875rem;
  line-height: 1.2;
}

.section-info small {
  font-size: 0.75rem;
  line-height: 1.3;
}

.builder-workspace {
  overflow: hidden;
}

.canvas-area {
  overflow-y: auto;
  background: #f8f9fa;
}

.report-canvas {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-height: 500px;
}

.drop-zone-header {
  padding: 3rem 1rem;
}

.report-sections {
  min-height: 400px;
  padding: 1rem;
}

.report-section {
  border: 2px solid #e9ecef;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  background: white;
  transition: all 0.3s;
  cursor: pointer;
}

.report-section:hover {
  border-color: #0d6efd;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.report-section.selected {
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}

.section-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 0.5rem 0.5rem 0 0;
}

.drag-handle {
  cursor: grab;
}

.drag-handle:active {
  cursor: grabbing;
}

.section-content {
  padding: 1rem;
}

.empty-drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
  padding: 3rem 1rem;
  text-align: center;
  margin: 2rem 0;
  transition: all 0.3s;
}

.empty-drop-zone:hover {
  border-color: #0d6efd;
  background: rgba(13, 110, 253, 0.05);
}

.properties-panel {
  background: white;
  border-left: 1px solid #e9ecef;
}

.panel-content {
  overflow-y: auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #0d6efd;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.preview-content {
  overflow-y: auto;
  background: #f8f9fa;
}

.preview-document {
  max-width: 800px;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 0.5rem;
}

/* Sortable.js styles */
.sortable-ghost {
  opacity: 0.5;
  transform: rotate(2deg);
}

.sortable-chosen {
  cursor: grabbing;
}

.sortable-drag {
  transform: rotate(5deg);
}

/* Responsive design */
@media (max-width: 1200px) {
  .builder-main {
    flex-direction: column;
  }
  
  .section-library {
    width: 100% !important;
    max-height: 200px;
    border-bottom: 1px solid #e9ecef;
    border-right: none;
  }
  
  .builder-content .row {
    flex-direction: column;
  }
  
  .builder-content .col-md-8,
  .builder-content .col-md-4 {
    width: 100%;
    max-width: 100%;
  }
  
  .properties-panel {
    border-left: none;
    border-top: 1px solid #e9ecef;
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0;
  }
  
  .builder-toolbar {
    padding: 0.5rem;
  }
  
  .builder-toolbar .d-flex {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .section-library {
    width: 100% !important;
    max-height: 150px;
  }
  
  .section-categories {
    display: flex;
    overflow-x: auto;
    gap: 1rem;
    padding-bottom: 0.5rem;
  }
  
  .category-group {
    min-width: 200px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .report-canvas {
    padding: 0.5rem;
  }
  
  .section-header {
    font-size: 0.875rem;
  }
  
  .section-actions button {
    padding: 0.25rem 0.5rem;
  }
  
  .preview-document {
    padding: 0.5rem;
  }
  
  /* Touch-friendly drag handles */
  .drag-handle {
    padding: 0.5rem;
    font-size: 1.25rem;
  }
  
  /* Optimize for touch interactions */
  .section-item {
    padding: 1rem;
    margin-bottom: 0.75rem;
  }
  
  .report-section {
    margin-bottom: 0.75rem;
  }
  
  /* Responsive text sizing */
  h5, h6 {
    font-size: 1rem;
  }
  
  .form-label {
    font-size: 0.875rem;
  }
  
  /* Mobile-optimized buttons */
  .btn-sm {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
  }
}

@media (max-width: 576px) {
  /* Ultra-mobile optimization */
  .builder-toolbar .btn-group {
    width: 100%;
  }
  
  .builder-toolbar .btn {
    flex: 1;
  }
  
  .section-library {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: white;
    border-top: 2px solid #0d6efd;
    transform: translateY(calc(100% - 40px));
    transition: transform 0.3s ease;
  }
  
  .section-library:hover,
  .section-library:focus-within {
    transform: translateY(0);
  }
  
  .section-library::before {
    content: "↑ Drag sections from here";
    display: block;
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    background: #0d6efd;
    color: white;
    padding: 0.25rem 1rem;
    border-radius: 0.25rem 0.25rem 0 0;
    font-size: 0.75rem;
  }
  
  /* Fullscreen preview on mobile */
  .preview-content {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 2000;
    background: white;
  }
  
  /* Simplified properties panel on mobile */
  .properties-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    max-height: 50vh;
    transform: translateY(100%);
    transition: transform 0.3s ease;
  }
  
  .properties-panel.active {
    transform: translateY(0);
  }
}

/* Touch and accessibility improvements */
@media (hover: none) and (pointer: coarse) {
  /* Touch devices */
  .section-item,
  .report-section {
    min-height: 60px;
    touch-action: none;
  }
  
  .drag-handle {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .section-actions button {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>