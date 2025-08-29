<template>
  <div class="client-portal-access">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">
          <i class="bi bi-key me-2"></i>
          Client Portal Access
        </h6>
        <span 
          class="badge"
          :class="client.portal_access_enabled ? 'bg-success' : 'bg-secondary'"
        >
          {{ client.portal_access_enabled ? 'Enabled' : 'Disabled' }}
        </span>
      </div>
      
      <div class="card-body">
        <!-- Access Status -->
        <div class="access-status mb-4">
          <div class="row align-items-center">
            <div class="col-md-8">
              <div class="d-flex align-items-center">
                <div class="me-3">
                  <i 
                    :class="client.portal_access_enabled ? 'bi bi-check-circle-fill text-success' : 'bi bi-x-circle-fill text-danger'"
                    style="font-size: 1.5rem;"
                  ></i>
                </div>
                <div>
                  <h6 class="mb-0">
                    {{ client.portal_access_enabled ? 'Portal Access Enabled' : 'Portal Access Disabled' }}
                  </h6>
                  <small class="text-muted">
                    <span v-if="client.portal_access_enabled && client.portal_last_login">
                      Last login: {{ formatDate(client.portal_last_login) }}
                    </span>
                    <span v-else-if="client.portal_access_enabled && client.portal_invitation_sent_at">
                      Invitation sent: {{ formatDate(client.portal_invitation_sent_at) }}
                    </span>
                    <span v-else-if="!client.portal_access_enabled">
                      Client cannot access the portal
                    </span>
                    <span v-else>
                      Ready to send invitation
                    </span>
                  </small>
                </div>
              </div>
            </div>
            <div class="col-md-4 text-end">
              <div class="btn-group">
                <button 
                  v-if="!client.portal_access_enabled"
                  class="btn btn-primary btn-sm"
                  @click="enablePortalAccess"
                  :disabled="processing"
                >
                  <div v-if="processing" class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                      <span class="visually-hidden">Processing...</span>
                    </div>
                    Processing...
                  </div>
                  <div v-else>
                    <i class="bi bi-key me-1"></i>
                    Enable Access
                  </div>
                </button>
                
                <template v-else>
                  <button 
                    class="btn btn-outline-primary btn-sm"
                    @click="sendInvitation"
                    :disabled="processing"
                  >
                    <i class="bi bi-envelope me-1"></i>
                    {{ client.portal_invitation_sent_at ? 'Resend' : 'Send' }} Invitation
                  </button>
                  <button 
                    class="btn btn-outline-danger btn-sm"
                    @click="revokeAccess"
                    :disabled="processing"
                  >
                    <i class="bi bi-x-circle me-1"></i>
                    Revoke Access
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- Client Information -->
        <div v-if="client.portal_access_enabled" class="access-details">
          <div class="row">
            <div class="col-md-6">
              <div class="detail-section">
                <h6 class="detail-title">Contact Information</h6>
                <div class="detail-item">
                  <strong>Email:</strong>
                  <span class="ms-2">{{ client.email }}</span>
                </div>
                <div class="detail-item">
                  <strong>Name:</strong>
                  <span class="ms-2">{{ client.first_name }} {{ client.last_name }}</span>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="detail-section">
                <h6 class="detail-title">Portal Activity</h6>
                <div class="detail-item">
                  <strong>Account Status:</strong>
                  <span 
                    class="badge ms-2"
                    :class="client.portal_user ? 'bg-success' : 'bg-warning'"
                  >
                    {{ client.portal_user ? 'Account Created' : 'Pending Setup' }}
                  </span>
                </div>
                <div v-if="client.portal_last_login" class="detail-item">
                  <strong>Last Login:</strong>
                  <span class="ms-2">{{ formatDateTime(client.portal_last_login) }}</span>
                </div>
                <div v-if="client.portal_invitation_sent_at" class="detail-item">
                  <strong>Invitation Sent:</strong>
                  <span class="ms-2">{{ formatDateTime(client.portal_invitation_sent_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sharing Summary -->
        <div v-if="client.portal_access_enabled" class="sharing-summary mt-4">
          <h6 class="mb-3">
            <i class="bi bi-share me-2"></i>
            Shared Content Summary
          </h6>
          
          <div class="row">
            <div class="col-md-4">
              <div class="summary-card text-center p-3 bg-light rounded">
                <div class="summary-icon text-primary mb-2">
                  <i class="bi bi-graph-up display-6"></i>
                </div>
                <h5 class="mb-1">{{ sharedScenarios.length }}</h5>
                <small class="text-muted">Shared Scenarios</small>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="summary-card text-center p-3 bg-light rounded">
                <div class="summary-icon text-success mb-2">
                  <i class="bi bi-folder display-6"></i>
                </div>
                <h5 class="mb-1">{{ sharedDocuments.length }}</h5>
                <small class="text-muted">Shared Documents</small>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="summary-card text-center p-3 bg-light rounded">
                <div class="summary-icon text-info mb-2">
                  <i class="bi bi-chat-dots display-6"></i>
                </div>
                <h5 class="mb-1">{{ messageCount || 0 }}</h5>
                <small class="text-muted">Messages</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div v-if="client.portal_access_enabled" class="quick-actions mt-4">
          <h6 class="mb-3">
            <i class="bi bi-lightning me-2"></i>
            Quick Actions
          </h6>
          
          <div class="btn-group-vertical w-100">
            <button class="btn btn-outline-secondary text-start d-flex justify-content-between align-items-center mb-2">
              <span>
                <i class="bi bi-graph-up me-2"></i>
                Manage Scenario Sharing
              </span>
              <i class="bi bi-chevron-right"></i>
            </button>
            
            <button class="btn btn-outline-secondary text-start d-flex justify-content-between align-items-center mb-2">
              <span>
                <i class="bi bi-folder me-2"></i>
                Manage Document Sharing
              </span>
              <i class="bi bi-chevron-right"></i>
            </button>
            
            <button 
              class="btn btn-outline-secondary text-start d-flex justify-content-between align-items-center mb-2"
              @click="composeMessage"
            >
              <span>
                <i class="bi bi-envelope me-2"></i>
                Send Message to Client
              </span>
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Modals -->
    <Teleport to="body">
      <!-- Enable Access Modal -->
      <div v-if="showEnableModal" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title">
                  <i class="bi bi-key me-2"></i>
                  Enable Portal Access
                </h5>
                <button type="button" class="btn-close" @click="showEnableModal = false"></button>
              </div>
              <div class="modal-body">
                <p>
                  This will enable {{ client.first_name }} {{ client.last_name }} to access the client portal.
                </p>
                <div class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  <strong>What happens next:</strong>
                  <ul class="mb-0 mt-2">
                    <li>Portal access will be enabled for this client</li>
                    <li>You can then send them an invitation email</li>
                    <li>They'll be able to view shared scenarios and documents</li>
                    <li>You can revoke access at any time</li>
                  </ul>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="showEnableModal = false">
                  Cancel
                </button>
                <button type="button" class="btn btn-primary" @click="confirmEnableAccess">
                  <i class="bi bi-key me-2"></i>
                  Enable Portal Access
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="showEnableModal = false"></div>
      </div>

      <!-- Revoke Access Modal -->
      <div v-if="showRevokeModal" class="modal-overlay">
        <div class="modal" style="display: block;" tabindex="-1">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title text-danger">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  Revoke Portal Access
                </h5>
                <button type="button" class="btn-close" @click="showRevokeModal = false"></button>
              </div>
              <div class="modal-body">
                <p>
                  Are you sure you want to revoke portal access for <strong>{{ client.first_name }} {{ client.last_name }}</strong>?
                </p>
                <div class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  <strong>This will:</strong>
                  <ul class="mb-0 mt-2">
                    <li>Immediately disable their portal access</li>
                    <li>Prevent them from logging in</li>
                    <li>Hide all shared scenarios and documents</li>
                    <li>You can re-enable access later if needed</li>
                  </ul>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="showRevokeModal = false">
                  Cancel
                </button>
                <button type="button" class="btn btn-danger" @click="confirmRevokeAccess">
                  <i class="bi bi-x-circle me-2"></i>
                  Revoke Access
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-backdrop" @click="showRevokeModal = false"></div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useClientStore } from '@/stores/clientStore.js'

const props = defineProps({
  client: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['client-updated'])

const clientStore = useClientStore()

// State
const processing = ref(false)
const showEnableModal = ref(false)
const showRevokeModal = ref(false)
const sharedScenarios = ref([])
const sharedDocuments = ref([])
const messageCount = ref(0)

// Computed
const portalUrl = computed(() => {
  return `${window.location.origin}/portal`
})

// Methods
const enablePortalAccess = () => {
  showEnableModal.value = true
}

const confirmEnableAccess = async () => {
  processing.value = true
  try {
    console.log('Enabling portal access for client:', props.client.id)
    const result = await clientStore.enablePortalAccess(props.client.id)
    console.log('Portal access enabled, result:', result)
    console.log('Emitting client-updated event')
    emit('client-updated')
    showEnableModal.value = false
    // Show success message
    alert('Portal access enabled successfully! You can now send an invitation to the client.')
  } catch (error) {
    console.error('Failed to enable portal access:', error)
    alert('Failed to enable portal access. Please try again.')
  } finally {
    processing.value = false
  }
}

const revokeAccess = () => {
  showRevokeModal.value = true
}

const confirmRevokeAccess = async () => {
  processing.value = true
  try {
    await clientStore.revokePortalAccess(props.client.id)
    emit('client-updated')
    showRevokeModal.value = false
    // Show success message
    alert('Portal access revoked successfully.')
  } catch (error) {
    console.error('Failed to revoke portal access:', error)
    alert('Failed to revoke portal access. Please try again.')
  } finally {
    processing.value = false
  }
}

const sendInvitation = async () => {
  processing.value = true
  try {
    await clientStore.sendPortalInvitation(props.client.id)
    emit('client-updated')
    // Show success message
    alert(`Invitation sent to ${props.client.email} successfully!`)
  } catch (error) {
    console.error('Failed to send invitation:', error)
    alert('Failed to send invitation. Please try again.')
  } finally {
    processing.value = false
  }
}

const composeMessage = () => {
  // This would navigate to messaging or open a compose modal
  alert('Message composition feature will be implemented soon.')
}

const loadSharingData = async () => {
  try {
    // Load shared scenarios
    const scenariosResponse = await clientStore.getClientScenarios(props.client.id)
    sharedScenarios.value = (scenariosResponse.results || []).filter(s => s.share_with_client)
    
    // Load shared documents
    // This would need to be implemented in the document store
    // const documentsResponse = await documentStore.getClientDocuments(props.client.id)
    // sharedDocuments.value = (documentsResponse.results || []).filter(d => d.is_client_visible)
    
    // For now, mock data
    sharedDocuments.value = []
    messageCount.value = 0
    
  } catch (error) {
    console.error('Failed to load sharing data:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  if (props.client.portal_access_enabled) {
    loadSharingData()
  }
})
</script>

<style scoped>
.client-portal-access {
  /* Component specific styles */
}

.access-status {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.detail-section {
  margin-bottom: 1rem;
}

.detail-title {
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.detail-item {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.summary-card {
  transition: all 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  opacity: 0.8;
}

.quick-actions .btn {
  border-radius: 8px;
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