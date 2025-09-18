<template>
  <div class="affiliate-edit">
    <div class="container">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3">Edit Affiliate</h1>
        <button class="btn btn-secondary" @click="cancel">
          <i class="fas fa-times me-2"></i>Cancel
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center p-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Edit Form -->
      <div v-else-if="affiliate" class="card">
        <div class="card-body">
          <form @submit.prevent="saveAffiliate">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="businessName" class="form-label">Business Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="businessName"
                  v-model="affiliate.business_name"
                  required
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="email" class="form-label">Email</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="affiliate.email"
                  required
                >
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="contactName" class="form-label">Contact Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="contactName"
                  v-model="affiliate.contact_name"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="phone" class="form-label">Phone</label>
                <input
                  type="tel"
                  class="form-control"
                  id="phone"
                  v-model="affiliate.phone"
                >
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="website" class="form-label">Website</label>
                <input
                  type="url"
                  class="form-control"
                  id="website"
                  v-model="affiliate.website"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="status" class="form-label">Status</label>
                <select class="form-select" id="status" v-model="affiliate.status">
                  <option value="pending">Pending</option>
                  <option value="active">Active</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="commissionRate" class="form-label">Commission Rate (%)</label>
                <input
                  type="number"
                  class="form-control"
                  id="commissionRate"
                  v-model.number="affiliate.commission_rate"
                  min="0"
                  max="100"
                  step="0.01"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="paymentMethod" class="form-label">Payment Method</label>
                <select class="form-select" id="paymentMethod" v-model="affiliate.payment_method">
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="paypal">PayPal</option>
                  <option value="stripe">Stripe</option>
                  <option value="check">Check</option>
                </select>
              </div>
            </div>

            <div class="mb-3">
              <label for="notes" class="form-label">Notes</label>
              <textarea
                class="form-control"
                id="notes"
                rows="3"
                v-model="affiliate.notes"
              ></textarea>
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button type="button" class="btn btn-secondary" @click="cancel">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving">
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Saving...
                </span>
                <span v-else>Save Changes</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger">
        <i class="fas fa-exclamation-triangle me-2"></i>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAffiliateStore } from '@/stores/affiliateStore'

const route = useRoute()
const router = useRouter()
const affiliateStore = useAffiliateStore()

// Data
const affiliate = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

// Methods
const loadAffiliate = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await affiliateStore.fetchAffiliateDetails(route.params.id)
    affiliate.value = { ...data }
  } catch (err) {
    error.value = 'Failed to load affiliate details'
  } finally {
    loading.value = false
  }
}

const saveAffiliate = async () => {
  try {
    saving.value = true
    await affiliateStore.updateAffiliate(route.params.id, affiliate.value)
    router.push(`/affiliates/${route.params.id}`)
  } catch (err) {
    alert('Failed to save changes: ' + (err.response?.data?.error || err.message))
  } finally {
    saving.value = false
  }
}

const cancel = () => {
  router.push(`/affiliates/${route.params.id}`)
}

// Lifecycle
onMounted(() => {
  loadAffiliate()
})
</script>

<style scoped>
.affiliate-edit {
  padding: 20px;
  margin-top: 60px; /* Add space for fixed header */
}
</style>