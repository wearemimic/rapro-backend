<template>
  <div class="modal fade" id="reportBuilderModal" tabindex="-1" aria-labelledby="reportBuilderModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="reportBuilderModalLabel">
            <i class="bi-file-plus me-2"></i>{{ isEditing ? 'Edit Report' : 'Create New Report' }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body">
          <!-- Progress Steps -->
          <div class="progress-steps mb-4">
            <div class="row text-center">
              <div class="col-3">
                <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
                  <div class="step-number">1</div>
                  <div class="step-title">Basic Info</div>
                </div>
              </div>
              <div class="col-3">
                <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
                  <div class="step-number">2</div>
                  <div class="step-title">Template</div>
                </div>
              </div>
              <div class="col-3">
                <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
                  <div class="step-number">3</div>
                  <div class="step-title">Content</div>
                </div>
              </div>
              <div class="col-3">
                <div class="step" :class="{ active: currentStep >= 4, completed: currentStep > 4 }">
                  <div class="step-number">4</div>
                  <div class="step-title">Review</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 1: Basic Information -->
          <div v-if="currentStep === 1" class="step-content">
            <div class="row">
              <div class="col-lg-8 mx-auto">
                <div class="card">
                  <div class="card-header">
                    <h6 class="mb-0">
                      <i class="bi-info-circle me-2"></i>Basic Report Information
                    </h6>
                  </div>
                  <div class="card-body">
                    <form @submit.prevent="nextStep">
                      <div class="mb-3">
                        <label for="reportName" class="form-label">Report Name *</label>
                        <input 
                          type="text" 
                          class="form-control" 
                          id="reportName"
                          v-model="formData.name"
                          placeholder="Enter a descriptive name for your report"
                          required
                        >
                      </div>
                      
                      <div class="mb-3">
                        <label for="reportDescription" class="form-label">Description</label>
                        <textarea 
                          class="form-control" 
                          id="reportDescription"
                          v-model="formData.description"
                          rows="3"
                          placeholder="Optional description of what this report covers"
                        ></textarea>
                      </div>

                      <div class="mb-3">
                        <label for="clientSelect" class="form-label">Client</label>
                        <select class="form-select" id="clientSelect" v-model="formData.client_id">
                          <option value="">Select a client (optional)</option>
                          <option v-for="client in availableClients" :key="client.id" :value="client.id">
                            {{ client.first_name }} {{ client.last_name }}
                          </option>
                        </select>
                        <div class="form-text">
                          <span v-if="availableClients.length === 0" class="text-muted">
                            <i class="bi-info-circle me-1"></i>
                            No clients found. You can create a report without selecting a client.
                          </span>
                          <span v-else>
                            Reports can be created without associating them to a specific client
                          </span>
                        </div>
                      </div>

                      <div class="mb-3">
                        <label for="scenarioSelect" class="form-label">Scenario</label>
                        <select 
                          class="form-select" 
                          id="scenarioSelect" 
                          v-model="formData.scenario_id"
                          :disabled="!formData.client_id"
                        >
                          <option value="">Select a scenario (optional)</option>
                          <option v-for="scenario in availableScenarios" :key="scenario.id" :value="scenario.id">
                            {{ scenario.name }}
                          </option>
                        </select>
                        <div class="form-text">
                          Select a client first to see available scenarios
                        </div>
                      </div>

                      <div class="mb-3">
                        <label for="exportFormat" class="form-label">Export Format</label>
                        <select class="form-select" id="exportFormat" v-model="formData.export_format">
                          <option value="pdf">📄 PDF Document</option>
                          <option value="pptx">📊 PowerPoint Presentation</option>
                          <option value="docx">📝 Word Document</option>
                        </select>
                        <div class="form-text">
                          Choose how you want to export the final report
                        </div>
                      </div>

                      <div class="d-flex justify-content-end">
                        <button type="submit" class="btn btn-primary">
                          Next <i class="bi-chevron-right ms-1"></i>
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: Template Selection -->
          <div v-else-if="currentStep === 2" class="step-content">
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">
                  <i class="bi-collection me-2"></i>Choose a Template
                </h6>
              </div>
              <div class="card-body">
                <!-- Template Type Filter -->
                <div class="row mb-3">
                  <div class="col-md-6">
                    <select class="form-select" v-model="templateFilter">
                      <option value="">All Template Types</option>
                      <option value="comprehensive">Comprehensive Report</option>
                      <option value="retirement_analysis">Retirement Analysis</option>
                      <option value="tax_planning">Tax Planning</option>
                      <option value="estate_planning">Estate Planning</option>
                      <option value="investment_review">Investment Review</option>
                      <option value="monte_carlo">Monte Carlo Analysis</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <button class="btn btn-outline-secondary" @click="formData.template_id = null">
                      <i class="bi-x-circle me-2"></i>Start from Scratch
                    </button>
                  </div>
                </div>

                <!-- Template Options -->
                <div class="row">
                  <!-- No Template Option -->
                  <div class="col-md-6 col-lg-4 mb-3">
                    <div 
                      class="card template-option h-100"
                      :class="{ 'border-primary': formData.template_id === null }"
                      @click="formData.template_id = null"
                    >
                      <div class="card-body text-center">
                        <i class="bi-file-blank display-1 text-muted mb-3"></i>
                        <h6 class="card-title">Blank Report</h6>
                        <p class="card-text text-muted small">
                          Start with a blank report and build from scratch
                        </p>
                        <div class="form-check">
                          <input 
                            class="form-check-input" 
                            type="radio" 
                            name="template" 
                            :checked="formData.template_id === null"
                            @change="formData.template_id = null"
                          >
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Available Templates -->
                  <div 
                    v-for="template in filteredTemplatesForBuilder" 
                    :key="template.id"
                    class="col-md-6 col-lg-4 mb-3"
                  >
                    <div 
                      class="card template-option h-100"
                      :class="{ 'border-primary': formData.template_id === template.id }"
                      @click="formData.template_id = template.id"
                    >
                      <div class="template-preview-small">
                        <img 
                          :src="template.preview_image || '/images/template-placeholder.png'" 
                          class="card-img-top"
                          :alt="template.name"
                        >
                      </div>
                      <div class="card-body">
                        <h6 class="card-title">{{ template.name }}</h6>
                        <p class="card-text text-muted small">
                          {{ template.description || 'No description available.' }}
                        </p>
                        <div class="d-flex justify-content-between align-items-center">
                          <span class="badge bg-primary">{{ getTypeLabel(template.template_type) }}</span>
                          <div class="form-check">
                            <input 
                              class="form-check-input" 
                              type="radio" 
                              name="template" 
                              :value="template.id"
                              v-model="formData.template_id"
                            >
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Empty state for templates -->
                <div v-if="filteredTemplatesForBuilder.length === 0" class="text-center py-4">
                  <i class="bi-collection text-muted display-4"></i>
                  <p class="text-muted mt-2">No templates available for the selected type.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Content Configuration (Pre-drag-drop version) -->
          <div v-else-if="currentStep === 3" class="step-content">
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">
                  <i class="bi-list-check me-2"></i>Report Content
                </h6>
              </div>
              <div class="card-body">
                <!-- Selected Template Info -->
                <div v-if="selectedTemplateForBuilder" class="alert alert-info mb-4">
                  <div class="d-flex align-items-center">
                    <i class="bi-info-circle me-2"></i>
                    <div>
                      <strong>Using Template:</strong> {{ selectedTemplateForBuilder.name }}
                      <br>
                      <small>{{ selectedTemplateForBuilder.description }}</small>
                    </div>
                  </div>
                </div>

                <!-- Content Sections Configuration -->
                <div class="row">
                  <div class="col-lg-8">
                    <h6 class="mb-3">Report Sections</h6>
                    
                    <!-- Default sections for blank report or template sections -->
                    <div class="sections-list">
                      <div 
                        v-for="(section, index) in reportSections" 
                        :key="index"
                        class="section-item card mb-3"
                      >
                        <div class="card-body">
                          <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center">
                              <div class="form-check me-3">
                                <input 
                                  class="form-check-input" 
                                  type="checkbox" 
                                  v-model="section.enabled"
                                  :id="`section-${index}`"
                                >
                              </div>
                              <div>
                                <h6 class="mb-1">{{ section.title }}</h6>
                                <small class="text-muted">{{ section.description }}</small>
                              </div>
                            </div>
                            <div class="section-controls">
                              <button 
                                class="btn btn-sm btn-outline-secondary me-1"
                                @click="moveSectionUp(index)"
                                :disabled="index === 0"
                              >
                                <i class="bi-chevron-up"></i>
                              </button>
                              <button 
                                class="btn btn-sm btn-outline-secondary"
                                @click="moveSectionDown(index)"
                                :disabled="index === reportSections.length - 1"
                              >
                                <i class="bi-chevron-down"></i>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Add Custom Section -->
                    <div class="card border-dashed">
                      <div class="card-body text-center">
                        <button class="btn btn-outline-primary" @click="addCustomSection">
                          <i class="bi-plus-circle me-2"></i>Add Custom Section
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Content Preview -->
                  <div class="col-lg-4">
                    <div class="card bg-light">
                      <div class="card-header">
                        <h6 class="mb-0">
                          <i class="bi-eye me-2"></i>Preview
                        </h6>
                      </div>
                      <div class="card-body">
                        <div class="preview-sections">
                          <div 
                            v-for="(section, index) in enabledSections" 
                            :key="index"
                            class="preview-section mb-2"
                          >
                            <div class="d-flex align-items-center">
                              <span class="badge bg-secondary me-2">{{ index + 1 }}</span>
                              <small>{{ section.title }}</small>
                            </div>
                          </div>
                        </div>
                        <hr>
                        <small class="text-muted">
                          <strong>Estimated pages:</strong> {{ estimatedPages }}
                          <br>
                          <strong>Sections:</strong> {{ enabledSections.length }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 4: Review and Create -->
          <div v-else-if="currentStep === 4" class="step-content">
            <div class="card">
              <div class="card-header">
                <h6 class="mb-0">
                  <i class="bi-check-circle me-2"></i>Review & Create Report
                </h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-lg-8">
                    <!-- Report Summary -->
                    <div class="report-summary">
                      <div class="row mb-4">
                        <div class="col-md-6">
                          <h6>Report Details</h6>
                          <table class="table table-sm table-borderless">
                            <tr>
                              <td class="text-muted">Name:</td>
                              <td><strong>{{ formData.name }}</strong></td>
                            </tr>
                            <tr>
                              <td class="text-muted">Description:</td>
                              <td>{{ formData.description || 'None' }}</td>
                            </tr>
                            <tr>
                              <td class="text-muted">Client:</td>
                              <td>{{ selectedClient?.first_name }} {{ selectedClient?.last_name || 'None' }}</td>
                            </tr>
                            <tr>
                              <td class="text-muted">Scenario:</td>
                              <td>{{ selectedScenario?.name || 'None' }}</td>
                            </tr>
                            <tr>
                              <td class="text-muted">Template:</td>
                              <td>{{ selectedTemplateForBuilder?.name || 'Blank Report' }}</td>
                            </tr>
                          </table>
                        </div>
                        <div class="col-md-6">
                          <h6>Content Overview</h6>
                          <table class="table table-sm table-borderless">
                            <tr>
                              <td class="text-muted">Sections:</td>
                              <td><strong>{{ enabledSections.length }}</strong></td>
                            </tr>
                            <tr>
                              <td class="text-muted">Estimated Pages:</td>
                              <td><strong>{{ estimatedPages }}</strong></td>
                            </tr>
                            <tr>
                              <td class="text-muted">Format:</td>
                              <td>
                                <select class="form-select form-select-sm" v-model="formData.export_format">
                                  <option value="pdf">PDF</option>
                                  <option value="docx">Word Document</option>
                                  <option value="pptx">PowerPoint</option>
                                </select>
                              </td>
                            </tr>
                          </table>
                        </div>
                      </div>

                      <!-- Enabled Sections List -->
                      <div class="mb-4">
                        <h6>Report Sections</h6>
                        <div class="sections-preview">
                          <div 
                            v-for="(section, index) in enabledSections" 
                            :key="index"
                            class="d-flex align-items-center mb-2"
                          >
                            <span class="badge bg-primary me-3">{{ index + 1 }}</span>
                            <div>
                              <strong>{{ section.title }}</strong>
                              <br>
                              <small class="text-muted">{{ section.description }}</small>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="col-lg-4">
                    <!-- Action Options -->
                    <div class="card bg-light">
                      <div class="card-header">
                        <h6 class="mb-0">Create Options</h6>
                      </div>
                      <div class="card-body">
                        <div class="mb-3">
                          <div class="form-check">
                            <input 
                              class="form-check-input" 
                              type="radio" 
                              name="createOption" 
                              id="saveDraft"
                              value="draft"
                              v-model="createOption"
                            >
                            <label class="form-check-label" for="saveDraft">
                              <strong>Save as Draft</strong>
                              <br>
                              <small class="text-muted">Save for later editing</small>
                            </label>
                          </div>
                        </div>
                        <div class="mb-3">
                          <div class="form-check">
                            <input 
                              class="form-check-input" 
                              type="radio" 
                              name="createOption" 
                              id="generateNow"
                              value="generate"
                              v-model="createOption"
                            >
                            <label class="form-check-label" for="generateNow">
                              <strong>Generate Now</strong>
                              <br>
                              <small class="text-muted">Create and download immediately</small>
                            </label>
                          </div>
                        </div>
                        <hr>
                        <small class="text-muted">
                          <i class="bi-info-circle me-1"></i>
                          Reports can be regenerated at any time with updated data.
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer with Step Navigation -->
        <div class="modal-footer">
          <div class="d-flex justify-content-between w-100">
            <div>
              <button 
                v-if="currentStep > 1"
                type="button" 
                class="btn btn-outline-secondary"
                @click="previousStep"
              >
                <i class="bi-chevron-left me-1"></i>Previous
              </button>
            </div>
            
            <div>
              <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">
                Cancel
              </button>
              
              <button 
                v-if="currentStep < 4"
                type="button" 
                class="btn btn-primary"
                @click="nextStep"
                :disabled="!canProceed"
              >
                Next <i class="bi-chevron-right ms-1"></i>
              </button>
              
              <button 
                v-else
                type="button" 
                class="btn btn-success"
                @click="createReport"
                :disabled="reportLoading"
              >
                <span v-if="reportLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi-check-circle me-2"></i>
                {{ createOption === 'draft' ? 'Save Draft' : 'Create Report' }}
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
import axios from 'axios'

export default {
  name: 'ReportBuilder',
  emits: ['report-created'],
  setup(_, { emit }) {
    const reportStore = useReportCenterStore()

    // Form state
    const currentStep = ref(1)
    const createOption = ref('draft')
    const templateFilter = ref('')
    
    // Form data
    const formData = ref({
      name: '',
      description: '',
      client_id: '',
      scenario_id: '',
      template_id: null,
      export_format: 'pdf',
      sections: []
    })

    // Client and scenario data
    const availableClients = ref([])
    const availableScenarios = ref([])
    
    // Load clients from API
    const loadClients = async () => {
      try {
        console.log('🔍 Loading clients...')
        const token = localStorage.getItem('token')
        console.log('🔑 Token exists:', !!token)
        const headers = { Authorization: `Bearer ${token}` }
        console.log('📡 Making API call to http://localhost:8000/api/clients/')
        const response = await axios.get('http://localhost:8000/api/clients/', { headers })
        console.log('📥 API Response:', response.status, response.data)
        availableClients.value = response.data || []
        console.log('👥 Available clients count:', availableClients.value.length)
      } catch (error) {
        console.error('❌ Failed to load clients:', error)
        console.error('❌ Error response:', error.response?.data)
        console.error('❌ Error status:', error.response?.status)
        availableClients.value = []
      }
    }
    
    // Load scenarios for a specific client
    const loadScenariosForClient = async (clientId) => {
      if (!clientId) {
        availableScenarios.value = []
        return
      }
      
      try {
        console.log('🔍 Loading scenarios for client ID:', clientId)
        const token = localStorage.getItem('token')
        const headers = { Authorization: `Bearer ${token}` }
        
        // Fetch client detail which includes scenarios
        console.log('📡 Fetching client details with scenarios...')
        const response = await axios.get(`http://localhost:8000/api/clients/${clientId}/`, { headers })
        console.log('📥 Client detail response:', response.data)
        
        const scenarios = response.data?.scenarios || []
        availableScenarios.value = scenarios
        console.log('📋 Available scenarios for client:', scenarios.length, scenarios)
      } catch (error) {
        console.error('❌ Failed to load scenarios for client:', error)
        console.error('❌ Error details:', error.response?.data)
        availableScenarios.value = []
      }
    }
    
    // Default report sections
    const defaultSections = [
      {
        title: 'Executive Summary',
        description: 'High-level overview of financial situation and recommendations',
        enabled: true,
        type: 'executive_summary'
      },
      {
        title: 'Client Information',
        description: 'Basic client demographics and financial profile',
        enabled: true,
        type: 'client_info'
      },
      {
        title: 'Current Financial Position',
        description: 'Assets, liabilities, income, and expenses',
        enabled: true,
        type: 'financial_position'
      },
      {
        title: 'Retirement Projections',
        description: 'Projected retirement income and asset growth',
        enabled: true,
        type: 'retirement_projections'
      },
      {
        title: 'Tax Analysis',
        description: 'Tax implications and optimization strategies',
        enabled: false,
        type: 'tax_analysis'
      },
      {
        title: 'Monte Carlo Analysis',
        description: 'Success probability analysis with various market scenarios',
        enabled: false,
        type: 'monte_carlo'
      },
      {
        title: 'Recommendations',
        description: 'Strategic recommendations and action items',
        enabled: true,
        type: 'recommendations'
      }
    ]

    const reportSections = ref([...defaultSections])

    // Computed properties
    const isEditing = computed(() => !!reportStore.selectedReport)
    const reportLoading = computed(() => reportStore.reportLoading)
    const templates = computed(() => reportStore.templates)
    
    const filteredTemplatesForBuilder = computed(() => {
      if (!templateFilter.value) return templates.value
      return templates.value.filter(t => t.template_type === templateFilter.value)
    })

    const selectedTemplateForBuilder = computed(() => {
      if (!formData.value.template_id) return null
      return templates.value.find(t => t.id === formData.value.template_id)
    })

    const selectedClient = computed(() => {
      if (!formData.value.client_id) return null
      return availableClients.value.find(c => c.id === formData.value.client_id)
    })

    const selectedScenario = computed(() => {
      if (!formData.value.scenario_id) return null
      return availableScenarios.value.find(s => s.id === formData.value.scenario_id)
    })

    const enabledSections = computed(() => {
      return reportSections.value.filter(section => section.enabled)
    })

    const estimatedPages = computed(() => {
      const basePages = 2 // Cover page and table of contents
      const sectionPages = enabledSections.value.length * 1.5 // Average pages per section
      return Math.ceil(basePages + sectionPages)
    })

    const canProceed = computed(() => {
      switch (currentStep.value) {
        case 1:
          return formData.value.name.trim() !== ''
        case 2:
          return true // Template is optional
        case 3:
          return enabledSections.value.length > 0
        case 4:
          return true
        default:
          return false
      }
    })

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

    const nextStep = () => {
      if (canProceed.value && currentStep.value < 4) {
        currentStep.value++
      }
    }

    const previousStep = () => {
      if (currentStep.value > 1) {
        currentStep.value--
      }
    }

    const moveSectionUp = (index) => {
      if (index > 0) {
        const sections = [...reportSections.value]
        const temp = sections[index]
        sections[index] = sections[index - 1]
        sections[index - 1] = temp
        reportSections.value = sections
      }
    }

    const moveSectionDown = (index) => {
      if (index < reportSections.value.length - 1) {
        const sections = [...reportSections.value]
        const temp = sections[index]
        sections[index] = sections[index + 1]
        sections[index + 1] = temp
        reportSections.value = sections
      }
    }

    const addCustomSection = () => {
      const customSection = {
        title: 'Custom Section',
        description: 'Add your own content here',
        enabled: true,
        type: 'custom',
        custom: true
      }
      reportSections.value.push(customSection)
    }

    const createReport = async () => {
      try {
        console.log('🚀 Starting report creation...')
        const reportData = {
          ...formData.value,
          sections: enabledSections.value,
          status: createOption.value === 'draft' ? 'draft' : 'generating'
        }
        console.log('📋 Report data to send:', reportData)

        let report
        if (isEditing.value) {
          console.log('📝 Updating existing report...')
          report = await reportStore.updateReport(reportStore.selectedReport.id, reportData)
        } else {
          console.log('➕ Creating new report...')
          report = await reportStore.createReport(reportData)
        }
        console.log('✅ Report API response:', report)

        // If generate option selected, trigger generation
        if (createOption.value === 'generate') {
          await reportStore.generateReport(report.id, formData.value.export_format)
        }

        console.log('✅ Report created successfully:', report)
        
        // Show success message
        if (createOption.value === 'draft') {
          alert('✅ Report saved as draft successfully!')
        } else {
          alert(`✅ Report created and ${formData.value.export_format.toUpperCase()} generation started!`)
        }
        
        emit('report-created', report)
        
        // Close modal
        const modal = document.getElementById('reportBuilderModal')
        const bsModal = window.bootstrap.Modal.getInstance(modal)
        bsModal?.hide()

        // Reset form
        resetForm()
      } catch (error) {
        console.error('❌ Failed to create report:', error)
        alert('❌ Failed to create report. Please try again.')
      }
    }

    const resetForm = () => {
      currentStep.value = 1
      createOption.value = 'draft'
      templateFilter.value = ''
      formData.value = {
        name: '',
        description: '',
        client_id: '',
        scenario_id: '',
        template_id: null,
        export_format: 'pdf',
        sections: []
      }
      reportSections.value = [...defaultSections]
    }

    // Watch for template changes to update sections
    watch(() => formData.value.template_id, (newTemplateId) => {
      if (newTemplateId && selectedTemplateForBuilder.value?.sections) {
        // Update sections based on template
        reportSections.value = selectedTemplateForBuilder.value.sections.map(section => ({
          ...section,
          enabled: section.enabled !== false
        }))
      } else if (newTemplateId === null) {
        // Reset to default sections for blank report
        reportSections.value = [...defaultSections]
      }
    })

    // Watch for client changes to load scenarios
    watch(() => formData.value.client_id, async (newClientId) => {
      formData.value.scenario_id = '' // Reset scenario selection
      await loadScenariosForClient(newClientId)
    })

    // Modal management
    onMounted(() => {
      // Watch store state to show/hide modal
      watch(() => reportStore.showReportBuilder, async (show) => {
        const modal = document.getElementById('reportBuilderModal')
        if (modal && show) {
          // Load clients when modal opens
          await loadClients()
          const bootstrapModal = new window.bootstrap.Modal(modal)
          bootstrapModal.show()
        }
      }, { immediate: true })

      // Reset store state when modal is hidden
      const modal = document.getElementById('reportBuilderModal')
      if (modal) {
        modal.addEventListener('hidden.bs.modal', () => {
          reportStore.hideReportBuilderModal()
          resetForm()
        })
      }
    })

    return {
      // Data
      currentStep,
      createOption,
      templateFilter,
      formData,
      reportSections,
      availableClients,
      availableScenarios,

      // Computed
      isEditing,
      reportLoading,
      templates,
      filteredTemplatesForBuilder,
      selectedTemplateForBuilder,
      selectedClient,
      selectedScenario,
      enabledSections,
      estimatedPages,
      canProceed,

      // Methods
      getTypeLabel,
      nextStep,
      previousStep,
      moveSectionUp,
      moveSectionDown,
      addCustomSection,
      createReport,
      resetForm
    }
  }
}
</script>

<style scoped>
/* Progress Steps */
.progress-steps .step {
  position: relative;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.progress-steps .step.active,
.progress-steps .step.completed {
  opacity: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-weight: bold;
  transition: all 0.3s;
}

.step.active .step-number {
  background-color: #0d6efd;
  color: white;
}

.step.completed .step-number {
  background-color: #198754;
  color: white;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 500;
}

/* Template Options */
.template-option {
  cursor: pointer;
  transition: all 0.3s;
}

.template-option:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.template-option.border-primary {
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
}

.template-preview-small img {
  height: 120px;
  object-fit: cover;
}

/* Sections */
.section-item {
  border-left: 4px solid #e9ecef;
  transition: border-color 0.3s;
}

.section-item:hover {
  border-left-color: #0d6efd;
}

.border-dashed {
  border: 2px dashed #dee2e6;
  background-color: #f8f9fa;
}

.border-dashed:hover {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

/* Preview */
.preview-section {
  padding: 0.5rem;
  background-color: white;
  border-radius: 0.25rem;
  border: 1px solid #dee2e6;
}

/* Modal sizing */
.modal-xl {
  max-width: 1200px;
}

/* Form styling */
.form-select-sm {
  min-width: 120px;
}
</style>