<template>
  <div class="client-portal-appointments">
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-0">Appointments</h5>
          <small class="text-muted">Schedule and manage your meetings</small>
        </div>
        <button 
          class="btn btn-primary"
          @click="showBookingModal = true"
        >
          <i class="bi bi-plus-circle me-2"></i>
          Book Appointment
        </button>
      </div>
    </div>

    <div class="row">
      <!-- Calendar View -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-calendar me-2"></i>
              Calendar View
            </h6>
            <div class="btn-group btn-group-sm">
              <button 
                class="btn"
                :class="calendarView === 'month' ? 'btn-primary' : 'btn-outline-primary'"
                @click="calendarView = 'month'"
              >
                Month
              </button>
              <button 
                class="btn"
                :class="calendarView === 'week' ? 'btn-primary' : 'btn-outline-primary'"
                @click="calendarView = 'week'"
              >
                Week
              </button>
            </div>
          </div>
          
          <div class="card-body">
            <!-- Calendar Header -->
            <div class="calendar-header d-flex justify-content-between align-items-center mb-3">
              <div class="calendar-nav">
                <button class="btn btn-outline-secondary btn-sm me-2" @click="navigateCalendar(-1)">
                  <i class="bi bi-chevron-left"></i>
                </button>
                <button class="btn btn-outline-secondary btn-sm me-2" @click="navigateCalendar(1)">
                  <i class="bi bi-chevron-right"></i>
                </button>
                <button class="btn btn-outline-primary btn-sm" @click="goToToday">
                  Today
                </button>
              </div>
              <h5 class="mb-0">{{ currentCalendarTitle }}</h5>
            </div>

            <!-- Mini Calendar Placeholder -->
            <div class="calendar-placeholder bg-light rounded p-5 text-center">
              <i class="bi bi-calendar-week display-4 text-muted mb-3"></i>
              <h6 class="text-muted">Calendar View</h6>
              <p class="text-muted small">
                Interactive calendar will be implemented here.<br>
                For now, view your appointments in the list below.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointment List -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-list-ul me-2"></i>
              Your Appointments
            </h6>
          </div>
          
          <div class="appointment-list" style="max-height: 500px; overflow-y: auto;">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="appointments.length === 0" class="text-center py-5 text-muted">
              <i class="bi bi-calendar-x display-4 mb-3 opacity-50"></i>
              <h6>No appointments scheduled</h6>
              <p class="small mb-3">Book your first appointment with your advisor</p>
              <button 
                class="btn btn-primary btn-sm"
                @click="showBookingModal = true"
              >
                Book Now
              </button>
            </div>
            
            <div v-else>
              <!-- Upcoming Appointments -->
              <div v-if="upcomingAppointments.length > 0" class="appointment-section">
                <div class="section-header p-3 bg-light border-bottom">
                  <small class="text-muted fw-medium">UPCOMING</small>
                </div>
                <div 
                  v-for="appointment in upcomingAppointments" 
                  :key="'upcoming-' + appointment.id"
                  class="appointment-item p-3 border-bottom"
                  :class="{ 'appointment-today': isToday(appointment.scheduled_time) }"
                >
                  <div class="appointment-content">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="mb-0">{{ appointment.title }}</h6>
                      <span 
                        class="badge"
                        :class="getStatusBadgeClass(appointment.status)"
                      >
                        {{ appointment.status }}
                      </span>
                    </div>
                    
                    <div class="appointment-details small text-muted mb-2">
                      <div>
                        <i class="bi bi-calendar me-1"></i>
                        {{ formatDate(appointment.scheduled_time) }}
                      </div>
                      <div>
                        <i class="bi bi-clock me-1"></i>
                        {{ formatTime(appointment.scheduled_time) }}
                        <span v-if="appointment.duration">
                          ({{ appointment.duration }} min)
                        </span>
                      </div>
                      <div v-if="appointment.type">
                        <i class="bi bi-tag me-1"></i>
                        {{ appointment.type }}
                      </div>
                      <div v-if="appointment.location || appointment.meeting_link">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ appointment.location || 'Online Meeting' }}
                      </div>
                    </div>
                    
                    <p v-if="appointment.description" class="appointment-description small mb-2">
                      {{ appointment.description }}
                    </p>
                    
                    <div class="appointment-actions">
                      <div class="btn-group btn-group-sm w-100">
                        <button 
                          v-if="appointment.meeting_link"
                          class="btn btn-outline-success"
                          @click="joinMeeting(appointment.meeting_link)"
                        >
                          <i class="bi bi-camera-video"></i>
                        </button>
                        <button 
                          class="btn btn-outline-primary"
                          @click="viewAppointment(appointment)"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button 
                          v-if="canReschedule(appointment)"
                          class="btn btn-outline-warning"
                          @click="rescheduleAppointment(appointment)"
                        >
                          <i class="bi bi-clock-history"></i>
                        </button>
                        <button 
                          v-if="canCancel(appointment)"
                          class="btn btn-outline-danger"
                          @click="cancelAppointment(appointment)"
                        >
                          <i class="bi bi-x-circle"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Past Appointments -->
              <div v-if="pastAppointments.length > 0" class="appointment-section">
                <div class="section-header p-3 bg-light border-bottom">
                  <small class="text-muted fw-medium">PAST</small>
                </div>
                <div 
                  v-for="appointment in pastAppointments.slice(0, 5)" 
                  :key="'past-' + appointment.id"
                  class="appointment-item p-3 border-bottom opacity-75"
                >
                  <div class="appointment-content">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="mb-0">{{ appointment.title }}</h6>
                      <span class="badge bg-secondary">Completed</span>
                    </div>
                    
                    <div class="appointment-details small text-muted mb-2">
                      <div>
                        <i class="bi bi-calendar me-1"></i>
                        {{ formatDate(appointment.scheduled_time) }}
                      </div>
                      <div>
                        <i class="bi bi-clock me-1"></i>
                        {{ formatTime(appointment.scheduled_time) }}
                      </div>
                    </div>
                    
                    <div class="appointment-actions">
                      <button 
                        class="btn btn-outline-secondary btn-sm"
                        @click="viewAppointment(appointment)"
                      >
                        <i class="bi bi-eye me-1"></i>
                        View Details
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

    <!-- Book Appointment Modal -->
    <Teleport to="body">
      <div v-if="showBookingModal" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-calendar-plus me-2"></i>
                  Book Appointment
                </h5>
                <button type="button" class="btn-close" @click="closeBookingModal"></button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="bookAppointment">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Appointment Type</label>
                      <select v-model="newAppointment.type" class="form-select" required>
                        <option value="">Select type</option>
                        <option value="consultation">Initial Consultation</option>
                        <option value="review">Portfolio Review</option>
                        <option value="planning">Retirement Planning</option>
                        <option value="tax_planning">Tax Planning</option>
                        <option value="follow_up">Follow-up Meeting</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Duration</label>
                      <select v-model="newAppointment.duration" class="form-select" required>
                        <option value="30">30 minutes</option>
                        <option value="45">45 minutes</option>
                        <option value="60">1 hour</option>
                        <option value="90">1.5 hours</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Preferred Date</label>
                      <input 
                        v-model="newAppointment.date"
                        type="date" 
                        class="form-control"
                        :min="minDate"
                        required
                      />
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Preferred Time</label>
                      <select v-model="newAppointment.time" class="form-select" required>
                        <option value="">Select time</option>
                        <option value="09:00">9:00 AM</option>
                        <option value="09:30">9:30 AM</option>
                        <option value="10:00">10:00 AM</option>
                        <option value="10:30">10:30 AM</option>
                        <option value="11:00">11:00 AM</option>
                        <option value="11:30">11:30 AM</option>
                        <option value="13:00">1:00 PM</option>
                        <option value="13:30">1:30 PM</option>
                        <option value="14:00">2:00 PM</option>
                        <option value="14:30">2:30 PM</option>
                        <option value="15:00">3:00 PM</option>
                        <option value="15:30">3:30 PM</option>
                        <option value="16:00">4:00 PM</option>
                        <option value="16:30">4:30 PM</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Meeting Preference</label>
                    <div class="form-check">
                      <input 
                        v-model="newAppointment.meeting_type"
                        class="form-check-input" 
                        type="radio" 
                        value="online" 
                        id="online"
                      />
                      <label class="form-check-label" for="online">
                        Online Meeting (Video Call)
                      </label>
                    </div>
                    <div class="form-check">
                      <input 
                        v-model="newAppointment.meeting_type"
                        class="form-check-input" 
                        type="radio" 
                        value="in_person" 
                        id="in_person"
                      />
                      <label class="form-check-label" for="in_person">
                        In-Person Meeting
                      </label>
                    </div>
                    <div class="form-check">
                      <input 
                        v-model="newAppointment.meeting_type"
                        class="form-check-input" 
                        type="radio" 
                        value="phone" 
                        id="phone"
                      />
                      <label class="form-check-label" for="phone">
                        Phone Call
                      </label>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Subject/Title</label>
                    <input 
                      v-model="newAppointment.title"
                      type="text" 
                      class="form-control"
                      placeholder="What would you like to discuss?"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label">Additional Details (Optional)</label>
                    <textarea 
                      v-model="newAppointment.description"
                      class="form-control"
                      rows="3"
                      placeholder="Any specific topics or questions you'd like to discuss..."
                    ></textarea>
                  </div>
                </form>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeBookingModal">
                  Cancel
                </button>
                <button 
                  type="button" 
                  class="btn btn-primary"
                  @click="bookAppointment"
                  :disabled="!isBookingFormValid || booking"
                >
                  <div v-if="booking" class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                      <span class="visually-hidden">Booking...</span>
                    </div>
                    Booking...
                  </div>
                  <div v-else>
                    <i class="bi bi-calendar-check me-2"></i>
                    Book Appointment
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="closeBookingModal"></div>
      </div>
    </Teleport>

    <!-- Appointment Detail Modal -->
    <Teleport to="body">
      <div v-if="viewingAppointment" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-calendar-event me-2"></i>
                  Appointment Details
                </h5>
                <button type="button" class="btn-close" @click="viewingAppointment = null"></button>
              </div>
              <div class="modal-body">
                <div class="appointment-details">
                  <h6>{{ viewingAppointment.title }}</h6>
                  
                  <div class="detail-row mb-2">
                    <strong>Date & Time:</strong>
                    {{ formatDateTime(viewingAppointment.scheduled_time) }}
                  </div>
                  
                  <div class="detail-row mb-2">
                    <strong>Duration:</strong>
                    {{ viewingAppointment.duration || 60 }} minutes
                  </div>
                  
                  <div class="detail-row mb-2">
                    <strong>Type:</strong>
                    {{ viewingAppointment.type }}
                  </div>
                  
                  <div class="detail-row mb-2">
                    <strong>Status:</strong>
                    <span 
                      class="badge"
                      :class="getStatusBadgeClass(viewingAppointment.status)"
                    >
                      {{ viewingAppointment.status }}
                    </span>
                  </div>
                  
                  <div v-if="viewingAppointment.location" class="detail-row mb-2">
                    <strong>Location:</strong>
                    {{ viewingAppointment.location }}
                  </div>
                  
                  <div v-if="viewingAppointment.meeting_link" class="detail-row mb-2">
                    <strong>Meeting Link:</strong>
                    <a :href="viewingAppointment.meeting_link" target="_blank" class="btn btn-sm btn-outline-success ms-2">
                      <i class="bi bi-camera-video me-1"></i>
                      Join Meeting
                    </a>
                  </div>
                  
                  <div v-if="viewingAppointment.description" class="detail-row mb-2">
                    <strong>Description:</strong>
                    <p class="mt-1 mb-0">{{ viewingAppointment.description }}</p>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="viewingAppointment = null">
                  Close
                </button>
                <div v-if="canReschedule(viewingAppointment)" class="btn-group">
                  <button 
                    type="button" 
                    class="btn btn-outline-warning"
                    @click="rescheduleAppointment(viewingAppointment)"
                  >
                    <i class="bi bi-clock-history me-1"></i>
                    Reschedule
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-danger"
                    @click="cancelAppointment(viewingAppointment)"
                  >
                    <i class="bi bi-x-circle me-1"></i>
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="viewingAppointment = null"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
})

// State
const appointments = ref([])
const loading = ref(false)
const showBookingModal = ref(false)
const viewingAppointment = ref(null)
const booking = ref(false)
const calendarView = ref('month')
const currentDate = ref(new Date())

const newAppointment = ref({
  type: '',
  duration: '60',
  date: '',
  time: '',
  meeting_type: 'online',
  title: '',
  description: ''
})

// Computed
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const upcomingAppointments = computed(() => {
  const now = new Date()
  return appointments.value
    .filter(apt => new Date(apt.scheduled_time) >= now)
    .sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time))
})

const pastAppointments = computed(() => {
  const now = new Date()
  return appointments.value
    .filter(apt => new Date(apt.scheduled_time) < now)
    .sort((a, b) => new Date(b.scheduled_time) - new Date(a.scheduled_time))
})

const currentCalendarTitle = computed(() => {
  if (calendarView.value === 'month') {
    return currentDate.value.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long' 
    })
  } else {
    return `Week of ${currentDate.value.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })}`
  }
})

const isBookingFormValid = computed(() => {
  return newAppointment.value.type &&
         newAppointment.value.duration &&
         newAppointment.value.date &&
         newAppointment.value.time &&
         newAppointment.value.meeting_type &&
         newAppointment.value.title.trim()
})

// Methods
const loadAppointments = async () => {
  loading.value = true
  try {
    // Mock appointments for demonstration
    appointments.value = [
      {
        id: 1,
        title: 'Quarterly Portfolio Review',
        scheduled_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        duration: 60,
        type: 'Portfolio Review',
        status: 'confirmed',
        meeting_link: 'https://meet.example.com/abc123',
        description: 'Review Q4 performance and discuss 2024 strategy'
      },
      {
        id: 2,
        title: 'Retirement Planning Session',
        scheduled_time: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        duration: 90,
        type: 'Retirement Planning',
        status: 'pending',
        location: '123 Main St, Office Suite 200',
        description: 'Comprehensive retirement planning discussion'
      },
      {
        id: 3,
        title: 'Tax Planning Meeting',
        scheduled_time: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        duration: 45,
        type: 'Tax Planning',
        status: 'completed',
        description: 'Year-end tax optimization strategies'
      }
    ]
  } catch (error) {
    console.error('Failed to load appointments:', error)
  } finally {
    loading.value = false
  }
}

const bookAppointment = async () => {
  if (!isBookingFormValid.value) return
  
  booking.value = true
  try {
    // Mock booking API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Add to appointments list
    const scheduledTime = new Date(`${newAppointment.value.date}T${newAppointment.value.time}:00`)
    appointments.value.push({
      id: Date.now(),
      title: newAppointment.value.title,
      scheduled_time: scheduledTime.toISOString(),
      duration: parseInt(newAppointment.value.duration),
      type: newAppointment.value.type,
      status: 'pending',
      description: newAppointment.value.description,
      meeting_link: newAppointment.value.meeting_type === 'online' ? 'https://meet.example.com/new123' : null,
      location: newAppointment.value.meeting_type === 'in_person' ? 'To be confirmed' : null
    })
    
    closeBookingModal()
    alert('Appointment request submitted! Your advisor will confirm the details shortly.')
    
  } catch (error) {
    console.error('Failed to book appointment:', error)
    alert('Failed to book appointment. Please try again.')
  } finally {
    booking.value = false
  }
}

const closeBookingModal = () => {
  showBookingModal.value = false
  newAppointment.value = {
    type: '',
    duration: '60',
    date: '',
    time: '',
    meeting_type: 'online',
    title: '',
    description: ''
  }
}

const viewAppointment = (appointment) => {
  viewingAppointment.value = appointment
}

const rescheduleAppointment = (appointment) => {
  alert(`Reschedule functionality for "${appointment.title}" will be implemented soon.`)
}

const cancelAppointment = async (appointment) => {
  if (confirm(`Are you sure you want to cancel "${appointment.title}"?`)) {
    try {
      // Mock cancel API call
      appointment.status = 'cancelled'
      alert('Appointment cancelled successfully.')
    } catch (error) {
      console.error('Failed to cancel appointment:', error)
      alert('Failed to cancel appointment. Please contact your advisor.')
    }
  }
}

const joinMeeting = (meetingLink) => {
  window.open(meetingLink, '_blank')
}

const canReschedule = (appointment) => {
  const appointmentTime = new Date(appointment.scheduled_time)
  const now = new Date()
  const hoursUntilAppointment = (appointmentTime - now) / (1000 * 60 * 60)
  return hoursUntilAppointment > 24 && appointment.status !== 'cancelled'
}

const canCancel = (appointment) => {
  const appointmentTime = new Date(appointment.scheduled_time)
  const now = new Date()
  const hoursUntilAppointment = (appointmentTime - now) / (1000 * 60 * 60)
  return hoursUntilAppointment > 4 && appointment.status !== 'cancelled'
}

const navigateCalendar = (direction) => {
  const newDate = new Date(currentDate.value)
  if (calendarView.value === 'month') {
    newDate.setMonth(newDate.getMonth() + direction)
  } else {
    newDate.setDate(newDate.getDate() + (direction * 7))
  }
  currentDate.value = newDate
}

const goToToday = () => {
  currentDate.value = new Date()
}

const isToday = (dateString) => {
  const appointmentDate = new Date(dateString)
  const today = new Date()
  return appointmentDate.toDateString() === today.toDateString()
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    weekday: 'short'
  })
}

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit'
  })
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    weekday: 'short',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const getStatusBadgeClass = (status) => {
  const statusMap = {
    'confirmed': 'bg-success',
    'pending': 'bg-warning text-dark',
    'cancelled': 'bg-danger',
    'completed': 'bg-secondary',
    'rescheduled': 'bg-info'
  }
  return statusMap[status] || 'bg-secondary'
}

// Lifecycle
onMounted(() => {
  loadAppointments()
})
</script>

<style scoped>
.client-portal-appointments {
  padding: 0;
}

.page-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.calendar-placeholder {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.appointment-list {
  border-top: 1px solid #dee2e6;
}

.appointment-item {
  transition: background-color 0.2s ease;
}

.appointment-item:hover {
  background-color: #f8f9fa;
}

.appointment-item.appointment-today {
  border-left: 4px solid #007bff;
  background-color: #f0f8ff;
}

.section-header {
  position: sticky;
  top: 0;
  z-index: 1;
}

.appointment-actions .btn-group .btn {
  flex: 1;
}

.appointment-content h6 {
  color: #212529;
}

.appointment-details div {
  margin-bottom: 0.25rem;
}

.appointment-details i {
  width: 16px;
  color: #6c757d;
}

.appointment-description {
  color: #495057;
  font-style: italic;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.detail-row strong {
  min-width: 120px;
  color: #495057;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

.modal-overlay .modal {
  position: relative;
  z-index: 10001;
}

.modal-overlay .modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 10000;
}
</style>