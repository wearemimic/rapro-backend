<template>
  <main id="content" role="main" class="main">
    <div class="container py-5 py-sm-7">
      <div class="mx-auto" style="max-width: 45rem;">
        <!-- Card -->
        <div class="text-center mb-4">
          <img src="/assets/img/logo.png" style="height:50px;margin-bottom:20px;" alt="Logo">
        </div>
        <div class="card card-lg mb-5">
          <div class="card-body">
            <!-- Steps -->
            <div class="steps steps-sm mb-5">
              <div class="step-item" :class="{ 'active': currentStep >= 1 }">
                <div class="step-content-wrapper">
                  <span class="step-icon step-icon-soft-primary">1</span>
                  <div class="step-content">
                    <span class="step-title">Account Details</span>
                  </div>
                </div>
              </div>

              <div class="step-item" :class="{ 'active': currentStep >= 2 }">
                <div class="step-content-wrapper">
                  <span class="step-icon step-icon-soft-primary">2</span>
                  <div class="step-content">
                    <span class="step-title">Professional Info</span>
                  </div>
                </div>
              </div>

              <div class="step-item" :class="{ 'active': currentStep >= 3 }">
                <div class="step-content-wrapper">
                  <span class="step-icon step-icon-soft-primary">3</span>
                  <div class="step-content">
                    <span class="step-title">Payment</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- End Steps -->

            <!-- Form -->
            <form @submit.prevent="handleSubmit">
              <!-- Step 1: Account Details -->
              <div v-if="currentStep === 1">
                <div class="text-center mb-5">
                  <h1 class="display-5">Create your account</h1>
                  <p>Already have an account? <router-link to="/login">Sign in here</router-link></p>
                </div>

                <div class="mb-4">
                  <label class="form-label" for="email">Email</label>
                  <input 
                    type="email" 
                    class="form-control form-control-lg" 
                    id="email"
                    v-model="form.email" 
                    required
                    :disabled="isLoading"
                  >
                </div>

                <div class="mb-4">
                  <label class="form-label" for="password">Password</label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg" 
                    id="password"
                    v-model="form.password" 
                    required
                    :disabled="isLoading"
                  >
                  <div class="form-text">
                    Must be at least 8 characters long and include numbers and special characters
                  </div>
                </div>

                <div class="mb-4">
                  <label class="form-label" for="confirmPassword">Confirm Password</label>
                  <input 
                    type="password" 
                    class="form-control form-control-lg" 
                    id="confirmPassword"
                    v-model="form.confirmPassword" 
                    required
                    :disabled="isLoading"
                  >
                </div>
              </div>

              <!-- Step 2: Professional Info -->
              <div v-if="currentStep === 2">
                <div class="text-center mb-5">
                  <h1 class="display-5">Professional Information</h1>
                  <p>Tell us about your practice</p>
                </div>

                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label class="form-label" for="firstName">First Name</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="firstName"
                      v-model="form.firstName" 
                      required
                      :disabled="isLoading"
                    >
                  </div>

                  <div class="col-sm-6 mb-4">
                    <label class="form-label" for="lastName">Last Name</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="lastName"
                      v-model="form.lastName" 
                      required
                      :disabled="isLoading"
                    >
                  </div>
                </div>

                <div class="mb-4">
                  <label class="form-label" for="companyName">Company Name</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    id="companyName"
                    v-model="form.companyName"
                    :disabled="isLoading"
                  >
                </div>

                <div class="mb-4">
                  <label class="form-label" for="phone">Phone Number</label>
                  <input 
                    type="tel" 
                    class="form-control form-control-lg" 
                    id="phone"
                    v-model="form.phone" 
                    required
                    :disabled="isLoading"
                  >
                </div>

                <div class="mb-4">
                  <label class="form-label" for="licenses">Professional Licenses/Certifications</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    id="licenses"
                    v-model="form.licenses" 
                    placeholder="e.g., CFP, CFA, etc."
                    :disabled="isLoading"
                  >
                </div>

                <div class="mb-4">
                  <label class="form-label" for="website">Website URL</label>
                  <input 
                    type="url" 
                    class="form-control form-control-lg" 
                    id="website"
                    v-model="form.website"
                    :disabled="isLoading"
                  >
                </div>

                <div class="mb-4">
                  <label class="form-label" for="address">Address</label>
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    id="address"
                    v-model="form.address"
                    :disabled="isLoading"
                  >
                </div>

                <div class="row">
                  <div class="col-sm-6 mb-4">
                    <label class="form-label" for="city">City</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="city"
                      v-model="form.city"
                      :disabled="isLoading"
                    >
                  </div>

                  <div class="col-sm-3 mb-4">
                    <label class="form-label" for="state">State</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="state"
                      v-model="form.state"
                      :disabled="isLoading"
                    >
                  </div>

                  <div class="col-sm-3 mb-4">
                    <label class="form-label" for="zipCode">ZIP Code</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="zipCode"
                      v-model="form.zipCode"
                      :disabled="isLoading"
                    >
                  </div>
                </div>
              </div>

              <!-- Step 3: Payment -->
              <div v-if="currentStep === 3">
                <div class="text-center mb-5">
                  <h1 class="display-5">Subscription Details</h1>
                  <p>Choose your plan and complete payment</p>
                </div>

                <!-- Subscription Plans -->
                <div class="mb-4">
                  <div class="form-check custom-option custom-option-basic mb-3">
                    <input 
                      type="radio" 
                      class="form-check-input" 
                      v-model="form.plan" 
                      value="monthly" 
                      id="monthlyPlan"
                      :disabled="isLoading"
                    >
                    <label class="form-check-label" for="monthlyPlan">
                      <span class="d-flex align-items-center">
                        <span class="flex-shrink-0">
                          <span class="display-6">$99</span>
                          <span>/month</span>
                        </span>
                        <span class="flex-grow-1 ms-3">
                          <span class="d-block">Monthly Plan</span>
                          <span class="d-block text-muted">Perfect for getting started</span>
                        </span>
                      </span>
                    </label>
                  </div>

                  <div class="form-check custom-option custom-option-basic">
                    <input 
                      type="radio" 
                      class="form-check-input" 
                      v-model="form.plan" 
                      value="annual" 
                      id="annualPlan"
                      :disabled="isLoading"
                    >
                    <label class="form-check-label" for="annualPlan">
                      <span class="d-flex align-items-center">
                        <span class="flex-shrink-0">
                          <span class="display-6">$999</span>
                          <span>/year</span>
                        </span>
                        <span class="flex-grow-1 ms-3">
                          <span class="d-block">Annual Plan</span>
                          <span class="d-block text-muted">Save 16% with annual billing</span>
                        </span>
                      </span>
                    </label>
                  </div>
                </div>

                <!-- Stripe Card Element -->
                <div class="mb-4">
                  <label class="form-label">Card Details</label>
                  <div id="card-element" class="form-control form-control-lg"></div>
                  <div id="card-errors" class="invalid-feedback" style="display: none;"></div>
                </div>
              </div>

              <!-- Navigation Buttons -->
              <div class="d-flex justify-content-between">
                <button 
                  type="button" 
                  class="btn btn-outline-primary btn-lg" 
                  @click="prevStep" 
                  v-if="currentStep > 1"
                  :disabled="isLoading"
                >
                  Back
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary btn-lg ms-auto" 
                  :disabled="isLoading"
                >
                  {{ 
                    isLoading ? 'Processing...' : 
                    currentStep === 3 ? 'Complete Registration' : 'Next'
                  }}
                </button>
              </div>
            </form>
            <!-- End Form -->
          </div>
        </div>
        <!-- End Card -->
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useRegistrationStore } from '@/stores/registration';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const registrationStore = useRegistrationStore();
const authStore = useAuthStore();
const isLoading = ref(false);

const currentStep = computed(() => registrationStore.currentStep);

const form = reactive({
  // Step 1: Account Details
  email: '',
  password: '',
  confirmPassword: '',

  // Step 2: Professional Info
  firstName: '',
  lastName: '',
  companyName: '',
  phone: '',
  licenses: '',
  website: '',
  address: '',
  city: '',
  state: '',
  zipCode: '',

  // Step 3: Payment
  plan: 'monthly'
});

const validateStep1 = () => {
  if (!form.email || !form.password || !form.confirmPassword) {
    alert('Please fill in all required fields');
    return false;
  }
  if (form.password !== form.confirmPassword) {
    alert('Passwords do not match');
    return false;
  }
  if (form.password.length < 8) {
    alert('Password must be at least 8 characters long');
    return false;
  }
  return true;
};

const validateStep2 = () => {
  if (!form.firstName || !form.lastName || !form.phone) {
    alert('Please fill in all required fields');
    return false;
  }
  return true;
};

const nextStep = async () => {
  if (currentStep.value === 1) {
    if (validateStep1()) {
      try {
        await registrationStore.registerStep1({
          email: form.email,
          password: form.password
        });
      } catch (error) {
        alert(error.message || 'Error in step 1');
        return;
      }
    }
  } else if (currentStep.value === 2) {
    if (validateStep2()) {
      try {
        await registrationStore.registerStep2({
          firstName: form.firstName,
          lastName: form.lastName,
          companyName: form.companyName,
          phoneNumber: form.phone,
          licenses: form.licenses,
          website: form.website,
          address: form.address,
          city: form.city,
          state: form.state,
          zipCode: form.zipCode
        });
      } catch (error) {
        alert(error.message || 'Error in step 2');
        return;
      }
    }
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    registrationStore.currentStep--;
  }
};

let stripe = null;
let card = null;

onMounted(async () => {
  // Only initialize Stripe on step 3
  if (currentStep.value === 3 && window.Stripe) {
    stripe = window.Stripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();
    card = elements.create('card', {
      style: {
        base: {
          fontSize: '16px',
          color: '#32325d',
          '::placeholder': {
            color: '#aab7c4'
          }
        },
        invalid: {
          color: '#fa755a',
          iconColor: '#fa755a'
        }
      }
    });
    card.mount('#card-element');

    card.addEventListener('change', function(event) {
      const displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
        displayError.style.display = 'block';
      } else {
        displayError.textContent = '';
        displayError.style.display = 'none';
      }
    });
  }
});

const handleSubmit = async () => {
  if (currentStep.value !== 3) {
    return nextStep();
  }

  isLoading.value = true;
  try {
    const { paymentMethod, error } = await stripe.createPaymentMethod({
      type: 'card',
      card: card
    });

    if (error) {
      throw error;
    }

    // Complete subscription with payment
    const response = await fetch('http://localhost:8000/api/complete-registration', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        paymentMethodId: paymentMethod.id,
        plan: form.plan
      })
    });

    const data = await response.json();
    
    if (data.success) {
      router.push('/dashboard');
    } else {
      throw new Error(data.message || 'Subscription failed');
    }
  } catch (error) {
    console.error('Payment error:', error);
    alert(error.message || 'An error occurred during payment processing');
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.main {
  background-color: #f9fafb;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}

.steps::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: #e7eaf3;
  transform: translateY(-50%);
  z-index: 0;
}

.step-item {
  flex: 1;
  text-align: center;
  position: relative;
  z-index: 1;
}

.step-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: white;
  border: 2px solid #e7eaf3;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.step-item.active .step-icon {
  background: #377dff;
  border-color: #377dff;
  color: white;
}

.step-title {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  display: block;
}

.custom-option {
  padding: 1rem;
  border: 1px solid #e7eaf3;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.custom-option:hover {
  border-color: #377dff;
}

.form-check-input:checked ~ .form-check-label .custom-option {
  border-color: #377dff;
  background-color: rgba(55, 125, 255, 0.1);
}

#card-element {
  padding: 1rem;
  background: white;
}
</style> 