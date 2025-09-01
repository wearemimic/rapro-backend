<template>
  <div class="communication-list">
    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading communications...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="communications.length === 0" class="text-center py-5">
      <div class="avatar avatar-xl avatar-circle bg-soft-secondary text-secondary mx-auto mb-3">
        <i class="bi-inbox"></i>
      </div>
      <h5 class="text-secondary mb-2">No Communications Found</h5>
      <p class="text-muted mb-0">
        There are no communications matching your current filters.
      </p>
    </div>

    <!-- Communications List -->
    <div v-else class="list-group list-group-flush">
      <!-- Select All Header -->
      <div class="list-group-item bg-light border-0 py-2" v-if="communications.length > 0">
        <div class="d-flex align-items-center">
          <div class="form-check me-3">
            <input 
              class="form-check-input" 
              type="checkbox" 
              :checked="allSelected"
              @change="toggleSelectAll"
              id="selectAll"
            >
            <label class="form-check-label" for="selectAll">
              <small class="text-muted">Select all</small>
            </label>
          </div>
          <small class="text-muted">
            {{ communications.length }} communication{{ communications.length !== 1 ? 's' : '' }}
          </small>
        </div>
      </div>

      <!-- Communication Items -->
      <div 
        v-for="communication in communications" 
        :key="communication.id"
        class="list-group-item list-group-item-action border-0 communication-item"
        :class="{ 
          'unread': !communication.is_read,
          'selected': isSelected(communication.id),
          'high-priority': isHighPriority(communication)
        }"
      >
        <div class="row align-items-center">
          <!-- Selection Checkbox -->
          <div class="col-auto">
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                :checked="isSelected(communication.id)"
                @change="toggleSelection(communication.id)"
                :id="`comm-${communication.id}`"
              >
            </div>
          </div>

          <!-- Communication Content -->
          <div class="col">
            <div class="d-flex align-items-start">
              <!-- Type Icon -->
              <div class="flex-shrink-0 me-3">
                <div 
                  class="avatar avatar-sm avatar-circle"
                  :class="getTypeAvatarClass(communication.communication_type)"
                >
                  <i :class="getTypeIcon(communication.communication_type)"></i>
                </div>
              </div>

              <!-- Content -->
              <div class="flex-grow-1 min-w-0">
                <div class="d-flex align-items-center justify-content-between mb-1">
                  <div class="d-flex align-items-center">
                    <!-- Recipient Name -->
                    <h6 class="text-truncate mb-0 me-2" @click="viewCommunication(communication.id)" role="button">
                      {{ getRecipientName(communication) }}
                    </h6>

                    <!-- Priority Indicator -->
                    <span 
                      v-if="isHighPriority(communication)"
                      class="badge badge-sm bg-danger ms-1"
                      title="High Priority"
                    >
                      <i class="bi-star-fill"></i>
                    </span>

                    <!-- Unread Indicator -->
                    <span 
                      v-if="!communication.is_read"
                      class="bg-primary rounded-circle ms-1"
                      style="width: 6px; height: 6px;"
                      title="Unread"
                    ></span>
                  </div>

                  <!-- Timestamp and Actions -->
                  <div class="d-flex align-items-center">
                    <small class="text-muted me-2">{{ formatDate(communication.created_at) }}</small>
                    
                    <!-- Quick Actions Dropdown -->
                    <div class="dropdown">
                      <button 
                        class="btn btn-sm btn-ghost-secondary btn-icon"
                        type="button" 
                        data-bs-toggle="dropdown"
                      >
                        <i class="bi-three-dots-vertical"></i>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end">
                        <li>
                          <button 
                            class="dropdown-item" 
                            @click="viewCommunication(communication.id)"
                          >
                            <i class="bi-eye me-2"></i>View Details
                          </button>
                        </li>
                        <li>
                          <button 
                            class="dropdown-item" 
                            @click="toggleRead(communication.id)"
                          >
                            <i :class="communication.is_read ? 'bi-envelope' : 'bi-envelope-open'" class="me-2"></i>
                            Mark as {{ communication.is_read ? 'Unread' : 'Read' }}
                          </button>
                        </li>
                        <li v-if="communication.ai_suggested_response">
                          <button 
                            class="dropdown-item" 
                            @click="showAISuggestion(communication)"
                          >
                            <i class="bi-robot me-2"></i>View AI Suggestion
                          </button>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button 
                            class="dropdown-item text-danger" 
                            @click="deleteCommunication(communication.id)"
                          >
                            <i class="bi-trash me-2"></i>Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- Subject -->
                <h6 
                  class="text-truncate mb-1 communication-subject" 
                  @click="viewCommunication(communication.id)" 
                  role="button"
                >
                  {{ communication.subject || 'No Subject' }}
                </h6>

                <!-- Content Preview -->
                <p class="text-muted text-truncate mb-2 small">
                  {{ communication.content_preview || 'No content preview' }}
                </p>

                <!-- Tags and Metadata Row -->
                <div class="d-flex align-items-center flex-wrap gap-1">
                  <!-- Communication Type Badge -->
                  <span 
                    class="badge badge-sm"
                    :class="getTypeBadgeClass(communication.communication_type)"
                  >
                    {{ communication.communication_type.toUpperCase() }}
                  </span>

                  <!-- Direction Badge -->
                  <span 
                    class="badge badge-sm"
                    :class="getDirectionBadgeClass(communication.direction)"
                  >
                    <i :class="getDirectionIcon(communication.direction)" class="me-1"></i>
                    {{ communication.direction.toUpperCase() }}
                  </span>

                  <!-- Sentiment Badge -->
                  <span 
                    v-if="communication.ai_sentiment_label"
                    class="badge badge-sm"
                    :class="getSentimentBadgeClass(communication.ai_sentiment_label)"
                    :title="`Sentiment: ${communication.ai_sentiment_label} (${communication.ai_sentiment_score})`"
                  >
                    <i :class="getSentimentIcon(communication.ai_sentiment_label)" class="me-1"></i>
                    {{ communication.ai_sentiment_label.toUpperCase() }}
                  </span>

                  <!-- Priority Score -->
                  <span 
                    v-if="communication.ai_priority_score"
                    class="badge badge-sm bg-info"
                    :title="`Priority Score: ${communication.ai_priority_score}`"
                  >
                    Priority: {{ Math.round(communication.ai_priority_score * 100) }}%
                  </span>

                  <!-- AI Topics -->
                  <span 
                    v-if="communication.ai_topics && communication.ai_topics.length > 0"
                    class="badge badge-sm bg-light text-dark"
                    :title="`Topics: ${communication.ai_topics.join(', ')}`"
                  >
                    <i class="bi-tags me-1"></i>
                    {{ communication.ai_topics[0] }}{{ communication.ai_topics.length > 1 ? ` +${communication.ai_topics.length - 1}` : '' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Analysis Expanded View (Optional) -->
        <div 
          v-if="expandedItems.includes(communication.id) && hasAIAnalysis(communication)"
          class="mt-3 pt-3 border-top"
        >
          <div class="row">
            <div class="col-md-4" v-if="communication.ai_sentiment_score">
              <small class="text-muted">Sentiment Analysis</small>
              <div class="progress mt-1" style="height: 6px;">
                <div 
                  class="progress-bar"
                  :class="getSentimentProgressClass(communication.ai_sentiment_label)"
                  :style="{ width: Math.abs(communication.ai_sentiment_score) * 100 + '%' }"
                ></div>
              </div>
              <small class="text-muted">{{ communication.ai_sentiment_score > 0 ? 'Positive' : 'Negative' }} ({{ Math.abs(communication.ai_sentiment_score).toFixed(2) }})</small>
            </div>

            <div class="col-md-4" v-if="communication.ai_urgency_score">
              <small class="text-muted">Urgency Level</small>
              <div class="progress mt-1" style="height: 6px;">
                <div 
                  class="progress-bar bg-warning"
                  :style="{ width: communication.ai_urgency_score * 100 + '%' }"
                ></div>
              </div>
              <small class="text-muted">{{ Math.round(communication.ai_urgency_score * 100) }}% Urgent</small>
            </div>

            <div class="col-md-4" v-if="communication.ai_priority_score">
              <small class="text-muted">Priority Score</small>
              <div class="progress mt-1" style="height: 6px;">
                <div 
                  class="progress-bar"
                  :class="getPriorityProgressClass(communication.ai_priority_score)"
                  :style="{ width: communication.ai_priority_score * 100 + '%' }"
                ></div>
              </div>
              <small class="text-muted">{{ Math.round(communication.ai_priority_score * 100) }}% Priority</small>
            </div>
          </div>

          <div v-if="communication.ai_suggested_response" class="mt-2">
            <small class="text-muted">AI Suggested Response</small>
            <div class="card border-0 bg-light mt-1">
              <div class="card-body p-2">
                <small class="text-muted">{{ communication.ai_suggested_response.substring(0, 150) }}...</small>
                <button 
                  class="btn btn-sm btn-outline-primary mt-1"
                  @click="showAISuggestion(communication)"
                >
                  View Full Suggestion
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Suggestion Modal -->
    <div 
      class="modal fade" 
      id="aiSuggestionModal" 
      tabindex="-1" 
      ref="aiSuggestionModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi-robot me-2"></i>
              AI Response Suggestion
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedSuggestion">
            <div class="mb-3">
              <h6>Original Message:</h6>
              <div class="card bg-light border-0">
                <div class="card-body p-3">
                  <p class="mb-1"><strong>{{ selectedSuggestion.subject }}</strong></p>
                  <p class="mb-0 text-muted">{{ selectedSuggestion.content_preview }}</p>
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <h6>Suggested Response:</h6>
              <div class="card border-0 bg-soft-primary">
                <div class="card-body p-3">
                  <p class="mb-0">{{ selectedSuggestion.ai_suggested_response }}</p>
                </div>
              </div>
            </div>
            
            <div v-if="selectedSuggestion.ai_response_confidence">
              <small class="text-muted">
                Confidence: {{ Math.round(selectedSuggestion.ai_response_confidence * 100) }}%
              </small>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="useAISuggestion"
            >
              <i class="bi-reply me-1"></i>
              Use This Response
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  communications: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedCommunications: {
    type: Array,
    default: () => []
  },
  clientFilter: {
    type: [String, Number],
    default: null
  },
  showClientFilter: {
    type: Boolean,
    default: true
  },
  compactMode: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'select-communication',
  'deselect-communication', 
  'toggle-read',
  'view-communication',
  'delete-communication'
])

// Component state
const expandedItems = ref([])
const selectedSuggestion = ref(null)
const aiSuggestionModal = ref(null)

// Computed
const allSelected = computed(() => {
  if (props.communications.length === 0) return false
  return props.communications.every(comm => 
    props.selectedCommunications.includes(comm.id)
  )
})

// Methods
const isSelected = (id) => {
  return props.selectedCommunications.includes(id)
}

const toggleSelection = (id) => {
  if (isSelected(id)) {
    emit('deselect-communication', id)
  } else {
    emit('select-communication', id)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    // Deselect all
    props.communications.forEach(comm => {
      if (isSelected(comm.id)) {
        emit('deselect-communication', comm.id)
      }
    })
  } else {
    // Select all
    props.communications.forEach(comm => {
      if (!isSelected(comm.id)) {
        emit('select-communication', comm.id)
      }
    })
  }
}

const toggleRead = (id) => {
  emit('toggle-read', id)
}

const viewCommunication = (id) => {
  emit('view-communication', id)
}

const deleteCommunication = (id) => {
  emit('delete-communication', id)
}

const getRecipientName = (communication) => {
  if (communication.recipient_name) {
    return communication.recipient_name
  }
  
  if (communication.direction === 'outbound') {
    return communication.to_addresses?.[0] || 'Unknown Recipient'
  }
  
  return communication.from_address || 'Unknown Sender'
}

const getTypeIcon = (type) => {
  switch (type) {
    case 'email':
      return 'bi-envelope'
    case 'sms':
      return 'bi-chat-dots'
    case 'call':
      return 'bi-telephone'
    case 'meeting':
      return 'bi-calendar'
    case 'note':
      return 'bi-sticky'
    default:
      return 'bi-chat'
  }
}

const getTypeAvatarClass = (type) => {
  switch (type) {
    case 'email':
      return 'bg-primary text-white'
    case 'sms':
      return 'bg-success text-white'
    case 'call':
      return 'bg-info text-white'
    case 'meeting':
      return 'bg-warning text-white'
    case 'note':
      return 'bg-secondary text-white'
    default:
      return 'bg-light text-muted'
  }
}

const getTypeBadgeClass = (type) => {
  switch (type) {
    case 'email':
      return 'bg-primary'
    case 'sms':
      return 'bg-success'
    case 'call':
      return 'bg-info'
    case 'meeting':
      return 'bg-warning'
    case 'note':
      return 'bg-secondary'
    default:
      return 'bg-light text-dark'
  }
}

const getDirectionIcon = (direction) => {
  switch (direction) {
    case 'inbound':
      return 'bi-arrow-down-left'
    case 'outbound':
      return 'bi-arrow-up-right'
    case 'internal':
      return 'bi-arrow-repeat'
    default:
      return 'bi-dash'
  }
}

const getDirectionBadgeClass = (direction) => {
  switch (direction) {
    case 'inbound':
      return 'bg-info'
    case 'outbound':
      return 'bg-success'
    case 'internal':
      return 'bg-secondary'
    default:
      return 'bg-light text-dark'
  }
}

const getSentimentIcon = (sentiment) => {
  switch (sentiment) {
    case 'positive':
      return 'bi-emoji-smile'
    case 'negative':
      return 'bi-emoji-frown'
    case 'neutral':
      return 'bi-emoji-neutral'
    case 'mixed':
      return 'bi-emoji-expressionless'
    default:
      return 'bi-dash'
  }
}

const getSentimentBadgeClass = (sentiment) => {
  switch (sentiment) {
    case 'positive':
      return 'bg-success'
    case 'negative':
      return 'bg-danger'
    case 'neutral':
      return 'bg-secondary'
    case 'mixed':
      return 'bg-warning'
    default:
      return 'bg-light text-dark'
  }
}

const getSentimentProgressClass = (sentiment) => {
  switch (sentiment) {
    case 'positive':
      return 'bg-success'
    case 'negative':
      return 'bg-danger'
    case 'neutral':
      return 'bg-secondary'
    case 'mixed':
      return 'bg-warning'
    default:
      return 'bg-light'
  }
}

const getPriorityProgressClass = (priority) => {
  if (priority >= 0.7) return 'bg-danger'
  if (priority >= 0.4) return 'bg-warning'
  return 'bg-success'
}

const isHighPriority = (communication) => {
  return communication.ai_priority_score >= 0.7
}

const hasAIAnalysis = (communication) => {
  return communication.ai_sentiment_score || 
         communication.ai_urgency_score || 
         communication.ai_priority_score ||
         communication.ai_suggested_response
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Now'
  if (diffMins < 60) return `${diffMins}m`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d`
  
  // Format as date for older items
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const showAISuggestion = (communication) => {
  selectedSuggestion.value = communication
  const modal = new bootstrap.Modal(aiSuggestionModal.value)
  modal.show()
}

const useAISuggestion = () => {
  // Emit event to use the AI suggestion for composing a response
  emit('use-ai-suggestion', selectedSuggestion.value)
  
  // Close modal
  const modal = bootstrap.Modal.getInstance(aiSuggestionModal.value)
  modal.hide()
}
</script>

<style scoped>
.communication-item {
  transition: all 0.2s ease;
  cursor: pointer;
}

.communication-item:hover {
  background-color: #f8f9fa;
}

.communication-item.selected {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.communication-item.unread {
  background-color: #fefefe;
  border-left: 3px solid #0d6efd;
}

.communication-item.high-priority {
  box-shadow: 0 0 0 1px rgba(220, 53, 69, 0.3);
}

.communication-subject {
  font-weight: 600;
  color: #212529;
}

.communication-subject:hover {
  color: #0d6efd;
  text-decoration: underline;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.875rem;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
}

.avatar-xl {
  width: 4rem;
  height: 4rem;
  font-size: 1.5rem;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.25em 0.5em;
}

.btn-ghost-secondary {
  color: #6c757d;
  background: transparent;
  border: none;
}

.btn-ghost-secondary:hover {
  color: #495057;
  background-color: #f8f9fa;
}

.btn-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.bg-soft-secondary {
  background-color: rgba(108, 117, 125, 0.1);
}

.bg-soft-primary {
  background-color: rgba(13, 110, 253, 0.1);
}

.progress {
  border-radius: 3px;
}

.min-w-0 {
  min-width: 0;
}

@media (max-width: 768px) {
  .communication-item .row {
    --bs-gutter-x: 0.5rem;
  }
  
  .communication-item .col {
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }
  
  .badge-sm {
    font-size: 0.6rem;
    padding: 0.2em 0.4em;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }
}
</style>