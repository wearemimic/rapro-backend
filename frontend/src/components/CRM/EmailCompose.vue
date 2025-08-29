<template>
  <div class="modal fade show" style="display: block; background-color: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-envelope me-2"></i>
            Compose Email
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- AI Draft Section -->
          <div v-if="showAIDrafting" class="card border-primary mb-3">
            <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
              <div>
                <i class="bi bi-robot me-2"></i>
                AI Email Drafting
              </div>
              <button 
                type="button" 
                class="btn btn-sm btn-outline-light"
                @click="showAIDrafting = false"
              >
                <i class="bi bi-x"></i>
              </button>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email Tone</label>
                  <select v-model="aiSettings.tone" class="form-select">
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="formal">Formal</option>
                    <option value="casual">Casual</option>
                    <option value="empathetic">Empathetic</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email Purpose</label>
                  <select v-model="aiSettings.purpose" class="form-select">
                    <option value="follow_up">Follow Up</option>
                    <option value="response">Response</option>
                    <option value="introduction">Introduction</option>
                    <option value="meeting_request">Meeting Request</option>
                    <option value="update">Update</option>
                    <option value="thank_you">Thank You</option>
                  </select>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Key Points to Include</label>
                <textarea 
                  v-model="aiSettings.keyPoints"
                  class="form-control" 
                  rows="2"
                  placeholder="Brief bullet points of what you want to communicate..."
                ></textarea>
              </div>

              <div class="d-flex justify-content-between">
                <button 
                  type="button" 
                  class="btn btn-primary"
                  @click="generateDraft"
                  :disabled="loading.aiDrafting"
                >
                  <i class="bi bi-magic me-1" :class="{ 'spin': loading.aiDrafting }"></i>
                  {{ loading.aiDrafting ? 'Generating...' : 'Generate Draft' }}
                </button>
                
                <button 
                  type="button" 
                  class="btn btn-outline-secondary"
                  @click="showDraftHistory = !showDraftHistory"
                  v-if="draftHistory.length > 0"
                >
                  <i class="bi bi-clock-history me-1"></i>
                  Draft History ({{ draftHistory.length }})
                </button>
              </div>

              <!-- Draft History -->
              <div v-if="showDraftHistory && draftHistory.length > 0" class="mt-3">
                <hr>
                <h6>Previous Drafts</h6>
                <div class="accordion" id="draftHistoryAccordion">
                  <div 
                    v-for="(draft, index) in draftHistory" 
                    :key="index"
                    class="accordion-item"
                  >
                    <h2 class="accordion-header">
                      <button 
                        class="accordion-button collapsed" 
                        type="button" 
                        data-bs-toggle="collapse" 
                        :data-bs-target="`#draft-${index}`"
                      >
                        Draft {{ index + 1 }} - {{ draft.tone }} / {{ draft.purpose }}
                        <small class="text-muted ms-2">{{ formatDraftTime(draft.timestamp) }}</small>
                      </button>
                    </h2>
                    <div 
                      :id="`draft-${index}`" 
                      class="accordion-collapse collapse" 
                      data-bs-parent="#draftHistoryAccordion"
                    >
                      <div class="accordion-body">
                        <p class="small mb-2">{{ draft.content }}</p>
                        <button 
                          type="button" 
                          class="btn btn-sm btn-outline-primary"
                          @click="useDraft(draft)"
                        >
                          Use This Draft
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Email Form -->
          <form @submit.prevent="sendEmail">
            <!-- From Account Selection -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">From Account</label>
                <select v-model="form.email_account_id" class="form-select" required>
                  <option value="">Select email account</option>
                  <option 
                    v-for="account in activeEmailAccounts" 
                    :key="account.id" 
                    :value="account.id"
                  >
                    {{ account.email }} ({{ account.provider }})
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Reply to Communication</label>
                <select v-model="form.reply_to_id" class="form-select">
                  <option value="">Not a reply</option>
                  <option 
                    v-for="comm in recentCommunications" 
                    :key="comm.id" 
                    :value="comm.id"
                  >
                    {{ comm.subject_preview || 'No Subject' }} - {{ comm.recipient_name }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Recipients -->
            <div class="row mb-3">
              <div class="col-md-4">
                <label class="form-label fw-semibold">To</label>
                <div class="input-group">
                  <input 
                    v-model="newRecipient.to"
                    @keyup.enter="addRecipient('to')"
                    type="email" 
                    class="form-control" 
                    placeholder="Enter email address"
                  >
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="addRecipient('to')"
                  >
                    <i class="bi bi-plus"></i>
                  </button>
                </div>
                <div class="mt-2">
                  <span 
                    v-for="(email, index) in form.to" 
                    :key="index"
                    class="badge bg-primary me-1 mb-1"
                  >
                    {{ email }}
                    <button 
                      type="button" 
                      class="btn-close btn-close-white ms-1" 
                      @click="removeRecipient('to', index)"
                      style="font-size: 0.6rem;"
                    ></button>
                  </span>
                </div>
              </div>
              
              <div class="col-md-4">
                <label class="form-label fw-semibold">CC</label>
                <div class="input-group">
                  <input 
                    v-model="newRecipient.cc"
                    @keyup.enter="addRecipient('cc')"
                    type="email" 
                    class="form-control" 
                    placeholder="CC email address"
                  >
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="addRecipient('cc')"
                  >
                    <i class="bi bi-plus"></i>
                  </button>
                </div>
                <div class="mt-2">
                  <span 
                    v-for="(email, index) in form.cc" 
                    :key="index"
                    class="badge bg-secondary me-1 mb-1"
                  >
                    {{ email }}
                    <button 
                      type="button" 
                      class="btn-close btn-close-white ms-1" 
                      @click="removeRecipient('cc', index)"
                      style="font-size: 0.6rem;"
                    ></button>
                  </span>
                </div>
              </div>

              <div class="col-md-4">
                <label class="form-label fw-semibold">BCC</label>
                <div class="input-group">
                  <input 
                    v-model="newRecipient.bcc"
                    @keyup.enter="addRecipient('bcc')"
                    type="email" 
                    class="form-control" 
                    placeholder="BCC email address"
                  >
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="addRecipient('bcc')"
                  >
                    <i class="bi bi-plus"></i>
                  </button>
                </div>
                <div class="mt-2">
                  <span 
                    v-for="(email, index) in form.bcc" 
                    :key="index"
                    class="badge bg-info me-1 mb-1"
                  >
                    {{ email }}
                    <button 
                      type="button" 
                      class="btn-close btn-close-white ms-1" 
                      @click="removeRecipient('bcc', index)"
                      style="font-size: 0.6rem;"
                    ></button>
                  </span>
                </div>
              </div>
            </div>

            <!-- Subject -->
            <div class="mb-3">
              <label class="form-label fw-semibold">Subject</label>
              <input 
                v-model="form.subject" 
                type="text" 
                class="form-control" 
                placeholder="Email subject"
                required
              >
            </div>

            <!-- Content -->
            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <label class="form-label fw-semibold">Message</label>
                <div class="d-flex gap-2">
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-primary"
                    @click="showAIDrafting = !showAIDrafting"
                  >
                    <i class="bi bi-robot me-1"></i>
                    {{ showAIDrafting ? 'Hide AI' : 'AI Assist' }}
                  </button>
                  
                  <div class="btn-group" role="group">
                    <button 
                      type="button" 
                      class="btn btn-sm"
                      :class="contentMode === 'text' ? 'btn-primary' : 'btn-outline-primary'"
                      @click="contentMode = 'text'"
                    >
                      Text
                    </button>
                    <button 
                      type="button" 
                      class="btn btn-sm"
                      :class="contentMode === 'html' ? 'btn-primary' : 'btn-outline-primary'"
                      @click="contentMode = 'html'"
                    >
                      HTML
                    </button>
                  </div>
                </div>
              </div>
              
              <textarea 
                v-if="contentMode === 'text'"
                v-model="form.content" 
                class="form-control" 
                rows="8"
                placeholder="Type your message here..."
                required
              ></textarea>

              <textarea 
                v-else
                v-model="form.html_content" 
                class="form-control" 
                rows="8"
                placeholder="HTML content..."
              ></textarea>

              <div class="form-text">
                <small class="text-muted">
                  Character count: {{ contentMode === 'text' ? form.content.length : form.html_content.length }}
                </small>
              </div>
            </div>

            <!-- Link to Client/Lead -->
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">Link to Client</label>
                <select v-model="form.client_id" class="form-select">
                  <option value="">No client linkage</option>
                  <option 
                    v-for="client in clients" 
                    :key="client.id" 
                    :value="client.id"
                  >
                    {{ client.first_name }} {{ client.last_name }}
                  </option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Link to Lead</label>
                <select v-model="form.lead_id" class="form-select">
                  <option value="">No lead linkage</option>
                  <option 
                    v-for="lead in leads" 
                    :key="lead.id" 
                    :value="lead.id"
                  >
                    {{ lead.first_name }} {{ lead.last_name }} - {{ lead.email }}
                  </option>
                </select>
              </div>
            </div>
          </form>
        </div>

        <!-- Footer -->
        <div class="modal-footer d-flex justify-content-between">
          <div>
            <button 
              type="button" 
              class="btn btn-outline-secondary me-2"
              @click="saveDraft"
              :disabled="!isDraftValid"
            >
              <i class="bi bi-save me-1"></i>
              Save Draft
            </button>
          </div>
          
          <div>
            <button 
              type="button" 
              class="btn btn-secondary me-2"
              @click="$emit('close')"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="sendEmail"
              :disabled="!isFormValid || loading.sending"
            >
              <i class="bi bi-send me-1" :class="{ 'spin': loading.sending }"></i>
              {{ loading.sending ? 'Sending...' : 'Send Email' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEmailStore } from '@/stores/emailStore'
import { useCommunicationStore } from '@/stores/communicationStore'

// Stores
const emailStore = useEmailStore()
const communicationStore = useCommunicationStore()

// Emits
const emit = defineEmits(['close', 'sent'])

// Component state
const form = ref({
  email_account_id: '',
  to: [],
  cc: [],
  bcc: [],
  subject: '',
  content: '',
  html_content: '',
  client_id: null,
  lead_id: null,
  reply_to_id: null
})

const newRecipient = ref({
  to: '',
  cc: '',
  bcc: ''
})

const contentMode = ref('text')
const showAIDrafting = ref(false)
const showDraftHistory = ref(false)

const aiSettings = ref({
  tone: 'professional',
  purpose: 'follow_up',
  keyPoints: ''
})

const draftHistory = ref([])
const loading = ref({
  sending: false,
  aiDrafting: false
})

// Mock data - in real app these would come from stores
const clients = ref([])
const leads = ref([])
const recentCommunications = ref([])

// Store computed
const activeEmailAccounts = computed(() => emailStore.activeEmailAccounts)

// Computed
const isFormValid = computed(() => {
  return form.value.email_account_id && 
         form.value.to.length > 0 && 
         form.value.subject.trim() && 
         (form.value.content.trim() || form.value.html_content.trim())
})

const isDraftValid = computed(() => {
  return form.value.subject.trim() || 
         form.value.content.trim() || 
         form.value.html_content.trim() ||
         form.value.to.length > 0
})

// Methods
const addRecipient = (type) => {
  const email = newRecipient.value[type].trim()
  if (email && isValidEmail(email) && !form.value[type].includes(email)) {
    form.value[type].push(email)
    newRecipient.value[type] = ''
  }
}

const removeRecipient = (type, index) => {
  form.value[type].splice(index, 1)
}

const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const generateDraft = async () => {
  loading.value.aiDrafting = true
  
  try {
    // Simulate AI draft generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const draftContent = generateAIDraftContent()
    
    // Add to draft history
    draftHistory.value.unshift({
      content: draftContent,
      tone: aiSettings.value.tone,
      purpose: aiSettings.value.purpose,
      timestamp: new Date().toISOString()
    })
    
    // Use the draft
    form.value.content = draftContent
    
    // Show success message
    // In real app, would use toast/notification
    alert('AI draft generated successfully!')
    
  } catch (error) {
    console.error('AI drafting error:', error)
    alert('Failed to generate AI draft. Please try again.')
  } finally {
    loading.value.aiDrafting = false
  }
}

const generateAIDraftContent = () => {
  // Mock AI content generation based on settings
  const { tone, purpose, keyPoints } = aiSettings.value
  
  let greeting = 'Hello'
  let body = ''
  let closing = 'Best regards'
  
  // Adjust based on tone
  switch (tone) {
    case 'friendly':
      greeting = 'Hi there!'
      closing = 'Warm regards'
      break
    case 'formal':
      greeting = 'Dear Sir/Madam'
      closing = 'Sincerely'
      break
    case 'casual':
      greeting = 'Hey!'
      closing = 'Thanks'
      break
    case 'empathetic':
      greeting = 'I hope this message finds you well'
      closing = 'With understanding'
      break
  }
  
  // Adjust based on purpose
  switch (purpose) {
    case 'follow_up':
      body = 'I wanted to follow up on our previous conversation and see how things are progressing.'
      break
    case 'response':
      body = 'Thank you for your message. I wanted to respond to the points you raised.'
      break
    case 'introduction':
      body = 'I hope this message finds you well. I wanted to take a moment to introduce myself and my services.'
      break
    case 'meeting_request':
      body = 'I would like to schedule a meeting to discuss your financial planning needs.'
      break
    case 'update':
      body = 'I wanted to provide you with an update on your financial situation.'
      break
    case 'thank_you':
      body = 'I wanted to take a moment to thank you for your continued trust in our services.'
      break
  }
  
  // Add key points if provided
  if (keyPoints.trim()) {
    body += '\n\nSpecifically, I wanted to address:\n' + 
            keyPoints.split('\n').map(point => point.trim()).filter(point => point).map(point => '• ' + point).join('\n')
  }
  
  return `${greeting},\n\n${body}\n\nPlease let me know if you have any questions or would like to discuss this further.\n\n${closing}`
}

const useDraft = (draft) => {
  form.value.content = draft.content
  showDraftHistory.value = false
}

const formatDraftTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  })
}

const saveDraft = () => {
  // Save to email store
  emailStore.updateDraftEmail({
    ...form.value,
    saved_at: new Date().toISOString()
  })
  
  // Show success message
  alert('Draft saved successfully!')
}

const sendEmail = async () => {
  if (!isFormValid.value) return
  
  loading.value.sending = true
  
  try {
    const emailData = {
      ...form.value,
      content: contentMode.value === 'text' ? form.value.content : form.value.html_content,
      html_content: contentMode.value === 'html' ? form.value.html_content : undefined
    }
    
    await emailStore.sendEmail(emailData)
    
    // Show success message
    alert('Email sent successfully!')
    
    // Clear form
    resetForm()
    
    // Emit sent event
    emit('sent')
    
    // Close modal
    emit('close')
    
  } catch (error) {
    console.error('Send email error:', error)
    alert('Failed to send email: ' + (error.message || 'Unknown error'))
  } finally {
    loading.value.sending = false
  }
}

const resetForm = () => {
  form.value = {
    email_account_id: '',
    to: [],
    cc: [],
    bcc: [],
    subject: '',
    content: '',
    html_content: '',
    client_id: null,
    lead_id: null,
    reply_to_id: null
  }
  
  newRecipient.value = {
    to: '',
    cc: '',
    bcc: ''
  }
  
  contentMode.value = 'text'
  showAIDrafting.value = false
}

// Lifecycle
onMounted(async () => {
  // Load necessary data
  try {
    await Promise.all([
      emailStore.fetchEmailAccounts(),
      // In real app, would load clients and leads
      // clientStore.fetchClients(),
      // leadStore.fetchLeads(),
      communicationStore.fetchCommunications({ limit: 10 })
    ])
    
    recentCommunications.value = communicationStore.communications.slice(0, 10)
    
    // Load draft if exists
    const draft = emailStore.draftEmail
    if (draft && (draft.subject || draft.content || draft.to.length > 0)) {
      Object.assign(form.value, draft)
    }
    
  } catch (error) {
    console.error('Error loading compose data:', error)
  }
})
</script>

<style scoped>
.modal {
  z-index: 1055;
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

.btn-close-white {
  opacity: 0.8;
}

.btn-close-white:hover {
  opacity: 1;
}

.form-label {
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.input-group .btn {
  border-left: none;
}

.accordion-button {
  font-size: 0.9rem;
  padding: 0.75rem 1rem;
}

.accordion-body {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .modal-dialog {
    max-width: 95%;
    margin: 0.5rem auto;
  }
  
  .row .col-md-4,
  .row .col-md-6 {
    margin-bottom: 1rem;
  }
  
  .btn-group .btn {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
  }
  
  .badge {
    font-size: 0.7rem;
    margin-bottom: 0.25rem;
  }
}
</style>