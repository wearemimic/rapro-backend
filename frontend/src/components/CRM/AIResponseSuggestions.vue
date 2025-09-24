<template>
  <div class="ai-response-suggestions">
    <div class="card border-primary">
      <div class="card-header bg-primary text-white">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <i class="bi bi-robot me-2"></i>
            <h6 class="mb-0">AI Response Suggestions</h6>
          </div>
          <div class="d-flex align-items-center">
            <span 
              v-if="communication.ai_response_confidence"
              class="badge bg-light text-primary me-2"
            >
              {{ Math.round(communication.ai_response_confidence * 100) }}% confidence
            </span>
            <button 
              type="button" 
              class="btn btn-sm btn-outline-light"
              @click="collapsed = !collapsed"
            >
              <i :class="collapsed ? 'bi-chevron-down' : 'bi-chevron-up'"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="card-body" v-show="!collapsed">
        <!-- AI Suggested Response -->
        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h6 class="text-primary mb-0">
              <i class="bi bi-lightbulb me-1"></i>
              Suggested Response
            </h6>
            <div class="d-flex gap-1">
              <button 
                class="btn btn-sm btn-outline-secondary"
                @click="copyToClipboard(communication.ai_suggested_response)"
                title="Copy to clipboard"
              >
                <i class="bi bi-clipboard"></i>
              </button>
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="editResponse"
                title="Edit and customize"
              >
                <i class="bi bi-pencil"></i>
              </button>
            </div>
          </div>
          
          <div class="card bg-light border-0">
            <div class="card-body p-3">
              <div 
                v-if="!editMode"
                class="ai-response-content"
                v-html="formattedResponse"
              ></div>
              
              <div v-else>
                <textarea 
                  v-model="editedResponse"
                  class="form-control border-0"
                  rows="6"
                  placeholder="Edit the AI suggested response..."
                ></textarea>
                <div class="d-flex justify-content-end gap-2 mt-2">
                  <button 
                    class="btn btn-sm btn-outline-secondary"
                    @click="cancelEdit"
                  >
                    Cancel
                  </button>
                  <button 
                    class="btn btn-sm btn-primary"
                    @click="saveEdit"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Response Analysis -->
        <div class="row mb-3" v-if="responseAnalysis">
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <div class="d-flex align-items-center justify-content-center mb-1">
                <i class="bi bi-heart text-danger me-1"></i>
                <small class="text-muted fw-semibold">Tone</small>
              </div>
              <div class="badge bg-secondary">{{ responseAnalysis.tone }}</div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <div class="d-flex align-items-center justify-content-center mb-1">
                <i class="bi bi-chat-text text-primary me-1"></i>
                <small class="text-muted fw-semibold">Style</small>
              </div>
              <div class="badge bg-secondary">{{ responseAnalysis.style }}</div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="text-center p-2 bg-light rounded">
              <div class="d-flex align-items-center justify-content-center mb-1">
                <i class="bi bi-bar-chart text-success me-1"></i>
                <small class="text-muted fw-semibold">Length</small>
              </div>
              <div class="badge bg-secondary">{{ responseAnalysis.length }}</div>
            </div>
          </div>
        </div>

        <!-- Alternative Responses -->
        <div v-if="alternativeResponses.length > 0" class="mb-3">
          <h6 class="text-muted mb-2">
            <i class="bi bi-collection me-1"></i>
            Alternative Responses
          </h6>
          
          <div class="accordion" id="alternativeResponsesAccordion">
            <div 
              v-for="(response, index) in alternativeResponses" 
              :key="index"
              class="accordion-item"
            >
              <h2 class="accordion-header">
                <button 
                  class="accordion-button collapsed py-2" 
                  type="button" 
                  data-bs-toggle="collapse" 
                  :data-bs-target="`#response-${index}`"
                >
                  <div class="d-flex align-items-center w-100">
                    <div class="flex-grow-1">
                      <span class="me-2">{{ response.title }}</span>
                      <span class="badge bg-light text-dark">{{ response.tone }}</span>
                    </div>
                    <div class="me-2">
                      <span class="badge bg-primary">{{ response.confidence }}%</span>
                    </div>
                  </div>
                </button>
              </h2>
              <div 
                :id="`response-${index}`" 
                class="accordion-collapse collapse" 
                data-bs-parent="#alternativeResponsesAccordion"
              >
                <div class="accordion-body py-2">
                  <div class="mb-2">{{ response.content }}</div>
                  <div class="d-flex gap-2">
                    <button 
                      class="btn btn-sm btn-outline-primary"
                      @click="selectAlternativeResponse(response)"
                    >
                      <i class="bi bi-check2 me-1"></i>
                      Use This Response
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-secondary"
                      @click="copyToClipboard(response.content)"
                    >
                      <i class="bi bi-clipboard me-1"></i>
                      Copy
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Customizations -->
        <div class="mb-3">
          <h6 class="text-muted mb-2">
            <i class="bi bi-sliders me-1"></i>
            Quick Customizations
          </h6>
          
          <div class="row">
            <div class="col-md-6 mb-2">
              <label class="form-label small">Adjust Tone:</label>
              <div class="btn-group w-100" role="group">
                <button 
                  v-for="tone in toneOptions" 
                  :key="tone.value"
                  type="button" 
                  class="btn btn-sm"
                  :class="selectedTone === tone.value ? 'btn-primary' : 'btn-outline-primary'"
                  @click="adjustTone(tone.value)"
                >
                  {{ tone.label }}
                </button>
              </div>
            </div>
            <div class="col-md-6 mb-2">
              <label class="form-label small">Response Length:</label>
              <div class="btn-group w-100" role="group">
                <button 
                  v-for="length in lengthOptions" 
                  :key="length.value"
                  type="button" 
                  class="btn btn-sm"
                  :class="selectedLength === length.value ? 'btn-primary' : 'btn-outline-primary'"
                  @click="adjustLength(length.value)"
                >
                  {{ length.label }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Key Points to Address -->
        <div v-if="keyPoints.length > 0" class="mb-3">
          <h6 class="text-muted mb-2">
            <i class="bi bi-check2-square me-1"></i>
            Key Points Addressed
          </h6>
          
          <div class="d-flex flex-wrap gap-1">
            <span 
              v-for="point in keyPoints" 
              :key="point"
              class="badge bg-success"
            >
              <i class="bi bi-check me-1"></i>
              {{ point }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex gap-2">
            <button 
              class="btn btn-sm btn-outline-secondary"
              @click="generateNewSuggestion"
              :disabled="loading.generating"
            >
              <i class="bi bi-arrow-clockwise me-1" :class="{ 'spin': loading.generating }"></i>
              {{ loading.generating ? 'Generating...' : 'Generate New' }}
            </button>
            
            <button 
              class="btn btn-sm btn-outline-info"
              @click="explainSuggestion"
            >
              <i class="bi bi-question-circle me-1"></i>
              Why This Response?
            </button>
          </div>
          
          <div class="d-flex gap-2">
            <button 
              class="btn btn-sm btn-outline-success"
              @click="provideFeedback('positive')"
            >
              <i class="bi bi-hand-thumbs-up me-1"></i>
              Helpful
            </button>
            
            <button 
              class="btn btn-sm btn-outline-danger"
              @click="provideFeedback('negative')"
            >
              <i class="bi bi-hand-thumbs-down me-1"></i>
              Not Helpful
            </button>
            
            <button 
              class="btn btn-sm btn-success"
              @click="useSuggestion"
            >
              <i class="bi bi-send me-1"></i>
              Use Response
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Explanation Modal -->
    <div 
      class="modal fade" 
      id="explanationModal" 
      tabindex="-1" 
      ref="explanationModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-lightbulb me-2"></i>
              AI Response Explanation
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6>Why this response was suggested:</h6>
              <ul class="list-unstyled">
                <li class="mb-2">
                  <i class="bi bi-check2 text-success me-2"></i>
                  <strong>Original sentiment:</strong> {{ communication.ai_sentiment_label || 'Unknown' }}
                  <small class="text-muted d-block">Response tone adjusted to {{ getRecommendedTone() }}</small>
                </li>
                <li class="mb-2">
                  <i class="bi bi-check2 text-success me-2"></i>
                  <strong>Urgency level:</strong> {{ getUrgencyLabel(communication.ai_urgency_score) }}
                  <small class="text-muted d-block">Response prioritizes {{ getResponsePriority() }}</small>
                </li>
                <li class="mb-2" v-if="communication.ai_topics && communication.ai_topics.length > 0">
                  <i class="bi bi-check2 text-success me-2"></i>
                  <strong>Key topics addressed:</strong> {{ communication.ai_topics.slice(0, 3).join(', ') }}
                  <small class="text-muted d-block">Response covers main discussion points</small>
                </li>
                <li class="mb-2">
                  <i class="bi bi-check2 text-success me-2"></i>
                  <strong>Professional standards:</strong> Financial advisory compliance
                  <small class="text-muted d-block">Language follows industry best practices</small>
                </li>
              </ul>
            </div>
            
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Confidence Score: {{ Math.round(communication.ai_response_confidence * 100) }}%</strong>
              <p class="mb-0 mt-1">This score reflects how well the AI understands the context and appropriateness of the suggested response.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { sanitizeHTML } from '@/utils/sanitizer'

// Props
const props = defineProps({
  communication: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['use-suggestion'])

// Component state
const collapsed = ref(false)
const editMode = ref(false)
const editedResponse = ref('')
const selectedTone = ref('professional')
const selectedLength = ref('medium')

const loading = ref({
  generating: false
})

// Mock data
const alternativeResponses = ref([
  {
    title: 'Concise Response',
    tone: 'Professional',
    confidence: 85,
    content: 'Thank you for reaching out. I\'ll review your request and get back to you within 24 hours with the information you need.'
  },
  {
    title: 'Detailed Response',
    tone: 'Friendly',
    confidence: 78,
    content: 'Hi! Thanks so much for your message. I really appreciate you taking the time to share your concerns with me. Let me look into this thoroughly and provide you with a comprehensive response that addresses all your questions.'
  }
])

const responseAnalysis = ref({
  tone: 'Professional',
  style: 'Advisory',
  length: 'Medium'
})

const keyPoints = ref(['Client concern', 'Follow-up needed', 'Financial planning'])

const toneOptions = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'formal', label: 'Formal' }
]

const lengthOptions = [
  { value: 'brief', label: 'Brief' },
  { value: 'medium', label: 'Medium' },
  { value: 'detailed', label: 'Detailed' }
]

// Computed
const formattedResponse = computed(() => {
  if (!props.communication.ai_suggested_response) return ''
  // Convert newlines to breaks
  const formatted = props.communication.ai_suggested_response.replace(/\n/g, '<br>')
  // Sanitize to prevent XSS
  return sanitizeHTML(formatted, false)
})

// Methods
const editResponse = () => {
  editMode.value = true
  editedResponse.value = props.communication.ai_suggested_response || ''
}

const cancelEdit = () => {
  editMode.value = false
  editedResponse.value = ''
}

const saveEdit = () => {
  // In real implementation, this would save the edited response
  editMode.value = false
  console.log('Saving edited response:', editedResponse.value)
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    // Show success feedback
    alert('Copied to clipboard!')
  } catch (error) {
    console.error('Copy failed:', error)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('Copied to clipboard!')
  }
}

const adjustTone = async (tone) => {
  selectedTone.value = tone
  // In real implementation, this would regenerate the response with new tone
  console.log('Adjusting tone to:', tone)
}

const adjustLength = async (length) => {
  selectedLength.value = length
  // In real implementation, this would regenerate the response with new length
  console.log('Adjusting length to:', length)
}

const selectAlternativeResponse = (response) => {
  // Use the alternative response
  emit('use-suggestion', response.content)
}

const generateNewSuggestion = async () => {
  loading.value.generating = true
  
  try {
    // Simulate API call to generate new suggestion
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // In real implementation, this would call the AI service
    console.log('Generating new suggestion...')
    
    alert('New suggestion generated!')
    
  } catch (error) {
    console.error('Generate new suggestion error:', error)
    alert('Failed to generate new suggestion')
  } finally {
    loading.value.generating = false
  }
}

const explainSuggestion = () => {
  const modal = new bootstrap.Modal(document.getElementById('explanationModal'))
  modal.show()
}

const provideFeedback = async (type) => {
  try {
    // In real implementation, this would send feedback to the AI service
    console.log('Providing feedback:', type)
    
    const message = type === 'positive' 
      ? 'Thank you for your positive feedback!' 
      : 'Thank you for your feedback. We\'ll use this to improve our suggestions.'
    
    alert(message)
    
  } catch (error) {
    console.error('Feedback error:', error)
  }
}

const useSuggestion = () => {
  const content = editMode.value ? editedResponse.value : props.communication.ai_suggested_response
  emit('use-suggestion', content)
}

const getRecommendedTone = () => {
  switch (props.communication.ai_sentiment_label) {
    case 'positive':
      return 'friendly and appreciative'
    case 'negative':
      return 'empathetic and solution-focused'
    case 'neutral':
      return 'professional and informative'
    default:
      return 'balanced and professional'
  }
}

const getUrgencyLabel = (urgency) => {
  if (!urgency) return 'Normal'
  if (urgency >= 0.8) return 'Very Urgent'
  if (urgency >= 0.6) return 'Urgent'
  if (urgency >= 0.4) return 'Moderate'
  return 'Low'
}

const getResponsePriority = () => {
  const urgency = props.communication.ai_urgency_score || 0
  if (urgency >= 0.7) return 'immediate acknowledgment'
  if (urgency >= 0.5) return 'timely response'
  return 'thorough consideration'
}

// Lifecycle
onMounted(() => {
  // Initialize component
  if (props.communication.ai_suggested_response) {
    editedResponse.value = props.communication.ai_suggested_response
  }
})
</script>

<style scoped>
.ai-response-suggestions {
  border-radius: 0.5rem;
}

.ai-response-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.badge {
  font-size: 0.75rem;
}

.btn-group .btn {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
}

.accordion-button {
  font-size: 0.9rem;
}

.accordion-body {
  font-size: 0.9rem;
}

.card-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.125);
}

.form-label.small {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

@media (max-width: 768px) {
  .row .col-md-4,
  .row .col-md-6 {
    margin-bottom: 0.5rem;
  }
  
  .btn-group .btn {
    font-size: 0.75rem;
    padding: 0.2rem 0.4rem;
  }
  
  .d-flex.gap-2 {
    gap: 0.5rem !important;
  }
  
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
  }
}

@media (max-width: 576px) {
  .d-flex.justify-content-between {
    flex-direction: column;
    align-items: stretch;
  }
  
  .d-flex.justify-content-between > div {
    margin-bottom: 0.5rem;
  }
  
  .d-flex.justify-content-between > div:last-child {
    margin-bottom: 0;
  }
  
  .btn-group {
    flex-direction: column;
  }
  
  .btn-group .btn {
    border-radius: 0.25rem !important;
    margin-bottom: 0.25rem;
  }
}
</style>