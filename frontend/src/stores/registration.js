import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import { API_CONFIG } from '@/config';
import { getValidAffiliateCode } from '@/utils/affiliateTracking';

export const useRegistrationStore = defineStore('registration', () => {
  const registrationData = ref({
    // Step 1: Account Details
    email: '',
    password: '',
    
    // Step 2: Professional Info
    firstName: '',
    lastName: '',
    companyName: '',
    phoneNumber: '',
    licenses: '',
    website: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
  });

  const isLoading = ref(false);
  const error = ref(null);
  const currentStep = ref(1);
  const authStore = useAuthStore();

  const registerStep1 = async (data) => {
    registrationData.value = {
      ...registrationData.value,
      email: data.email,
      password: data.password,
    };
    currentStep.value = 2;
  };

  const registerStep2 = async (data) => {
    try {
      isLoading.value = true;
      error.value = null;

      // Check for affiliate code (uses utility to validate 30-day window)
      const affiliateCode = getValidAffiliateCode();

      // Combine step 1 and step 2 data
      const fullData = {
        email: registrationData.value.email,
        password: registrationData.value.password,
        first_name: data.firstName,
        last_name: data.lastName,
        company_name: data.companyName,
        phone_number: data.phoneNumber,
        licenses: data.licenses,
        website_url: data.website,
        address: data.address,
        city: data.city,
        state: data.state,
        zip_code: data.zipCode,
      };

      // Add affiliate code if present
      if (affiliateCode) {
        fullData.affiliate_code = affiliateCode;
        console.log('📊 Including affiliate code in registration:', affiliateCode);
      }

      // Send registration request to backend
      const response = await fetch(`${API_CONFIG.API_URL}/register-advisor/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fullData),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.message || 'Registration failed');
      }

      // Store tokens and user data
      await authStore.setTokens(responseData.tokens);
      await authStore.setUser(responseData.user);

      // Move to payment step
      currentStep.value = 3;
      return responseData;

    } catch (err) {
      error.value = err.message || 'An error occurred during registration';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const reset = () => {
    registrationData.value = {
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      companyName: '',
      phoneNumber: '',
      licenses: '',
      website: '',
      address: '',
      city: '',
      state: '',
      zipCode: '',
    };
    currentStep.value = 1;
    error.value = null;
  };

  return {
    registrationData,
    isLoading,
    error,
    currentStep,
    registerStep1,
    registerStep2,
    reset,
  };
}); 