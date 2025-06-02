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
                  <label for="phone" class="form-label">Phone number</label>
                  <input type="text" id="phone" class="form-control" v-model="form.phone_number">
                </div>
                <div class="col-sm-6 mb-4">
                  <label for="company" class="form-label">Company name</label>
                  <input type="text" id="company" class="form-control" v-model="form.company_name">
                </div>
              </div>
              <div class="row">
                <div class="col-sm-6 mb-4">
                  <label for="website" class="form-label">Website URL</label>
                  <input type="url" id="website" class="form-control" v-model="form.website_url">
                </div>
                <div class="col-sm-6 mb-4">
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
                  <input type="text" id="primaryColor" class="form-control" v-model="form.primary_color">
                </div>
                <div class="col-sm-6 mb-4">
                  <label for="logo" class="form-label">Logo</label>
                  <input type="file" id="logo" class="form-control" @change="handleLogoUpload">
                </div>
              </div>
              <button class="btn btn-primary" @click="updateProfile">Save changes</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
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
        logo: null
      }
    }
  },
  methods: {
    handleLogoUpload(event) {
      this.form.logo = event.target.files[0];
    },
    updateProfile() {
      // implement API call here
    }
  }
}
</script>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'

const toast = useToast()

const formData = ref({
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
  logo: null,
})

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }


onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:8000/api/profile/', { headers })
    Object.assign(formData.value, res.data)
  } catch (err) {
    toast.error('Failed to load profile')
  }
})

const handleSubmit = async () => {
  try {
    const res = await axios.put('http://localhost:8000/api/profile/update/', formData.value, { headers })
    toast.success('Profile updated successfully')
  } catch (err) {
    toast.error('Update failed')
  }
}
</script>