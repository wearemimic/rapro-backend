<template>
  <div class="modal fade show" style="display: block; background-color: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <div class="d-flex align-items-center">
            <div 
              class="avatar avatar-sm avatar-circle me-3"
              :class="getTypeAvatarClass(communication?.communication_type)"
              v-if="communication"
            >
              <i :class="getTypeIcon(communication.communication_type)"></i>
            </div>
            <div>
              <h5 class="modal-title mb-0">Communication Details</h5>
              <small class="text-muted" v-if="communication">
                {{ communication.communication_type.toUpperCase() }} • {{ formatDate(communication.created_at) }}
              </small>
            </div>
          </div>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="modal-body text-center py-5">
          <div class="spinner-border text-primary mb-3" role="status">
            <span class="visually-hidden">Loading communication...</span>
          </div>
          <p class="text-muted">Loading communication details...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="modal-body text-center py-5">
          <div class="avatar avatar-xl avatar-circle bg-danger text-white mx-auto mb-3">
            <i class="bi bi-exclamation-triangle"></i>
          </div>
          <h6 class="text-danger mb-2">Failed to Load Communication</h6>
          <p class="text-muted mb-3">{{ error }}</p>
          <button class="btn btn-outline-primary" @click="loadCommunication">
            <i class="bi bi-arrow-clockwise me-1"></i>
            Try Again
          </button>
        </div>

        <!-- Content -->
        <div v-else-if="communication" class="modal-body p-0">
          <div class="row g-0">
            <!-- Main Content -->
            <div class="col-lg-8">
              <div class="p-4">
                <!-- Header Info -->
                <div class="d-flex justify-content-between align-items-start mb-4">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center flex-wrap gap-2 mb-2">
                      <!-- Direction Badge -->
                      <span 
                        class="badge"
                        :class="getDirectionBadgeClass(communication.direction)"
                      >
                        <i :class="getDirectionIcon(communication.direction)" class="me-1"></i>
                        {{ communication.direction.toUpperCase() }}
                      </span>

                      <!-- Read Status -->
                      <span 
                        v-if="!communication.is_read"
                        class="badge bg-warning"
                      >
                        <i class="bi bi-envelope me-1"></i>
                        UNREAD
                      </span>

                      <!-- Priority Badge -->
                      <span 
                        v-if="isHighPriority"
                        class="badge bg-danger"
                      >
                        <i class="bi bi-star-fill me-1"></i>
                        HIGH PRIORITY
                      </span>
                    </div>

                    <!-- Subject -->
                    <h4 class="mb-2">{{ communication.subject || 'No Subject' }}</h4>

                    <!-- Participants -->
                    <div class="mb-3">
                      <div class="row">
                        <div class="col-md-6" v-if="communication.from_address">
                          <small class="text-muted d-block">From</small>
                          <strong>{{ communication.from_address }}</strong>
                        </div>
                        <div class="col-md-6" v-if="communication.to_addresses && communication.to_addresses.length > 0">
                          <small class="text-muted d-block">To</small>
                          <strong>{{ communication.to_addresses.join(', ') }}</strong>
                        </div>
                      </div>
                      
                      <div class="row mt-2" v-if="communication.cc_addresses && communication.cc_addresses.length > 0">
                        <div class="col-md-6">
                          <small class="text-muted d-block">CC</small>
                          <span>{{ communication.cc_addresses.join(', ') }}</span>
                        </div>
                      </div>
                      
                      <div class="row mt-2" v-if="communication.recipient_name">
                        <div class="col-md-6">
                          <small class="text-muted d-block">Linked Contact</small>
                          <span class="d-flex align-items-center">
                            <i :class="communication.recipient_type === 'client' ? 'bi-person-fill' : 'bi-person-plus'" class="me-1 text-primary"></i>
                            <strong>{{ communication.recipient_name }}</strong>
                            <span class="badge badge-sm bg-light text-dark ms-2">{{ communication.recipient_type }}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Action Buttons -->
                  <div class="d-flex flex-column gap-2">
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="toggleRead"
                    >
                      <i :class="communication.is_read ? 'bi-envelope' : 'bi-envelope-open'" class="me-1"></i>
                      Mark {{ communication.is_read ? 'Unread' : 'Read' }}
                    </button>
                    
                    <button 
                      v-if="communication.communication_type === 'email'"
                      class="btn btn-sm btn-outline-success"
                      @click="replyToEmail"
                    >
                      <i class="bi bi-reply me-1"></i>
                      Reply
                    </button>
                    
                    <div class="dropdown">
                      <button 
                        class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                        data-bs-toggle="dropdown"
                      >
                        <i class="bi bi-three-dots"></i>
                      </button>
                      <ul class="dropdown-menu">
                        <li>
                          <button class="dropdown-item" @click="analyzeWithAI" :disabled="loadingAI">
                            <i class="bi bi-robot me-2"></i>
                            {{ loadingAI ? 'Analyzing...' : 'Analyze with AI' }}
                          </button>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button class="dropdown-item text-danger" @click="deleteCommunication">
                            <i class="bi bi-trash me-2"></i>
                            Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- Content -->
                <div class="communication-content">
                  <div class="card border-0 bg-light">
                    <div class="card-body">
                      <div class="content-display" v-html="formattedContent"></div>
                    </div>
                  </div>
                </div>

                <!-- AI Suggested Response -->
                <div v-if="communication.ai_suggested_response" class="mt-4">
                  <AIResponseSuggestions 
                    :communication="communication"
                    @use-suggestion="useAISuggestion"
                  />
                </div>
              </div>
            </div>

            <!-- Sidebar -->
            <div class="col-lg-4 border-start bg-light">
              <div class="p-4">
                <!-- AI Analysis Section -->
                <div v-if="hasAIAnalysis" class="mb-4">
                  <h6 class="mb-3">
                    <i class="bi bi-robot me-2"></i>
                    AI Analysis
                  </h6>

                  <!-- Sentiment Analysis -->
                  <div v-if="communication.ai_sentiment_label" class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <small class="text-muted fw-semibold">Sentiment</small>
                      <span 
                        class="badge"
                        :class="getSentimentBadgeClass(communication.ai_sentiment_label)"
                      >
                        <i :class="getSentimentIcon(communication.ai_sentiment_label)" class="me-1"></i>
                        {{ communication.ai_sentiment_label.toUpperCase() }}
                      </span>
                    </div>
                    
                    <div v-if="communication.ai_sentiment_score" class="mb-2">
                      <div class="progress" style="height: 8px;">
                        <div 
                          class="progress-bar"
                          :class="getSentimentProgressClass(communication.ai_sentiment_label)"
                          :style="{ width: Math.abs(communication.ai_sentiment_score) * 100 + '%' }"
                        ></div>
                      </div>
                      <small class="text-muted">
                        {{ communication.ai_sentiment_score > 0 ? 'Positive' : 'Negative' }} 
                        ({{ Math.abs(communication.ai_sentiment_score).toFixed(2) }})
                      </small>
                    </div>
                  </div>

                  <!-- Urgency Score -->
                  <div v-if="communication.ai_urgency_score" class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <small class="text-muted fw-semibold">Urgency Level</small>
                      <span class="badge bg-warning">
                        {{ Math.round(communication.ai_urgency_score * 100) }}%
                      </span>
                    </div>
                    
                    <div class="progress mb-1" style="height: 8px;">
                      <div 
                        class="progress-bar bg-warning"
                        :style="{ width: communication.ai_urgency_score * 100 + '%' }"
                      ></div>
                    </div>
                    <small class="text-muted">
                      {{ getUrgencyLabel(communication.ai_urgency_score) }}
                    </small>
                  </div>

                  <!-- Priority Score -->
                  <div v-if="communication.ai_priority_score" class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <small class="text-muted fw-semibold">Priority Score</small>
                      <span 
                        class="badge"
                        :class="getPriorityBadgeClass(communication.ai_priority_score)"
                      >
                        {{ Math.round(communication.ai_priority_score * 100) }}%
                      </span>
                    </div>
                    
                    <div class="progress mb-1" style="height: 8px;">
                      <div 
                        class="progress-bar"
                        :class="getPriorityProgressClass(communication.ai_priority_score)"
                        :style="{ width: communication.ai_priority_score * 100 + '%' }"
                      ></div>
                    </div>
                    <small class="text-muted">
                      {{ getPriorityLabel(communication.ai_priority_score) }}
                    </small>
                  </div>

                  <!-- AI Topics -->
                  <div v-if="communication.ai_topics && communication.ai_topics.length > 0" class="mb-3">
                    <small class="text-muted fw-semibold d-block mb-2">Detected Topics</small>
                    <div class="d-flex flex-wrap gap-1">
                      <span 
                        v-for="topic in communication.ai_topics.slice(0, 5)" 
                        :key="topic"
                        class="badge bg-secondary"
                      >
                        {{ topic }}
                      </span>
                      <span 
                        v-if="communication.ai_topics.length > 5"
                        class="badge bg-light text-dark"
                        :title="communication.ai_topics.slice(5).join(', ')"
                      >
                        +{{ communication.ai_topics.length - 5 }} more
                      </span>
                    </div>
                  </div>

                  <!-- AI Analysis Date -->
                  <div v-if="communication.ai_analysis_date" class="mb-3">
                    <small class="text-muted d-block">
                      <i class="bi bi-clock me-1"></i>
                      Analyzed {{ formatDate(communication.ai_analysis_date) }}
                    </small>
                    <small class="text-muted d-block" v-if="communication.ai_model_version">
                      Model: {{ communication.ai_model_version }}
                    </small>
                  </div>
                </div>

                <!-- Metadata -->
                <div class="mb-4">
                  <h6 class="mb-3">
                    <i class="bi bi-info-circle me-2"></i>
                    Details
                  </h6>

                  <div class="mb-2">
                    <small class="text-muted d-block">Created</small>
                    <span>{{ formatFullDate(communication.created_at) }}</span>
                  </div>

                  <div v-if="communication.sent_at" class="mb-2">
                    <small class="text-muted d-block">Sent</small>
                    <span>{{ formatFullDate(communication.sent_at) }}</span>
                  </div>

                  <div v-if="communication.read_at" class="mb-2">
                    <small class="text-muted d-block">Read</small>
                    <span>{{ formatFullDate(communication.read_at) }}</span>
                  </div>

                  <div v-if="communication.email_account" class="mb-2">
                    <small class="text-muted d-block">Email Account</small>
                    <div class="d-flex align-items-center">
                      <i :class="getProviderIcon(communication.email_account.provider)" class="me-2"></i>
                      <span>{{ communication.email_account.email }}</span>
                    </div>
                  </div>

                  <div v-if="communication.provider_message_id" class="mb-2">
                    <small class="text-muted d-block">Message ID</small>
                    <small class="font-monospace">{{ communication.provider_message_id }}</small>
                  </div>
                </div>

                <!-- Quick Actions -->
                <div class="d-grid gap-2">
                  <button 
                    v-if="!hasAIAnalysis && !loadingAI"
                    class="btn btn-outline-primary btn-sm"
                    @click="analyzeWithAI"
                  >
                    <i class="bi bi-robot me-1"></i>
                    Analyze with AI
                  </button>

                  <button 
                    v-if="loadingAI"
                    class="btn btn-outline-primary btn-sm"
                    disabled
                  >
                    <i class="bi bi-hourglass-split me-1 spin"></i>
                    Analyzing...
                  </button>

                  <button 
                    v-if="communication.communication_type === 'email'"
                    class="btn btn-outline-success btn-sm"
                    @click="forwardEmail"
                  >
                    <i class="bi bi-arrow-right me-1"></i>
                    Forward
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCommunicationStore } from '@/stores/communicationStore'
import { useEmailStore } from '@/stores/emailStore'
import AIResponseSuggestions from './AIResponseSuggestions.vue'
import { sanitizeHTML } from '@/utils/sanitizer'

// Props
const props = defineProps({
  communicationId: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'updated'])

// Stores
const communicationStore = useCommunicationStore()
const emailStore = useEmailStore()

// Component state
const communication = ref(null)
const loading = ref(false)
const loadingAI = ref(false)
const error = ref(null)

// Computed
const hasAIAnalysis = computed(() => {
  if (!communication.value) return false
  
  return communication.value.ai_sentiment_score || 
         communication.value.ai_urgency_score || 
         communication.value.ai_priority_score ||
         communication.value.ai_suggested_response ||
         (communication.value.ai_topics && communication.value.ai_topics.length > 0)
})

const isHighPriority = computed(() => {
  return communication.value?.ai_priority_score >= 0.7
})

const formattedContent = computed(() => {
  if (!communication.value?.content) return ''

  // First format the content
  let formatted = communication.value.content
    .replace(/\n/g, '<br>')
    .replace(/\r/g, '')
    .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')

  // Then sanitize to prevent XSS
  return sanitizeHTML(formatted, false)
})

// Methods
const loadCommunication = async () => {
  loading.value = true
  error.value = null
  
  try {
    const comm = await communicationStore.fetchCommunication(props.communicationId)
    communication.value = comm
  } catch (err) {
    console.error('Load communication error:', err)
    error.value = err.message || 'Failed to load communication'
  } finally {
    loading.value = false
  }
}

const toggleRead = async () => {
  try {
    if (communication.value.is_read) {
      await communicationStore.markAsUnread(props.communicationId)
      communication.value.is_read = false
      communication.value.read_at = null
    } else {
      await communicationStore.markAsRead(props.communicationId)
      communication.value.is_read = true
      communication.value.read_at = new Date().toISOString()
    }
    
    emit('updated')
  } catch (error) {
    console.error('Toggle read error:', error)
    alert('Failed to update read status')
  }
}

const analyzeWithAI = async () => {
  loadingAI.value = true
  
  try {
    const result = await emailStore.analyzeWithAI(props.communicationId)
    
    // Refresh communication to get updated AI data
    await loadCommunication()
    
    emit('updated')
    
    // Show success message
    alert('AI analysis completed successfully!')
    
  } catch (error) {
    console.error('AI analysis error:', error)
    alert('Failed to analyze with AI: ' + (error.message || 'Unknown error'))
  } finally {
    loadingAI.value = false
  }
}

const replyToEmail = () => {
  // Close this modal and open compose modal with reply data
  emit('close')
  
  // Emit event to parent to open compose modal with reply
  // In a real implementation, this would trigger the compose modal
  console.log('Reply to email:', communication.value)
}

const forwardEmail = () => {
  // Close this modal and open compose modal with forward data
  emit('close')
  
  // Emit event to parent to open compose modal with forward
  console.log('Forward email:', communication.value)
}

const useAISuggestion = (suggestion) => {
  // Close this modal and open compose modal with AI suggestion
  emit('close')
  
  console.log('Use AI suggestion:', suggestion)
}

const deleteCommunication = async () => {
  if (confirm('Are you sure you want to delete this communication?')) {
    try {
      await communicationStore.deleteCommunication(props.communicationId)
      emit('updated')
      emit('close')
    } catch (error) {
      console.error('Delete error:', error)
      alert('Failed to delete communication')
    }
  }
}

// Utility methods
const getTypeIcon = (type) => {
  switch (type) {
    case 'email': return 'bi-envelope'
    case 'sms': return 'bi-chat-dots'
    case 'call': return 'bi-telephone'
    case 'meeting': return 'bi-calendar'
    case 'note': return 'bi-sticky'
    default: return 'bi-chat'
  }
}

const getTypeAvatarClass = (type) => {
  switch (type) {
    case 'email': return 'bg-primary text-white'
    case 'sms': return 'bg-success text-white'
    case 'call': return 'bg-info text-white'
    case 'meeting': return 'bg-warning text-white'
    case 'note': return 'bg-secondary text-white'
    default: return 'bg-light text-muted'
  }
}

const getDirectionIcon = (direction) => {
  switch (direction) {
    case 'inbound': return 'bi-arrow-down-left'
    case 'outbound': return 'bi-arrow-up-right'
    case 'internal': return 'bi-arrow-repeat'
    default: return 'bi-dash'
  }
}

const getDirectionBadgeClass = (direction) => {
  switch (direction) {
    case 'inbound': return 'bg-info'
    case 'outbound': return 'bg-success'
    case 'internal': return 'bg-secondary'
    default: return 'bg-light text-dark'
  }
}

const getSentimentIcon = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bi-emoji-smile'
    case 'negative': return 'bi-emoji-frown'
    case 'neutral': return 'bi-emoji-neutral'
    case 'mixed': return 'bi-emoji-expressionless'
    default: return 'bi-dash'
  }
}

const getSentimentBadgeClass = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bg-success'
    case 'negative': return 'bg-danger'
    case 'neutral': return 'bg-secondary'
    case 'mixed': return 'bg-warning'
    default: return 'bg-light text-dark'
  }
}

const getSentimentProgressClass = (sentiment) => {
  return getSentimentBadgeClass(sentiment).replace('bg-', 'bg-')
}

const getPriorityBadgeClass = (priority) => {
  if (priority >= 0.7) return 'bg-danger'
  if (priority >= 0.4) return 'bg-warning'
  return 'bg-success'
}

const getPriorityProgressClass = (priority) => {
  return getPriorityBadgeClass(priority)
}

const getPriorityLabel = (priority) => {
  if (priority >= 0.8) return 'Very High Priority'
  if (priority >= 0.7) return 'High Priority'
  if (priority >= 0.5) return 'Medium Priority'
  if (priority >= 0.3) return 'Low Priority'
  return 'Very Low Priority'
}

const getUrgencyLabel = (urgency) => {
  if (urgency >= 0.8) return 'Very Urgent'
  if (urgency >= 0.6) return 'Urgent'
  if (urgency >= 0.4) return 'Moderate'
  return 'Not Urgent'
}

const getProviderIcon = (provider) => {
  switch (provider) {
    case 'gmail': return 'bi-google'
    case 'outlook': return 'bi-microsoft'
    default: return 'bi-envelope'
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const formatFullDate = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

// Lifecycle
onMounted(() => {
  loadCommunication()
})
</script>

<style scoped>
.modal {
  z-index: 1055;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
  font-size: 0.875rem;
}

.avatar-xl {
  width: 4rem;
  height: 4rem;
  font-size: 1.5rem;
}

.communication-content {
  max-height: 60vh;
  overflow-y: auto;
}

.content-display {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
}

.content-display a {
  color: #0d6efd;
  text-decoration: none;
}

.content-display a:hover {
  text-decoration: underline;
}

.badge {
  font-size: 0.75rem;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.25em 0.5em;
}

.progress {
  border-radius: 4px;
}

.font-monospace {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.875em;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.fw-semibold {
  font-weight: 600;
}

@media (max-width: 992px) {
  .modal-dialog {
    max-width: 95%;
  }
  
  .col-lg-8,
  .col-lg-4 {
    flex: 0 0 100%;
    max-width: 100%;
  }
  
  .border-start {
    border-start: none !important;
    border-top: 1px solid #dee2e6 !important;
  }
  
  .communication-content {
    max-height: 40vh;
  }
}

@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
  
  .row .col-md-6 {
    margin-bottom: 0.5rem;
  }
  
  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .badge {
    font-size: 0.7rem;
  }
}
</style>