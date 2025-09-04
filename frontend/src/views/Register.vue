<template>
  <main id="content" role="main" class="main register-main">
    <div class="container py-5 py-sm-7">
      <div class="mx-auto" style="max-width: 45rem;">
        <!-- Card -->
        <div class="text-center mb-4">
          <img src="/assets/img/RAD-white-logo.png" style="height:50px;margin-bottom:20px;" alt="Logo">
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
                    <img src="/assets/svg/brands/apple.svg.png" class="me-2" width="20" alt="Apple">
                    Continue with Apple
                  </button>
                  
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-lg"
                    @click="showEmbeddedEmailRegistration"
                    :disabled="isLoading"
                  >
                    Continue with Email
                  </button>
                </div>
                
                <!-- Embedded Auth0 Email Registration -->
                <div v-if="showEmailRegistration" class="mt-4 p-4 border rounded">
                  <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0">Sign up with Email</h5>
                    <button type="button" class="btn-close" @click="showEmailRegistration = false"></button>
                  </div>
                  
                  <!-- Fully Embedded Signup Form (No Redirect) -->
                  <form @submit.prevent="handleEmbeddedSignup" v-if="!useAuth0Lock">
                    <div class="mb-3">
                      <label for="signup-email" class="form-label">Email address</label>
                      <input 
                        type="email" 
                        class="form-control form-control-lg" 
                        id="signup-email"
                        v-model="embeddedForm.email"
                        placeholder="Enter your email"
                        required
                        :disabled="isLoading"
                      >
                    </div>
                    <div class="mb-3">
                      <label for="signup-password" class="form-label">Password</label>
                      <input 
                        type="password" 
                        class="form-control form-control-lg" 
                        id="signup-password"
                        v-model="embeddedForm.password"
                        placeholder="Enter a secure password"
                        required
                        :disabled="isLoading"
                        minlength="8"
                        @input="updatePasswordStrength"
                      >
                      <!-- Dynamic Password Requirements -->
                      <div class="password-requirements mt-2">
                        <small class="d-block mb-1 fw-bold">Password must contain:</small>
                        <div class="requirement-list">
                          <div class="requirement-item" :class="{ 'requirement-met': passwordChecks.length }">
                            <i class="bi" :class="passwordChecks.length ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'"></i>
                            <span class="ms-1">At least 8 characters</span>
                          </div>
                          <div class="requirement-item" :class="{ 'requirement-met': passwordChecks.lowercase }">
                            <i class="bi" :class="passwordChecks.lowercase ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'"></i>
                            <span class="ms-1">Lowercase letters (a-z)</span>
                          </div>
                          <div class="requirement-item" :class="{ 'requirement-met': passwordChecks.uppercase }">
                            <i class="bi" :class="passwordChecks.uppercase ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'"></i>
                            <span class="ms-1">Uppercase letters (A-Z)</span>
                          </div>
                          <div class="requirement-item" :class="{ 'requirement-met': passwordChecks.numbers }">
                            <i class="bi" :class="passwordChecks.numbers ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'"></i>
                            <span class="ms-1">Numbers (0-9)</span>
                          </div>
                          <div class="requirement-item" :class="{ 'requirement-met': passwordChecks.special }">
                            <i class="bi" :class="passwordChecks.special ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'"></i>
                            <span class="ms-1">Special characters (!@#$%^&*)</span>
                          </div>
                        </div>
                        <div class="mt-2">
                          <small class="fw-bold">
                            <span :class="passwordStrengthClass">{{ passwordStrengthText }}</span>
                            <span v-if="!isPasswordValid" class="text-muted"> (Need {{ 3 - passwordStrengthScore }} more type{{ 3 - passwordStrengthScore === 1 ? '' : 's' }})</span>
                          </small>
                        </div>
                      </div>
                    </div>
                    <div class="mb-3">
                      <label for="signup-confirm-password" class="form-label">Confirm Password</label>
                      <input 
                        type="password" 
                        class="form-control form-control-lg" 
                        id="signup-confirm-password"
                        v-model="embeddedForm.confirmPassword"
                        placeholder="Confirm your password"
                        required
                        :disabled="isLoading"
                      >
                    </div>
                    <div v-if="signupError" class="alert alert-danger" role="alert">
                      <i class="bi bi-exclamation-triangle"></i>
                      {{ signupError }}
                    </div>
                    <div class="mb-3">
                      <small class="text-muted">
                        Your account will be created securely without leaving this page.
                      </small>
                    </div>
                    <button 
                      type="submit" 
                      class="btn btn-primary btn-lg w-100"
                      :disabled="isLoading || !canSubmitEmbedded"
                    >
                      {{ isLoading ? 'Creating Account...' : 'Create Account' }}
                    </button>
                  </form>
                  
                  <!-- Auth0 Lock container (hidden due to timeout issues) -->
                  <div v-if="useAuth0Lock" id="auth0-register-lock-container"></div>
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
                
                <!-- SMS Consent Checkbox -->
                <div class="mb-4">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      v-model="form.smsConsent" 
                      id="smsConsent"
                      :disabled="isLoading"
                    >
                    <label class="form-check-label" for="smsConsent">
                      <small class="text-muted">
                        I consent to receive text messages from RetirementAdvisorPro about product updates, 
                        industry insights, and company information. Message and data rates may apply. 
                        I understand I can opt out at any time by replying STOP.
                        <span class="text-danger">*</span>
                      </small>
                    </label>
                  </div>
                  <div class="mt-1">
                    <small class="text-muted">
                      By checking this box, you agree to receive SMS messages. Standard messaging rates apply. 
                      You can unsubscribe at any time by texting STOP.
                    </small>
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
                <div class="mb-4" v-if="paymentRequired">
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
                  <!-- Billing Address Fields -->
                  <div>
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
                
                <!-- Zero Cost Message -->
                <div v-if="!paymentRequired" class="mb-4">
                  <div class="alert alert-success" role="alert">
                    <i class="bi bi-check-circle-fill"></i>
                    <strong>Great news!</strong> Your coupon covers the full cost. No payment information required!
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
                    currentStep === 3 ? (paymentRequired ? 'Complete Registration' : 'Activate Free Account') : 'Next'
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
import { API_CONFIG } from '@/config';

const router = useRouter();
const registrationStore = useRegistrationStore();
const authStore = useAuthStore();
const isLoading = ref(false);
const showLegacyForm = ref(false);
const showEmailRegistration = ref(false);
const embeddedEmail = ref('');
const useAuth0Lock = ref(false); // Set to false to use simple form instead
let auth0RegisterLock = null;
const signupError = ref('');

// Embedded signup form data
const embeddedForm = reactive({
  email: '',
  password: '',
  confirmPassword: ''
});

// Password strength checking
const passwordChecks = reactive({
  length: false,
  lowercase: false,
  uppercase: false,
  numbers: false,
  special: false
});

// Coupon functionality
const showCouponField = ref(false);
const couponValidating = ref(false);
const couponStatus = ref({ type: '', message: '' });
const appliedDiscount = ref(null);

const currentStep = computed(() => registrationStore.currentStep);

// Password strength computed properties
const passwordStrengthScore = computed(() => {
  let score = 0;
  if (passwordChecks.lowercase) score++;
  if (passwordChecks.uppercase) score++;
  if (passwordChecks.numbers) score++;
  if (passwordChecks.special) score++;
  return score;
});

const isPasswordValid = computed(() => {
  return passwordChecks.length && passwordStrengthScore.value >= 3;
});

const passwordStrengthText = computed(() => {
  if (!embeddedForm.password) return '';
  if (!passwordChecks.length) return 'Too short';
  
  const score = passwordStrengthScore.value;
  if (score >= 3) return 'Strong password ✓';
  if (score === 2) return 'Fair password';
  if (score === 1) return 'Weak password';
  return 'Very weak password';
});

const passwordStrengthClass = computed(() => {
  if (!embeddedForm.password) return '';
  if (!passwordChecks.length) return 'text-danger';
  
  const score = passwordStrengthScore.value;
  if (score >= 3) return 'text-success';
  if (score === 2) return 'text-warning';
  return 'text-danger';
});

// Check if embedded form can be submitted
const canSubmitEmbedded = computed(() => {
  return embeddedForm.email && 
         embeddedForm.password && 
         embeddedForm.confirmPassword &&
         isPasswordValid.value &&
         embeddedForm.password === embeddedForm.confirmPassword;
});

// Check if user is completing registration after Auth0 authentication
const isCompletingRegistration = computed(() => {
  return currentStep.value === 2 && localStorage.getItem('auth0_flow') === 'registration';
});

// Check if payment is required based on coupon discount
const isZeroCost = computed(() => {
  if (!appliedDiscount.value) return false;
  
  const plan = form.plan;
  const basePrice = plan === 'monthly' ? 99 : 999;
  
  if (appliedDiscount.value.discounted_price !== undefined) {
    return appliedDiscount.value.discounted_price === 0;
  }
  
  // Fallback calculation
  if (appliedDiscount.value.type === 'percentage') {
    return appliedDiscount.value.value === 100;
  } else {
    return appliedDiscount.value.value >= basePrice;
  }
});

// Check if payment info is required
const paymentRequired = computed(() => {
  return !isZeroCost.value;
});

// Price calculation with discounts
const getDisplayPrice = (plan) => {
  const basePrice = plan === 'monthly' ? 99 : 999;
  
  if (!appliedDiscount.value) {
    return basePrice;
  }
  
  // If we have API data with calculated prices, use those
  if (appliedDiscount.value.original_price && appliedDiscount.value.discounted_price) {
    // Make sure we're showing the right price for the current plan
    const discountPlan = appliedDiscount.value.original_price === 99 ? 'monthly' : 'annual';
    if (discountPlan === plan) {
      return Math.round(appliedDiscount.value.discounted_price);
    }
  }
  
  // Fallback to manual calculation
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
  phone: '',
  smsConsent: false,

  // Step 3: Payment
  plan: 'monthly',
  cardholderName: '',
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
    console.log('✅ User already authenticated, checking registration status');
    
    // Check registration completeness
    const user = authStore.user;
    const hasProfileInfo = user.phone_number && user.first_name && user.last_name;
    const hasSubscription = user.subscription_status && user.stripe_customer_id;
    
    console.log('📋 Registration status check:', {
      hasProfileInfo,
      hasSubscription,
      subscription_status: user.subscription_status
    });
    
    if (hasSubscription) {
      // Registration already complete - redirect to dashboard
      console.log('✅ Registration already complete, redirecting to dashboard');
      router.push('/dashboard');
      return;
    } else if (hasProfileInfo && !hasSubscription) {
      // Professional info complete but no payment - go to step 3
      console.log('🔄 Professional info complete, moving to payment step');
      registrationStore.currentStep = 3;
      
      // Pre-fill form with existing data
      form.email = user.email || '';
      form.firstName = user.first_name || '';
      form.lastName = user.last_name || '';
      form.phone = user.phone_number || '';
    } else {
      // New user or incomplete profile - go to step 2
      console.log('🔄 New or incomplete registration, moving to professional info step');
      if (registrationStore.currentStep === 1) {
        registrationStore.currentStep = 2;
      }
      
      // Pre-fill form with Auth0 user data
      form.email = user.email || '';
      form.firstName = user.first_name || '';
      form.lastName = user.last_name || '';
      
      console.log('✅ Form pre-filled with user data:', {
        email: form.email,
        firstName: form.firstName,
        lastName: form.lastName
      });
    }
  }
  
  // Auth0 SDK removed - using direct Auth0 redirects now
  
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
  
  if (!form.smsConsent) {
    alert('Please consent to receive SMS messages to continue. This helps us provide important updates about your account.');
    return false;
  }
  
  return true;
};

const validateStep3 = () => {
  if (!form.plan) {
    alert('Please select a subscription plan');
    return false;
  }
  
  // Skip payment validation for zero-cost subscriptions
  if (isZeroCost.value) {
    console.log('✅ Zero-cost subscription detected, skipping payment validation');
    return true;
  }
  
  // Validate payment info for paid subscriptions
  if (!form.cardholderName.trim()) {
    alert('Please enter the cardholder name');
    return false;
  }
  
  // Validate billing address fields
  if (!form.billingAddress || !form.billingCity || !form.billingState || !form.billingZip) {
    alert('Please fill in all billing address fields');
    return false;
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
    const response = await fetch(`${import.meta.env.VITE_API_URL}/validate-coupon/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
        // No Authorization header needed - endpoint allows anonymous access
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
        value: data.discount_value,
        original_price: data.original_price,
        discounted_price: data.discounted_price
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

// Password strength checking function
const updatePasswordStrength = () => {
  const password = embeddedForm.password;
  
  // Check length
  passwordChecks.length = password.length >= 8;
  
  // Check for lowercase letters
  passwordChecks.lowercase = /[a-z]/.test(password);
  
  // Check for uppercase letters
  passwordChecks.uppercase = /[A-Z]/.test(password);
  
  // Check for numbers
  passwordChecks.numbers = /[0-9]/.test(password);
  
  // Check for special characters
  passwordChecks.special = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
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
          phoneNumber: form.phone,
          smsConsent: form.smsConsent
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

const showEmbeddedEmailRegistration = () => {
  console.log('🔵 Starting fully embedded email registration');
  
  // Set registration flow in localStorage
  localStorage.setItem('auth0_flow', 'registration');
  showEmailRegistration.value = true;
  
  // Clear the embedded form
  embeddedForm.email = '';
  embeddedForm.password = '';
  embeddedForm.confirmPassword = '';
  signupError.value = '';
  
  // Since Auth0 Lock has timeout issues, we'll use the simple form approach
  if (useAuth0Lock.value) {
    // Only load Auth0 Lock if we're using it (currently disabled due to timeout issues)
    if (!window.Auth0Lock) {
      console.log('📦 Loading Auth0 Lock script...');
      const script = document.createElement('script');
      script.src = 'https://cdn.auth0.com/js/lock/11.32.2/lock.min.js';
      script.onload = () => {
        console.log('✅ Auth0 Lock script loaded');
        initAuth0RegisterLock();
      };
      script.onerror = (error) => {
        console.error('❌ Failed to load Auth0 Lock script:', error);
        alert('Failed to load authentication library. Please refresh and try again.');
      };
      document.head.appendChild(script);
    } else {
      console.log('✅ Auth0 Lock already loaded, initializing...');
      initAuth0RegisterLock();
    }
  }
};

const handleEmbeddedSignup = async () => {
  console.log('📧 Handling truly embedded signup - account creation only');
  
  // Clear any previous errors
  signupError.value = '';
  
  // Validate form
  if (!embeddedForm.email) {
    signupError.value = 'Please enter your email address';
    return;
  }
  
  if (!embeddedForm.password || embeddedForm.password.length < 8) {
    signupError.value = 'Password must be at least 8 characters long';
    return;
  }
  
  if (embeddedForm.password !== embeddedForm.confirmPassword) {
    signupError.value = 'Passwords do not match';
    return;
  }
  
  // Validate password strength using our dynamic checker
  if (!isPasswordValid.value) {
    signupError.value = 'Password does not meet requirements. Please ensure it has at least 8 characters with uppercase, lowercase, numbers, and special characters.';
    return;
  }
  
  try {
    isLoading.value = true;
    
    console.log('🔄 Creating Auth0 account without immediate authentication...');
    
    // Call backend to create the account only (no authentication)
    const signupResponse = await fetch(`${import.meta.env.VITE_API_URL}/auth0/create-account/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: embeddedForm.email.trim().toLowerCase(),
        password: embeddedForm.password
      })
    });
    
    const signupData = await signupResponse.json();
    
    if (!signupResponse.ok || !signupData.success) {
      console.error('❌ Account creation failed:', signupResponse.status, signupData);
      signupError.value = signupData.message || 'Account creation failed. Please try again.';
      return;
    }
    
    console.log('✅ Auth0 account created successfully, proceeding to next step');
    
    // Store email and password for later authentication during final step
    sessionStorage.setItem('registration_email', embeddedForm.email.trim().toLowerCase());
    sessionStorage.setItem('registration_password', embeddedForm.password);
    
    // Clear the form
    embeddedForm.email = '';
    embeddedForm.password = '';
    embeddedForm.confirmPassword = '';
    
    // Mark as registration flow and close the embedded form
    localStorage.setItem('auth0_flow', 'registration');
    showEmailRegistration.value = false;
    
    // Pre-fill form with email
    form.email = signupData.email;
    
    // Move to step 2 (Professional Info)
    registrationStore.currentStep = 2;
    
  } catch (error) {
    console.error('❌ Embedded signup error:', error);
    signupError.value = 'Network error. Please check your connection and try again.';
  } finally {
    isLoading.value = false;
  }
};

// Legacy function for backward compatibility
const handleEmailSignup = () => {
  // This function is now replaced by handleEmbeddedSignup
  handleEmbeddedSignup();
};

const initAuth0RegisterLock = () => {
  try {
    const domain = import.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
    
    console.log('🔧 Initializing Auth0 Lock with:', { domain, clientId });
    
    // Wait for the container to be rendered
    setTimeout(() => {
      const container = document.getElementById('auth0-register-lock-container');
      if (!container) {
        console.error('❌ Auth0 Lock container not found');
        alert('Failed to load registration form. Please refresh and try again.');
        return;
      }
      
      console.log('✅ Container found, initializing Auth0 Lock...');
      
      auth0RegisterLock = new window.Auth0Lock(clientId, domain, {
        container: 'auth0-register-lock-container',
        auth: {
          redirectUrl: `${API_CONFIG.FRONTEND_URL}/auth/callback`,
          responseType: 'code',
          params: {
            scope: 'openid profile email'
          }
        },
        allowedConnections: ['Username-Password-Authentication'],
        allowSignUp: true,  // Enable signup for registration
        allowLogin: false,  // Disable login to force signup only
        allowForgotPassword: false,  // Hide forgot password for registration
        initialScreen: 'signUp',  // Force signup screen
        languageDictionary: {
          title: 'Create your account',
          signUpSubmitLabel: 'Sign Up'
        },
        theme: {
          primaryColor: '#377dff'
        },
        closable: false
      });
    
      // Handle successful authentication/registration
      auth0RegisterLock.on('authenticated', (authResult) => {
        console.log('✅ Auth0 Lock authenticated:', authResult);
        // The callback will be handled by our existing Auth0CallbackSimple.vue
        window.location.href = `${API_CONFIG.FRONTEND_URL}/auth/callback?code=${authResult.accessToken}&state=registration`;
      });
      
      // Handle unrecoverable errors
      auth0RegisterLock.on('unrecoverable_error', (error) => {
        console.error('❌ Auth0 Lock unrecoverable error - Full object:', error);
        console.error('Error details:', {
          error: error.error,
          errorDescription: error.error_description,
          description: error.description,
          message: error.message,
          code: error.code,
          statusCode: error.statusCode,
          original: error.original
        });
        
        // Try to get a meaningful error message
        const errorMessage = error.error_description || 
                           error.description || 
                           error.error || 
                           error.message || 
                           'An error occurred. Please check the console for details.';
        
        alert(`Registration error: ${errorMessage}`);
      });
      
      // Handle authorization errors
      auth0RegisterLock.on('authorization_error', (error) => {
        console.error('❌ Auth0 Lock authorization error:', error);
        alert(`Authorization failed: ${error.error_description || error.error || 'Please try again'}`);
      });
      
      // Handle signin event (even though we're in signup mode, this might fire)
      auth0RegisterLock.on('signin submit', (options) => {
        console.log('📝 Signin form submitted (unexpected in signup mode):', options);
      });
      
      // Handle show event
      auth0RegisterLock.on('show', () => {
        console.log('✅ Auth0 Lock is now visible');
      });
      
      // Handle hide event
      auth0RegisterLock.on('hide', () => {
        console.log('🔒 Auth0 Lock is now hidden');
      });
      
      console.log('📱 Showing Auth0 Lock...');
      auth0RegisterLock.show();
      console.log('✅ Auth0 Lock initialized and shown');
    }, 100); // Small delay to ensure DOM is ready
    
  } catch (error) {
    console.error('❌ Failed to initialize Auth0 Lock:', error);
    alert(`Failed to initialize registration form: ${error.message || 'Unknown error'}`);
    showEmailRegistration.value = false;
  }
};

const signupWithAuth0 = async (connection) => {
  console.log('🔵 Auth0 registration started with connection:', connection);
  
  try {
    isLoading.value = true;
    
    // Store registration flow in localStorage for callback detection
    localStorage.setItem('auth0_flow', 'registration');
    console.log('✅ Set auth0_flow to registration');
    console.log('🔍 localStorage auth0_flow after setting:', localStorage.getItem('auth0_flow'));
    console.log('🔍 All localStorage items:', Object.keys(localStorage));
    
    // Build Auth0 authorization URL for registration
    const domain = import.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
    const callbackUrl = `${API_CONFIG.FRONTEND_URL}/auth/callback`;
    
    // Generate state parameter for security
    const state = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(32))));
    sessionStorage.setItem('auth0_state', state);
    
    // Map connection names to Auth0 connection identifiers
    const connectionMap = {
      'google': 'google-oauth2',
      'facebook': 'facebook', 
      'apple': 'apple'
    };
    
    const actualConnection = connectionMap[connection] || connection;
    
    // Build Auth0 URL with signup parameters
    let authUrl = `https://${domain}/authorize?` +
      `client_id=${clientId}&` +
      `response_type=code&` +
      `redirect_uri=${encodeURIComponent(callbackUrl)}&` +
      `scope=openid profile email&` +
      `state=${state}&` +
      `screen_hint=signup&` +  // This tells Auth0 to show signup form by default
      `prompt=login`;  // Force Auth0 to show login/signup form even if user has existing session
    
    // Add connection parameter if specified
    if (actualConnection && connection !== 'email') {
      authUrl += `&connection=${actualConnection}`;
    } else if (connection === 'email') {
      // For email registration, use Username-Password-Authentication to show only email/password form
      authUrl += `&connection=Username-Password-Authentication`;
    }
    
    console.log('🔗 Redirecting to Auth0 registration:', authUrl);
    console.log('🔗 Using callback URL:', callbackUrl);
    
    // Redirect to Auth0
    window.location.href = authUrl;
    
  } catch (error) {
    console.error('❌ Auth0 registration error:', error);
    alert(`Registration failed: ${error.message}`);
    isLoading.value = false;
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

      let paymentMethodId = null;
      let billingDetails = {};
      
      // Only create payment method for paid subscriptions
      if (paymentRequired.value) {
        // Create billing details
        billingDetails = {
          name: form.cardholderName,
          address: {
            line1: form.billingAddress,
            city: form.billingCity,
            state: form.billingState,
            postal_code: form.billingZip,
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

        paymentMethodId = paymentMethod.id;
        console.log('✅ Payment method created:', paymentMethodId);
      } else {
        console.log('✅ Skipping payment method creation for zero-cost subscription');
      }

      // Get registration credentials
      const email = sessionStorage.getItem('registration_email');
      const password = sessionStorage.getItem('registration_password');
      
      if (!email || !password) {
        throw new Error('Missing registration credentials. Please start registration again.');
      }
      
      console.log('🔄 Completing registration with payment-first security flow...');

      // Complete Auth0 registration with professional info and payment
      // Backend will authenticate AFTER payment succeeds (secure flow)
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth0/complete-registration/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          registrationEmail: email,
          registrationPassword: password,
          professionalInfo: {
            firstName: form.firstName,
            lastName: form.lastName,
            phone: form.phone,
            smsConsent: form.smsConsent
          },
          paymentInfo: {
            paymentMethodId: paymentMethodId,
            plan: form.plan,
            billingDetails: billingDetails,
            couponCode: appliedDiscount.value ? form.couponCode : null,
            appliedDiscount: appliedDiscount.value,
            isZeroCost: isZeroCost.value
          }
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        console.log('✅ Registration completed successfully');
        
        // Store authentication tokens returned after payment
        if (data.access && data.refresh) {
          authStore.setTokens({
            access: data.access,
            refresh: data.refresh
          });
          
          authStore.setUser(data.user);
          console.log('✅ Authentication tokens stored after payment');
        }
        
        // Clear registration credentials
        sessionStorage.removeItem('registration_email');
        sessionStorage.removeItem('registration_password');
        localStorage.removeItem('auth0_flow');
        sessionStorage.removeItem('auth0_state');
        
        // Handle 3D Secure authentication if required
        if (data.payment_intent && data.payment_intent.status === 'requires_action') {
          console.log('🔄 Payment requires 3D Secure authentication');
          
          const { error: confirmError } = await stripe.confirmCardPayment(
            data.payment_intent.client_secret
          );
          
          if (confirmError) {
            throw new Error(`Payment authentication failed: ${confirmError.message}`);
          }
        }
        
        // Show success message and redirect
        alert('Registration completed successfully! Welcome to RetirementAdvisorPro.');
        router.push('/dashboard');
      } else {
        throw new Error(data.message || 'Registration failed');
      }
    } catch (error) {
      console.error('❌ Registration error:', error);
      
      // Enhanced error handling with user-friendly messages
      let errorMessage = 'An error occurred during registration. Please try again.';
      
      if (error.message) {
        if (error.message.includes('card_declined')) {
          errorMessage = 'Your card was declined. Please check your payment information or try a different card.';
        } else if (error.message.includes('invalid_expiry_month') || error.message.includes('invalid_expiry_year')) {
          errorMessage = 'Please check your card expiration date and try again.';
        } else if (error.message.includes('invalid_cvc')) {
          errorMessage = 'Please check your card security code (CVC) and try again.';
        } else if (error.message.includes('insufficient_funds')) {
          errorMessage = 'Your card was declined due to insufficient funds. Please try a different card.';
        } else if (error.message.includes('expired_card')) {
          errorMessage = 'Your card has expired. Please use a different card.';
        } else if (error.message.includes('incorrect_cvc')) {
          errorMessage = 'The security code (CVC) you entered is incorrect. Please try again.';
        } else if (error.message.includes('subscription creation failed')) {
          errorMessage = 'We encountered an issue setting up your subscription. Your card was not charged. Please try again.';
        } else if (error.message.includes('Payment setup failed')) {
          errorMessage = 'There was an issue with your payment information. Please check your details and try again.';
        } else if (error.message.includes('authentication_required')) {
          errorMessage = 'Your bank requires additional authentication. Please try again or use a different card.';
        } else {
          errorMessage = error.message;
        }
      }
      
      alert(errorMessage);
    } finally {
      isLoading.value = false;
    }
  }
};
</script>

<style scoped>
.register-main {
  background-color: #377dff;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.card {
  background-color: white;
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
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

/* Auth0 Lock Registration Styles */
#auth0-register-lock-container >>> .auth0-lock-header-logo,
#auth0-register-lock-container >>> .auth0-lock-header-avatar,
#auth0-register-lock-container >>> .auth0-lock-header,
#auth0-register-lock-container >>> .auth0-lock-badge-bottom {
  display: none !important;
}

/* Hide login-related elements for registration */
#auth0-register-lock-container >>> .auth0-lock-alternative-link,
#auth0-register-lock-container >>> .auth0-lock-alternative,
#auth0-register-lock-container >>> [data-auth0-lock-action="login"],
#auth0-register-lock-container >>> .auth0-lock-tabs,
#auth0-register-lock-container >>> .auth0-lock-tab {
  display: none !important;
}

/* Customize signup button */
#auth0-register-lock-container >>> .auth0-lock-submit .auth0-lock-submit-label::before {
  display: none !important;
}

#auth0-register-lock-container >>> .auth0-lock-submit .auth0-lock-submit-label {
  background-image: none !important;
}

#auth0-register-lock-container >>> .auth0-lock-submit {
  background-image: none !important;
}

#auth0-register-lock-container >>> .auth0-lock-submit::before {
  display: none !important;
}

#auth0-register-lock-container >>> .auth0-lock {
  box-shadow: none !important;
  border: 1px solid #e7eaf3;
}

#auth0-register-lock-container >>> .auth0-lock-widget {
  box-shadow: none !important;
}

#auth0-register-lock-container >>> .auth0-lock-form {
  padding-top: 10px !important;
}

/* Password Requirements Styling */
.password-requirements {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.requirement-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.requirement-item {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.requirement-item.requirement-met {
  color: #198754;
}

.requirement-item:not(.requirement-met) {
  color: #6c757d;
}

.requirement-item i {
  width: 16px;
  height: 16px;
  font-size: 14px;
}

.password-requirements .fw-bold {
  font-weight: 600 !important;
}
</style> 