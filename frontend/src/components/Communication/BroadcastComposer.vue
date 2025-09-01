<template>
  <div class="broadcast-composer">
    <form @submit.prevent="handleSave">
      <div class="row">
        <!-- Message Details -->
        <div class="col-md-8">
          <div class="mb-3">
            <label for="title" class="form-label">Broadcast Title *</label>
            <input 
              type="text" 
              class="form-control" 
              id="title"
              v-model="broadcast.title" 
              required
              maxlength="200"
            >
            <div class="form-text">{{ broadcast.title.length }}/200 characters</div>
          </div>
          
          <div class="mb-3">
            <label for="message" class="form-label">Message Content *</label>
            <textarea 
              class="form-control" 
              id="message"
              v-model="broadcast.message" 
              rows="6"
              required
              maxlength="2000"
            ></textarea>
            <div class="form-text">{{ broadcast.message.length }}/2000 characters</div>
          </div>

          <!-- Action Button -->
          <div class="mb-3">
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="hasActionButton"
                v-model="broadcast.has_action_button"
              >
              <label class="form-check-label" for="hasActionButton">
                Include action button
              </label>
            </div>
          </div>

          <div v-if="broadcast.has_action_button" class="row mb-3">
            <div class="col-6">
              <label for="actionButtonText" class="form-label">Button Text</label>
              <input 
                type="text" 
                class="form-control" 
                id="actionButtonText"
                v-model="broadcast.action_button_text"
                maxlength="50"
              >
            </div>
            <div class="col-6">
              <label for="actionButtonUrl" class="form-label">Button URL</label>
              <input 
                type="url" 
                class="form-control" 
                id="actionButtonUrl"
                v-model="broadcast.action_button_url"
              >
            </div>
          </div>
        </div>

        <!-- Settings -->
        <div class="col-md-4">
          <div class="mb-3">
            <label for="messageType" class="form-label">Message Type *</label>
            <select class="form-select" id="messageType" v-model="broadcast.message_type" required>
              <option value="">Select Type</option>
              <option value="announcement">Announcement</option>
              <option value="maintenance">Maintenance Alert</option>
              <option value="feature_update">Feature Update</option>
              <option value="promotion">Promotion</option>
              <option value="urgent">Urgent Notice</option>
              <option value="newsletter">Newsletter</option>
            </select>
          </div>

          <div class="mb-3">
            <label for="deliveryMethod" class="form-label">Delivery Method *</label>
            <select class="form-select" id="deliveryMethod" v-model="broadcast.delivery_method" required>
              <option value="both">In-App + Email</option>
              <option value="in_app">In-App Only</option>
              <option value="email">Email Only</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">Send Schedule</label>
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="radio" 
                name="sendSchedule" 
                id="sendNow"
                v-model="broadcast.send_immediately"
                :value="true"
              >
              <label class="form-check-label" for="sendNow">
                Send immediately
              </label>
            </div>
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="radio" 
                name="sendSchedule" 
                id="sendLater"
                v-model="broadcast.send_immediately"
                :value="false"
              >
              <label class="form-check-label" for="sendLater">
                Schedule for later
              </label>
            </div>
          </div>

          <div v-if="!broadcast.send_immediately" class="mb-3">
            <label for="scheduledTime" class="form-label">Scheduled Send Time</label>
            <input 
              type="datetime-local" 
              class="form-control" 
              id="scheduledTime"
              v-model="scheduledDateTime"
            >
          </div>
        </div>
      </div>

      <!-- Target Audience -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Target Audience</h6>
        
        <div class="mb-3">
          <div class="form-check">
            <input 
              class="form-check-input" 
              type="radio" 
              name="targetAudience" 
              id="allUsers"
              v-model="audienceType"
              value="all"
            >
            <label class="form-check-label" for="allUsers">
              <strong>All Users</strong>
              <div class="text-muted small">Send to all active users</div>
            </label>
          </div>
        </div>

        <div class="mb-3">
          <div class="form-check">
            <input 
              class="form-check-input" 
              type="radio" 
              name="targetAudience" 
              id="segments"
              v-model="audienceType"
              value="segments"
            >
            <label class="form-check-label" for="segments">
              <strong>User Segments</strong>
              <div class="text-muted small">Target specific user groups</div>
            </label>
          </div>
        </div>

        <div v-if="audienceType === 'segments'" class="ms-4 mb-3">
          <div class="row">
            <div class="col-md-6">
              <label class="form-label">User Roles</label>
              <div class="form-check" v-for="role in availableRoles" :key="role.value">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="role.value"
                  :value="role.value"
                  v-model="broadcast.target_roles"
                >
                <label class="form-check-label" :for="role.value">
                  {{ role.label }}
                </label>
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">User Segments</label>
              <div class="form-check" v-for="segment in availableSegments" :key="segment.value">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="segment.value"
                  :value="segment.value"
                  v-model="selectedSegments"
                >
                <label class="form-check-label" :for="segment.value">
                  {{ segment.label }}
                  <div class="text-muted small">{{ segment.description }}</div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <div class="form-check">
            <input 
              class="form-check-input" 
              type="radio" 
              name="targetAudience" 
              id="specific"
              v-model="audienceType"
              value="specific"
            >
            <label class="form-check-label" for="specific">
              <strong>Specific Users</strong>
              <div class="text-muted small">Select individual users</div>
            </label>
          </div>
        </div>

        <div v-if="audienceType === 'specific'" class="ms-4 mb-3">
          <label for="userSearch" class="form-label">Search and Select Users</label>
          <input 
            type="text" 
            class="form-control mb-2" 
            id="userSearch"
            placeholder="Type user name or email..."
            v-model="userSearchQuery"
            @input="searchUsers"
          >
          
          <!-- Selected Users -->
          <div v-if="selectedUsers.length > 0" class="mb-3">
            <label class="form-label">Selected Users ({{ selectedUsers.length }})</label>
            <div class="selected-users">
              <span 
                v-for="user in selectedUsers" 
                :key="user.id"
                class="badge bg-primary me-1 mb-1"
              >
                {{ user.name || user.email }}
                <button 
                  type="button" 
                  class="btn-close btn-close-white ms-1" 
                  aria-label="Remove"
                  @click="removeUser(user)"
                ></button>
              </span>
            </div>
          </div>

          <!-- Search Results -->
          <div v-if="userSearchResults.length > 0" class="search-results border rounded p-2" style="max-height: 200px; overflow-y: auto;">
            <div 
              v-for="user in userSearchResults" 
              :key="user.id"
              class="search-result-item d-flex justify-content-between align-items-center p-2 hover-bg-light"
              @click="addUser(user)"
              style="cursor: pointer;"
            >
              <div>
                <strong>{{ user.name || user.email }}</strong>
                <div class="text-muted small">{{ user.email }}</div>
              </div>
              <i class="fas fa-plus text-primary"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Section -->
      <div class="mb-4" v-if="showPreview">
        <h6 class="border-bottom pb-2">Message Preview</h6>
        <div class="alert alert-light border">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <strong>{{ broadcast.title || 'Broadcast Title' }}</strong>
              <span class="badge bg-secondary ms-2">{{ formatMessageType(broadcast.message_type) }}</span>
            </div>
            <small class="text-muted">Now</small>
          </div>
          <p class="mb-2">{{ broadcast.message || 'Your message content will appear here...' }}</p>
          <div v-if="broadcast.has_action_button && broadcast.action_button_text">
            <button class="btn btn-primary btn-sm" disabled>
              {{ broadcast.action_button_text }}
            </button>
          </div>
        </div>
        <div class="text-muted small">
          <i class="fas fa-info-circle me-1"></i>
          This is how your message will appear to users
        </div>
      </div>

      <!-- Estimated Recipients -->
      <div class="mb-4" v-if="estimatedRecipients > 0">
        <div class="alert alert-info">
          <i class="fas fa-users me-2"></i>
          Estimated recipients: <strong>{{ estimatedRecipients }}</strong>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="d-flex justify-content-between">
        <div>
          <button type="button" class="btn btn-outline-secondary me-2" @click="resetForm">
            <i class="fas fa-undo me-1"></i>Reset
          </button>
          <button type="button" class="btn btn-outline-info" @click="togglePreview">
            <i class="fas fa-eye me-1"></i>{{ showPreview ? 'Hide' : 'Show' }} Preview
          </button>
          <button type="button" class="btn btn-outline-warning ms-2" @click="previewRecipients">
            <i class="fas fa-users me-1"></i>Preview Recipients
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-secondary me-2" @click="$emit('cancel')">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isValid">
            <i class="fas fa-save me-1"></i>
            {{ broadcast.send_immediately ? 'Create & Send' : 'Create Broadcast' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import api from '@/services/api'

export default {
  name: 'BroadcastComposer',
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const broadcast = ref({
      title: '',
      message: '',
      message_type: '',
      delivery_method: 'both',
      target_all_users: false,
      target_roles: [],
      target_user_segments: {},
      specific_users: [],
      send_immediately: true,
      scheduled_send_time: null,
      has_action_button: false,
      action_button_text: '',
      action_button_url: ''
    })

    const audienceType = ref('all')
    const selectedSegments = ref([])
    const selectedUsers = ref([])
    const userSearchQuery = ref('')
    const userSearchResults = ref([])
    const scheduledDateTime = ref('')
    const showPreview = ref(false)
    const estimatedRecipients = ref(0)

    const availableRoles = [
      { value: 'advisor', label: 'Financial Advisors' },
      { value: 'admin', label: 'Administrators' },
      { value: 'manager', label: 'Managers' },
      { value: 'user', label: 'Regular Users' }
    ]

    const availableSegments = [
      { value: 'new_users', label: 'New Users', description: 'Users who joined in the last 30 days' },
      { value: 'active_users', label: 'Active Users', description: 'Users active in the last 7 days' },
      { value: 'inactive_users', label: 'Inactive Users', description: 'Users not active in 30+ days' },
      { value: 'high_value', label: 'High Value Users', description: 'Users with premium subscriptions' },
      { value: 'trial_ending', label: 'Trial Ending', description: 'Trial users with <7 days left' }
    ]

    const isValid = computed(() => {
      const hasTitle = broadcast.value.title.trim().length > 0
      const hasMessage = broadcast.value.message.trim().length > 0
      const hasType = broadcast.value.message_type.length > 0
      const hasAudience = broadcast.value.target_all_users || 
                         broadcast.value.target_roles.length > 0 || 
                         selectedSegments.value.length > 0 ||
                         selectedUsers.value.length > 0

      return hasTitle && hasMessage && hasType && hasAudience
    })

    // Watch for audience type changes
    watch(audienceType, (newType) => {
      broadcast.value.target_all_users = newType === 'all'
      if (newType !== 'segments') {
        broadcast.value.target_roles = []
        selectedSegments.value = []
      }
      if (newType !== 'specific') {
        selectedUsers.value = []
      }
      updateEstimatedRecipients()
    })

    // Watch for segment changes
    watch(selectedSegments, () => {
      const segments = {}
      selectedSegments.value.forEach(segment => {
        segments[segment] = true
      })
      broadcast.value.target_user_segments = segments
      updateEstimatedRecipients()
    }, { deep: true })

    // Watch for selected users changes
    watch(selectedUsers, () => {
      broadcast.value.specific_users = selectedUsers.value.map(user => user.id)
      updateEstimatedRecipients()
    }, { deep: true })

    // Watch for scheduled time changes
    watch(scheduledDateTime, (newDateTime) => {
      if (newDateTime) {
        broadcast.value.scheduled_send_time = new Date(newDateTime).toISOString()
      } else {
        broadcast.value.scheduled_send_time = null
      }
    })

    const searchUsers = async () => {
      if (!userSearchQuery.value || userSearchQuery.value.length < 2) {
        userSearchResults.value = []
        return
      }

      try {
        const response = await api.get(`/api/users/?search=${userSearchQuery.value}`)
        userSearchResults.value = (response.data.results || response.data)
          .filter(user => !selectedUsers.value.some(selected => selected.id === user.id))
          .slice(0, 10) // Limit to 10 results
      } catch (error) {
        console.error('Error searching users:', error)
      }
    }

    const addUser = (user) => {
      if (!selectedUsers.value.some(selected => selected.id === user.id)) {
        selectedUsers.value.push({
          id: user.id,
          name: user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : null,
          email: user.email
        })
        userSearchResults.value = userSearchResults.value.filter(u => u.id !== user.id)
        userSearchQuery.value = ''
      }
    }

    const removeUser = (user) => {
      selectedUsers.value = selectedUsers.value.filter(u => u.id !== user.id)
    }

    const updateEstimatedRecipients = () => {
      // Mock estimation logic - in a real app, this would call the backend
      if (broadcast.value.target_all_users) {
        estimatedRecipients.value = 1250 // Mock total users
      } else if (selectedUsers.value.length > 0) {
        estimatedRecipients.value = selectedUsers.value.length
      } else if (broadcast.value.target_roles.length > 0 || selectedSegments.value.length > 0) {
        // Mock calculation based on segments
        let estimate = 0
        if (broadcast.value.target_roles.includes('advisor')) estimate += 450
        if (broadcast.value.target_roles.includes('admin')) estimate += 25
        if (selectedSegments.value.includes('new_users')) estimate += 125
        if (selectedSegments.value.includes('active_users')) estimate += 800
        estimatedRecipients.value = estimate
      } else {
        estimatedRecipients.value = 0
      }
    }

    const previewRecipients = async () => {
      try {
        // This would call the backend to get actual recipient preview
        alert(`This feature would show a preview of the ${estimatedRecipients.value} users who will receive this broadcast.`)
      } catch (error) {
        console.error('Error previewing recipients:', error)
      }
    }

    const handleSave = () => {
      if (!isValid.value) return

      const broadcastData = { ...broadcast.value }

      // Clean up specific users data
      if (audienceType.value === 'specific') {
        broadcastData.specific_users = selectedUsers.value.map(user => user.id)
      }

      emit('save', broadcastData)
    }

    const resetForm = () => {
      broadcast.value = {
        title: '',
        message: '',
        message_type: '',
        delivery_method: 'both',
        target_all_users: false,
        target_roles: [],
        target_user_segments: {},
        specific_users: [],
        send_immediately: true,
        scheduled_send_time: null,
        has_action_button: false,
        action_button_text: '',
        action_button_url: ''
      }
      audienceType.value = 'all'
      selectedSegments.value = []
      selectedUsers.value = []
      userSearchQuery.value = ''
      userSearchResults.value = []
      scheduledDateTime.value = ''
      showPreview.value = false
    }

    const togglePreview = () => {
      showPreview.value = !showPreview.value
    }

    const formatMessageType = (type) => {
      if (!type) return ''
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    // Initialize
    updateEstimatedRecipients()

    return {
      broadcast,
      audienceType,
      selectedSegments,
      selectedUsers,
      userSearchQuery,
      userSearchResults,
      scheduledDateTime,
      showPreview,
      estimatedRecipients,
      availableRoles,
      availableSegments,
      isValid,
      searchUsers,
      addUser,
      removeUser,
      previewRecipients,
      handleSave,
      resetForm,
      togglePreview,
      formatMessageType
    }
  }
}
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid #dee2e6 !important;
}

.form-text {
  font-size: 0.8rem;
}

.selected-users {
  max-height: 150px;
  overflow-y: auto;
}

.search-results {
  background-color: #fff;
  z-index: 1000;
}

.search-result-item:hover,
.hover-bg-light:hover {
  background-color: #f8f9fa;
}

.btn-close-white {
  filter: invert(1) grayscale(100%) brightness(200%);
}

h6 {
  font-weight: 600;
  color: #495057;
}

.alert {
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
}

.alert-light {
  color: #495057;
  background-color: #fefefe;
  border-color: #e9ecef;
}

.alert-info {
  color: #055160;
  background-color: #cff4fc;
  border-color: #b8daff;
}

.badge {
  font-size: 0.75em;
}

.form-check-label strong {
  font-weight: 600;
}

.form-check-label .text-muted.small {
  font-size: 0.8rem;
  font-weight: normal;
}
</style>