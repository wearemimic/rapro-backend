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
              <!-- Step 1: Choose Login Method -->
              <div v-if="currentStep === 1">
                <div class="text-center mb-5">
                  <h1 class="display-5">Create your account</h1>
                  <p>Already have an account? <router-link to="/login">Sign in here</router-link></p>
                </div>

                <div class="text-center mb-4">
                  <h5 class="mb-3">Choose how you'd like to sign up:</h5>
                </div>
                
                <!-- Primary Auth0 Signup Buttons -->
                <div class="d-grid gap-3 mb-4">
                  <button 
                    type="button" 
                    class="btn btn-primary btn-lg d-flex justify-content-center align-items-center"
                    @click="signupWithAuth0('google')"
                    :disabled="isLoading"
                  >
                    <img src="/assets/svg/brands/google-icon.svg" class="me-2" width="20" alt="Google">
                    Continue with Google
                  </button>
                  
                  <button 
                    type="button" 
                    class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                    @click="signupWithAuth0('facebook')"
                    :disabled="isLoading"
                  >
                    <img src="/assets/svg/brands/facebook-icon.svg" class="me-2" width="20" alt="Facebook">
                    Continue with Facebook
                  </button>
                  
                  <button 
                    type="button" 
                    class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                    @click="signupWithAuth0('apple')"
                    :disabled="isLoading"
                  >
                    <img src="/assets/svg/brands/apple-icon.svg" class="me-2" width="20" alt="Apple">
                    Continue with Apple
                  </button>
                  
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-lg"
                    @click="signupWithAuth0()"
                    :disabled="isLoading"
                  >
                    Continue with Email
                  </button>
                </div>
                
                <!-- Legacy Registration (Hidden) -->
                <div class="text-center">
                  <button 
                    type="button" 
                    class="btn btn-link btn-sm text-muted"
                    @click="showLegacyForm = !showLegacyForm"
                    v-if="false"
                  >
                    Use traditional registration instead
                  </button>
                </div>
                
                <!-- Legacy Form (Collapsed) -->
                <div v-if="showLegacyForm" class="border-top pt-4 mt-3">
                  <div class="alert alert-warning" role="alert">
                    <strong>Note:</strong> We recommend using one of the social login options above for better security and convenience.
                  </div>
                  
                  <div class="mb-3">
                    <label class="form-label" for="email">Email</label>
                    <input 
                      type="email" 
                      class="form-control" 
                      id="email"
                      v-model="form.email" 
                      required
                      :disabled="isLoading"
                    >
                  </div>

                  <div class="mb-3">
                    <label class="form-label" for="password">Password</label>
                    <input 
                      type="password" 
                      class="form-control" 
                      id="password"
                      v-model="form.password" 
                      required
                      :disabled="isLoading"
                    >
                  </div>

                  <div class="mb-3">
                    <label class="form-label" for="confirmPassword">Confirm Password</label>
                    <input 
                      type="password" 
                      class="form-control" 
                      id="confirmPassword"
                      v-model="form.confirmPassword" 
                      required
                      :disabled="isLoading"
                    >
                  </div>
                </div>
              </div>

              <!-- Step 2: Professional Info -->
              <div v-if="currentStep === 2">
                <div class="text-center mb-5">
                  <h1 class="display-5">Professional Information</h1>
                  <p>Tell us about your practice</p>
                  <div v-if="isCompletingRegistration" class="alert alert-info" role="alert">
                    <i class="bi bi-info-circle"></i>
                    Welcome! Please complete your professional information to finish setting up your account.
                  </div>
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
                          <span class="display-6">${{ getDisplayPrice('monthly') }}</span>
                          <span>/month</span>
                          <div v-if="appliedDiscount && form.plan === 'monthly'" class="text-success small">
                            <s class="text-muted">$99</s> {{ appliedDiscount.name }}
                          </div>
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
                          <span class="display-6">${{ getDisplayPrice('annual') }}</span>
                          <span>/year</span>
                          <div v-if="appliedDiscount && form.plan === 'annual'" class="text-success small">
                            <s class="text-muted">$999</s> {{ appliedDiscount.name }}
                          </div>
                        </span>
                        <span class="flex-grow-1 ms-3">
                          <span class="d-block">Annual Plan</span>
                          <span class="d-block text-muted">Save 16% with annual billing</span>
                        </span>
                      </span>
                    </label>
                  </div>
                </div>

                <!-- Coupon Code Section -->
                <div class="mb-4">
                  <div class="d-flex align-items-center mb-2">
                    <h6 class="mb-0 me-3">Have a coupon code?</h6>
                    <button 
                      type="button" 
                      class="btn btn-link btn-sm p-0"
                      @click="showCouponField = !showCouponField"
                      :disabled="isLoading"
                    >
                      {{ showCouponField ? 'Hide' : 'Enter code' }}
                    </button>
                  </div>
                  
                  <div v-if="showCouponField" class="coupon-section">
                    <div class="input-group">
                      <input 
                        type="text" 
                        class="form-control" 
                        v-model="form.couponCode"
                        placeholder="Enter coupon code"
                        :disabled="isLoading || couponValidating"
                        @blur="validateCoupon"
                        @keyup.enter="validateCoupon"
                      >
                      <button 
                        class="btn btn-outline-primary" 
                        type="button"
                        @click="validateCoupon"
                        :disabled="isLoading || couponValidating || !form.couponCode.trim()"
                      >
                        {{ couponValidating ? 'Checking...' : 'Apply' }}
                      </button>
                    </div>
                    
                    <!-- Coupon Status Messages -->
                    <div v-if="couponStatus.message" class="mt-2">
                      <div 
                        :class="['alert', 'alert-sm', 'mb-0', couponStatus.type === 'success' ? 'alert-success' : 'alert-danger']"
                        role="alert"
                      >
                        <i :class="['bi', couponStatus.type === 'success' ? 'bi-check-circle' : 'bi-exclamation-triangle']"></i>
                        {{ couponStatus.message }}
                      </div>
                    </div>
                    
                    <!-- Applied Discount Summary -->
                    <div v-if="appliedDiscount" class="mt-3 p-3 bg-success bg-opacity-10 rounded">
                      <div class="d-flex justify-content-between align-items-center">
                        <div>
                          <strong class="text-success">{{ appliedDiscount.name }}</strong>
                          <div class="small text-muted">{{ appliedDiscount.description }}</div>
                        </div>
                        <div class="text-end">
                          <div class="text-success fw-bold">
                            {{ appliedDiscount.type === 'percentage' ? `-${appliedDiscount.value}%` : `-$${appliedDiscount.value}` }}
                          </div>
                          <button 
                            type="button" 
                            class="btn btn-link btn-sm p-0 text-muted"
                            @click="removeCoupon"
                            :disabled="isLoading"
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Credit Card Information -->
                <div class="mb-4">
                  <h5 class="mb-3">Payment Information</h5>
                  
                  <!-- Cardholder Name -->
                  <div class="mb-3">
                    <label class="form-label" for="cardholderName">Cardholder Name</label>
                    <input 
                      type="text" 
                      class="form-control form-control-lg" 
                      id="cardholderName"
                      v-model="form.cardholderName" 
                      placeholder="Name as it appears on card"
                      required
                      :disabled="isLoading"
                    >
                  </div>

                  <!-- Card Number -->
                  <div class="mb-3">
                    <label class="form-label" for="cardNumber">Card Number</label>
                    <div id="card-number-element" class="form-control form-control-lg"></div>
                    <div id="card-number-errors" class="invalid-feedback" style="display: none;"></div>
                  </div>

                  <!-- Expiry and CVV Row -->
                  <div class="row mb-3">
                    <div class="col-sm-6">
                      <label class="form-label" for="cardExpiry">Expiry Date</label>
                      <div id="card-expiry-element" class="form-control form-control-lg"></div>
                      <div id="card-expiry-errors" class="invalid-feedback" style="display: none;"></div>
                    </div>
                    <div class="col-sm-6">
                      <label class="form-label" for="cardCvc">CVV</label>
                      <div id="card-cvc-element" class="form-control form-control-lg"></div>
                      <div id="card-cvc-errors" class="invalid-feedback" style="display: none;"></div>
                    </div>
                  </div>

                  <!-- Billing Address -->
                  <div class="mb-3">
                    <div class="form-check">
                      <input 
                        class="form-check-input" 
                        type="checkbox" 
                        v-model="form.sameBillingAddress" 
                        id="sameBillingAddress"
                        :disabled="isLoading"
                      >
                      <label class="form-check-label" for="sameBillingAddress">
                        Billing address is the same as professional address
                      </label>
                    </div>
                  </div>

                  <!-- Billing Address Fields (if different) -->
                  <div v-if="!form.sameBillingAddress">
                    <h6 class="mb-3">Billing Address</h6>
                    
                    <div class="mb-3">
                      <label class="form-label" for="billingAddress">Address</label>
                      <input 
                        type="text" 
                        class="form-control form-control-lg" 
                        id="billingAddress"
                        v-model="form.billingAddress"
                        required
                        :disabled="isLoading"
                      >
                    </div>

                    <div class="row">
                      <div class="col-sm-6 mb-3">
                        <label class="form-label" for="billingCity">City</label>
                        <input 
                          type="text" 
                          class="form-control form-control-lg" 
                          id="billingCity"
                          v-model="form.billingCity"
                          required
                          :disabled="isLoading"
                        >
                      </div>
                      <div class="col-sm-3 mb-3">
                        <label class="form-label" for="billingState">State</label>
                        <input 
                          type="text" 
                          class="form-control form-control-lg" 
                          id="billingState"
                          v-model="form.billingState"
                          required
                          :disabled="isLoading"
                        >
                      </div>
                      <div class="col-sm-3 mb-3">
                        <label class="form-label" for="billingZip">ZIP Code</label>
                        <input 
                          type="text" 
                          class="form-control form-control-lg" 
                          id="billingZip"
                          v-model="form.billingZip"
                          required
                          :disabled="isLoading"
                        >
                      </div>
                    </div>
                  </div>
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
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useRegistrationStore } from '@/stores/registration';
import { useAuthStore } from '@/stores/auth';
import { useAuth0 } from '@auth0/auth0-vue';

const router = useRouter();
const registrationStore = useRegistrationStore();
const authStore = useAuthStore();
const { loginWithRedirect, getAccessTokenSilently, user, isAuthenticated } = useAuth0();
const isLoading = ref(false);
const showLegacyForm = ref(false);

// Coupon functionality
const showCouponField = ref(false);
const couponValidating = ref(false);
const couponStatus = ref({ type: '', message: '' });
const appliedDiscount = ref(null);

const currentStep = computed(() => registrationStore.currentStep);

// Check if user is completing registration after Auth0 authentication
const isCompletingRegistration = computed(() => {
  return currentStep.value === 2 && localStorage.getItem('auth0_flow') === 'registration';
});

// Price calculation with discounts
const getDisplayPrice = (plan) => {
  const basePrice = plan === 'monthly' ? 99 : 999;
  
  if (!appliedDiscount.value) {
    return basePrice;
  }
  
  if (appliedDiscount.value.type === 'percentage') {
    return Math.round(basePrice * (1 - appliedDiscount.value.value / 100));
  } else {
    return Math.max(0, basePrice - appliedDiscount.value.value);
  }
};

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
  plan: 'monthly',
  cardholderName: '',
  sameBillingAddress: true,
  billingAddress: '',
  billingCity: '',
  billingState: '',
  billingZip: '',
  couponCode: ''
});

onMounted(async () => {
  // Check for step query parameter (from Auth0 callback)
  const urlParams = new URLSearchParams(window.location.search);
  const stepParam = urlParams.get('step');
  
  if (stepParam) {
    const step = parseInt(stepParam);
    if (step >= 1 && step <= 3) {
      registrationStore.currentStep = step;
      console.log(`🔄 Set registration step to ${step} from URL parameter`);
      
      // Show a message if they're completing registration after Auth0 login
      if (step === 2 && localStorage.getItem('auth0_flow') === 'registration') {
        console.log('✅ User redirected to complete registration after Auth0 authentication');
        // You could show a toast message here if you have a notification system
      }
    }
  }
  
  // Check if user is already authenticated (from Auth0 callback)
  if (authStore.isAuthenticated && authStore.user) {
    console.log('✅ User already authenticated, pre-filling form data');
    
    // Move to step 2 if not already there
    if (registrationStore.currentStep === 1) {
      registrationStore.currentStep = 2;
    }
    
    // Pre-fill form with user data
    form.email = authStore.user.email || '';
    form.firstName = authStore.user.first_name || '';
    form.lastName = authStore.user.last_name || '';
    
    console.log('✅ Form pre-filled with user data:', {
      email: form.email,
      firstName: form.firstName,
      lastName: form.lastName
    });
  }
  
  // Legacy Auth0 Vue plugin check (fallback)
  if (isAuthenticated.value && user.value) {
    try {
      const accessToken = await getAccessTokenSilently();
      const success = await authStore.loginWithAuth0(accessToken);
      
      if (success) {
        if (registrationStore.currentStep === 1) {
          registrationStore.currentStep = 2;
        }
        
        if (user.value) {
          form.email = user.value.email || '';
          form.firstName = user.value.given_name || '';
          form.lastName = user.value.family_name || '';
        }
      }
    } catch (error) {
      console.error('Error handling Auth0 authentication:', error);
    }
  }
  
  // Initialize Stripe if already on step 3
  if (currentStep.value === 3) {
    initializeStripe();
  }
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

const validateStep3 = () => {
  if (!form.cardholderName.trim()) {
    alert('Please enter the cardholder name');
    return false;
  }
  
  if (!form.plan) {
    alert('Please select a subscription plan');
    return false;
  }
  
  // Validate billing address if different from professional address
  if (!form.sameBillingAddress) {
    if (!form.billingAddress || !form.billingCity || !form.billingState || !form.billingZip) {
      alert('Please fill in all billing address fields');
      return false;
    }
  }
  
  return true;
};

// Coupon validation and management
const validateCoupon = async () => {
  if (!form.couponCode.trim()) {
    return;
  }
  
  couponValidating.value = true;
  couponStatus.value = { type: '', message: '' };
  
  try {
    // Call backend to validate coupon
    const response = await fetch('http://localhost:8000/api/validate-coupon/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        coupon_code: form.couponCode.trim(),
        plan: form.plan
      })
    });
    
    const data = await response.json();
    
    if (response.ok && data.valid) {
      appliedDiscount.value = {
        id: data.coupon_id,
        name: data.name,
        description: data.description,
        type: data.discount_type, // 'percentage' or 'fixed'
        value: data.discount_value
      };
      
      couponStatus.value = {
        type: 'success',
        message: `Coupon applied! ${data.description}`
      };
      
      console.log('✅ Coupon applied:', appliedDiscount.value);
    } else {
      couponStatus.value = {
        type: 'error',
        message: data.message || 'Invalid coupon code'
      };
      appliedDiscount.value = null;
    }
  } catch (error) {
    console.error('❌ Coupon validation error:', error);
    couponStatus.value = {
      type: 'error',
      message: 'Failed to validate coupon. Please try again.'
    };
    appliedDiscount.value = null;
  } finally {
    couponValidating.value = false;
  }
};

const removeCoupon = () => {
  appliedDiscount.value = null;
  couponStatus.value = { type: '', message: '' };
  form.couponCode = '';
  console.log('🗑️ Coupon removed');
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

const signupWithAuth0 = async (connection) => {
  console.log('🔵 signupWithAuth0 called with connection:', connection);
  
  try {
    // Use direct Auth0 redirect method for signup
    console.log('🔄 Using direct Auth0 redirect method for signup...');
    
    // Map common connection names to Auth0 connection names
    const connectionMap = {
      'google': 'google-oauth2',
      'facebook': 'facebook',
      'apple': 'apple'
    };
    
    const actualConnection = connectionMap[connection] || connection;
    console.log(`🔵 Using connection: ${connection} -> ${actualConnection}`);
    
    // Store registration flow in localStorage
    localStorage.setItem('auth0_flow', 'registration');
    
    let authUrl = `https://genai-030069804226358743.us.auth0.com/authorize?` +
      `client_id=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw&` +
      `response_type=code&` +
      `redirect_uri=http://localhost:3000/auth/callback&` +
      `scope=openid profile email&` +
      `screen_hint=signup`;
    
    // Add connection if specified
    if (actualConnection) {
      authUrl += `&connection=${actualConnection}`;
    } else {
      // For email signup, force the signup screen
      authUrl += `&prompt=login`;
    }
    
    console.log('🔵 Redirecting to:', authUrl);
    window.location.href = authUrl;
    
  } catch (error) {
    console.error('❌ Auth0 signup error:', error);
    alert(`Auth0 signup failed: ${error.message}`);
  }
};

let stripe = null;
let cardNumber = null;
let cardExpiry = null;
let cardCvc = null;

const initializeStripe = async () => {
  if (currentStep.value === 3 && window.Stripe && !stripe) {
    console.log('🔄 Initializing Stripe...');
    stripe = window.Stripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);
    const elements = stripe.elements();
    
    const style = {
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
    };

    // Create separate elements
    cardNumber = elements.create('cardNumber', { style });
    cardExpiry = elements.create('cardExpiry', { style });
    cardCvc = elements.create('cardCvc', { style });
    
    // Wait for the elements to be available
    setTimeout(() => {
      const cardNumberElement = document.getElementById('card-number-element');
      const cardExpiryElement = document.getElementById('card-expiry-element');
      const cardCvcElement = document.getElementById('card-cvc-element');
      
      if (cardNumberElement && cardExpiryElement && cardCvcElement) {
        cardNumber.mount('#card-number-element');
        cardExpiry.mount('#card-expiry-element');
        cardCvc.mount('#card-cvc-element');
        
        // Add error handling for each element
        cardNumber.addEventListener('change', function(event) {
          const displayError = document.getElementById('card-number-errors');
          if (event.error) {
            displayError.textContent = event.error.message;
            displayError.style.display = 'block';
          } else {
            displayError.textContent = '';
            displayError.style.display = 'none';
          }
        });

        cardExpiry.addEventListener('change', function(event) {
          const displayError = document.getElementById('card-expiry-errors');
          if (event.error) {
            displayError.textContent = event.error.message;
            displayError.style.display = 'block';
          } else {
            displayError.textContent = '';
            displayError.style.display = 'none';
          }
        });

        cardCvc.addEventListener('change', function(event) {
          const displayError = document.getElementById('card-cvc-errors');
          if (event.error) {
            displayError.textContent = event.error.message;
            displayError.style.display = 'block';
          } else {
            displayError.textContent = '';
            displayError.style.display = 'none';
          }
        });
        
        console.log('✅ Stripe card elements mounted');
      }
    }, 100);
  }
};

// Watch for step changes to initialize Stripe when needed
watch(currentStep, (newStep) => {
  if (newStep === 3) {
    initializeStripe();
  }
});


const handleSubmit = async () => {
  if (currentStep.value === 1) {
    // Skip traditional step 1 validation since we're using Auth0
    return;
  }
  
  if (currentStep.value === 2) {
    if (!validateStep2()) {
      return;
    }
    // Move to payment step
    registrationStore.currentStep = 3;
    return;
  }

  if (currentStep.value === 3) {
    if (!validateStep3()) {
      return;
    }
    
    isLoading.value = true;
    try {

      // Create billing details
      const billingDetails = {
        name: form.cardholderName,
        address: {
          line1: form.sameBillingAddress ? form.address : form.billingAddress,
          city: form.sameBillingAddress ? form.city : form.billingCity,
          state: form.sameBillingAddress ? form.state : form.billingState,
          postal_code: form.sameBillingAddress ? form.zipCode : form.billingZip,
          country: 'US'
        }
      };

      // Create payment method using the separate card elements
      const { paymentMethod, error } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardNumber,
        billing_details: billingDetails
      });

      if (error) {
        throw error;
      }

      console.log('✅ Payment method created:', paymentMethod.id);

      // Complete Auth0 registration with professional info and payment
      const response = await fetch('http://localhost:8000/api/auth0/complete-registration/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify({
          professionalInfo: {
            firstName: form.firstName,
            lastName: form.lastName,
            companyName: form.companyName,
            phone: form.phone,
            licenses: form.licenses,
            website: form.website,
            address: form.address,
            city: form.city,
            state: form.state,
            zipCode: form.zipCode
          },
          paymentInfo: {
            paymentMethodId: paymentMethod.id,
            plan: form.plan,
            billingDetails: billingDetails,
            couponCode: appliedDiscount.value ? form.couponCode : null,
            appliedDiscount: appliedDiscount.value
          }
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        console.log('✅ Registration completed successfully');
        router.push('/dashboard');
      } else {
        throw new Error(data.message || 'Registration failed');
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      alert(error.message || 'An error occurred during registration');
    } finally {
      isLoading.value = false;
    }
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

#card-number-element,
#card-expiry-element,
#card-cvc-element {
  padding: 1rem;
  background: white;
  border: 1px solid #e7eaf3;
  border-radius: 0.5rem;
  transition: border-color 0.15s ease-in-out;
}

#card-number-element:focus-within,
#card-expiry-element:focus-within,
#card-cvc-element:focus-within {
  border-color: #377dff;
  box-shadow: 0 0 0 0.2rem rgba(55, 125, 255, 0.25);
}

.StripeElement {
  border: none !important;
}

.StripeElement--focus {
  border: none !important;
  box-shadow: none !important;
}

.coupon-section {
  border: 1px solid #e7eaf3;
  border-radius: 0.5rem;
  padding: 1rem;
  background-color: #f8f9fa;
}

.alert-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.coupon-section .input-group {
  margin-bottom: 0;
}

.bg-success.bg-opacity-10 {
  background-color: rgba(25, 135, 84, 0.1) !important;
}
</style> 