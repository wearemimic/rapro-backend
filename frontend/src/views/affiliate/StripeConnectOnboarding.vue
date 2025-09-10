<template>
  <div class="stripe-connect-onboarding">
    <div class="card">
      <div class="card-header">
        <h5 class="card-header-title">Payment Setup</h5>
      </div>
      <div class="card-body">
        <!-- Status Display -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3">Checking account status...</p>
        </div>

        <!-- Not Connected State -->
        <div v-else-if="accountStatus === 'not_created'" class="text-center py-5">
          <i class="bi bi-credit-card-2-back fs-1 text-muted mb-3"></i>
          <h5>Connect Your Payment Account</h5>
          <p class="text-muted mb-4">
            Set up your Stripe account to receive commission payouts automatically.
          </p>
          <button 
            @click="startOnboarding" 
            class="btn btn-primary btn-lg"
            :disabled="onboardingLoading"
          >
            <span v-if="onboardingLoading">
              <span class="spinner-border spinner-border-sm me-2"></span>
              Setting up...
            </span>
            <span v-else>
              <i class="bi bi-stripe me-2"></i>
              Connect with Stripe
            </span>
          </button>
        </div>

        <!-- Pending Verification State -->
        <div v-else-if="accountStatus === 'pending'" class="text-center py-5">
          <i class="bi bi-clock-history fs-1 text-warning mb-3"></i>
          <h5>Account Setup In Progress</h5>
          <p class="text-muted mb-4">
            Your Stripe account setup is incomplete. Please complete the verification process.
          </p>
          
          <div v-if="requirements.currently_due.length > 0" class="alert alert-warning text-start">
            <h6>Action Required:</h6>
            <ul class="mb-0">
              <li v-for="req in requirements.currently_due" :key="req">
                {{ formatRequirement(req) }}
              </li>
            </ul>
          </div>

          <button 
            @click="continueOnboarding" 
            class="btn btn-warning"
            :disabled="onboardingLoading"
          >
            <span v-if="onboardingLoading">
              <span class="spinner-border spinner-border-sm me-2"></span>
              Loading...
            </span>
            <span v-else>
              Continue Setup
            </span>
          </button>
        </div>

        <!-- Active State -->
        <div v-else-if="accountStatus === 'active'" class="text-center py-5">
          <i class="bi bi-check-circle-fill fs-1 text-success mb-3"></i>
          <h5>Payment Account Active</h5>
          <p class="text-muted mb-4">
            Your Stripe account is connected and ready to receive payouts.
          </p>

          <!-- Payout Dashboard -->
          <div class="row mt-4">
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="text-muted">Total Paid</h6>
                  <h3 class="text-success">${{ payoutData.total_paid }}</h3>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="text-muted">Pending</h6>
                  <h3 class="text-warning">${{ payoutData.pending_amount }}</h3>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body text-center">
                  <h6 class="text-muted">Next Payout</h6>
                  <h3 class="text-primary">{{ nextPayoutDate }}</h3>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Payouts -->
          <div v-if="payoutData.recent_payouts.length > 0" class="mt-4">
            <h6>Recent Payouts</h6>
            <div class="table-responsive">
              <table class="table table-sm">
                <thead>
                  <tr>
                    <th>Period</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="payout in payoutData.recent_payouts" :key="payout.id">
                    <td>{{ payout.period }}</td>
                    <td>${{ payout.amount }}</td>
                    <td>
                      <span :class="getStatusBadgeClass(payout.status)">
                        {{ payout.status }}
                      </span>
                    </td>
                    <td>{{ formatDate(payout.date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="mt-4">
            <button 
              @click="updateAccountInfo" 
              class="btn btn-outline-primary me-2"
            >
              Update Account Info
            </button>
            <a 
              href="https://dashboard.stripe.com/express/dashboard" 
              target="_blank"
              class="btn btn-outline-secondary"
            >
              View Stripe Dashboard
              <i class="bi bi-box-arrow-up-right ms-1"></i>
            </a>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from 'vue-toastification';
import { API_CONFIG } from '@/config';

const route = useRoute();
const toast = useToast();

// State
const loading = ref(true);
const onboardingLoading = ref(false);
const accountStatus = ref('not_created');
const requirements = ref({
  currently_due: [],
  eventually_due: [],
  past_due: []
});
const payoutData = ref({
  total_paid: '0.00',
  pending_amount: '0.00',
  recent_payouts: []
});
const error = ref('');

// Computed
const nextPayoutDate = computed(() => {
  // Calculate first of next month
  const now = new Date();
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return nextMonth.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
});

// Methods
const checkAccountStatus = async () => {
  try {
    loading.value = true;
    error.value = '';
    
    const response = await fetch(`${API_CONFIG.API_URL}/stripe-connect/account-status/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      accountStatus.value = data.status;
      if (data.requirements) {
        requirements.value = data.requirements;
      }
      
      // If account is active, fetch payout dashboard data
      if (data.status === 'active') {
        await fetchPayoutDashboard();
      }
    } else {
      error.value = data.error || 'Failed to check account status';
    }
  } catch (err) {
    error.value = 'Failed to connect to server';
    console.error('Account status error:', err);
  } finally {
    loading.value = false;
  }
};

const fetchPayoutDashboard = async () => {
  try {
    const response = await fetch(`${API_CONFIG.API_URL}/stripe-connect/payout-dashboard/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    const data = await response.json();
    
    if (response.ok) {
      payoutData.value = data;
    }
  } catch (err) {
    console.error('Failed to fetch payout dashboard:', err);
  }
};

const startOnboarding = async () => {
  try {
    onboardingLoading.value = true;
    
    const response = await fetch(`${API_CONFIG.API_URL}/stripe-connect/account-link/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    if (response.ok && data.url) {
      // Redirect to Stripe onboarding
      window.location.href = data.url;
    } else {
      error.value = data.error || 'Failed to start onboarding';
      onboardingLoading.value = false;
    }
  } catch (err) {
    error.value = 'Failed to connect to server';
    onboardingLoading.value = false;
  }
};

const continueOnboarding = async () => {
  // Same as startOnboarding but for continuing incomplete setup
  await startOnboarding();
};

const updateAccountInfo = async () => {
  // Create new account link for updating info
  await startOnboarding();
};

const formatRequirement = (req) => {
  // Convert Stripe requirement codes to human-readable text
  const requirementMap = {
    'individual.verification.document': 'Identity verification document',
    'individual.address.line1': 'Address information',
    'individual.dob.day': 'Date of birth',
    'individual.ssn_last_4': 'Last 4 digits of SSN',
    'tos_acceptance.date': 'Terms of service acceptance',
    'external_account': 'Bank account information'
  };
  
  return requirementMap[req] || req.replace(/_/g, ' ').replace(/\./g, ' - ');
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

const getStatusBadgeClass = (status) => {
  const classes = {
    'completed': 'badge bg-success',
    'pending': 'badge bg-warning',
    'processing': 'badge bg-info',
    'failed': 'badge bg-danger'
  };
  return classes[status] || 'badge bg-secondary';
};

// Lifecycle
onMounted(() => {
  // Check if returning from Stripe onboarding
  if (route.query.success === 'true') {
    toast.success('Stripe account setup completed!');
  } else if (route.query.refresh === 'true') {
    toast.info('Please complete your account setup');
  }
  
  checkAccountStatus();
});
</script>

<style scoped>
.stripe-connect-onboarding {
  max-width: 800px;
  margin: 0 auto;
}

.badge {
  font-size: 0.75rem;
}
</style>