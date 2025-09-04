<template>
  <div class="billing-page">
    <!-- Debug Information (temporary) -->
    <div class="alert alert-info mb-3">
      <h6>🔍 Debug Info:</h6>
      <p><strong>Loading:</strong> {{ loading }}</p>
      <p><strong>Subscription:</strong> {{ subscription ? 'Found' : 'None' }}</p>
      <p><strong>Invoices:</strong> {{ invoices.length }}</p>
      <p><strong>Payment Method:</strong> {{ paymentMethod ? 'Found' : 'None' }}</p>
      <details>
        <summary>Raw Data</summary>
        <pre>{{ JSON.stringify({ subscription, invoices, paymentMethod }, null, 2) }}</pre>
      </details>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div class="row align-items-center">
        <div class="col">
          <h1 class="page-header-title">
            <i class="bi-credit-card me-2"></i>
            Billing & Subscription
          </h1>
          <p class="page-header-text">Manage your subscription and billing information</p>
        </div>
        <div class="col-auto">
          <button @click="refreshBilling" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Cancellation Notice -->
    <div v-if="subscription?.effective_status === 'canceled_pending'" class="alert alert-warning mb-4 cancellation-notice">
      <div class="d-flex align-items-center">
        <i class="bi-exclamation-triangle-fill me-3" style="font-size: 1.5rem;"></i>
        <div>
          <h5 class="alert-heading mb-1">Subscription Canceled</h5>
          <p class="mb-0">
            Your subscription has been canceled and will end on <strong>{{ formatDate(subscription.current_period_end) }}</strong>. 
            You will continue to have full access until that date.
          </p>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Current Subscription -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
              <i class="bi-bookmark-check me-2"></i>
              Current Subscription
            </h5>
            <span class="badge" :class="{
              'bg-success': subscription?.status === 'active' && subscription?.effective_status !== 'canceled_pending',
              'bg-warning': subscription?.status === 'trialing' || subscription?.effective_status === 'canceled_pending',
              'bg-danger': subscription?.status === 'canceled' || subscription?.status === 'past_due',
              'bg-secondary': !subscription?.status
            }">
              {{ 
                subscription?.effective_status === 'canceled_pending' 
                  ? 'CANCELED (ACTIVE UNTIL END)' 
                  : (subscription?.status?.toUpperCase() || 'NO SUBSCRIPTION') 
              }}
            </span>
          </div>
          <div class="card-body">
            <div v-if="subscription" class="row">
              <div class="col-md-6">
                <h6 class="fw-bold">Plan Details</h6>
                <p class="mb-1"><strong>Plan:</strong> {{ subscription.plan_name || 'N/A' }}</p>
                <p class="mb-1"><strong>Price:</strong> ${{ subscription.amount || '0' }} / {{ subscription.interval || 'month' }}</p>
                <p class="mb-3"><strong>Next billing:</strong> {{ formatDate(subscription.current_period_end) }}</p>
                
                <h6 class="fw-bold">Billing Information</h6>
                <p class="mb-1"><strong>Customer ID:</strong> {{ subscription.stripe_customer_id }}</p>
                <p class="mb-1"><strong>Subscription ID:</strong> {{ subscription.stripe_subscription_id }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold">Payment Method</h6>
                <div v-if="paymentMethod" class="d-flex align-items-center mb-3">
                  <i class="bi-credit-card-fill me-2"></i>
                  <div>
                    <div>**** **** **** {{ paymentMethod.last4 }}</div>
                    <small class="text-muted">{{ paymentMethod.brand?.toUpperCase() }} expires {{ paymentMethod.exp_month }}/{{ paymentMethod.exp_year }}</small>
                  </div>
                </div>
                <div v-else class="text-muted">
                  <i class="bi-exclamation-triangle me-2"></i>
                  No payment method on file
                </div>
              </div>
            </div>
            <div v-else class="text-center py-5">
              <i class="bi-credit-card display-1 text-muted"></i>
              <h5 class="mt-3">No Active Subscription</h5>
              <p class="text-muted">You don't have an active subscription yet.</p>
            </div>
          </div>
        </div>

        <!-- Billing History -->
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi-receipt me-2"></i>
              Billing History
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="invoices.length > 0">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="invoice in invoices" :key="invoice.id">
                      <td>{{ formatDate(invoice.created) }}</td>
                      <td>{{ invoice.description || 'Monthly Subscription' }}</td>
                      <td>${{ (invoice.amount_paid / 100).toFixed(2) }}</td>
                      <td>
                        <span class="badge" :class="{
                          'bg-success': invoice.status === 'paid',
                          'bg-warning': invoice.status === 'open',
                          'bg-danger': invoice.status === 'overdue'
                        }">
                          {{ invoice.status?.toUpperCase() }}
                        </span>
                      </td>
                      <td>
                        <a v-if="invoice.invoice_pdf" :href="invoice.invoice_pdf" target="_blank" class="btn btn-sm btn-outline-primary">
                          <i class="bi-download me-1"></i>
                          PDF
                        </a>
                        <span v-else class="text-muted">N/A</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="bi-receipt display-1 text-muted"></i>
              <h6 class="mt-3">No billing history</h6>
              <p class="text-muted">Your invoices will appear here once billing begins.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions Sidebar -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="bi-gear me-2"></i>
              Subscription Actions
            </h5>
          </div>
          <div class="card-body">
            <div v-if="subscription?.status === 'active' && subscription?.effective_status !== 'canceled_pending'" class="d-grid gap-2">
              <button class="btn btn-outline-primary" @click="updatePaymentMethod">
                <i class="bi-credit-card me-2"></i>
                Update Payment Method
              </button>
              <button class="btn btn-outline-warning" @click="confirmCancelSubscription">
                <i class="bi-x-circle me-2"></i>
                Cancel Subscription
              </button>
            </div>
            <div v-else-if="subscription?.effective_status === 'canceled_pending'" class="d-grid">
              <button class="btn btn-success" @click="reactivateSubscription">
                <i class="bi-arrow-clockwise me-2"></i>
                Reactivate Subscription
              </button>
              <small class="text-muted mt-2">
                Your subscription is set to end on {{ formatDate(subscription.current_period_end) }}. 
                Click above to continue your subscription.
              </small>
            </div>
            <div v-else-if="subscription?.status === 'canceled'" class="d-grid">
              <button class="btn btn-primary" @click="reactivateSubscription">
                <i class="bi-arrow-clockwise me-2"></i>
                Reactivate Subscription
              </button>
              <small class="text-muted mt-2">
                Your subscription has ended.
              </small>
            </div>
            <div v-else class="text-center">
              <p class="text-muted">No active subscription to manage.</p>
            </div>
          </div>
        </div>

        <!-- Support Contact -->
        <div class="card mt-4">
          <div class="card-body text-center">
            <i class="bi-question-circle display-4 text-primary"></i>
            <h6 class="mt-3">Need Help?</h6>
            <p class="text-muted small">Contact our billing support team for assistance with your subscription.</p>
            <button class="btn btn-sm btn-outline-primary">
              <i class="bi-envelope me-1"></i>
              Contact Support
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Cancel Subscription Modal -->
    <div v-if="showCancelModal" class="modal-overlay" @click="showCancelModal = false">
      <div class="modal-dialog" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Cancel Subscription</h5>
            <button type="button" class="btn-close" @click="showCancelModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning">
              <i class="bi-exclamation-triangle me-2"></i>
              <strong>Are you sure you want to cancel your subscription?</strong>
            </div>
            <p>If you cancel your subscription:</p>
            <ul>
              <li>You'll continue to have access until {{ formatDate(subscription?.current_period_end) }}</li>
              <li>Your account will be downgraded at the end of the billing period</li>
              <li>You can reactivate your subscription at any time before it expires</li>
            </ul>
            <div class="form-group">
              <label for="cancelReason" class="form-label">Reason for canceling (optional):</label>
              <select v-model="cancelReason" class="form-select">
                <option value="">Select a reason</option>
                <option value="too_expensive">Too expensive</option>
                <option value="not_using">Not using enough</option>
                <option value="missing_features">Missing features</option>
                <option value="technical_issues">Technical issues</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="form-group mt-3">
              <label for="cancelFeedback" class="form-label">Additional feedback (optional):</label>
              <textarea v-model="cancelFeedback" class="form-control" rows="3" placeholder="Help us improve..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCancelModal = false">Keep Subscription</button>
            <button type="button" class="btn btn-danger" @click="cancelSubscription" :disabled="cancelling">
              <span v-if="cancelling" class="spinner-border spinner-border-sm me-2"></span>
              Cancel Subscription
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { API_CONFIG } from '@/config'

const authStore = useAuthStore()
const router = useRouter()

// Reactive data
const loading = ref(false)
const subscription = ref(null)
const invoices = ref([])
const paymentMethod = ref(null)
const cancelling = ref(false)
const cancelReason = ref('')
const cancelFeedback = ref('')
const showCancelModal = ref(false)

// Format date helper
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric'
  })
}

// Fetch billing data
const fetchBillingData = async () => {
  console.log('🔄 Starting to fetch billing data...')
  loading.value = true
  try {
    console.log('📡 Making API call to /api/billing/subscription/')
    const response = await axios.get('${API_CONFIG.API_URL}/billing/subscription/')
    console.log('✅ API response received:', response.status, response.data)
    const data = response.data
    
    subscription.value = data.subscription
    invoices.value = data.invoices || []
    paymentMethod.value = data.payment_method
    
    console.log('💾 Data stored:', {
      subscription: subscription.value,
      invoicesCount: invoices.value.length,
      paymentMethod: paymentMethod.value
    })
  } catch (error) {
    console.error('❌ Failed to fetch billing data:', error)
    console.error('❌ Error details:', error.response?.data, error.response?.status)
    // Handle error - maybe show a toast notification
  } finally {
    loading.value = false
    console.log('🏁 Billing data fetch complete')
  }
}

// Refresh billing data
const refreshBilling = () => {
  fetchBillingData()
}

// Update payment method
const updatePaymentMethod = () => {
  // TODO: Implement Stripe payment method update
  console.log('Update payment method')
}

// Confirm cancel subscription
const confirmCancelSubscription = () => {
  showCancelModal.value = true
}

// Cancel subscription
const cancelSubscription = async () => {
  cancelling.value = true
  try {
    await axios.post('${API_CONFIG.API_URL}/billing/cancel-subscription/', {
      reason: cancelReason.value,
      feedback: cancelFeedback.value
    })
    
    // Refresh data and close modal
    await fetchBillingData()
    showCancelModal.value = false
    
    // Show success message
    alert('Your subscription has been canceled successfully.')
  } catch (error) {
    console.error('Failed to cancel subscription:', error)
    alert('Failed to cancel subscription. Please try again.')
  } finally {
    cancelling.value = false
  }
}

// Reactivate subscription
const reactivateSubscription = async () => {
  try {
    await axios.post('${API_CONFIG.API_URL}/billing/reactivate-subscription/')
    await fetchBillingData()
    alert('Your subscription has been reactivated successfully.')
  } catch (error) {
    console.error('Failed to reactivate subscription:', error)
    alert('Failed to reactivate subscription. Please try again.')
  }
}

// Load data on component mount
onMounted(() => {
  fetchBillingData()
})
</script>

<style scoped>
.billing-page {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.page-header-title {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.page-header-text {
  color: #6c757d;
  margin-bottom: 0;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid #dee2e6;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.badge {
  font-size: 0.75rem;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.btn-outline-primary {
  border-color: #dee2e6;
}

.btn-outline-primary:hover {
  background-color: #377dff;
  border-color: #377dff;
}

.modal-content {
  border-radius: 0.5rem;
}

.alert {
  border-radius: 0.375rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-dialog {
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #000;
  opacity: 0.5;
}

.btn-close:hover {
  opacity: 1;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.cancellation-notice {
  position: relative;
  z-index: 1000;
}
</style>