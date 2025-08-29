<template>
  <div class="modal fade show" style="display: block" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-calendar-plus me-2"></i>
            Schedule Meeting
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>

        <form @submit.prevent="scheduleMeeting">
          <div class="modal-body">
            <!-- Step Indicator -->
            <div class="steps-indicator mb-4">
              <div class="step" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
                <div class="step-number">1</div>
                <div class="step-title">Basic Details</div>
              </div>
              <div class="step-line"></div>
              <div class="step" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
                <div class="step-number">2</div>
                <div class="step-title">Date & Time</div>
              </div>
              <div class="step-line"></div>
              <div class="step" :class="{ active: currentStep === 3, completed: currentStep > 3 }">
                <div class="step-number">3</div>
                <div class="step-title">Meeting Options</div>
              </div>
              <div class="step-line"></div>
              <div class="step" :class="{ active: currentStep === 4 }">
                <div class="step-number">4</div>
                <div class="step-title">Confirm</div>
              </div>
            </div>

            <!-- Step 1: Basic Details -->
            <div v-show="currentStep === 1" class="step-content">
              <h6 class="mb-3">Meeting Details</h6>
              
              <!-- Template Selection -->
              <div v-if="meetingTemplates.length > 0" class="mb-3">
                <label class="form-label">Use Template (Optional)</label>
                <select class="form-select" v-model="selectedTemplate" @change="applyTemplate">
                  <option value="">Select a template...</option>
                  <option
                    v-for="template in meetingTemplates"
                    :key="template.id"
                    :value="template"
                  >
                    {{ template.name }} ({{ template.default_duration }}min)
                  </option>
                </select>
                <div class="form-text">Templates help you schedule meetings faster with pre-filled details.</div>
              </div>

              <div class="row">
                <div class="col-12 mb-3">
                  <label class="form-label">Meeting Title *</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="meetingForm.title"
                    :class="{ 'is-invalid': errors.title }"
                    placeholder="Enter meeting title"
                    required
                  >
                  <div v-if="errors.title" class="invalid-feedback">{{ errors.title }}</div>
                </div>

                <div class="col-12 mb-3">
                  <label class="form-label">Description</label>
                  <textarea
                    class="form-control"
                    v-model="meetingForm.description"
                    rows="3"
                    placeholder="Add meeting agenda or notes"
                  ></textarea>
                </div>

                <!-- Client/Lead Selection -->
                <div class="col-md-6 mb-3">
                  <label class="form-label">Client</label>
                  <select class="form-select" v-model="meetingForm.client_id">
                    <option value="">Select a client...</option>
                    <option
                      v-for="client in clients"
                      :key="client.id"
                      :value="client.id"
                    >
                      {{ client.name }}
                    </option>
                  </select>
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">Lead</label>
                  <select class="form-select" v-model="meetingForm.lead_id">
                    <option value="">Select a lead...</option>
                    <option
                      v-for="lead in leads"
                      :key="lead.id"
                      :value="lead.id"
                    >
                      {{ lead.name }}
                    </option>
                  </select>
                </div>

                <!-- Location -->
                <div class="col-12 mb-3">
                  <label class="form-label">Location</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="meetingForm.location"
                    placeholder="Meeting location (optional if video meeting)"
                  >
                </div>
              </div>
            </div>

            <!-- Step 2: Date & Time -->
            <div v-show="currentStep === 2" class="step-content">
              <h6 class="mb-3">Schedule</h6>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Date *</label>
                  <input
                    type="date"
                    class="form-control"
                    v-model="meetingForm.date"
                    :class="{ 'is-invalid': errors.date }"
                    :min="today"
                    required
                    @change="checkAvailability"
                  >
                  <div v-if="errors.date" class="invalid-feedback">{{ errors.date }}</div>
                </div>

                <div class="col-md-3 mb-3">
                  <label class="form-label">Start Time *</label>
                  <input
                    type="time"
                    class="form-control"
                    v-model="meetingForm.start_time"
                    :class="{ 'is-invalid': errors.start_time }"
                    required
                    @change="updateEndTime"
                  >
                  <div v-if="errors.start_time" class="invalid-feedback">{{ errors.start_time }}</div>
                </div>

                <div class="col-md-3 mb-3">
                  <label class="form-label">Duration</label>
                  <select class="form-select" v-model="meetingForm.duration" @change="updateEndTime">
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="45">45 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="90">1.5 hours</option>
                    <option value="120">2 hours</option>
                  </select>
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">End Time</label>
                  <input
                    type="time"
                    class="form-control"
                    v-model="meetingForm.end_time"
                    readonly
                  >
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">Time Zone</label>
                  <select class="form-select" v-model="meetingForm.timezone">
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                </div>
              </div>

              <!-- Availability Check -->
              <div v-if="checkingAvailability" class="text-center mb-3">
                <div class="spinner-border spinner-border-sm text-primary me-2"></div>
                Checking availability...
              </div>

              <div v-if="availabilityChecked && !isTimeAvailable" class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Potential Conflict:</strong> You may have other meetings scheduled around this time.
                <div class="mt-2">
                  <small>
                    Conflicting events:
                    <ul class="mb-0 mt-1">
                      <li v-for="conflict in conflicts" :key="conflict.id">
                        {{ conflict.title }} ({{ formatTime(conflict.start_datetime) }} - {{ formatTime(conflict.end_datetime) }})
                      </li>
                    </ul>
                  </small>
                </div>
              </div>

              <!-- Suggested Times -->
              <div v-if="suggestedTimes.length > 0" class="suggested-times">
                <h6 class="mb-2">Suggested Available Times</h6>
                <div class="row">
                  <div
                    v-for="suggestion in suggestedTimes.slice(0, 6)"
                    :key="suggestion.time"
                    class="col-md-4 mb-2"
                  >
                    <button
                      type="button"
                      class="btn btn-outline-success btn-sm w-100"
                      @click="selectSuggestedTime(suggestion)"
                    >
                      {{ suggestion.display }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 3: Meeting Options -->
            <div v-show="currentStep === 3" class="step-content">
              <h6 class="mb-3">Meeting Options</h6>

              <!-- Video Conferencing -->
              <div class="mb-4">
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="includeVideo"
                    v-model="meetingForm.include_video"
                  >
                  <label class="form-check-label" for="includeVideo">
                    Include video meeting link
                  </label>
                </div>
              </div>

              <div v-if="meetingForm.include_video" class="video-options mb-4">
                <label class="form-label">Video Platform</label>
                <div class="row">
                  <div class="col-md-4 mb-2">
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="radio"
                        name="meetingType"
                        id="zoom"
                        value="zoom"
                        v-model="meetingForm.meeting_type"
                      >
                      <label class="form-check-label" for="zoom">
                        <i class="fab fa-zoom me-1"></i>
                        Zoom
                      </label>
                    </div>
                  </div>
                  <div class="col-md-4 mb-2">
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="radio"
                        name="meetingType"
                        id="meet"
                        value="meet"
                        v-model="meetingForm.meeting_type"
                      >
                      <label class="form-check-label" for="meet">
                        <i class="fab fa-google me-1"></i>
                        Google Meet
                      </label>
                    </div>
                  </div>
                  <div class="col-md-4 mb-2">
                    <div class="form-check">
                      <input
                        class="form-check-input"
                        type="radio"
                        name="meetingType"
                        id="teams"
                        value="teams"
                        v-model="meetingForm.meeting_type"
                      >
                      <label class="form-check-label" for="teams">
                        <i class="fab fa-microsoft me-1"></i>
                        Microsoft Teams
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Calendar Account Selection -->
              <div v-if="calendarAccounts.length > 0" class="mb-4">
                <label class="form-label">Add to Calendar</label>
                <select class="form-select" v-model="meetingForm.calendar_account_id">
                  <option value="">Don't add to external calendar</option>
                  <option
                    v-for="account in calendarAccounts"
                    :key="account.id"
                    :value="account.id"
                  >
                    {{ account.display_name }} ({{ account.get_provider_display }})
                  </option>
                </select>
                <div class="form-text">Choose which calendar to sync this meeting to.</div>
              </div>

              <!-- Reminders -->
              <div class="mb-4">
                <label class="form-label">Reminders</label>
                <div class="reminder-options">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="reminder15"
                      value="15"
                      v-model="meetingForm.reminders"
                    >
                    <label class="form-check-label" for="reminder15">
                      15 minutes before
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="reminder60"
                      value="60"
                      v-model="meetingForm.reminders"
                    >
                    <label class="form-check-label" for="reminder60">
                      1 hour before
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="reminder1day"
                      value="1440"
                      v-model="meetingForm.reminders"
                    >
                    <label class="form-check-label" for="reminder1day">
                      1 day before
                    </label>
                  </div>
                </div>
              </div>

              <!-- Additional Options -->
              <div class="additional-options">
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="sendInvite"
                    v-model="meetingForm.send_calendar_invite"
                  >
                  <label class="form-check-label" for="sendInvite">
                    Send calendar invite to attendees
                  </label>
                </div>

                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="createTask"
                    v-model="meetingForm.create_follow_up_task"
                  >
                  <label class="form-check-label" for="createTask">
                    Create follow-up task after meeting
                  </label>
                </div>

                <div v-if="meetingForm.create_follow_up_task" class="ms-4 mt-2">
                  <div class="row">
                    <div class="col-md-8 mb-2">
                      <input
                        type="text"
                        class="form-control form-control-sm"
                        v-model="meetingForm.follow_up_task_title"
                        placeholder="Follow-up task title"
                      >
                    </div>
                    <div class="col-md-4">
                      <select class="form-select form-select-sm" v-model="meetingForm.follow_up_days">
                        <option value="0">Same day</option>
                        <option value="1">Next day</option>
                        <option value="2">2 days later</option>
                        <option value="7">1 week later</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Attendees -->
              <div class="mb-3">
                <label class="form-label">Additional Attendees</label>
                <div class="attendee-input">
                  <input
                    type="email"
                    class="form-control"
                    v-model="newAttendee"
                    placeholder="Enter email address"
                    @keyup.enter="addAttendee"
                  >
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="addAttendee"
                    :disabled="!isValidEmail(newAttendee)"
                  >
                    Add
                  </button>
                </div>
                
                <div v-if="meetingForm.attendees.length > 0" class="attendees-list mt-2">
                  <div
                    v-for="(attendee, index) in meetingForm.attendees"
                    :key="index"
                    class="attendee-tag"
                  >
                    {{ attendee }}
                    <button
                      type="button"
                      class="btn-close btn-close-sm"
                      @click="removeAttendee(index)"
                    ></button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 4: Confirmation -->
            <div v-show="currentStep === 4" class="step-content">
              <h6 class="mb-3">Confirm Meeting Details</h6>
              
              <div class="meeting-summary">
                <div class="row">
                  <div class="col-md-6">
                    <div class="summary-item">
                      <strong>Title:</strong>
                      <span>{{ meetingForm.title }}</span>
                    </div>
                    <div class="summary-item">
                      <strong>Date:</strong>
                      <span>{{ formatDate(meetingForm.date) }}</span>
                    </div>
                    <div class="summary-item">
                      <strong>Time:</strong>
                      <span>{{ meetingForm.start_time }} - {{ meetingForm.end_time }}</span>
                    </div>
                    <div v-if="meetingForm.location" class="summary-item">
                      <strong>Location:</strong>
                      <span>{{ meetingForm.location }}</span>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div v-if="selectedClient" class="summary-item">
                      <strong>Client:</strong>
                      <span>{{ selectedClient.name }}</span>
                    </div>
                    <div v-if="selectedLead" class="summary-item">
                      <strong>Lead:</strong>
                      <span>{{ selectedLead.name }}</span>
                    </div>
                    <div v-if="meetingForm.include_video" class="summary-item">
                      <strong>Video Platform:</strong>
                      <span>{{ meetingForm.meeting_type?.toUpperCase() }}</span>
                    </div>
                    <div v-if="meetingForm.attendees.length > 0" class="summary-item">
                      <strong>Attendees:</strong>
                      <span>{{ meetingForm.attendees.join(', ') }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="meetingForm.description" class="summary-item mt-3">
                  <strong>Description:</strong>
                  <div class="description-text">{{ meetingForm.description }}</div>
                </div>
              </div>
            </div>

            <!-- Error Display -->
            <div v-if="submitError" class="alert alert-danger">
              <i class="fas fa-exclamation-circle me-2"></i>
              {{ submitError }}
            </div>
          </div>

          <div class="modal-footer">
            <!-- Navigation Buttons -->
            <div class="step-navigation w-100 d-flex justify-content-between">
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="previousStep"
                :disabled="currentStep === 1 || submitting"
                v-show="currentStep > 1"
              >
                <i class="fas fa-chevron-left me-1"></i>
                Previous
              </button>

              <div class="ms-auto">
                <button
                  type="button"
                  class="btn btn-secondary me-2"
                  @click="$emit('close')"
                  :disabled="submitting"
                >
                  Cancel
                </button>

                <button
                  v-if="currentStep < 4"
                  type="button"
                  class="btn btn-primary"
                  @click="nextStep"
                  :disabled="!canProceedToNext || submitting"
                >
                  Next
                  <i class="fas fa-chevron-right ms-1"></i>
                </button>

                <button
                  v-else
                  type="submit"
                  class="btn btn-success"
                  :disabled="!isFormValid || submitting"
                >
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-calendar-check me-1"></i>
                  Schedule Meeting
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Modal Backdrop -->
  <div class="modal-backdrop fade show"></div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCalendarStore } from '@/stores/calendarStore'
import { useClientStore } from '@/stores/clientStore'
import { storeToRefs } from 'pinia'
import calendarService from '@/services/calendarService'

const emit = defineEmits(['close', 'meeting-scheduled'])

const props = defineProps({
  initialDate: {
    type: Date,
    default: () => new Date()
  },
  clientId: {
    type: String,
    default: null
  },
  leadId: {
    type: String,
    default: null
  }
})

// Stores
const calendarStore = useCalendarStore()
const clientStore = useClientStore()
const { calendarAccounts, meetingTemplates } = storeToRefs(calendarStore)
const { clients } = storeToRefs(clientStore)

// State
const currentStep = ref(1)
const submitting = ref(false)
const submitError = ref('')
const selectedTemplate = ref('')
const newAttendee = ref('')
const checkingAvailability = ref(false)
const availabilityChecked = ref(false)
const isTimeAvailable = ref(true)
const conflicts = ref([])
const suggestedTimes = ref([])

// Mock leads data (replace with actual leads store when available)
const leads = ref([])

// Form data
const meetingForm = ref({
  title: '',
  description: '',
  date: '',
  start_time: '',
  end_time: '',
  duration: 60,
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  location: '',
  client_id: props.clientId || '',
  lead_id: props.leadId || '',
  include_video: true,
  meeting_type: 'zoom',
  calendar_account_id: '',
  send_calendar_invite: true,
  create_follow_up_task: true,
  follow_up_task_title: 'Follow up on meeting',
  follow_up_days: 1,
  reminders: ['15', '60'],
  attendees: []
})

// Validation errors
const errors = ref({})

// Computed
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const selectedClient = computed(() => {
  return clients.value.find(client => client.id === meetingForm.value.client_id)
})

const selectedLead = computed(() => {
  return leads.value.find(lead => lead.id === meetingForm.value.lead_id)
})

const canProceedToNext = computed(() => {
  switch (currentStep.value) {
    case 1:
      return meetingForm.value.title.trim() !== ''
    case 2:
      return meetingForm.value.date && meetingForm.value.start_time
    case 3:
      return true
    default:
      return false
  }
})

const isFormValid = computed(() => {
  return meetingForm.value.title.trim() !== '' &&
         meetingForm.value.date &&
         meetingForm.value.start_time &&
         Object.keys(errors.value).length === 0
})

// Methods
const initializeForm = () => {
  // Set initial date if provided
  if (props.initialDate) {
    const date = new Date(props.initialDate)
    meetingForm.value.date = date.toISOString().split('T')[0]
    
    // Round to next hour if time is provided
    const hours = date.getHours()
    const minutes = date.getMinutes()
    if (minutes > 0) {
      date.setHours(hours + 1, 0, 0, 0)
    }
    meetingForm.value.start_time = date.toTimeString().slice(0, 5)
    updateEndTime()
  }

  // Set default calendar account
  if (calendarAccounts.value.length > 0) {
    const primaryAccount = calendarAccounts.value.find(account => account.primary_calendar)
    if (primaryAccount) {
      meetingForm.value.calendar_account_id = primaryAccount.id
    }
  }
}

const applyTemplate = () => {
  if (!selectedTemplate.value) return
  
  const template = selectedTemplate.value
  meetingForm.value.title = template.default_title || meetingForm.value.title
  meetingForm.value.description = template.default_description || meetingForm.value.description
  meetingForm.value.location = template.default_location || meetingForm.value.location
  meetingForm.value.duration = template.default_duration || meetingForm.value.duration
  meetingForm.value.include_video = template.include_video
  meetingForm.value.meeting_type = template.preferred_meeting_type || meetingForm.value.meeting_type
  meetingForm.value.send_calendar_invite = template.send_calendar_invite
  meetingForm.value.create_follow_up_task = template.create_follow_up_task
  meetingForm.value.follow_up_task_title = template.follow_up_task_title || meetingForm.value.follow_up_task_title
  meetingForm.value.follow_up_days = template.follow_up_task_days || meetingForm.value.follow_up_days
  
  updateEndTime()
}

const updateEndTime = () => {
  if (!meetingForm.value.start_time || !meetingForm.value.duration) return
  
  const [hours, minutes] = meetingForm.value.start_time.split(':').map(Number)
  const startTime = new Date()
  startTime.setHours(hours, minutes, 0, 0)
  
  const endTime = new Date(startTime.getTime() + meetingForm.value.duration * 60000)
  meetingForm.value.end_time = endTime.toTimeString().slice(0, 5)
}

const checkAvailability = async () => {
  if (!meetingForm.value.date || !meetingForm.value.start_time) return
  
  checkingAvailability.value = true
  availabilityChecked.value = false
  
  try {
    const startDateTime = `${meetingForm.value.date}T${meetingForm.value.start_time}`
    const endDateTime = `${meetingForm.value.date}T${meetingForm.value.end_time}`
    
    // Check for conflicts
    const response = await calendarService.getCalendarEvents({
      start_date: meetingForm.value.date,
      end_date: meetingForm.value.date
    })
    
    const existingEvents = response.results || response
    conflicts.value = existingEvents.filter(event => {
      if (event.status === 'cancelled') return false
      
      const eventStart = new Date(event.start_datetime)
      const eventEnd = new Date(event.end_datetime)
      const newStart = new Date(startDateTime)
      const newEnd = new Date(endDateTime)
      
      return (newStart < eventEnd && newEnd > eventStart)
    })
    
    isTimeAvailable.value = conflicts.value.length === 0
    
    // Generate suggested times if there are conflicts
    if (!isTimeAvailable.value) {
      generateSuggestedTimes()
    }
    
    availabilityChecked.value = true
  } catch (error) {
    console.error('Error checking availability:', error)
  } finally {
    checkingAvailability.value = false
  }
}

const generateSuggestedTimes = () => {
  const suggestions = []
  const date = new Date(meetingForm.value.date)
  const duration = meetingForm.value.duration
  
  // Generate suggestions for business hours (9 AM - 5 PM)
  for (let hour = 9; hour < 17; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const suggestedStart = new Date(date)
      suggestedStart.setHours(hour, minute, 0, 0)
      
      const suggestedEnd = new Date(suggestedStart.getTime() + duration * 60000)
      
      // Check if this time conflicts with existing events
      const hasConflict = conflicts.value.some(event => {
        const eventStart = new Date(event.start_datetime)
        const eventEnd = new Date(event.end_datetime)
        return (suggestedStart < eventEnd && suggestedEnd > eventStart)
      })
      
      if (!hasConflict) {
        suggestions.push({
          time: suggestedStart.toTimeString().slice(0, 5),
          display: `${formatTime(suggestedStart)} - ${formatTime(suggestedEnd)}`
        })
        
        if (suggestions.length >= 6) break
      }
    }
    if (suggestions.length >= 6) break
  }
  
  suggestedTimes.value = suggestions
}

const selectSuggestedTime = (suggestion) => {
  meetingForm.value.start_time = suggestion.time
  updateEndTime()
  checkAvailability()
}

const addAttendee = () => {
  if (!newAttendee.value || !isValidEmail(newAttendee.value)) return
  
  if (!meetingForm.value.attendees.includes(newAttendee.value)) {
    meetingForm.value.attendees.push(newAttendee.value)
  }
  
  newAttendee.value = ''
}

const removeAttendee = (index) => {
  meetingForm.value.attendees.splice(index, 1)
}

const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateStep = (step) => {
  errors.value = {}
  
  switch (step) {
    case 1:
      if (!meetingForm.value.title.trim()) {
        errors.value.title = 'Meeting title is required'
      }
      break
    case 2:
      if (!meetingForm.value.date) {
        errors.value.date = 'Meeting date is required'
      }
      if (!meetingForm.value.start_time) {
        errors.value.start_time = 'Start time is required'
      }
      if (new Date(`${meetingForm.value.date}T${meetingForm.value.start_time}`) < new Date()) {
        errors.value.date = 'Meeting cannot be scheduled in the past'
      }
      break
  }
  
  return Object.keys(errors.value).length === 0
}

const nextStep = () => {
  if (!validateStep(currentStep.value)) return
  
  if (currentStep.value === 2) {
    checkAvailability()
  }
  
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const scheduleMeeting = async () => {
  if (!validateStep(currentStep.value) || !isFormValid.value) return
  
  submitting.value = true
  submitError.value = ''
  
  try {
    const meetingData = {
      title: meetingForm.value.title,
      description: meetingForm.value.description,
      start_datetime: `${meetingForm.value.date}T${meetingForm.value.start_time}`,
      end_datetime: `${meetingForm.value.date}T${meetingForm.value.end_time}`,
      timezone: meetingForm.value.timezone,
      location: meetingForm.value.location,
      client_id: meetingForm.value.client_id || null,
      lead_id: meetingForm.value.lead_id || null,
      attendees: meetingForm.value.attendees.map(email => ({ email, status: 'invited' })),
      calendar_account_id: meetingForm.value.calendar_account_id || null,
      send_calendar_invite: meetingForm.value.send_calendar_invite,
      create_follow_up_task: meetingForm.value.create_follow_up_task,
      follow_up_task_title: meetingForm.value.follow_up_task_title,
      follow_up_days: meetingForm.value.follow_up_days,
      reminders: meetingForm.value.reminders.map(minutes => ({ minutes_before: parseInt(minutes), reminder_type: 'email' }))
    }
    
    // Add video meeting details if requested
    if (meetingForm.value.include_video) {
      meetingData.meeting_type = meetingForm.value.meeting_type
      meetingData.generate_meeting_link = true
    }
    
    const meeting = await calendarService.scheduleMeeting(meetingData)
    
    // Increment template usage if one was used
    if (selectedTemplate.value) {
      try {
        await calendarService.useMeetingTemplate(selectedTemplate.value.id)
      } catch (error) {
        console.error('Error updating template usage:', error)
      }
    }
    
    emit('meeting-scheduled', meeting)
  } catch (error) {
    console.error('Error scheduling meeting:', error)
    submitError.value = error.response?.data?.detail || 'Failed to schedule meeting. Please try again.'
  } finally {
    submitting.value = false
  }
}

// Utility methods
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatTime = (datetime) => {
  const date = new Date(datetime)
  return date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true
  })
}

// Lifecycle
onMounted(async () => {
  // Load data
  await Promise.all([
    calendarStore.fetchMeetingTemplates(),
    clientStore.fetchClients()
  ])
  
  initializeForm()
})

// Watch for changes to update end time
watch(() => [meetingForm.value.start_time, meetingForm.value.duration], updateEndTime)
</script>

<style scoped>
.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background-color: #007bff;
  color: white;
}

.step.completed .step-number {
  background-color: #28a745;
  color: white;
}

.step-title {
  font-size: 0.75rem;
  color: #6c757d;
  text-align: center;
  font-weight: 500;
}

.step.active .step-title {
  color: #007bff;
  font-weight: 600;
}

.step-line {
  height: 2px;
  background-color: #e9ecef;
  flex: 1;
  margin: 0 1rem;
  margin-top: -20px;
  z-index: -1;
}

.step-content {
  min-height: 300px;
}

.meeting-summary {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.summary-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.summary-item strong {
  color: #495057;
  min-width: 100px;
}

.summary-item span {
  flex: 1;
  text-align: right;
}

.description-text {
  background: white;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
  margin-top: 0.5rem;
  font-style: italic;
  color: #6c757d;
}

.video-options {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.reminder-options {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.reminder-options .form-check {
  margin-bottom: 0.5rem;
}

.additional-options {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #dee2e6;
}

.attendee-input {
  display: flex;
  gap: 0.5rem;
}

.attendee-input .form-control {
  flex: 1;
}

.attendees-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attendee-tag {
  background-color: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.attendee-tag .btn-close {
  filter: invert(1);
  opacity: 0.8;
}

.suggested-times {
  background-color: #e7f3ff;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #b8daff;
}

.suggested-times h6 {
  color: #004085;
  margin-bottom: 0.75rem;
}

.step-navigation {
  min-height: 40px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .steps-indicator {
    flex-direction: column;
    gap: 1rem;
  }
  
  .step {
    flex-direction: row;
    align-items: center;
    width: 100%;
  }
  
  .step-number {
    margin-bottom: 0;
    margin-right: 0.75rem;
  }
  
  .step-title {
    text-align: left;
    flex: 1;
  }
  
  .step-line {
    display: none;
  }
  
  .meeting-summary .row > div {
    margin-bottom: 1rem;
  }
  
  .summary-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .summary-item span {
    text-align: left;
    margin-top: 0.25rem;
  }
}

@media (max-width: 576px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .step-content {
    min-height: auto;
  }
  
  .attendee-input {
    flex-direction: column;
  }
  
  .video-options .row > div {
    margin-bottom: 0.5rem;
  }
}
</style>