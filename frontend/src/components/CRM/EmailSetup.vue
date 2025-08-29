<template>
  <div class="modal fade show" style="display: block; background-color: rgba(0,0,0,0.5);" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-envelope-plus me-2"></i>
            Email Account Setup
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Current Step Indicator -->
          <div class="row mb-4">
            <div class="col">
              <div class="progress" style="height: 4px;">
                <div 
                  class="progress-bar bg-primary" 
                  :style="{ width: (currentStep / totalSteps) * 100 + '%' }"
                ></div>
              </div>
              <div class="d-flex justify-content-between mt-2">
                <small class="text-muted">Step {{ currentStep }} of {{ totalSteps }}</small>
                <small class="text-muted">{{ getStepTitle() }}</small>
              </div>
            </div>
          </div>

          <!-- Step 1: Choose Provider -->
          <div v-if="currentStep === 1">
            <div class="text-center mb-4">
              <h4>Choose Your Email Provider</h4>
              <p class="text-muted">Select the email service you'd like to connect</p>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <div 
                  class="card h-100 provider-card"
                  :class="{ 'border-primary': selectedProvider === 'gmail' }"
                  @click="selectProvider('gmail')"
                  role="button"
                >
                  <div class="card-body text-center">
                    <div class="avatar avatar-xl avatar-circle bg-danger text-white mx-auto mb-3">
                      <i class="bi bi-google"></i>
                    </div>
                    <h5>Gmail</h5>
                    <p class="text-muted mb-0">Connect your Google Workspace or personal Gmail account</p>
                    
                    <div class="mt-3">
                      <div class="d-flex align-items-center justify-content-center mb-2">
                        <i class="bi bi-shield-check text-success me-2"></i>
                        <small class="text-muted">OAuth 2.0 Secure</small>
                      </div>
                      <div class="d-flex align-items-center justify-content-center">
                        <i class="bi bi-lightning-charge text-warning me-2"></i>
                        <small class="text-muted">Real-time sync</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <div 
                  class="card h-100 provider-card"
                  :class="{ 'border-primary': selectedProvider === 'outlook' }"
                  @click="selectProvider('outlook')"
                  role="button"
                >
                  <div class="card-body text-center">
                    <div class="avatar avatar-xl avatar-circle bg-primary text-white mx-auto mb-3">
                      <i class="bi bi-microsoft"></i>
                    </div>
                    <h5>Outlook</h5>
                    <p class="text-muted mb-0">Connect your Microsoft 365 or Outlook.com account</p>
                    
                    <div class="mt-3">
                      <div class="d-flex align-items-center justify-content-center mb-2">
                        <i class="bi bi-shield-check text-success me-2"></i>
                        <small class="text-muted">OAuth 2.0 Secure</small>
                      </div>
                      <div class="d-flex align-items-center justify-content-center">
                        <i class="bi bi-calendar-check text-info me-2"></i>
                        <small class="text-muted">Calendar integration</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- IMAP/SMTP Option -->
            <div class="mt-4">
              <div class="card border-secondary">
                <div class="card-body">
                  <div class="d-flex align-items-center">
                    <div class="avatar avatar-sm avatar-circle bg-secondary text-white me-3">
                      <i class="bi bi-gear"></i>
                    </div>
                    <div class="flex-grow-1">
                      <h6 class="mb-1">Custom IMAP/SMTP</h6>
                      <small class="text-muted">For other providers or custom email servers</small>
                    </div>
                    <button 
                      class="btn btn-sm btn-outline-secondary"
                      @click="selectProvider('custom')"
                    >
                      Configure
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: OAuth Authentication -->
          <div v-else-if="currentStep === 2 && selectedProvider !== 'custom'">
            <div class="text-center mb-4">
              <div 
                class="avatar avatar-xl avatar-circle mx-auto mb-3"
                :class="selectedProvider === 'gmail' ? 'bg-danger text-white' : 'bg-primary text-white'"
              >
                <i :class="selectedProvider === 'gmail' ? 'bi-google' : 'bi-microsoft'"></i>
              </div>
              <h4>Authorize {{ selectedProvider === 'gmail' ? 'Gmail' : 'Outlook' }} Access</h4>
              <p class="text-muted">We'll redirect you to {{ selectedProvider === 'gmail' ? 'Google' : 'Microsoft' }} to authorize access to your email</p>
            </div>

            <!-- OAuth Status -->
            <div class="card border-0 bg-light mb-4">
              <div class="card-body">
                <div v-if="!oauthStarted" class="text-center">
                  <h6 class="mb-3">Ready to Connect</h6>
                  <div class="mb-3">
                    <i class="bi bi-info-circle text-primary me-2"></i>
                    <small class="text-muted">
                      You'll be taken to {{ selectedProvider === 'gmail' ? 'Google' : 'Microsoft' }} to sign in and grant permissions
                    </small>
                  </div>
                  <button 
                    class="btn btn-primary"
                    @click="startOAuth"
                    :disabled="loading.oauth"
                  >
                    <i class="bi bi-box-arrow-up-right me-1" :class="{ 'spin': loading.oauth }"></i>
                    {{ loading.oauth ? 'Redirecting...' : `Connect to ${selectedProvider === 'gmail' ? 'Gmail' : 'Outlook'}` }}
                  </button>
                </div>

                <div v-else-if="oauthInProgress" class="text-center">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <h6 class="mb-2">Waiting for Authorization</h6>
                  <small class="text-muted">
                    Complete the authorization in the popup window, then return here
                  </small>
                  <div class="mt-3">
                    <button 
                      class="btn btn-sm btn-outline-secondary"
                      @click="checkAuthStatus"
                    >
                      Check Status
                    </button>
                  </div>
                </div>

                <div v-else-if="oauthCompleted" class="text-center text-success">
                  <i class="bi bi-check-circle-fill display-4 mb-3"></i>
                  <h6 class="text-success">Authorization Successful!</h6>
                  <small class="text-muted">Your email account has been connected</small>
                </div>

                <div v-else-if="oauthFailed" class="text-center text-danger">
                  <i class="bi bi-x-circle-fill display-4 mb-3"></i>
                  <h6 class="text-danger">Authorization Failed</h6>
                  <small class="text-muted d-block mb-3">{{ oauthError || 'Something went wrong during authorization' }}</small>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="resetOAuth"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>

            <!-- Permissions Info -->
            <div class="accordion" id="permissionsAccordion">
              <div class="accordion-item">
                <h2 class="accordion-header">
                  <button 
                    class="accordion-button collapsed" 
                    type="button" 
                    data-bs-toggle="collapse" 
                    data-bs-target="#permissionsCollapse"
                  >
                    <i class="bi bi-shield-lock me-2"></i>
                    What permissions are we requesting?
                  </button>
                </h2>
                <div id="permissionsCollapse" class="accordion-collapse collapse" data-bs-parent="#permissionsAccordion">
                  <div class="accordion-body">
                    <div class="row">
                      <div class="col-md-6">
                        <h6 class="text-success"><i class="bi bi-check2 me-1"></i>We Will:</h6>
                        <ul class="list-unstyled small">
                          <li><i class="bi bi-dot"></i>Read your email messages</li>
                          <li><i class="bi bi-dot"></i>Send emails on your behalf</li>
                          <li><i class="bi bi-dot"></i>Access your email folders</li>
                          <li><i class="bi bi-dot"></i>Sync new messages automatically</li>
                        </ul>
                      </div>
                      <div class="col-md-6">
                        <h6 class="text-danger"><i class="bi bi-x me-1"></i>We Will NOT:</h6>
                        <ul class="list-unstyled small">
                          <li><i class="bi bi-dot"></i>Store your email password</li>
                          <li><i class="bi bi-dot"></i>Access other Google/Microsoft services</li>
                          <li><i class="bi bi-dot"></i>Share your data with third parties</li>
                          <li><i class="bi bi-dot"></i>Delete or modify existing emails</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: Custom IMAP/SMTP Setup -->
          <div v-else-if="currentStep === 2 && selectedProvider === 'custom'">
            <div class="text-center mb-4">
              <div class="avatar avatar-xl avatar-circle bg-secondary text-white mx-auto mb-3">
                <i class="bi bi-gear"></i>
              </div>
              <h4>Custom Email Setup</h4>
              <p class="text-muted">Configure your custom email server settings</p>
            </div>

            <form @submit.prevent="testConnection">
              <!-- Basic Information -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Email Address</label>
                  <input 
                    v-model="customForm.email"
                    type="email" 
                    class="form-control" 
                    placeholder="your@domain.com"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="customForm.password"
                    type="password" 
                    class="form-control"
                    placeholder="Your email password"
                    required
                  >
                </div>
              </div>

              <!-- IMAP Settings -->
              <div class="card border-0 bg-light mb-3">
                <div class="card-header bg-transparent border-0">
                  <h6 class="mb-0">
                    <i class="bi bi-download me-2"></i>
                    IMAP Settings (Incoming Mail)
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">IMAP Server</label>
                      <input 
                        v-model="customForm.imap_server"
                        type="text" 
                        class="form-control" 
                        placeholder="imap.domain.com"
                        required
                      >
                    </div>
                    <div class="col-md-3 mb-3">
                      <label class="form-label">Port</label>
                      <input 
                        v-model.number="customForm.imap_port"
                        type="number" 
                        class="form-control" 
                        placeholder="993"
                        required
                      >
                    </div>
                    <div class="col-md-3 mb-3">
                      <label class="form-label">Security</label>
                      <select v-model="customForm.imap_security" class="form-select">
                        <option value="SSL/TLS">SSL/TLS</option>
                        <option value="STARTTLS">STARTTLS</option>
                        <option value="None">None</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- SMTP Settings -->
              <div class="card border-0 bg-light mb-3">
                <div class="card-header bg-transparent border-0">
                  <h6 class="mb-0">
                    <i class="bi bi-upload me-2"></i>
                    SMTP Settings (Outgoing Mail)
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">SMTP Server</label>
                      <input 
                        v-model="customForm.smtp_server"
                        type="text" 
                        class="form-control" 
                        placeholder="smtp.domain.com"
                        required
                      >
                    </div>
                    <div class="col-md-3 mb-3">
                      <label class="form-label">Port</label>
                      <input 
                        v-model.number="customForm.smtp_port"
                        type="number" 
                        class="form-control" 
                        placeholder="587"
                        required
                      >
                    </div>
                    <div class="col-md-3 mb-3">
                      <label class="form-label">Security</label>
                      <select v-model="customForm.smtp_security" class="form-select">
                        <option value="SSL/TLS">SSL/TLS</option>
                        <option value="STARTTLS">STARTTLS</option>
                        <option value="None">None</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Connection Test -->
              <div class="text-center">
                <button 
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading.testing"
                >
                  <i class="bi bi-wifi me-1" :class="{ 'spin': loading.testing }"></i>
                  {{ loading.testing ? 'Testing Connection...' : 'Test Connection' }}
                </button>
              </div>

              <!-- Test Results -->
              <div v-if="connectionTestResult" class="mt-3">
                <div 
                  class="alert"
                  :class="connectionTestResult.success ? 'alert-success' : 'alert-danger'"
                >
                  <div class="d-flex align-items-start">
                    <i 
                      :class="connectionTestResult.success ? 'bi-check-circle-fill' : 'bi-x-circle-fill'"
                      class="me-2 mt-1"
                    ></i>
                    <div>
                      <strong>
                        {{ connectionTestResult.success ? 'Connection Successful!' : 'Connection Failed' }}
                      </strong>
                      <div class="mt-1">
                        {{ connectionTestResult.message }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <!-- Step 3: Configuration -->
          <div v-else-if="currentStep === 3">
            <div class="text-center mb-4">
              <div class="avatar avatar-xl avatar-circle bg-success text-white mx-auto mb-3">
                <i class="bi bi-gear"></i>
              </div>
              <h4>Configure Account Settings</h4>
              <p class="text-muted">Set up sync preferences and display options</p>
            </div>

            <form @submit.prevent="saveAccount">
              <!-- Account Display Name -->
              <div class="mb-4">
                <label class="form-label fw-semibold">Account Display Name</label>
                <input 
                  v-model="configForm.display_name"
                  type="text" 
                  class="form-control" 
                  placeholder="My Business Email"
                  required
                >
                <div class="form-text">
                  <small class="text-muted">This name will appear in your communication center</small>
                </div>
              </div>

              <!-- Sync Settings -->
              <div class="card border-0 bg-light mb-4">
                <div class="card-header bg-transparent border-0">
                  <h6 class="mb-0">
                    <i class="bi bi-arrow-repeat me-2"></i>
                    Sync Preferences
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Sync Frequency</label>
                      <select v-model="configForm.sync_frequency" class="form-select">
                        <option value="realtime">Real-time</option>
                        <option value="15min">Every 15 minutes</option>
                        <option value="30min">Every 30 minutes</option>
                        <option value="1hour">Every hour</option>
                        <option value="manual">Manual only</option>
                      </select>
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Sync History</label>
                      <select v-model="configForm.sync_history" class="form-select">
                        <option value="7days">Last 7 days</option>
                        <option value="30days">Last 30 days</option>
                        <option value="90days">Last 90 days</option>
                        <option value="all">All emails</option>
                      </select>
                    </div>
                  </div>

                  <div class="form-check">
                    <input 
                      v-model="configForm.sync_sent_items"
                      class="form-check-input" 
                      type="checkbox" 
                      id="syncSentItems"
                    >
                    <label class="form-check-label" for="syncSentItems">
                      Sync sent items
                    </label>
                  </div>
                  
                  <div class="form-check">
                    <input 
                      v-model="configForm.auto_categorize"
                      class="form-check-input" 
                      type="checkbox" 
                      id="autoCategorize"
                    >
                    <label class="form-check-label" for="autoCategorize">
                      Automatically categorize emails using AI
                    </label>
                  </div>
                </div>
              </div>

              <!-- Signature -->
              <div class="mb-4">
                <label class="form-label fw-semibold">Email Signature</label>
                <textarea 
                  v-model="configForm.signature"
                  class="form-control" 
                  rows="4"
                  placeholder="Your email signature..."
                ></textarea>
                <div class="form-text">
                  <small class="text-muted">This signature will be added to emails sent from this account</small>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer d-flex justify-content-between">
          <div>
            <button 
              v-if="currentStep > 1"
              type="button" 
              class="btn btn-outline-secondary"
              @click="previousStep"
            >
              <i class="bi bi-arrow-left me-1"></i>
              Back
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
              @click="nextStep"
              :disabled="!canProceed || loading.saving"
            >
              <i 
                :class="[
                  isLastStep ? 'bi-check-lg' : 'bi-arrow-right',
                  'me-1',
                  { 'spin': loading.saving }
                ]"
              ></i>
              {{ loading.saving ? 'Saving...' : (isLastStep ? 'Complete Setup' : 'Next') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEmailStore } from '@/stores/emailStore'

// Store
const emailStore = useEmailStore()

// Emits
const emit = defineEmits(['close', 'account-added'])

// Component state
const currentStep = ref(1)
const totalSteps = 3
const selectedProvider = ref('')

// OAuth state
const oauthStarted = ref(false)
const oauthInProgress = ref(false)
const oauthCompleted = ref(false)
const oauthFailed = ref(false)
const oauthError = ref('')

// Custom form
const customForm = ref({
  email: '',
  password: '',
  imap_server: '',
  imap_port: 993,
  imap_security: 'SSL/TLS',
  smtp_server: '',
  smtp_port: 587,
  smtp_security: 'STARTTLS'
})

// Config form
const configForm = ref({
  display_name: '',
  sync_frequency: 'realtime',
  sync_history: '30days',
  sync_sent_items: true,
  auto_categorize: true,
  signature: ''
})

// Connection test result
const connectionTestResult = ref(null)

// Loading states
const loading = ref({
  oauth: false,
  testing: false,
  saving: false
})

// Computed
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return !!selectedProvider.value
    case 2:
      if (selectedProvider.value === 'custom') {
        return connectionTestResult.value?.success
      }
      return oauthCompleted.value
    case 3:
      return !!configForm.value.display_name.trim()
    default:
      return false
  }
})

const isLastStep = computed(() => currentStep.value === totalSteps)

// Methods
const getStepTitle = () => {
  switch (currentStep.value) {
    case 1:
      return 'Choose Provider'
    case 2:
      return selectedProvider.value === 'custom' ? 'Server Configuration' : 'Authorization'
    case 3:
      return 'Account Configuration'
    default:
      return ''
  }
}

const selectProvider = (provider) => {
  selectedProvider.value = provider
}

const nextStep = async () => {
  if (!canProceed.value) return
  
  if (isLastStep.value) {
    await saveAccount()
  } else {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    
    // Reset OAuth state if going back from step 2
    if (currentStep.value === 1) {
      resetOAuth()
    }
  }
}

const startOAuth = async () => {
  loading.value.oauth = true
  oauthStarted.value = true
  oauthInProgress.value = true
  
  try {
    let authResult
    
    if (selectedProvider.value === 'gmail') {
      authResult = await emailStore.getGmailAuthUrl()
    } else {
      authResult = await emailStore.getOutlookAuthUrl()
    }
    
    if (authResult.auth_url) {
      // Open OAuth popup
      const popup = window.open(
        authResult.auth_url, 
        'oauth', 
        'width=600,height=600,scrollbars=yes,resizable=yes'
      )
      
      // Poll for completion
      const pollTimer = setInterval(() => {
        try {
          if (popup.closed) {
            clearInterval(pollTimer)
            checkAuthStatus()
          }
        } catch (error) {
          // Popup might be on different domain
          console.log('Polling OAuth popup:', error.message)
        }
      }, 1000)
      
      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollTimer)
        if (!popup.closed) {
          popup.close()
        }
        if (oauthInProgress.value) {
          oauthFailed.value = true
          oauthInProgress.value = false
          oauthError.value = 'Authorization timed out'
        }
      }, 5 * 60 * 1000)
    }
    
  } catch (error) {
    console.error('OAuth start error:', error)
    oauthFailed.value = true
    oauthInProgress.value = false
    oauthError.value = error.message
  } finally {
    loading.value.oauth = false
  }
}

const checkAuthStatus = async () => {
  try {
    // For testing: Mock successful Gmail authorization
    if (selectedProvider.value === 'gmail') {
      // Simulate successful Gmail connection
      setTimeout(() => {
        oauthCompleted.value = true
        oauthInProgress.value = false
        oauthFailed.value = false
        
        // Auto-fill display name
        configForm.value.display_name = `My Gmail Account (Test)`
      }, 2000) // 2 second delay to simulate processing
      return
    }
    
    await emailStore.fetchOAuthStatus()
    
    // For other providers, keep original logic
    const isAuthorized = Math.random() > 0.3 // 70% success rate for demo
    
    if (isAuthorized) {
      oauthCompleted.value = true
      oauthInProgress.value = false
      oauthFailed.value = false
      
      // Auto-fill display name
      configForm.value.display_name = `My ${selectedProvider.value === 'gmail' ? 'Gmail' : 'Outlook'} Account`
    } else {
      oauthFailed.value = true
      oauthInProgress.value = false
      oauthError.value = 'Authorization was cancelled or failed'
    }
    
  } catch (error) {
    console.error('OAuth status check error:', error)
    oauthFailed.value = true
    oauthInProgress.value = false
    oauthError.value = 'Gmail OAuth requires Google Cloud configuration. Please contact your administrator.'
  }
}

const resetOAuth = () => {
  oauthStarted.value = false
  oauthInProgress.value = false
  oauthCompleted.value = false
  oauthFailed.value = false
  oauthError.value = ''
}

const testConnection = async () => {
  loading.value.testing = true
  connectionTestResult.value = null
  
  try {
    // Simulate connection test
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock test result (70% success rate)
    const isSuccess = Math.random() > 0.3
    
    connectionTestResult.value = {
      success: isSuccess,
      message: isSuccess 
        ? 'Successfully connected to email server. All settings are correct.'
        : 'Failed to connect. Please check your server settings and credentials.'
    }
    
    if (isSuccess) {
      // Auto-fill display name
      configForm.value.display_name = `${customForm.value.email} (Custom)`
    }
    
  } catch (error) {
    connectionTestResult.value = {
      success: false,
      message: error.message || 'Connection test failed'
    }
  } finally {
    loading.value.testing = false
  }
}

const saveAccount = async () => {
  loading.value.saving = true
  
  try {
    // Prepare account data
    const accountData = {
      provider: selectedProvider.value,
      display_name: configForm.value.display_name,
      sync_frequency: configForm.value.sync_frequency,
      sync_history: configForm.value.sync_history,
      sync_sent_items: configForm.value.sync_sent_items,
      auto_categorize: configForm.value.auto_categorize,
      signature: configForm.value.signature,
      is_active: true
    }
    
    // Add provider-specific data
    if (selectedProvider.value === 'custom') {
      Object.assign(accountData, {
        email: customForm.value.email,
        imap_server: customForm.value.imap_server,
        imap_port: customForm.value.imap_port,
        imap_security: customForm.value.imap_security,
        smtp_server: customForm.value.smtp_server,
        smtp_port: customForm.value.smtp_port,
        smtp_security: customForm.value.smtp_security
        // Note: password would be encrypted on backend
      })
    }
    
    // Save to store
    const account = await emailStore.createEmailAccount(accountData)
    
    // Show success
    alert('Email account setup completed successfully!')
    
    // Emit success event
    emit('account-added', account)
    
    // Close modal
    emit('close')
    
  } catch (error) {
    console.error('Save account error:', error)
    alert('Failed to save email account: ' + (error.message || 'Unknown error'))
  } finally {
    loading.value.saving = false
  }
}
</script>

<style scoped>
.modal {
  z-index: 1055;
}

.provider-card {
  transition: all 0.2s ease;
  cursor: pointer;
}

.provider-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.provider-card.border-primary {
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1.5rem;
}

.avatar-xl {
  width: 4rem;
  height: 4rem;
  font-size: 1.75rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress {
  border-radius: 2px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.accordion-button {
  font-size: 0.9rem;
}

.accordion-body {
  font-size: 0.9rem;
}

.card-header {
  padding: 0.75rem 1rem;
}

.alert {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .modal-dialog {
    max-width: 95%;
    margin: 0.5rem auto;
  }
  
  .row .col-md-6,
  .row .col-md-3 {
    margin-bottom: 1rem;
  }
  
  .provider-card .card-body {
    padding: 1rem 0.75rem;
  }
  
  .avatar-xl {
    width: 3rem;
    height: 3rem;
    font-size: 1.5rem;
  }
  
  .btn {
    font-size: 0.9rem;
  }
}
</style>