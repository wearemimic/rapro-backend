<template>
  <div 
    v-if="show" 
    class="modal d-block"
    style="background: rgba(0,0,0,0.5);"
    @click.self="$emit('close')"
  >
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-calendar-plus me-2"></i>
            {{ isEditing ? 'Edit Schedule' : 'Create New Schedule' }}
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            @click="$emit('close')"
          ></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Basic Information -->
            <div class="row mb-4">
              <div class="col-md-8">
                <label class="form-label">Schedule Name *</label>
                <input 
                  v-model="formData.name" 
                  type="text" 
                  class="form-control"
                  placeholder="Enter schedule name..."
                  required
                >
              </div>
              <div class="col-md-4">
                <label class="form-label">Status</label>
                <select v-model="formData.status" class="form-select">
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="disabled">Disabled</option>
                </select>
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label">Description</label>
              <textarea 
                v-model="formData.description" 
                class="form-control" 
                rows="2"
                placeholder="Optional description..."
              ></textarea>
            </div>

            <!-- Template Selection -->
            <div class="mb-4">
              <label class="form-label">Report Template *</label>
              <div class="row">
                <div 
                  v-for="template in availableTemplates" 
                  :key="template.id"
                  class="col-md-4 mb-3"
                >
                  <div class="template-option" :class="{ 'selected': formData.template_id === template.id }">
                    <input 
                      :id="`template-${template.id}`"
                      v-model="formData.template_id" 
                      type="radio" 
                      class="form-check-input"
                      :value="template.id"
                    >
                    <label :for="`template-${template.id}`" class="template-label">
                      <h6>{{ template.name }}</h6>
                      <p class="small text-muted">{{ template.description }}</p>
                      <span class="badge bg-secondary">{{ template.category }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Target Configuration -->
            <div class="mb-4">
              <label class="form-label">Report Target *</label>
              <div class="target-options">
                <div class="form-check mb-2">
                  <input 
                    id="targetSingle" 
                    v-model="formData.targetType" 
                    type="radio" 
                    class="form-check-input"
                    value="single"
                  >
                  <label for="targetSingle" class="form-check-label">Single Client/Scenario</label>
                </div>
                <div class="form-check mb-2">
                  <input 
                    id="targetBulk" 
                    v-model="formData.targetType" 
                    type="radio" 
                    class="form-check-input"
                    value="bulk"
                  >
                  <label for="targetBulk" class="form-check-label">Bulk (Multiple Clients)</label>
                </div>
              </div>

              <!-- Single Target Options -->
              <div v-if="formData.targetType === 'single'" class="mt-3">
                <div class="row">
                  <div class="col-md-6">
                    <label class="form-label">Client</label>
                    <select v-model="formData.client_id" class="form-select" @change="loadClientScenarios">
                      <option value="">Select client...</option>
                      <option 
                        v-for="client in availableClients" 
                        :key="client.id"
                        :value="client.id"
                      >
                        {{ client.first_name }} {{ client.last_name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Scenario (Optional)</label>
                    <select v-model="formData.scenario_id" class="form-select" :disabled="!formData.client_id">
                      <option value="">Use primary scenario</option>
                      <option 
                        v-for="scenario in clientScenarios" 
                        :key="scenario.id"
                        :value="scenario.id"
                      >
                        {{ scenario.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Bulk Target Options -->
              <div v-if="formData.targetType === 'bulk'" class="mt-3">
                <div class="bulk-filter-options">
                  <h6>Client Filters</h6>
                  <div class="row">
                    <div class="col-md-6">
                      <label class="form-label">Created After</label>
                      <input 
                        v-model="formData.client_filter.created_after" 
                        type="date" 
                        class="form-control"
                      >
                    </div>
                    <div class="col-md-6">
                      <label class="form-label">Created Before</label>
                      <input 
                        v-model="formData.client_filter.created_before" 
                        type="date" 
                        class="form-control"
                      >
                    </div>
                  </div>
                  <div class="form-check mt-2">
                    <input 
                      id="hasScenarios" 
                      v-model="formData.client_filter.has_scenarios" 
                      type="checkbox" 
                      class="form-check-input"
                    >
                    <label for="hasScenarios" class="form-check-label">
                      Only clients with scenarios
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Scheduling Configuration -->
            <div class="row mb-4">
              <div class="col-md-4">
                <label class="form-label">Frequency *</label>
                <select v-model="formData.frequency" class="form-select" @change="updateFrequencyConfig">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="yearly">Yearly</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Time *</label>
                <input 
                  v-model="formData.scheduled_time" 
                  type="time" 
                  class="form-control"
                  required
                >
              </div>
              <div class="col-md-4">
                <label class="form-label">Timezone</label>
                <select v-model="formData.timezone" class="form-select">
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                </select>
              </div>
            </div>

            <!-- Frequency-specific Configuration -->
            <div v-if="formData.frequency === 'weekly'" class="mb-4">
              <label class="form-label">Day of Week</label>
              <select v-model="formData.frequency_config.day_of_week" class="form-select">
                <option :value="0">Monday</option>
                <option :value="1">Tuesday</option>
                <option :value="2">Wednesday</option>
                <option :value="3">Thursday</option>
                <option :value="4">Friday</option>
                <option :value="5">Saturday</option>
                <option :value="6">Sunday</option>
              </select>
            </div>

            <div v-if="formData.frequency === 'monthly'" class="mb-4">
              <label class="form-label">Day of Month</label>
              <select v-model="formData.frequency_config.day_of_month" class="form-select">
                <option v-for="day in 31" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>

            <div v-if="formData.frequency === 'custom'" class="mb-4">
              <div class="row">
                <div class="col-md-6">
                  <label class="form-label">Every</label>
                  <input 
                    v-model.number="formData.frequency_config.interval_value" 
                    type="number" 
                    class="form-control"
                    min="1"
                    placeholder="1"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Period</label>
                  <select v-model="formData.frequency_config.interval_type" class="form-select">
                    <option value="days">Days</option>
                    <option value="weeks">Weeks</option>
                    <option value="months">Months</option>
                    <option value="years">Years</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Generation Options -->
            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label">Export Format</label>
                <select v-model="formData.format" class="form-select">
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                  <option value="powerpoint">PowerPoint</option>
                  <option value="both">PDF + PowerPoint</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Page Size (PDF)</label>
                <select v-model="formData.generation_options.page_size" class="form-select">
                  <option value="letter">Letter</option>
                  <option value="a4">A4</option>
                  <option value="legal">Legal</option>
                </select>
              </div>
            </div>

            <!-- Email Configuration -->
            <div class="mb-4">
              <div class="form-check mb-3">
                <input 
                  id="autoEmail" 
                  v-model="formData.auto_email" 
                  type="checkbox" 
                  class="form-check-input"
                >
                <label for="autoEmail" class="form-check-label">
                  <strong>Automatically email reports</strong>
                </label>
              </div>

              <div v-if="formData.auto_email" class="email-config">
                <div class="mb-3">
                  <label class="form-label">Email Recipients *</label>
                  <textarea 
                    v-model="emailRecipientsText" 
                    class="form-control" 
                    rows="3"
                    placeholder="Enter email addresses, one per line..."
                    @input="updateEmailRecipients"
                  ></textarea>
                  <small class="text-muted">Enter one email address per line</small>
                </div>

                <div class="mb-3">
                  <label class="form-label">Email Subject Template</label>
                  <input 
                    v-model="formData.email_subject_template" 
                    type="text" 
                    class="form-control"
                    placeholder="Scheduled Report: {{ schedule.name }}"
                  >
                  <small class="text-muted">Available variables: {{ "{{ client.first_name }}, {{ client.last_name }}, {{ schedule.name }}" }}</small>
                </div>

                <div class="mb-3">
                  <label class="form-label">Email Body Template</label>
                  <textarea 
                    v-model="formData.email_body_template" 
                    class="form-control" 
                    rows="4"
                    placeholder="Please find your scheduled report attached."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- End Conditions -->
            <div class="mb-4">
              <h6>End Conditions (Optional)</h6>
              <div class="row">
                <div class="col-md-6">
                  <label class="form-label">End Date</label>
                  <input 
                    v-model="formData.end_date" 
                    type="date" 
                    class="form-control"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Maximum Runs</label>
                  <input 
                    v-model.number="formData.max_runs" 
                    type="number" 
                    class="form-control"
                    min="1"
                    placeholder="Unlimited"
                  >
                </div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleSubmit"
            :disabled="!isValid || isSaving"
          >
            <span v-if="isSaving" class="spinner-border spinner-border-sm me-1"></span>
            {{ isSaving ? 'Saving...' : (isEditing ? 'Update Schedule' : 'Create Schedule') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/api'

export default {
  name: 'ScheduleFormModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    schedule: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    // Reactive data
    const isSaving = ref(false)
    const availableTemplates = ref([])
    const availableClients = ref([])
    const clientScenarios = ref([])
    const emailRecipientsText = ref('')
    
    const formData = ref({
      name: '',
      description: '',
      status: 'active',
      template_id: null,
      targetType: 'single',
      client_id: null,
      scenario_id: null,
      client_filter: {
        created_after: '',
        created_before: '',
        has_scenarios: false
      },
      frequency: 'weekly',
      frequency_config: {
        day_of_week: 0,
        day_of_month: 1,
        interval_value: 1,
        interval_type: 'days'
      },
      scheduled_time: '09:00',
      timezone: 'UTC',
      format: 'pdf',
      generation_options: {
        page_size: 'letter',
        orientation: 'portrait'
      },
      auto_email: false,
      email_recipients: [],
      email_subject_template: '',
      email_body_template: '',
      end_date: '',
      max_runs: null
    })

    // Computed properties
    const isEditing = computed(() => !!props.schedule)

    const isValid = computed(() => {
      return (
        formData.value.name &&
        formData.value.template_id &&
        formData.value.scheduled_time &&
        (
          (formData.value.targetType === 'single' && formData.value.client_id) ||
          (formData.value.targetType === 'bulk')
        )
      )
    })

    // Methods
    const loadInitialData = async () => {
      try {
        // Load templates
        const templatesResponse = await api.get('/api/report-center/templates/')
        availableTemplates.value = templatesResponse.data.results || templatesResponse.data

        // Load clients
        const clientsResponse = await api.get('/api/clients/')
        availableClients.value = clientsResponse.data.results || clientsResponse.data
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    const loadClientScenarios = async () => {
      if (!formData.value.client_id) {
        clientScenarios.value = []
        return
      }
      
      try {
        const response = await api.get(`/api/scenarios/?client=${formData.value.client_id}`)
        clientScenarios.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading client scenarios:', error)
      }
    }

    const updateFrequencyConfig = () => {
      // Reset frequency config when frequency changes
      if (formData.value.frequency === 'weekly') {
        formData.value.frequency_config = { day_of_week: 0 }
      } else if (formData.value.frequency === 'monthly') {
        formData.value.frequency_config = { day_of_month: 1 }
      } else if (formData.value.frequency === 'custom') {
        formData.value.frequency_config = { interval_value: 1, interval_type: 'days' }
      } else {
        formData.value.frequency_config = {}
      }
    }

    const updateEmailRecipients = () => {
      formData.value.email_recipients = emailRecipientsText.value
        .split('\n')
        .map(email => email.trim())
        .filter(email => email && email.includes('@'))
    }

    const populateForm = () => {
      if (!props.schedule) return

      const schedule = props.schedule
      
      formData.value = {
        name: schedule.name,
        description: schedule.description,
        status: schedule.status,
        template_id: schedule.template.id,
        targetType: schedule.client ? 'single' : 'bulk',
        client_id: schedule.client?.id || null,
        scenario_id: schedule.scenario?.id || null,
        client_filter: schedule.client_filter || {
          created_after: '',
          created_before: '',
          has_scenarios: false
        },
        frequency: schedule.frequency,
        frequency_config: schedule.frequency_config,
        scheduled_time: schedule.scheduled_time,
        timezone: schedule.timezone,
        format: schedule.format,
        generation_options: schedule.generation_options,
        auto_email: schedule.auto_email,
        email_recipients: schedule.email_recipients,
        email_subject_template: schedule.email_subject_template,
        email_body_template: schedule.email_body_template,
        end_date: schedule.end_date ? schedule.end_date.split('T')[0] : '',
        max_runs: schedule.max_runs
      }

      emailRecipientsText.value = schedule.email_recipients.join('\n')
    }

    const handleSubmit = async () => {
      if (!isValid.value || isSaving.value) return

      isSaving.value = true

      try {
        // Prepare submission data
        const submitData = { ...formData.value }
        
        // Convert target type to specific fields
        if (submitData.targetType === 'single') {
          delete submitData.client_filter
        } else {
          submitData.client_id = null
          submitData.scenario_id = null
        }
        delete submitData.targetType

        // Convert end_date to ISO format if provided
        if (submitData.end_date) {
          submitData.end_date = new Date(submitData.end_date).toISOString()
        } else {
          submitData.end_date = null
        }

        if (isEditing.value) {
          await api.put(`/api/report-center/schedules/${props.schedule.id}/`, submitData)
        } else {
          await api.post('/api/report-center/schedules/', submitData)
        }

        emit('save')
      } catch (error) {
        console.error('Error saving schedule:', error)
      } finally {
        isSaving.value = false
      }
    }

    // Watchers
    watch(() => props.show, (show) => {
      if (show) {
        loadInitialData()
        if (isEditing.value) {
          populateForm()
        }
      }
    })

    watch(() => formData.value.client_id, () => {
      formData.value.scenario_id = null
      loadClientScenarios()
    })

    // Lifecycle
    onMounted(() => {
      if (props.show) {
        loadInitialData()
        if (isEditing.value) {
          populateForm()
        }
      }
    })

    return {
      // Data
      isSaving,
      availableTemplates,
      availableClients,
      clientScenarios,
      emailRecipientsText,
      formData,
      
      // Computed
      isEditing,
      isValid,
      
      // Methods
      loadClientScenarios,
      updateFrequencyConfig,
      updateEmailRecipients,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.modal {
  z-index: 1060;
}

.template-option {
  border: 2px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  height: 100%;
}

.template-option:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0,123,255,0.15);
}

.template-option.selected {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.template-label {
  cursor: pointer;
  margin-bottom: 0;
  width: 100%;
}

.template-option input[type="radio"] {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.target-options {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.bulk-filter-options {
  background: #f0f8ff;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #b3d9ff;
}

.email-config {
  background: #f0f8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #c3e6cb;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .template-option {
    margin-bottom: 1rem;
  }
}
</style>