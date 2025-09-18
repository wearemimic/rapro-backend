<template>
  <div class="affiliate-portal-login">
    <div class="container-fluid vh-100">
      <div class="row h-100 align-items-center justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <h2 class="text-success mb-2">
                  <i class="bi bi-graph-up me-2"></i>
                  Affiliate Portal
                </h2>
                <p class="text-muted">Access your affiliate dashboard</p>
              </div>

              <!-- Error Messages -->
              <div v-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ error }}
              </div>

              <!-- Success Messages -->
              <div v-if="successMessage" class="alert alert-success" role="alert">
                <i class="bi bi-check-circle me-2"></i>
                {{ successMessage }}
              </div>

              <!-- Login Form -->
              <form v-if="!showPasswordSetup" @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    v-model="loginForm.email"
                    class="form-control"
                    :class="{ 'is-invalid': errors.email }"
                    required
                    :disabled="loading"
                    placeholder="your@email.com"
                  >
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="code" class="form-label">
                    {{ usePassword ? 'Password' : 'Affiliate Code' }}
                  </label>
                  <input
                    :type="usePassword ? 'password' : 'text'"
                    id="code"
                    v-model="loginForm.credential"
                    class="form-control"
                    :class="{ 'is-invalid': errors.credential }"
                    required
                    :disabled="loading"
                    :placeholder="usePassword ? 'Enter your password' : 'Enter your affiliate code'"
                  >
                  <div v-if="errors.credential" class="invalid-feedback">
                    {{ errors.credential }}
                  </div>
                </div>

                <div class="mb-3">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      id="usePassword"
                      v-model="usePassword"
                      class="form-check-input"
                      :disabled="loading"
                    >
                    <label for="usePassword" class="form-check-label">
                      I have a password
                    </label>
                  </div>
                </div>

                <button
                  type="submit"
                  class="btn btn-success w-100"
                  :disabled="loading"
                >
                  <div v-if="loading" class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                      <span class="visually-hidden">Logging in...</span>
                    </div>
                    Verifying Credentials...
                  </div>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Access Dashboard
                  </span>
                </button>
              </form>

              <!-- Password Setup Form -->
              <form v-else @submit.prevent="handlePasswordSetup">
                <div class="alert alert-info mb-4">
                  <i class="bi bi-info-circle me-2"></i>
                  <strong>First Time Access</strong> 
                  <br>Please create a password to secure your affiliate portal access.
                </div>

                <div class="mb-3">
                  <label for="new-password" class="form-label">Create Password</label>
                  <input
                    type="password"
                    id="new-password"
                    v-model="passwordForm.password"
                    class="form-control"
                    :class="{ 'is-invalid': errors.password }"
                    required
                    :disabled="loading"
                    minlength="8"
                    placeholder="Minimum 8 characters"
                  >
                  <div v-if="errors.password" class="invalid-feedback">
                    {{ errors.password }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="confirm-password" class="form-label">Confirm Password</label>
                  <input
                    type="password"
                    id="confirm-password"
                    v-model="passwordForm.confirmPassword"
                    class="form-control"
                    :class="{ 'is-invalid': errors.confirmPassword }"
                    required
                    :disabled="loading"
                    minlength="8"
                    placeholder="Re-enter your password"
                  >
                  <div v-if="errors.confirmPassword" class="invalid-feedback">
                    {{ errors.confirmPassword }}
                  </div>
                </div>

                <div class="mb-4">
                  <small class="text-muted">
                    <i class="bi bi-shield-check me-1"></i>
                    Password must be at least 8 characters long and contain a mix of letters and numbers.
                  </small>
                </div>

                <div class="d-flex gap-2">
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPasswordSetup = false"
                    :disabled="loading"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    class="btn btn-success flex-fill"
                    :disabled="loading"
                  >
                    <div v-if="loading" class="d-flex align-items-center justify-content-center">
                      <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Setting up...</span>
                      </div>
                      Creating Password...
                    </div>
                    <span v-else>
                      <i class="bi bi-check-circle me-2"></i>
                      Complete Setup
                    </span>
                  </button>
                </div>
              </form>

              <hr class="my-4">

              <div class="text-center">
                <small class="text-muted">
                  <i class="bi bi-question-circle me-1"></i>
                  Need help? Contact 
                  <a href="mailto:support@retirementadvisorpro.com">support@retirementadvisorpro.com</a>
                </small>
                <br>
                <small class="text-muted mt-2">
                  <a href="/login" class="text-decoration-none">
                    <i class="bi bi-arrow-left me-1"></i>
                    Back to Advisor Login
                  </a>
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// State
const loading = ref(false)
const error = ref('')
const successMessage = ref('')
const showPasswordSetup = ref(false)
const errors = ref({})
const usePassword = ref(false)

// Forms
const loginForm = reactive({
  email: '',
  credential: '' // Can be code or password
})

const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

// Methods
const clearErrors = () => {
  errors.value = {}
  error.value = ''
}

const validatePasswordForm = () => {
  clearErrors()
  let isValid = true

  if (!passwordForm.password || passwordForm.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters long'
    isValid = false
  }

  if (passwordForm.password !== passwordForm.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleLogin = async () => {
  clearErrors()
  loading.value = true

  try {
    const payload = {
      email: loginForm.email
    }
    
    if (usePassword.value) {
      payload.password = loginForm.credential
    } else {
      payload.code = loginForm.credential
    }

    const response = await axios.post('http://localhost:8000/api/affiliates/portal_login/', payload)

    if (response.data.success) {
      // Store session data
      localStorage.setItem('affiliate_portal_token', response.data.session.token)
      localStorage.setItem('affiliate_portal_refresh', response.data.session.refresh)
      localStorage.setItem('affiliate_portal_data', JSON.stringify(response.data.session.affiliate))

      successMessage.value = 'Login successful! Redirecting to your dashboard...'
      
      setTimeout(() => {
        router.push('/affiliate/portal/dashboard')
      }, 1500)
    }
  } catch (err) {
    if (err.response?.status === 401) {
      // Check if this is a first-time access that needs password setup
      if (err.response.data?.needs_password_setup) {
        error.value = '' // Clear any error
        showPasswordSetup.value = true
        successMessage.value = 'Welcome! Please create a password for your account.'
      } else {
        error.value = err.response.data?.error || 'Invalid credentials. Please check your email and code/password.'
      }
    } else {
      error.value = err.response?.data?.error || 'Login failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const handlePasswordSetup = async () => {
  if (!validatePasswordForm()) {
    return
  }

  loading.value = true

  try {
    const response = await axios.post('http://localhost:8000/api/affiliates/setup_password/', {
      email: loginForm.email,
      code: loginForm.credential,
      password: passwordForm.password
    })

    if (response.data.success) {
      // Store session data
      localStorage.setItem('affiliate_portal_token', response.data.session.token)
      localStorage.setItem('affiliate_portal_refresh', response.data.session.refresh)
      localStorage.setItem('affiliate_portal_data', JSON.stringify(response.data.session.affiliate))

      successMessage.value = 'Password created successfully! Redirecting to your dashboard...'
      
      setTimeout(() => {
        router.push('/affiliate/portal/dashboard')
      }, 2000)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Password setup failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// Initialize form from URL parameters if provided
onMounted(() => {
  if (route.query.email) {
    loginForm.email = route.query.email
  }
  if (route.query.code) {
    loginForm.credential = route.query.code
  }
})
</script>

<style scoped>
.affiliate-portal-login {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  min-height: 100vh;
}

.card {
  border-radius: 15px;
}

.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
}

.btn-success {
  background: linear-gradient(45deg, #28a745, #20c997);
  border: none;
}

.btn-success:hover {
  background: linear-gradient(45deg, #218838, #17a2b8);
  transform: translateY(-1px);
}

.alert {
  border-radius: 10px;
}

.text-success {
  color: #28a745 !important;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-check-input:checked {
  background-color: #28a745;
  border-color: #28a745;
}
</style>