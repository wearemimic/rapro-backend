<template>
  <div class="client-portal-messages">
    <div class="page-header mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h5 class="mb-0">Messages</h5>
          <small class="text-muted">Secure communication with your advisor</small>
        </div>
        <button 
          class="btn btn-primary"
          @click="showNewMessageModal = true"
        >
          <i class="bi bi-plus-circle me-2"></i>
          New Message
        </button>
      </div>
    </div>

    <div class="row">
      <!-- Message List -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-chat-dots me-2"></i>
              Conversations
            </h6>
            <div class="btn-group btn-group-sm">
              <button 
                class="btn"
                :class="messageFilter === 'all' ? 'btn-primary' : 'btn-outline-primary'"
                @click="messageFilter = 'all'"
              >
                All
              </button>
              <button 
                class="btn"
                :class="messageFilter === 'unread' ? 'btn-primary' : 'btn-outline-primary'"
                @click="messageFilter = 'unread'"
              >
                Unread
              </button>
            </div>
          </div>
          
          <div class="message-list">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="filteredMessages.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-chat-square-text display-4 mb-2 opacity-50"></i>
              <p>No messages found</p>
              <button 
                class="btn btn-sm btn-primary"
                @click="showNewMessageModal = true"
              >
                Start Conversation
              </button>
            </div>
            
            <div v-else>
              <div 
                v-for="message in filteredMessages" 
                :key="message.id"
                class="message-item"
                :class="{ 
                  'active': selectedMessage?.id === message.id,
                  'unread': !message.is_read && message.sender_type === 'advisor'
                }"
                @click="selectMessage(message)"
              >
                <div class="message-preview p-3">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="message-info flex-grow-1">
                      <h6 class="message-subject mb-1" :class="{ 'fw-bold': !message.is_read && message.sender_type === 'advisor' }">
                        {{ message.subject }}
                      </h6>
                      <p class="message-snippet mb-1 text-muted small">
                        {{ truncateText(message.content, 60) }}
                      </p>
                      <div class="message-meta d-flex align-items-center">
                        <small class="text-muted me-2">
                          {{ formatDate(message.created_at) }}
                        </small>
                        <span 
                          v-if="message.sender_type === 'advisor'"
                          class="badge bg-info badge-sm"
                        >
                          From Advisor
                        </span>
                        <span 
                          v-else
                          class="badge bg-secondary badge-sm"
                        >
                          From You
                        </span>
                      </div>
                    </div>
                    <div class="message-indicators ms-2">
                      <i 
                        v-if="!message.is_read && message.sender_type === 'advisor'"
                        class="bi bi-circle-fill text-primary"
                        style="font-size: 0.5rem;"
                      ></i>
                      <i 
                        v-if="message.has_attachments"
                        class="bi bi-paperclip text-muted ms-1"
                      ></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Detail -->
      <div class="col-md-8">
        <div class="card" style="height: 600px; display: flex; flex-direction: column;">
          <div v-if="!selectedMessage" class="card-body d-flex align-items-center justify-content-center flex-grow-1">
            <div class="text-center text-muted">
              <i class="bi bi-chat-square-text display-1 mb-3 opacity-50"></i>
              <h5>Select a message to read</h5>
              <p>Choose a conversation from the list to view its contents</p>
            </div>
          </div>
          
          <div v-else style="display: flex; flex-direction: column; height: 100%;">
            <!-- Message Header -->
            <div class="card-header">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-0">{{ selectedMessage.subject }}</h6>
                  <small class="text-muted">
                    {{ selectedMessage.sender_type === 'advisor' ? 'From' : 'To' }} your advisor • 
                    {{ formatDateTime(selectedMessage.created_at) }}
                  </small>
                </div>
                <div class="btn-group btn-group-sm">
                  <button 
                    class="btn btn-outline-primary"
                    @click="replyToMessage"
                    title="Reply"
                  >
                    <i class="bi bi-reply"></i>
                  </button>
                  <button 
                    class="btn btn-outline-secondary"
                    @click="markAsUnread(selectedMessage)"
                    title="Mark as unread"
                  >
                    <i class="bi bi-envelope"></i>
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Message Content -->
            <div class="card-body flex-grow-1" style="overflow-y: auto;">
              <div class="message-content">
                <div class="message-body" v-html="sanitizeMessageContent(selectedMessage.content)"></div>
                
                <!-- Attachments -->
                <div v-if="selectedMessage.attachments && selectedMessage.attachments.length > 0" class="message-attachments mt-3">
                  <h6 class="small text-muted mb-2">
                    <i class="bi bi-paperclip me-1"></i>
                    Attachments ({{ selectedMessage.attachments.length }})
                  </h6>
                  <div class="attachments-list">
                    <div 
                      v-for="attachment in selectedMessage.attachments" 
                      :key="attachment.id"
                      class="attachment-item d-flex align-items-center p-2 bg-light rounded mb-2"
                    >
                      <i :class="getFileIcon(attachment.content_type) + ' me-2'"></i>
                      <div class="flex-grow-1">
                        <div class="fw-medium">{{ attachment.filename }}</div>
                        <small class="text-muted">{{ formatFileSize(attachment.file_size) }}</small>
                      </div>
                      <button 
                        class="btn btn-sm btn-outline-primary"
                        @click="downloadAttachment(attachment)"
                      >
                        <i class="bi bi-download"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Reply Section -->
            <div v-if="showReplyForm" class="card-footer">
              <div class="reply-form">
                <div class="mb-3">
                  <textarea 
                    v-model="replyContent"
                    class="form-control"
                    rows="3"
                    placeholder="Type your reply..."
                  ></textarea>
                </div>
                <div class="d-flex justify-content-between">
                  <div>
                    <input 
                      ref="attachmentInput"
                      type="file"
                      multiple
                      style="display: none"
                      @change="handleAttachmentSelection"
                    />
                    <button 
                      class="btn btn-outline-secondary btn-sm me-2"
                      @click="$refs.attachmentInput.click()"
                    >
                      <i class="bi bi-paperclip me-1"></i>
                      Attach
                    </button>
                    <small class="text-muted">{{ attachments.length }} file(s) selected</small>
                  </div>
                  <div>
                    <button 
                      class="btn btn-outline-secondary btn-sm me-2"
                      @click="cancelReply"
                    >
                      Cancel
                    </button>
                    <button 
                      class="btn btn-primary btn-sm"
                      @click="sendReply"
                      :disabled="!replyContent.trim() || sending"
                    >
                      <div v-if="sending" class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-2" role="status">
                          <span class="visually-hidden">Sending...</span>
                        </div>
                        Sending...
                      </div>
                      <div v-else>
                        <i class="bi bi-send me-1"></i>
                        Send Reply
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Message Modal -->
    <Teleport to="body">
      <div v-if="showNewMessageModal" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-envelope me-2"></i>
                  New Message
                </h5>
                <button type="button" class="btn-close" @click="closeNewMessageModal"></button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="sendNewMessage">
                  <div class="mb-3">
                    <label class="form-label">Subject</label>
                    <input 
                      v-model="newMessage.subject"
                      type="text" 
                      class="form-control"
                      placeholder="Enter subject"
                      required
                    />
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Message</label>
                    <textarea 
                      v-model="newMessage.content"
                      class="form-control"
                      rows="6"
                      placeholder="Type your message..."
                      required
                    ></textarea>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Attachments (optional)</label>
                    <input 
                      ref="newMessageAttachmentInput"
                      type="file"
                      class="form-control"
                      multiple
                      @change="handleNewMessageAttachments"
                    />
                    <small class="text-muted">Multiple files supported (up to 50MB each)</small>
                  </div>
                </form>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeNewMessageModal">
                  Cancel
                </button>
                <button 
                  type="button" 
                  class="btn btn-primary"
                  @click="sendNewMessage"
                  :disabled="!newMessage.subject.trim() || !newMessage.content.trim() || sending"
                >
                  <div v-if="sending" class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                      <span class="visually-hidden">Sending...</span>
                    </div>
                    Sending...
                  </div>
                  <div v-else>
                    <i class="bi bi-send me-2"></i>
                    Send Message
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="closeNewMessageModal"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCommunicationStore } from '@/stores/communicationStore.js'
import { sanitizeHTML } from '@/utils/sanitizer'

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['messages-updated'])

const communicationStore = useCommunicationStore()

// State
const messages = ref([])
const selectedMessage = ref(null)
const loading = ref(false)
const messageFilter = ref('all')
const showNewMessageModal = ref(false)
const showReplyForm = ref(false)
const replyContent = ref('')
const attachments = ref([])
const sending = ref(false)

const newMessage = ref({
  subject: '',
  content: '',
  attachments: []
})

// Computed
const filteredMessages = computed(() => {
  if (messageFilter.value === 'unread') {
    return messages.value.filter(msg => !msg.is_read && msg.sender_type === 'advisor')
  }
  return messages.value
})

const unreadCount = computed(() => {
  return messages.value.filter(msg => !msg.is_read && msg.sender_type === 'advisor').length
})

// Methods
const loadMessages = async () => {
  loading.value = true
  try {
    const response = await communicationStore.getClientMessages(props.client.id)
    messages.value = response.results || []
    emit('messages-updated', unreadCount.value)
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    loading.value = false
  }
}

const selectMessage = async (message) => {
  selectedMessage.value = message
  showReplyForm.value = false
  
  // Mark as read if it's from advisor
  if (!message.is_read && message.sender_type === 'advisor') {
    try {
      await communicationStore.markMessageAsRead(message.id)
      message.is_read = true
      emit('messages-updated', unreadCount.value)
    } catch (error) {
      console.error('Failed to mark message as read:', error)
    }
  }
}

const replyToMessage = () => {
  showReplyForm.value = true
  replyContent.value = ''
  attachments.value = []
}

const cancelReply = () => {
  showReplyForm.value = false
  replyContent.value = ''
  attachments.value = []
}

const sendReply = async () => {
  if (!replyContent.value.trim()) return
  
  sending.value = true
  try {
    await communicationStore.sendMessage({
      client_id: props.client.id,
      subject: `Re: ${selectedMessage.value.subject}`,
      content: replyContent.value,
      attachments: attachments.value,
      parent_message_id: selectedMessage.value.id
    })
    
    await loadMessages()
    cancelReply()
  } catch (error) {
    console.error('Failed to send reply:', error)
    alert('Failed to send reply. Please try again.')
  } finally {
    sending.value = false
  }
}

const handleAttachmentSelection = (e) => {
  attachments.value = Array.from(e.target.files)
}

const sendNewMessage = async () => {
  if (!newMessage.value.subject.trim() || !newMessage.value.content.trim()) return
  
  sending.value = true
  try {
    await communicationStore.sendMessage({
      client_id: props.client.id,
      subject: newMessage.value.subject,
      content: newMessage.value.content,
      attachments: newMessage.value.attachments
    })
    
    await loadMessages()
    closeNewMessageModal()
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message. Please try again.')
  } finally {
    sending.value = false
  }
}

const handleNewMessageAttachments = (e) => {
  newMessage.value.attachments = Array.from(e.target.files)
}

const closeNewMessageModal = () => {
  showNewMessageModal.value = false
  newMessage.value = {
    subject: '',
    content: '',
    attachments: []
  }
}

const markAsUnread = async (message) => {
  try {
    await communicationStore.markMessageAsUnread(message.id)
    message.is_read = false
    emit('messages-updated', unreadCount.value)
  } catch (error) {
    console.error('Failed to mark message as unread:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

const sanitizeMessageContent = (content) => {
  if (!content) return ''
  // Convert newlines to <br> tags first
  const withBreaks = content.replace(/\n/g, '<br>')
  // Then sanitize to prevent XSS
  return sanitizeHTML(withBreaks, false)
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (contentType) => {
  const iconMap = {
    'application/pdf': 'bi-file-pdf-fill text-danger',
    'application/msword': 'bi-file-word-fill text-primary',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'bi-file-word-fill text-primary',
    'application/vnd.ms-excel': 'bi-file-excel-fill text-success',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'bi-file-excel-fill text-success',
    'image/jpeg': 'bi-file-image-fill text-warning',
    'image/png': 'bi-file-image-fill text-warning'
  }
  return iconMap[contentType] || 'bi-file-fill text-muted'
}

const downloadAttachment = async (attachment) => {
  try {
    // This would need to be implemented in the communication store
    console.log('Download attachment:', attachment)
    alert('Download functionality will be implemented soon.')
  } catch (error) {
    console.error('Download failed:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.client-portal-messages {
  padding: 0;
}

.page-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.message-list {
  max-height: 600px;
  overflow-y: auto;
  border-top: 1px solid #dee2e6;
}

.message-item {
  border-bottom: 1px solid #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.message-item:hover {
  background-color: #f8f9fa;
}

.message-item.active {
  background-color: #e3f2fd;
  border-left: 3px solid #007bff;
}

.message-item.unread {
  background-color: #fff8e1;
}

.message-item.unread .message-subject {
  color: #1976d2;
}

.message-preview {
  position: relative;
}

.message-indicators {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.message-content {
  line-height: 1.6;
}

.message-body {
  color: #495057;
}

.attachment-item {
  border: 1px solid #dee2e6;
}

.reply-form {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
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

.badge-sm {
  font-size: 0.65rem;
  padding: 0.25em 0.5em;
}
</style>