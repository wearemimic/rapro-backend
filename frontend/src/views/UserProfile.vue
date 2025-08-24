<template>
  <div class="container content-space-1" style="margin-top: 80px;">
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
                    <input type="text" id="website" class="form-control" v-model="form.website_url" 
                           placeholder="https://example.com (optional)">
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
                    <label for="primaryColor" class="form-label">Header Color</label>
                    <div class="input-group">
                      <input type="color" id="primaryColorPicker" class="form-control form-control-color" 
                             v-model="form.primary_color" title="Choose header color">
                      <input type="text" id="primaryColor" class="form-control" v-model="form.primary_color" 
                             placeholder="#123456" style="flex: 1;">
                      <span class="input-group-text" style="width: 40px; background-color: white;">
                        <div :style="{ backgroundColor: form.primary_color || '#377dff', width: '20px', height: '20px', borderRadius: '3px' }"></div>
                      </span>
                    </div>
                    <small class="text-muted">Choose a color for the header background</small>
                  </div>
                  <div class="col-sm-6 mb-4">
                    <label for="logo" class="form-label">Company Logo</label>
                    <ImageDropzone 
                      v-model:value="logoFile" 
                      :existingImageUrl="form.logo"
                      @fileChanged="onLogoFileChanged"
                    />
                  </div>
                </div>
                
                <h5 class="mt-4 mb-3">Custom Disclosure</h5>
                <div class="row">
                  <div class="col-12 mb-4">
                    <label for="customDisclosure" class="form-label">
                      Custom Disclosure Text
                      <small class="text-muted ms-2">(Optional - will appear above default RetirementAdvisorPro disclosure)</small>
                    </label>
                    <textarea 
                      id="customDisclosure" 
                      class="form-control" 
                      v-model="form.custom_disclosure"
                      rows="5"
                      placeholder="Enter your custom disclosure text here. This will appear on all scenario pages above the default RetirementAdvisorPro disclosure."
                    ></textarea>
                    <small class="text-muted">This disclosure will be displayed on all client scenario reports and pages.</small>
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
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import ImageDropzone from '../components/ImageDropzone.vue'
import { useAuthStore } from '@/stores/auth'

const toast = useToast()
const authStore = useAuthStore()

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
  logo: '',
  custom_disclosure: ''
})

const logoFile = ref(null)
const loading = ref(true)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// API base URL - change this to match your environment
const apiBaseUrl = 'http://localhost:8000/api'

// Helper to get token
const getAuthHeaders = (isMultipart = false) => {
  const token = localStorage.getItem('token')
  const headers = {
    Authorization: `Bearer ${token}`
  }
  
  if (isMultipart) {
    // Don't set Content-Type for multipart/form-data as it will be set automatically with boundary
    return { headers }
  }
  
  headers['Content-Type'] = 'application/json'
  return { headers }
}

// Handle logo file change from the dropzone component
const onLogoFileChanged = async (file) => {
  logoFile.value = file
  if (file === null) {
    await deleteLogo();
  }
}

const deleteLogo = async () => {
  saving.value = true;
  errorMessage.value = '';
  try {
    const formData = new FormData();
    // Set logo to empty to trigger removal in backend
    formData.append('logo', '');
    const response = await axios.put(
      `${apiBaseUrl}/profile/`,
      formData,
      getAuthHeaders(true)
    );
    // Update form with response data
    Object.keys(form.value).forEach(key => {
      if (response.data[key] !== undefined) {
        form.value[key] = response.data[key];
      }
    });
    logoFile.value = null;
    successMessage.value = 'Logo deleted successfully!';
    toast.success('Logo deleted successfully!');
    await authStore.fetchProfile();
  } catch (error) {
    errorMessage.value = 'Failed to delete logo.';
    toast.error('Failed to delete logo.');
  } finally {
    saving.value = false;
  }
};

// Fetch user profile data
const fetchUserProfile = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const response = await axios.get(`${apiBaseUrl}/profile/`, getAuthHeaders())
    
    // Update form with response data, ensuring no null values
    Object.keys(form.value).forEach(key => {
      if (response.data[key] !== undefined) {
        // Convert null values to empty strings to prevent backend "may not be null" errors
        form.value[key] = response.data[key] || ''
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
  
  // Validate website URL only if there's actually a value
  if (form.value.website_url && form.value.website_url.trim() !== '' && !isValidUrl(form.value.website_url)) {
    errorMessage.value = 'Please enter a valid website URL including http:// or https://'
    toast.error('Invalid website URL format')
    saving.value = false
    return
  }
  
  try {
    // Use FormData for file uploads
    const formData = new FormData()
    
    // Add all form fields to FormData
    Object.keys(form.value).forEach(key => {
      // Skip logo since we'll handle it separately
      if (key !== 'logo') {
        let value = form.value[key]
        if (value === null || value === undefined) {
          value = ''
        }
        
        // For website_url, don't send it if it's empty (backend expects null, not empty string)
        if (key === 'website_url' && value.trim() === '') {
          console.log(`Skipping empty ${key}`) // Debug log
          return // Don't send empty website_url
        }
        
        formData.append(key, value)
        console.log(`Sending ${key}:`, value) // Debug log
      }
    })
    
    // Add logo file if a new one was selected
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }
    
    // Send multipart/form-data request
    const response = await axios.put(
      `${apiBaseUrl}/profile/`, 
      formData, 
      getAuthHeaders(true)
    )
    
    // Update form with the response data
    Object.keys(form.value).forEach(key => {
      if (response.data[key] !== undefined) {
        form.value[key] = response.data[key]
      }
    })
    
    // Clear the selected file since it's now uploaded
    logoFile.value = null
    
    successMessage.value = 'Profile updated successfully!'
    toast.success('Profile updated successfully')

    // Refresh the user profile in the store so the header updates
    await authStore.fetchProfile()
  } catch (error) {
    console.error('Error updating profile:', error)
    console.error('Raw error response data:', error.response?.data)
    console.error('Error status:', error.response?.status)
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