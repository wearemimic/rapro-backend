<template>
  <div class="modal fade show" style="display: block" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-link me-2"></i>
            Calendar Account Setup
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>

        <div class="modal-body">
          <!-- Existing Accounts -->
          <div v-if="calendarAccounts.length > 0" class="mb-4">
            <h6 class="mb-3">Connected Calendars</h6>
            <div class="connected-accounts">
              <div
                v-for="account in calendarAccounts"
                :key="account.id"
                class="account-item"
              >
                <div class="account-info">
                  <div class="account-header">
                    <div class="account-provider">
                      <i :class="getProviderIcon(account.provider)" class="me-2"></i>
                      {{ account.get_provider_display }}
                    </div>
                    <div class="account-status">
                      <span
                        class="badge"
                        :class="account.is_active ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ account.is_active ? 'Active' : 'Inactive' }}
                      </span>
                      <span
                        v-if="account.primary_calendar"
                        class="badge bg-primary ms-1"
                      >
                        Primary
                      </span>
                    </div>
                  </div>
                  
                  <div class="account-details">
                    <div class="detail-item">
                      <strong>{{ account.display_name }}</strong>
                    </div>
                    <div class="detail-item text-muted">
                      {{ account.email_address }}
                    </div>
                    <div class="detail-item small text-muted">
                      Last synced: {{ formatLastSync(account.last_sync_at) }}
                    </div>
                  </div>
                </div>

                <div class="account-actions">
                  <div class="dropdown">
                    <button
                      class="btn btn-outline-secondary btn-sm dropdown-toggle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      <i class="fas fa-cog"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                      <li>
                        <button
                          class="dropdown-item"
                          @click="syncAccount(account)"
                          :disabled="syncingAccounts.has(account.id)"
                        >
                          <i class="fas fa-sync me-2"></i>
                          <span v-if="syncingAccounts.has(account.id)">Syncing...</span>
                          <span v-else>Sync Now</span>
                        </button>
                      </li>
                      <li>
                        <button
                          class="dropdown-item"
                          @click="editAccount(account)"
                        >
                          <i class="fas fa-edit me-2"></i>
                          Settings
                        </button>
                      </li>
                      <li>
                        <button
                          class="dropdown-item"
                          @click="toggleAccountStatus(account)"
                        >
                          <i :class="account.is_active ? 'fas fa-pause' : 'fas fa-play'" class="me-2"></i>
                          {{ account.is_active ? 'Disable' : 'Enable' }}
                        </button>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <button
                          class="dropdown-item text-danger"
                          @click="confirmDeleteAccount(account)"
                        >
                          <i class="fas fa-trash me-2"></i>
                          Disconnect
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Add New Account -->
          <div class="add-account-section">
            <h6 class="mb-3">Connect New Calendar</h6>
            <p class="text-muted mb-4">
              Connect your Google Calendar or Microsoft Outlook to automatically sync meetings and appointments.
            </p>

            <div class="provider-options">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <div class="provider-card" :class="{ 'connecting': connectingProvider === 'google' }">
                    <div class="provider-icon">
                      <i class="fab fa-google"></i>
                    </div>
                    <div class="provider-info">
                      <h6>Google Calendar</h6>
                      <p>Sync with your Google Calendar and Gmail events</p>
                      <ul class="feature-list">
                        <li>Bi-directional sync</li>
                        <li>Meeting link generation</li>
                        <li>Automatic reminders</li>
                      </ul>
                    </div>
                    <div class="provider-action">
                      <button
                        class="btn btn-primary"
                        @click="connectProvider('google')"
                        :disabled="connectingProvider === 'google'"
                      >
                        <span v-if="connectingProvider === 'google'">
                          <span class="spinner-border spinner-border-sm me-2"></span>
                          Connecting...
                        </span>
                        <span v-else>
                          <i class="fas fa-plus me-1"></i>
                          Connect Google
                        </span>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <div class="provider-card" :class="{ 'connecting': connectingProvider === 'outlook' }">
                    <div class="provider-icon">
                      <i class="fab fa-microsoft"></i>
                    </div>
                    <div class="provider-info">
                      <h6>Microsoft Outlook</h6>
                      <p>Sync with Outlook Calendar and Office 365</p>
                      <ul class="feature-list">
                        <li>Exchange integration</li>
                        <li>Teams meeting links</li>
                        <li>Corporate calendar sync</li>
                      </ul>
                    </div>
                    <div class="provider-action">
                      <button
                        class="btn btn-primary"
                        @click="connectProvider('outlook')"
                        :disabled="connectingProvider === 'outlook'"
                      >
                        <span v-if="connectingProvider === 'outlook'">
                          <span class="spinner-border spinner-border-sm me-2"></span>
                          Connecting...
                        </span>
                        <span v-else>
                          <i class="fas fa-plus me-1"></i>
                          Connect Outlook
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Connection Instructions -->
          <div v-if="showInstructions" class="connection-instructions mt-4">
            <div class="alert alert-info">
              <div class="d-flex align-items-start">
                <i class="fas fa-info-circle mt-1 me-3"></i>
                <div>
                  <h6 class="alert-heading">Connection Instructions</h6>
                  <p class="mb-2">Follow these steps to connect your calendar:</p>
                  <ol class="mb-0">
                    <li>Click the "Connect" button for your calendar provider</li>
                    <li>You'll be redirected to sign in with your calendar account</li>
                    <li>Grant permission for RetirementAdvisorPro to access your calendar</li>
                    <li>You'll be redirected back here automatically</li>
                    <li>Your calendar will start syncing immediately</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            {{ error }}
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            @click="$emit('close')"
          >
            Close
          </button>
          <button
            v-if="calendarAccounts.length === 0"
            type="button"
            class="btn btn-outline-primary"
            @click="showInstructions = !showInstructions"
          >
            <i class="fas fa-question-circle me-1"></i>
            Need Help?
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Account Settings Modal -->
  <div
    v-if="showAccountSettings && editingAccount"
    class="modal fade show"
    style="display: block"
    @click.self="closeAccountSettings"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Calendar Settings</h5>
          <button
            type="button"
            class="btn-close"
            @click="closeAccountSettings"
          ></button>
        </div>
        <form @submit.prevent="saveAccountSettings">
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Display Name</label>
              <input
                type="text"
                class="form-control"
                v-model="accountSettings.display_name"
                required
              >
            </div>

            <div class="mb-3">
              <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="isActive"
                  v-model="accountSettings.is_active"
                >
                <label class="form-check-label" for="isActive">
                  Enable calendar sync
                </label>
              </div>
            </div>

            <div class="mb-3">
              <div class="form-check form-switch">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="primaryCalendar"
                  v-model="accountSettings.primary_calendar"
                >
                <label class="form-check-label" for="primaryCalendar">
                  Set as primary calendar
                </label>
              </div>
              <div class="form-text">
                New meetings will be added to your primary calendar by default.
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Sync Past Days</label>
                <select class="form-select" v-model="accountSettings.sync_past_days">
                  <option value="7">1 week</option>
                  <option value="14">2 weeks</option>
                  <option value="30">1 month</option>
                  <option value="90">3 months</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Sync Future Days</label>
                <select class="form-select" v-model="accountSettings.sync_future_days">
                  <option value="30">1 month</option>
                  <option value="60">2 months</option>
                  <option value="90">3 months</option>
                  <option value="180">6 months</option>
                  <option value="365">1 year</option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Time Zone</label>
              <select class="form-select" v-model="accountSettings.timezone">
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeAccountSettings"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingSettings"
            >
              <span v-if="savingSettings">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Saving...
              </span>
              <span v-else>Save Settings</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div
    v-if="showDeleteConfirm && accountToDelete"
    class="modal fade show"
    style="display: block"
    @click.self="closeDeleteConfirm"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title text-danger">Disconnect Calendar</h5>
          <button
            type="button"
            class="btn-close"
            @click="closeDeleteConfirm"
          ></button>
        </div>
        <div class="modal-body">
          <div class="text-center">
            <i class="fas fa-exclamation-triangle text-warning fa-3x mb-3"></i>
            <h6>Are you sure you want to disconnect this calendar?</h6>
            <p class="text-muted">
              <strong>{{ accountToDelete.display_name }}</strong><br>
              {{ accountToDelete.email_address }}
            </p>
            <p class="text-muted small">
              This will stop syncing events from this calendar. Existing events will remain in your calendar.
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            @click="closeDeleteConfirm"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-danger"
            @click="deleteAccount"
            :disabled="deletingAccount"
          >
            <span v-if="deletingAccount">
              <span class="spinner-border spinner-border-sm me-2"></span>
              Disconnecting...
            </span>
            <span v-else>Disconnect Calendar</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Backdrops -->
  <div class="modal-backdrop fade show"></div>
  <div
    v-if="showAccountSettings || showDeleteConfirm"
    class="modal-backdrop fade show"
    style="z-index: 1055"
  ></div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCalendarStore } from '@/stores/calendarStore'
import { storeToRefs } from 'pinia'
import calendarService from '@/services/calendarService'

const emit = defineEmits(['close', 'account-connected'])

// Store
const calendarStore = useCalendarStore()
const { calendarAccounts, syncingAccounts } = storeToRefs(calendarStore)

// Local state
const connectingProvider = ref('')
const error = ref('')
const showInstructions = ref(false)
const showAccountSettings = ref(false)
const showDeleteConfirm = ref(false)
const editingAccount = ref(null)
const accountToDelete = ref(null)
const savingSettings = ref(false)
const deletingAccount = ref(false)

// Account settings form
const accountSettings = ref({
  display_name: '',
  is_active: true,
  primary_calendar: false,
  sync_past_days: 30,
  sync_future_days: 90,
  timezone: 'America/New_York'
})

// Methods
const getProviderIcon = (provider) => {
  switch (provider) {
    case 'google':
      return 'fab fa-google text-danger'
    case 'outlook':
      return 'fab fa-microsoft text-primary'
    default:
      return 'fas fa-calendar'
  }
}

const formatLastSync = (dateString) => {
  if (!dateString) return 'Never'
  
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now - date) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hours ago`
  return date.toLocaleDateString()
}

const connectProvider = async (provider) => {
  connectingProvider.value = provider
  error.value = ''
  
  try {
    // Initiate OAuth flow
    const response = await calendarService.initiateOAuthFlow(provider)
    
    if (response.authorization_url) {
      // Redirect to OAuth provider
      window.location.href = response.authorization_url
    } else {
      throw new Error('Failed to get authorization URL')
    }
  } catch (err) {
    console.error('Error connecting provider:', err)
    error.value = `Failed to connect ${provider}. Please try again.`
    connectingProvider.value = ''
  }
}

const syncAccount = async (account) => {
  try {
    await calendarStore.syncCalendarAccount(account.id)
  } catch (err) {
    console.error('Error syncing account:', err)
    error.value = 'Failed to sync calendar. Please try again.'
  }
}

const toggleAccountStatus = async (account) => {
  try {
    await calendarStore.updateCalendarAccount(account.id, {
      is_active: !account.is_active
    })
  } catch (err) {
    console.error('Error toggling account status:', err)
    error.value = 'Failed to update account status.'
  }
}

const editAccount = (account) => {
  editingAccount.value = account
  accountSettings.value = {
    display_name: account.display_name,
    is_active: account.is_active,
    primary_calendar: account.primary_calendar,
    sync_past_days: account.sync_past_days,
    sync_future_days: account.sync_future_days,
    timezone: account.timezone
  }
  showAccountSettings.value = true
}

const closeAccountSettings = () => {
  showAccountSettings.value = false
  editingAccount.value = null
  accountSettings.value = {
    display_name: '',
    is_active: true,
    primary_calendar: false,
    sync_past_days: 30,
    sync_future_days: 90,
    timezone: 'America/New_York'
  }
}

const saveAccountSettings = async () => {
  if (!editingAccount.value) return
  
  savingSettings.value = true
  
  try {
    await calendarStore.updateCalendarAccount(editingAccount.value.id, accountSettings.value)
    closeAccountSettings()
  } catch (err) {
    console.error('Error saving account settings:', err)
    error.value = 'Failed to save account settings.'
  } finally {
    savingSettings.value = false
  }
}

const confirmDeleteAccount = (account) => {
  accountToDelete.value = account
  showDeleteConfirm.value = true
}

const closeDeleteConfirm = () => {
  showDeleteConfirm.value = false
  accountToDelete.value = null
}

const deleteAccount = async () => {
  if (!accountToDelete.value) return
  
  deletingAccount.value = true
  
  try {
    await calendarStore.deleteCalendarAccount(accountToDelete.value.id)
    closeDeleteConfirm()
  } catch (err) {
    console.error('Error deleting account:', err)
    error.value = 'Failed to disconnect calendar.'
  } finally {
    deletingAccount.value = false
  }
}

// Handle OAuth callback if present in URL
const handleOAuthCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  const provider = urlParams.get('provider')
  
  if (code && state && provider) {
    try {
      connectingProvider.value = provider
      
      const account = await calendarService.completeOAuthFlow(provider, code, state)
      
      // Refresh accounts list
      await calendarStore.fetchCalendarAccounts()
      
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
      
      emit('account-connected', account)
      
      // Show success message
      showSuccessMessage(`${provider} calendar connected successfully!`)
    } catch (err) {
      console.error('Error completing OAuth flow:', err)
      error.value = 'Failed to complete calendar connection. Please try again.'
    } finally {
      connectingProvider.value = ''
    }
  }
}

const showSuccessMessage = (message) => {
  // You could implement a toast notification system here
  console.log(message)
}

// Lifecycle
onMounted(async () => {
  // Handle OAuth callback if present
  await handleOAuthCallback()
  
  // Fetch latest calendar accounts
  await calendarStore.fetchCalendarAccounts()
})
</script>

<style scoped>
.connected-accounts {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  background: white;
  transition: all 0.2s ease;
}

.account-item:hover {
  border-color: #007bff;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 123, 255, 0.1);
}

.account-info {
  flex: 1;
}

.account-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.account-provider {
  font-weight: 600;
  color: #495057;
}

.account-status .badge {
  font-size: 0.75rem;
}

.account-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item {
  font-size: 0.875rem;
}

.account-actions {
  margin-left: 1rem;
}

.provider-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.provider-card {
  display: flex;
  align-items: center;
  padding: 2rem;
  border: 2px solid #dee2e6;
  border-radius: 0.75rem;
  background: white;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.provider-card:hover {
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 123, 255, 0.15);
}

.provider-card.connecting {
  border-color: #007bff;
  background: #f8f9fa;
}

.provider-card.connecting::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 123, 255, 0.1), transparent);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.provider-icon {
  font-size: 3rem;
  margin-right: 1.5rem;
  color: #495057;
}

.provider-icon .fab.fa-google {
  color: #ea4335;
}

.provider-icon .fab.fa-microsoft {
  color: #0078d4;
}

.provider-info {
  flex: 1;
}

.provider-info h6 {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #212529;
}

.provider-info p {
  margin-bottom: 1rem;
  color: #6c757d;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
  position: relative;
  padding-left: 1.25rem;
}

.feature-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #28a745;
  font-weight: bold;
}

.provider-action {
  margin-left: 1rem;
}

.connection-instructions {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
}

.connection-instructions ol {
  padding-left: 1.25rem;
}

.connection-instructions li {
  margin-bottom: 0.5rem;
  color: #495057;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .account-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .account-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .account-actions {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .provider-card {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .provider-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .provider-action {
    margin-left: 0;
    margin-top: 1rem;
  }
}

@media (max-width: 576px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .account-item {
    padding: 1rem;
  }
  
  .provider-card {
    padding: 1rem;
  }
  
  .provider-icon {
    font-size: 2rem;
  }
  
  .connection-instructions {
    font-size: 0.875rem;
  }
}

/* Dark mode support (if needed) */
@media (prefers-color-scheme: dark) {
  .account-item {
    background: #2d3748;
    border-color: #4a5568;
  }
  
  .provider-card {
    background: #2d3748;
    border-color: #4a5568;
  }
  
  .provider-card:hover {
    border-color: #3182ce;
  }
  
  .connection-instructions {
    background: #2d3748;
  }
}
</style>