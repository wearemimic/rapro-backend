<template>
  <div class="modal fade show" style="display: block" @click.self="$emit('close')">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-calendar-alt me-2"></i>
            {{ isEditing ? 'Edit Meeting' : 'Meeting Details' }}
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>

        <div class="modal-body">
          <div class="row">
            <!-- Left Column - Meeting Details -->
            <div class="col-md-8">
              <div v-if="!isEditing" class="meeting-details">
                <!-- Meeting Header -->
                <div class="meeting-header mb-4">
                  <div class="d-flex align-items-start justify-content-between">
                    <div>
                      <h4 class="meeting-title">{{ event.title }}</h4>
                      <div class="meeting-meta">
                        <span class="badge" :class="getStatusBadgeClass(event.status)">
                          {{ event.status.charAt(0).toUpperCase() + event.status.slice(1) }}
                        </span>
                        <span v-if="event.privacy === 'private'" class="badge bg-secondary ms-1">
                          <i class="fas fa-lock me-1"></i>
                          Private
                        </span>
                        <span v-if="event.is_recurring" class="badge bg-info ms-1">
                          <i class="fas fa-repeat me-1"></i>
                          Recurring
                        </span>
                      </div>
                    </div>
                    <div class="meeting-actions">
                      <div class="dropdown">
                        <button
                          class="btn btn-outline-secondary btn-sm dropdown-toggle"
                          type="button"
                          data-bs-toggle="dropdown"
                        >
                          Actions
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                          <li v-if="canEdit">
                            <button class="dropdown-item" @click="startEditing">
                              <i class="fas fa-edit me-2"></i>
                              Edit Meeting
                            </button>
                          </li>
                          <li v-if="event.meeting_url">
                            <a class="dropdown-item" :href="event.meeting_url" target="_blank">
                              <i class="fas fa-video me-2"></i>
                              Join Meeting
                            </a>
                          </li>
                          <li v-if="canEdit">
                            <button class="dropdown-item" @click="duplicateEvent">
                              <i class="fas fa-copy me-2"></i>
                              Duplicate
                            </button>
                          </li>
                          <li v-if="canReschedule">
                            <button class="dropdown-item" @click="showRescheduleModal = true">
                              <i class="fas fa-clock me-2"></i>
                              Reschedule
                            </button>
                          </li>
                          <li><hr class="dropdown-divider"></li>
                          <li v-if="event.status !== 'cancelled' && canEdit">
                            <button class="dropdown-item text-warning" @click="cancelMeeting">
                              <i class="fas fa-ban me-2"></i>
                              Cancel Meeting
                            </button>
                          </li>
                          <li v-if="canDelete">
                            <button class="dropdown-item text-danger" @click="confirmDelete = true">
                              <i class="fas fa-trash me-2"></i>
                              Delete Meeting
                            </button>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Date & Time -->
                <div class="info-section mb-4">
                  <div class="row">
                    <div class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-calendar me-2 text-primary"></i>
                        <div>
                          <div class="info-label">Date</div>
                          <div class="info-value">{{ formatDate(event.start_datetime) }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-clock me-2 text-primary"></i>
                        <div>
                          <div class="info-label">Time</div>
                          <div class="info-value">
                            {{ formatTimeRange(event.start_datetime, event.end_datetime) }}
                            <span class="text-muted">({{ event.duration_minutes }} min)</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Location & Video -->
                <div v-if="event.location || event.meeting_url" class="info-section mb-4">
                  <div class="row">
                    <div v-if="event.location" class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-map-marker-alt me-2 text-danger"></i>
                        <div>
                          <div class="info-label">Location</div>
                          <div class="info-value">{{ event.location }}</div>
                        </div>
                      </div>
                    </div>
                    <div v-if="event.meeting_url" class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-video me-2 text-success"></i>
                        <div>
                          <div class="info-label">Video Meeting</div>
                          <div class="info-value">
                            <a :href="event.meeting_url" target="_blank" class="btn btn-success btn-sm">
                              <i class="fas fa-external-link-alt me-1"></i>
                              Join {{ event.meeting_type?.toUpperCase() || 'Meeting' }}
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Client/Lead Info -->
                <div v-if="event.client || event.lead" class="info-section mb-4">
                  <div class="row">
                    <div v-if="event.client" class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-user me-2 text-info"></i>
                        <div>
                          <div class="info-label">Client</div>
                          <div class="info-value">
                            <router-link :to="`/clients/${event.client.id}`" class="text-decoration-none">
                              {{ event.client.name }}
                            </router-link>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="event.lead" class="col-sm-6">
                      <div class="info-item">
                        <i class="fas fa-user-plus me-2 text-warning"></i>
                        <div>
                          <div class="info-label">Lead</div>
                          <div class="info-value">{{ event.lead.name }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Description -->
                <div v-if="event.description" class="info-section mb-4">
                  <h6 class="section-title">
                    <i class="fas fa-align-left me-2"></i>
                    Description
                  </h6>
                  <div class="description-content">
                    {{ event.description }}
                  </div>
                </div>

                <!-- Attendees -->
                <div v-if="event.attendees && event.attendees.length > 0" class="info-section mb-4">
                  <h6 class="section-title">
                    <i class="fas fa-users me-2"></i>
                    Attendees ({{ event.attendees.length }})
                  </h6>
                  <div class="attendees-list">
                    <div
                      v-for="attendee in event.attendees"
                      :key="attendee.email"
                      class="attendee-item"
                    >
                      <div class="attendee-avatar">
                        {{ getInitials(attendee.name || attendee.email) }}
                      </div>
                      <div class="attendee-info">
                        <div class="attendee-name">{{ attendee.name || attendee.email }}</div>
                        <div v-if="attendee.name" class="attendee-email">{{ attendee.email }}</div>
                      </div>
                      <div class="attendee-status">
                        <span 
                          class="badge"
                          :class="getAttendeeStatusClass(attendee.responseStatus)"
                        >
                          {{ formatAttendeeStatus(attendee.responseStatus) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Reminders -->
                <div v-if="event.reminders && event.reminders.length > 0" class="info-section mb-4">
                  <h6 class="section-title">
                    <i class="fas fa-bell me-2"></i>
                    Reminders
                  </h6>
                  <div class="reminders-list">
                    <div
                      v-for="reminder in event.reminders"
                      :key="reminder.id"
                      class="reminder-item"
                    >
                      <i class="fas fa-bell-o me-2"></i>
                      {{ formatReminderTime(reminder.minutes_before) }} before
                      <span class="text-muted">({{ reminder.reminder_type }})</span>
                      <span
                        v-if="reminder.is_sent"
                        class="badge bg-success ms-2"
                      >
                        Sent
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Meeting Notes -->
                <div class="info-section">
                  <h6 class="section-title">
                    <i class="fas fa-sticky-note me-2"></i>
                    Meeting Notes
                  </h6>
                  <div v-if="!editingNotes" class="notes-display">
                    <div v-if="meetingNotes" class="notes-content">
                      {{ meetingNotes }}
                    </div>
                    <div v-else class="no-notes text-muted">
                      No notes added yet.
                    </div>
                    <button
                      class="btn btn-outline-primary btn-sm mt-2"
                      @click="editingNotes = true"
                    >
                      <i class="fas fa-edit me-1"></i>
                      {{ meetingNotes ? 'Edit Notes' : 'Add Notes' }}
                    </button>
                  </div>
                  <div v-else class="notes-editor">
                    <textarea
                      v-model="notesForm"
                      class="form-control"
                      rows="4"
                      placeholder="Add meeting notes, action items, or follow-ups..."
                    ></textarea>
                    <div class="mt-2">
                      <button
                        class="btn btn-primary btn-sm me-2"
                        @click="saveNotes"
                        :disabled="savingNotes"
                      >
                        <span v-if="savingNotes" class="spinner-border spinner-border-sm me-1"></span>
                        Save Notes
                      </button>
                      <button
                        class="btn btn-outline-secondary btn-sm"
                        @click="cancelNotesEdit"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Edit Form -->
              <div v-else class="meeting-edit-form">
                <form @submit.prevent="saveChanges">
                  <!-- Basic Info -->
                  <div class="row mb-3">
                    <div class="col-12">
                      <label class="form-label">Meeting Title</label>
                      <input
                        type="text"
                        class="form-control"
                        v-model="editForm.title"
                        required
                      >
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-12">
                      <label class="form-label">Description</label>
                      <textarea
                        class="form-control"
                        v-model="editForm.description"
                        rows="3"
                      ></textarea>
                    </div>
                  </div>

                  <!-- Date & Time -->
                  <div class="row mb-3">
                    <div class="col-md-4">
                      <label class="form-label">Date</label>
                      <input
                        type="date"
                        class="form-control"
                        v-model="editForm.date"
                        required
                      >
                    </div>
                    <div class="col-md-4">
                      <label class="form-label">Start Time</label>
                      <input
                        type="time"
                        class="form-control"
                        v-model="editForm.start_time"
                        required
                      >
                    </div>
                    <div class="col-md-4">
                      <label class="form-label">End Time</label>
                      <input
                        type="time"
                        class="form-control"
                        v-model="editForm.end_time"
                        required
                      >
                    </div>
                  </div>

                  <!-- Location -->
                  <div class="mb-3">
                    <label class="form-label">Location</label>
                    <input
                      type="text"
                      class="form-control"
                      v-model="editForm.location"
                    >
                  </div>

                  <!-- Status -->
                  <div class="mb-3">
                    <label class="form-label">Status</label>
                    <select class="form-select" v-model="editForm.status">
                      <option value="confirmed">Confirmed</option>
                      <option value="tentative">Tentative</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>

                  <!-- Form Actions -->
                  <div class="form-actions">
                    <button
                      type="submit"
                      class="btn btn-primary me-2"
                      :disabled="saving"
                    >
                      <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                      Save Changes
                    </button>
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="cancelEditing"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>

            <!-- Right Column - Quick Actions & Info -->
            <div class="col-md-4">
              <div class="quick-actions mb-4">
                <h6 class="section-title">Quick Actions</h6>
                <div class="d-grid gap-2">
                  <button
                    v-if="event.meeting_url && !isPastEvent"
                    class="btn btn-success"
                    @click="joinMeeting"
                  >
                    <i class="fas fa-video me-1"></i>
                    Join Meeting
                  </button>
                  
                  <button
                    v-if="canEdit && !isPastEvent"
                    class="btn btn-outline-primary"
                    @click="showRescheduleModal = true"
                  >
                    <i class="fas fa-clock me-1"></i>
                    Reschedule
                  </button>
                  
                  <button
                    class="btn btn-outline-secondary"
                    @click="addToCalendar"
                  >
                    <i class="fas fa-calendar-plus me-1"></i>
                    Add to Calendar
                  </button>
                  
                  <button
                    class="btn btn-outline-info"
                    @click="copyMeetingLink"
                    v-if="event.meeting_url"
                  >
                    <i class="fas fa-link me-1"></i>
                    Copy Meeting Link
                  </button>
                </div>
              </div>

              <!-- Meeting Info -->
              <div class="meeting-info-card">
                <h6 class="section-title">Meeting Information</h6>
                <div class="info-list">
                  <div class="info-row">
                    <span class="label">Created:</span>
                    <span class="value">{{ formatDate(event.created_at) }}</span>
                  </div>
                  <div class="info-row">
                    <span class="label">Updated:</span>
                    <span class="value">{{ formatDate(event.updated_at) }}</span>
                  </div>
                  <div v-if="event.calendar_account" class="info-row">
                    <span class="label">Calendar:</span>
                    <span class="value">{{ event.calendar_account.display_name }}</span>
                  </div>
                  <div v-if="event.organizer_email" class="info-row">
                    <span class="label">Organizer:</span>
                    <span class="value">{{ event.organizer_name || event.organizer_email }}</span>
                  </div>
                </div>
              </div>

              <!-- Related Items -->
              <div v-if="event.task" class="related-items mt-4">
                <h6 class="section-title">Related Task</h6>
                <div class="related-item">
                  <i class="fas fa-tasks me-2"></i>
                  <router-link :to="`/tasks/${event.task.id}`" class="text-decoration-none">
                    {{ event.task.title }}
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="alert alert-danger mx-3">
          <i class="fas fa-exclamation-circle me-2"></i>
          {{ error }}
        </div>
      </div>
    </div>
  </div>

  <!-- Reschedule Modal -->
  <div
    v-if="showRescheduleModal"
    class="modal fade show"
    style="display: block"
    @click.self="showRescheduleModal = false"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Reschedule Meeting</h5>
          <button
            type="button"
            class="btn-close"
            @click="showRescheduleModal = false"
          ></button>
        </div>
        <form @submit.prevent="rescheduleEvent">
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">New Date</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="rescheduleForm.date"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">New Start Time</label>
                <input
                  type="time"
                  class="form-control"
                  v-model="rescheduleForm.start_time"
                  required
                >
              </div>
            </div>
            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="notifyAttendees"
                  v-model="rescheduleForm.notify_attendees"
                >
                <label class="form-check-label" for="notifyAttendees">
                  Notify attendees about the change
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showRescheduleModal = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="rescheduling"
            >
              <span v-if="rescheduling" class="spinner-border spinner-border-sm me-1"></span>
              Reschedule Meeting
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation -->
  <div
    v-if="confirmDelete"
    class="modal fade show"
    style="display: block"
    @click.self="confirmDelete = false"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title text-danger">Delete Meeting</h5>
          <button
            type="button"
            class="btn-close"
            @click="confirmDelete = false"
          ></button>
        </div>
        <div class="modal-body">
          <div class="text-center">
            <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
            <h6>Are you sure you want to delete this meeting?</h6>
            <p class="text-muted">
              <strong>{{ event.title }}</strong><br>
              {{ formatDate(event.start_datetime) }} at {{ formatTime(event.start_datetime) }}
            </p>
            <p class="text-muted">This action cannot be undone.</p>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            @click="confirmDelete = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-danger"
            @click="deleteEvent"
            :disabled="deleting"
          >
            <span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>
            Delete Meeting
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Backdrops -->
  <div class="modal-backdrop fade show"></div>
  <div
    v-if="showRescheduleModal || confirmDelete"
    class="modal-backdrop fade show"
    style="z-index: 1055"
  ></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCalendarStore } from '@/stores/calendarStore'
import calendarService from '@/services/calendarService'

const emit = defineEmits(['close', 'event-updated', 'event-deleted'])

const props = defineProps({
  event: {
    type: Object,
    required: true
  }
})

// Store
const calendarStore = useCalendarStore()

// Local state
const isEditing = ref(false)
const saving = ref(false)
const deleting = ref(false)
const rescheduling = ref(false)
const error = ref('')
const confirmDelete = ref(false)
const showRescheduleModal = ref(false)
const editingNotes = ref(false)
const savingNotes = ref(false)
const meetingNotes = ref('')
const notesForm = ref('')

// Edit form
const editForm = ref({
  title: '',
  description: '',
  date: '',
  start_time: '',
  end_time: '',
  location: '',
  status: 'confirmed'
})

// Reschedule form
const rescheduleForm = ref({
  date: '',
  start_time: '',
  notify_attendees: true
})

// Computed properties
const canEdit = computed(() => {
  return calendarService.isEventEditable(props.event)
})

const canDelete = computed(() => {
  return canEdit.value && props.event.calendar_account
})

const canReschedule = computed(() => {
  return canEdit.value && props.event.status !== 'cancelled'
})

const isPastEvent = computed(() => {
  return new Date(props.event.end_datetime) < new Date()
})

// Methods
const initializeEditForm = () => {
  const startDate = new Date(props.event.start_datetime)
  const endDate = new Date(props.event.end_datetime)
  
  editForm.value = {
    title: props.event.title,
    description: props.event.description || '',
    date: startDate.toISOString().split('T')[0],
    start_time: startDate.toTimeString().slice(0, 5),
    end_time: endDate.toTimeString().slice(0, 5),
    location: props.event.location || '',
    status: props.event.status
  }
}

const initializeRescheduleForm = () => {
  const startDate = new Date(props.event.start_datetime)
  
  rescheduleForm.value = {
    date: startDate.toISOString().split('T')[0],
    start_time: startDate.toTimeString().slice(0, 5),
    notify_attendees: true
  }
}

const startEditing = () => {
  initializeEditForm()
  isEditing.value = true
}

const cancelEditing = () => {
  isEditing.value = false
  editForm.value = {}
}

const saveChanges = async () => {
  saving.value = true
  error.value = ''
  
  try {
    const updateData = {
      title: editForm.value.title,
      description: editForm.value.description,
      start_datetime: `${editForm.value.date}T${editForm.value.start_time}`,
      end_datetime: `${editForm.value.date}T${editForm.value.end_time}`,
      location: editForm.value.location,
      status: editForm.value.status
    }
    
    const updatedEvent = await calendarStore.updateEvent(props.event.id, updateData)
    emit('event-updated', updatedEvent)
    isEditing.value = false
  } catch (err) {
    console.error('Error updating event:', err)
    error.value = 'Failed to update meeting. Please try again.'
  } finally {
    saving.value = false
  }
}

const rescheduleEvent = async () => {
  rescheduling.value = true
  error.value = ''
  
  try {
    const duration = new Date(props.event.end_datetime) - new Date(props.event.start_datetime)
    const newStart = new Date(`${rescheduleForm.value.date}T${rescheduleForm.value.start_time}`)
    const newEnd = new Date(newStart.getTime() + duration)
    
    const updatedEvent = await calendarStore.rescheduleMeeting(props.event.id, {
      start: newStart.toISOString(),
      end: newEnd.toISOString()
    })
    
    emit('event-updated', updatedEvent)
    showRescheduleModal.value = false
  } catch (err) {
    console.error('Error rescheduling event:', err)
    error.value = 'Failed to reschedule meeting. Please try again.'
  } finally {
    rescheduling.value = false
  }
}

const cancelMeeting = async () => {
  try {
    const cancelledEvent = await calendarStore.cancelMeeting(props.event.id)
    emit('event-updated', cancelledEvent)
  } catch (err) {
    console.error('Error cancelling meeting:', err)
    error.value = 'Failed to cancel meeting. Please try again.'
  }
}

const deleteEvent = async () => {
  deleting.value = true
  error.value = ''
  
  try {
    await calendarStore.deleteEvent(props.event.id)
    emit('event-deleted', props.event.id)
    confirmDelete.value = false
  } catch (err) {
    console.error('Error deleting event:', err)
    error.value = 'Failed to delete meeting. Please try again.'
  } finally {
    deleting.value = false
  }
}

const duplicateEvent = () => {
  // Emit event to parent to open meeting scheduler with prefilled data
  emit('duplicate-event', props.event)
}

const joinMeeting = () => {
  if (props.event.meeting_url) {
    window.open(props.event.meeting_url, '_blank')
  }
}

const addToCalendar = () => {
  // Generate calendar file or link
  const startDate = new Date(props.event.start_datetime)
  const endDate = new Date(props.event.end_datetime)
  
  const event = {
    title: props.event.title,
    start: startDate,
    end: endDate,
    description: props.event.description || '',
    location: props.event.location || ''
  }
  
  // Create .ics file content
  const icsContent = generateICS(event)
  
  // Create download link
  const blob = new Blob([icsContent], { type: 'text/calendar' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.event.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.ics`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  URL.revokeObjectURL(url)
}

const copyMeetingLink = async () => {
  if (props.event.meeting_url) {
    try {
      await navigator.clipboard.writeText(props.event.meeting_url)
      // Show success toast or notification
      console.log('Meeting link copied to clipboard')
    } catch (err) {
      console.error('Failed to copy meeting link:', err)
    }
  }
}

const saveNotes = async () => {
  savingNotes.value = true
  
  try {
    // This would typically save to a notes API endpoint
    meetingNotes.value = notesForm.value
    editingNotes.value = false
    
    // You could also update the event with notes
    // await calendarStore.updateEvent(props.event.id, { notes: notesForm.value })
  } catch (err) {
    console.error('Error saving notes:', err)
    error.value = 'Failed to save notes. Please try again.'
  } finally {
    savingNotes.value = false
  }
}

const cancelNotesEdit = () => {
  editingNotes.value = false
  notesForm.value = meetingNotes.value
}

// Utility methods
const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'confirmed':
      return 'bg-success'
    case 'tentative':
      return 'bg-warning text-dark'
    case 'cancelled':
      return 'bg-danger'
    default:
      return 'bg-secondary'
  }
}

const getAttendeeStatusClass = (status) => {
  switch (status) {
    case 'accepted':
      return 'bg-success'
    case 'declined':
      return 'bg-danger'
    case 'tentative':
      return 'bg-warning text-dark'
    default:
      return 'bg-secondary'
  }
}

const formatAttendeeStatus = (status) => {
  switch (status) {
    case 'accepted':
      return 'Accepted'
    case 'declined':
      return 'Declined'
    case 'tentative':
      return 'Maybe'
    default:
      return 'Pending'
  }
}

const getInitials = (name) => {
  return name
    .split(' ')
    .map(part => part.charAt(0).toUpperCase())
    .join('')
    .substring(0, 2)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

const formatTimeRange = (startString, endString) => {
  return `${formatTime(startString)} - ${formatTime(endString)}`
}

const formatReminderTime = (minutes) => {
  if (minutes < 60) return `${minutes} minutes`
  if (minutes < 1440) return `${Math.floor(minutes / 60)} hours`
  return `${Math.floor(minutes / 1440)} days`
}

const generateICS = (event) => {
  const formatICSDate = (date) => {
    return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'
  }
  
  const now = new Date()
  const uid = `${now.getTime()}@retirementadvisorpro.com`
  
  return `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//RetirementAdvisorPro//Event//EN
BEGIN:VEVENT
UID:${uid}
DTSTART:${formatICSDate(event.start)}
DTEND:${formatICSDate(event.end)}
SUMMARY:${event.title}
DESCRIPTION:${event.description}
LOCATION:${event.location}
DTSTAMP:${formatICSDate(now)}
END:VEVENT
END:VCALENDAR`
}

// Lifecycle
onMounted(() => {
  initializeRescheduleForm()
  notesForm.value = meetingNotes.value
})
</script>

<style scoped>
.meeting-details {
  padding: 1rem 0;
}

.meeting-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1.5rem;
}

.meeting-title {
  color: #212529;
  margin-bottom: 0.75rem;
}

.meeting-meta .badge {
  font-size: 0.75rem;
}

.info-section {
  margin-bottom: 2rem;
}

.section-title {
  color: #495057;
  font-weight: 600;
  margin-bottom: 1rem;
  border-bottom: 2px solid #f8f9fa;
  padding-bottom: 0.5rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.info-item i {
  margin-top: 0.25rem;
  width: 20px;
  flex-shrink: 0;
}

.info-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-weight: 500;
  color: #212529;
}

.description-content {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.25rem;
  border: 1px solid #e9ecef;
  white-space: pre-wrap;
  line-height: 1.6;
}

.attendees-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attendee-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border: 1px solid #e9ecef;
}

.attendee-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.attendee-info {
  flex: 1;
}

.attendee-name {
  font-weight: 500;
  color: #212529;
}

.attendee-email {
  font-size: 0.875rem;
  color: #6c757d;
}

.attendee-status {
  margin-left: 0.75rem;
}

.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reminder-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #e3f2fd;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1565c0;
}

.notes-display,
.notes-editor {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #e9ecef;
}

.notes-content {
  white-space: pre-wrap;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.no-notes {
  font-style: italic;
  margin-bottom: 1rem;
}

.quick-actions {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.25rem;
  border: 1px solid #e9ecef;
}

.meeting-info-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.25rem;
  border: 1px solid #e9ecef;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.info-row .label {
  color: #6c757d;
  font-weight: 500;
}

.info-row .value {
  color: #212529;
  font-weight: 500;
}

.related-items {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1.25rem;
  border: 1px solid #e9ecef;
}

.related-item {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
}

.form-actions {
  border-top: 1px solid #dee2e6;
  padding-top: 1.5rem;
  margin-top: 2rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-xl {
    margin: 0.5rem;
  }
  
  .meeting-header {
    padding-bottom: 1rem;
  }
  
  .meeting-header .d-flex {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .meeting-actions {
    align-self: flex-end;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .attendee-item {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .attendee-avatar {
    margin-right: 0;
  }
  
  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}

@media (max-width: 576px) {
  .modal-body {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 1rem;
  }
  
  .quick-actions,
  .meeting-info-card,
  .related-items {
    margin-bottom: 1rem;
  }
}
</style>