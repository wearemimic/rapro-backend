<template>
  <div class="client-portal-login">
    <div class="container-fluid vh-100">
      <div class="row h-100 align-items-center justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow-lg border-0">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <h2 class="text-primary mb-2">
                  <i class="bi bi-shield-lock me-2"></i>
                  Client Portal
                </h2>
                <p class="text-muted">Access your retirement planning information</p>
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
                  >
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="token" class="form-label">Access Token</label>
                  <input
                    type="text"
                    id="token"
                    v-model="loginForm.token"
                    class="form-control"
                    :class="{ 'is-invalid': errors.token }"
                    required
                    :disabled="loading"
                    placeholder="Enter the token from your invitation email"
                  >
                  <div v-if="errors.token" class="invalid-feedback">
                    {{ errors.token }}
                  </div>
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  :disabled="loading"
                >
                  <div v-if="loading" class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                      <span class="visually-hidden">Logging in...</span>
                    </div>
                    Verifying Access...
                  </div>
                  <span v-else>
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Access Portal
                  </span>
                </button>
              </form>

              <!-- Password Setup Form -->
              <form v-else @submit.prevent="handlePasswordSetup">
                <div class="alert alert-info mb-4">
                  <i class="bi bi-info-circle me-2"></i>
                  <strong>Welcome!</strong> Please set up your secure password to complete portal access.
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
                    class="btn btn-primary flex-fill"
                    :disabled="loading"
                  >
                    <div v-if="loading" class="d-flex align-items-center justify-content-center">
                      <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Setting up...</span>
                      </div>
                      Setting up...
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
                  Need help? Contact your financial advisor directly.
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

// Forms
const loginForm = reactive({
  email: '',
  token: ''
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
    const response = await axios.post('http://localhost:8000/api/client-portal/auth/login/', {
      email: loginForm.email,
      token: loginForm.token
    })

    if (response.data.success) {
      // Store session data
      localStorage.setItem('client_portal_token', response.data.session.token)
      localStorage.setItem('client_portal_user', JSON.stringify(response.data.session.user))
      localStorage.setItem('client_portal_client', JSON.stringify(response.data.client))

      successMessage.value = 'Login successful! Redirecting to your dashboard...'
      
      setTimeout(() => {
        router.push('/portal/dashboard')
      }, 1500)
    }
  } catch (err) {
    if (err.response?.status === 401) {
      // Check if this is a first-time access that needs password setup
      if (err.response.data.error?.includes('password setup')) {
        showPasswordSetup.value = true
      } else {
        error.value = 'Invalid credentials or expired invitation. Please check your email and token.'
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
    const response = await axios.post('http://localhost:8000/api/client-portal/auth/setup-password/', {
      email: loginForm.email,
      token: loginForm.token,
      password: passwordForm.password
    })

    if (response.data.success) {
      // Store session data
      localStorage.setItem('client_portal_token', response.data.session.token)
      localStorage.setItem('client_portal_user', JSON.stringify(response.data.session.user))

      successMessage.value = 'Portal access activated successfully! Redirecting to your dashboard...'
      
      setTimeout(() => {
        router.push('/portal/dashboard')
      }, 2000)
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Password setup failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// Initialize form from URL parameters
onMounted(() => {
  if (route.query.email) {
    loginForm.email = route.query.email
  }
  if (route.query.token) {
    loginForm.token = route.query.token
  }
})
</script>

<style scoped>
.client-portal-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border-radius: 15px;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.btn-primary {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(45deg, #5a67d8, #6b46a0);
  transform: translateY(-1px);
}

.alert {
  border-radius: 10px;
}

.text-primary {
  color: #667eea !important;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>