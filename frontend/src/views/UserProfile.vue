<template>
  <div class="container content-space-1">
    <div class="row">
      <div class="col-lg-3">
        <div id="navbarVerticalNavMenu" class="js-sticky-block card mb-5 mb-lg-0"
             data-hs-sticky-block-options='{
               "parentSelector": "#navbarVerticalNavMenu",
               "targetSelector": "#header",
               "breakpoint": "lg",
               "startPoint": "#navbarVerticalNavMenu",
               "endPoint": "#stickyBlockEndPoint",
               "stickyOffsetTop": 20
             }'>
          <ul class="js-scrollspy card card-navbar-nav nav nav-tabs nav-sm nav-vertical">
            <li class="nav-item">
              <a class="nav-link active" href="#content">
                <i class="bi-person nav-icon"></i> Basic information
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#emailSection">
                <i class="bi-at nav-icon"></i> Email
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#passwordSection">
                <i class="bi-key nav-icon"></i> Password
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#preferencesSection">
                <i class="bi-gear nav-icon"></i> Preferences
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#socialAccountsSection">
                <i class="bi-instagram nav-icon"></i> White Label Options
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#deleteAccountSection">
                <i class="bi-trash nav-icon"></i> Delete account
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-lg-9">
        <div class="d-grid gap-3 gap-lg-5">
          <div class="card">
            <div class="card-header">
              <h5 class="card-header-title">Basic information</h5>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading your profile...</p>
              </div>
              <div v-else>
                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label for="firstName" class="form-label">First name</label>
                    <input type="text" id="firstName" class="form-control" v-model="form.first_name">
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="lastName" class="form-label">Last name</label>
                    <input type="text" id="lastName" class="form-control" v-model="form.last_name">
                  </div>
                </div>
                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" class="form-control" v-model="form.email" readonly>
                    <small class="text-muted">Email cannot be changed</small>
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="phone" class="form-label">Phone number</label>
                    <input type="text" id="phone" class="form-control" v-model="form.phone_number">
                  </div>
                </div>
                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label for="company" class="form-label">Company name</label>
                    <input type="text" id="company" class="form-control" v-model="form.company_name">
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="website" class="form-label">Website URL</label>
                    <input type="url" id="website" class="form-control" v-model="form.website_url" 
                           placeholder="https://example.com">
                    <small class="text-muted">Must include http:// or https://</small>
                  </div>
                </div>
                <div class="row">
                  <div class="col-sm-12 mb-4">
                    <label for="address" class="form-label">Address</label>
                    <input type="text" id="address" class="form-control" v-model="form.address">
                  </div>
                </div>
                <div class="row">
                  <div class="col-sm-4 mb-4">
                    <label for="city" class="form-label">City</label>
                    <input type="text" id="city" class="form-control" v-model="form.city">
                  </div>
                  <div class="col-sm-4 mb-4">
                    <label for="state" class="form-label">State</label>
                    <input type="text" id="state" class="form-control" v-model="form.state">
                  </div>
                  <div class="col-sm-4 mb-4">
                    <label for="zip" class="form-label">Zip Code</label>
                    <input type="text" id="zip" class="form-control" v-model="form.zip_code">
                  </div>
                </div>

                <h5 class="mt-4 mb-3">White Label Settings</h5>
                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label for="whiteLabelCompanyName" class="form-label">White Label Company</label>
                    <input type="text" id="whiteLabelCompanyName" class="form-control" v-model="form.white_label_company_name">
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="supportEmail" class="form-label">Support Email</label>
                    <input type="email" id="supportEmail" class="form-control" v-model="form.white_label_support_email">
                  </div>
                </div>
                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label for="primaryColor" class="form-label">Primary Color</label>
                    <input type="text" id="primaryColor" class="form-control" v-model="form.primary_color" placeholder="#123456">
                    <small class="text-muted">Enter a hex color code (e.g., #123456)</small>
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="logo" class="form-label">Logo</label>
                    <div v-if="form.logo" class="mb-2">
                      <img :src="form.logo" alt="Company Logo" style="max-width: 150px; max-height: 80px;" />
                    </div>
                    <div class="alert alert-info">
                      Logo upload is not available in this version. Please contact support to update your logo.
                    </div>
                  </div>
                </div>
                <div class="mt-3">
                  <button class="btn btn-primary" @click="updateProfile" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ saving ? 'Saving...' : 'Save changes' }}
                  </button>
                  <div v-if="successMessage" class="alert alert-success mt-3">
                    {{ successMessage }}
                  </div>
                  <div v-if="errorMessage" class="alert alert-danger mt-3">
                    {{ errorMessage }}
                  </div>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

// State variables
const form = ref({
  id: '',
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  company_name: '',
  website_url: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  white_label_company_name: '',
  white_label_support_email: '',
  primary_color: '',
  logo: ''
})

const loading = ref(true)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// API base URL - change this to match your environment
const apiBaseUrl = 'http://localhost:8000/api'

// Helper to get token
const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
}

// Fetch user profile data
const fetchUserProfile = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await axios.get(`${apiBaseUrl}/profile/`, getAuthHeaders())
    
    // Update form with response data
    Object.keys(form.value).forEach(key => {
      if (response.data[key] !== undefined) {
        form.value[key] = response.data[key]
      }
    })
  } catch (error) {
    console.error('Error fetching profile:', error)
    errorMessage.value = error.response?.data?.detail || error.message || 'Failed to load profile'
    toast.error('Failed to load profile')
  } finally {
    loading.value = false
  }
}

// Update user profile
const updateProfile = async () => {
  saving.value = true
  successMessage.value = ''
  errorMessage.value = ''
  
  // Validate website URL
  if (form.value.website_url && !isValidUrl(form.value.website_url)) {
    errorMessage.value = 'Please enter a valid website URL including http:// or https://'
    toast.error('Invalid website URL format')
    saving.value = false
    return
  }
  
  try {
    const response = await axios.put(`${apiBaseUrl}/profile/`, form.value, getAuthHeaders())
    
    // Update form with the response data in case the server modified anything
    Object.keys(form.value).forEach(key => {
      if (response.data[key] !== undefined) {
        form.value[key] = response.data[key]
      }
    })
    
    successMessage.value = 'Profile updated successfully!'
    toast.success('Profile updated successfully')
  } catch (error) {
    console.error('Error updating profile:', error)
    if (error.response?.data) {
      // Format the error messages from Django's validation errors
      const errorData = error.response.data
      const formattedErrors = []
      
      // Handle field-specific errors
      Object.keys(errorData).forEach(field => {
        if (Array.isArray(errorData[field])) {
          formattedErrors.push(`${field}: ${errorData[field].join(', ')}`)
        }
      })
      
      if (formattedErrors.length > 0) {
        errorMessage.value = formattedErrors.join('. ')
      } else {
        errorMessage.value = JSON.stringify(errorData)
      }
    } else {
      errorMessage.value = error.message || 'Failed to update profile'
    }
    toast.error('Failed to update profile')
  } finally {
    saving.value = false
  }
}

// Helper function to validate URLs
const isValidUrl = (url) => {
  try {
    const parsedUrl = new URL(url)
    return ['http:', 'https:'].includes(parsedUrl.protocol)
  } catch (e) {
    return false
  }
}

// Load profile data when component mounts
onMounted(() => {
  fetchUserProfile()
})
</script>