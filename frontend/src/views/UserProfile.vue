<template>
  <div class="container content-space-1" style="margin-top: 20px;">
    <!-- Page Header -->
    <div class="page-header mb-4">
      <div class="row align-items-center">
        <div class="col">
          <h1 class="page-header-title">Your Profile Information</h1>
          <p class="page-header-text text-muted">Manage your personal information, authentication settings, and preferences</p>
        </div>
      </div>
    </div>
    
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
              <a class="nav-link active" href="#basicInfoSection" @click.prevent="scrollToSection('basicInfoSection', $event)">
                <i class="bi-person nav-icon"></i> Basic information
              </a>
            </li>
            <li class="nav-item" v-if="form.auth_provider === 'password'">
              <a class="nav-link" href="#passwordSection" @click.prevent="scrollToSection('passwordSection', $event)">
                <i class="bi-key nav-icon"></i> Password
              </a>
            </li>
            <li class="nav-item" v-if="form.auth_provider !== 'password'">
              <a class="nav-link" href="#authMethodSection" @click.prevent="scrollToSection('authMethodSection', $event)">
                <i class="bi-shield-lock nav-icon"></i> Authentication
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#whiteLabelSection" @click.prevent="scrollToSection('whiteLabelSection', $event)">
                <i class="bi-palette nav-icon"></i> White Label Options
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#customDisclosureSection" @click.prevent="scrollToSection('customDisclosureSection', $event)">
                <i class="bi-file-text nav-icon"></i> Custom Disclosure
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="col-lg-9">
        <div class="d-grid gap-3 gap-lg-5">
          <!-- Loading state -->
          <div v-if="loading" class="card">
            <div class="card-body text-center p-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Loading your profile...</p>
            </div>
          </div>

          <!-- Basic Information Card -->
          <div v-if="!loading" id="basicInfoSection" class="card">
            <div class="card-header">
              <h5 class="card-header-title">Basic information</h5>
            </div>
            <div class="card-body">
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
            </div>
          </div>

          <!-- Password Change Card - Only show for password authentication -->
          <div v-if="!loading && form.auth_provider === 'password'" id="passwordSection" class="card">
            <div class="card-header">
              <h5 class="card-header-title">Change Password</h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-sm-6 mb-4">
                  <label for="newPassword" class="form-label">New Password</label>
                  <input type="password" id="newPassword" class="form-control" v-model="passwordForm.newPassword" 
                         placeholder="Enter new password">
                  <small class="text-muted">Password must be at least 8 characters</small>
                </div>
                <div class="col-sm-6 mb-4">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input type="password" id="confirmPassword" class="form-control" v-model="passwordForm.confirmPassword" 
                         placeholder="Confirm new password">
                  <small class="text-muted">Passwords must match</small>
                </div>
              </div>
              <div class="mt-3">
                <button class="btn btn-primary" @click="changePassword" :disabled="changingPassword">
                  <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ changingPassword ? 'Changing...' : 'Change Password' }}
                </button>
                <div v-if="passwordSuccessMessage" class="alert alert-success mt-3">
                  {{ passwordSuccessMessage }}
                </div>
                <div v-if="passwordErrorMessage" class="alert alert-danger mt-3">
                  {{ passwordErrorMessage }}
                </div>
              </div>
            </div>
          </div>

          <!-- Authentication Method Card - Only show for social login -->
          <div v-if="!loading && form.auth_provider !== 'password'" id="authMethodSection" class="card">
            <div class="card-header">
              <h5 class="card-header-title">Authentication Method</h5>
            </div>
            <div class="card-body">
              <div class="alert alert-info mb-0">
                <i class="bi bi-info-circle me-2"></i>
                <span v-if="form.auth_provider === 'google-oauth2'">
                  You are signed in with <strong>Google</strong>. To change your password, please visit your Google account settings.
                </span>
                <span v-else-if="form.auth_provider === 'facebook'">
                  You are signed in with <strong>Facebook</strong>. To change your password, please visit your Facebook account settings.
                </span>
                <span v-else-if="form.auth_provider === 'apple'">
                  You are signed in with <strong>Apple</strong>. To change your password, please visit your Apple ID account settings.
                </span>
                <span v-else-if="form.auth_provider === 'linkedin'">
                  You are signed in with <strong>LinkedIn</strong>. To change your password, please visit your LinkedIn account settings.
                </span>
                <span v-else-if="form.auth_provider === 'microsoft'">
                  You are signed in with <strong>Microsoft</strong>. To change your password, please visit your Microsoft account settings.
                </span>
                <span v-else>
                  You are signed in with a social provider. Password changes must be made through your provider's account settings.
                </span>
              </div>
            </div>
          </div>

          <!-- White Label Settings Card -->
          <div v-if="!loading" id="whiteLabelSection" class="card">
            <div class="card-header">
              <h5 class="card-header-title">White Label Settings</h5>
            </div>
            <div class="card-body">
              <!-- Company Information -->
              <h6 class="mb-3">Company Information</h6>
              <div class="row">
                <div class="col-sm-6 mb-4">
                  <label for="company" class="form-label">Company Name</label>
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
              
              <hr class="my-4">
              
              <!-- Branding -->
              <h6 class="mb-3">Branding</h6>
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
            </div>
          </div>
          
          <!-- Custom Disclosure Card -->
          <div v-if="!loading" id="customDisclosureSection" class="card">
            <div class="card-header">
              <h5 class="card-header-title">Custom Disclosure</h5>
            </div>
            <div class="card-body">
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
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '@/config'
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
  custom_disclosure: '',
  auth_provider: 'password'
})

const logoFile = ref(null)
const loading = ref(true)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Password change form
const passwordForm = ref({
  newPassword: '',
  confirmPassword: ''
})
const changingPassword = ref(false)
const passwordSuccessMessage = ref('')
const passwordErrorMessage = ref('')

// API base URL - change this to match your environment
const apiBaseUrl = API_CONFIG.API_URL

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

// Scroll to section function
const scrollToSection = async (sectionId, event) => {
  // Update active nav link
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active')
  })
  if (event && event.target) {
    event.target.closest('.nav-link').classList.add('active')
  }
  
  // Wait for next tick to ensure DOM is updated
  await nextTick()
  
  // Try to find and scroll to the element
  setTimeout(() => {
    const targetElement = document.getElementById(sectionId)
    console.log('Looking for section:', sectionId, 'Found:', targetElement)
    
    if (targetElement) {
      // Use scrollIntoView for better compatibility
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      
      // Add offset for header after scroll
      setTimeout(() => {
        window.scrollBy({ top: -100, behavior: 'smooth' })
      }, 300)
    } else {
      console.error('Section not found:', sectionId)
    }
  }, 100) // Small delay to ensure everything is rendered
}

// Change password function
const changePassword = async () => {
  changingPassword.value = true
  passwordSuccessMessage.value = ''
  passwordErrorMessage.value = ''
  
  // Validate passwords
  if (!passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    passwordErrorMessage.value = 'Please enter both password fields'
    changingPassword.value = false
    return
  }
  
  if (passwordForm.value.newPassword.length < 8) {
    passwordErrorMessage.value = 'Password must be at least 8 characters long'
    changingPassword.value = false
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordErrorMessage.value = 'Passwords do not match'
    changingPassword.value = false
    return
  }
  
  try {
    const response = await axios.post(
      `${apiBaseUrl}/change-password/`,
      {
        new_password: passwordForm.value.newPassword,
        confirm_password: passwordForm.value.confirmPassword
      },
      getAuthHeaders()
    )
    
    // Clear the form
    passwordForm.value.newPassword = ''
    passwordForm.value.confirmPassword = ''
    
    passwordSuccessMessage.value = 'Password changed successfully!'
    toast.success('Password changed successfully')
  } catch (error) {
    console.error('Error changing password:', error)
    if (error.response?.data?.detail) {
      passwordErrorMessage.value = error.response.data.detail
    } else if (error.response?.data) {
      const errorData = error.response.data
      const formattedErrors = []
      Object.keys(errorData).forEach(field => {
        if (Array.isArray(errorData[field])) {
          formattedErrors.push(`${field}: ${errorData[field].join(', ')}`)
        }
      })
      passwordErrorMessage.value = formattedErrors.length > 0 ? formattedErrors.join('. ') : 'Failed to change password'
    } else {
      passwordErrorMessage.value = error.message || 'Failed to change password'
    }
    toast.error('Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

// Load profile data when component mounts
onMounted(() => {
  fetchUserProfile()
})
</script>

<style scoped>
/* Smooth scroll behavior for the entire page */
html {
  scroll-behavior: smooth;
}

/* Add some padding to sections to account for fixed header */
.card[id] {
  scroll-margin-top: 100px;
}

/* Style for active nav link */
.nav-link.active {
  font-weight: 600;
  border-left: 3px solid #377dff;
}

/* Hover effect for nav links */
.nav-link:hover {
  background-color: rgba(55, 125, 255, 0.05);
}
</style>