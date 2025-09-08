<template>
  <div class="d-flex justify-content-center align-items-center" style="height: 100vh;">
    <div class="text-center">
      <div v-if="!error" class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <div v-if="error" class="alert alert-danger mb-3" role="alert">
        <h4 class="alert-heading">Authentication Error</h4>
        <p>{{ error }}</p>
        <hr>
        <router-link to="/login" class="btn btn-secondary">Back to Login</router-link>
      </div>
      <h3 v-if="!error">Processing your authentication...</h3>
      <p v-if="!error">Please wait while we log you in.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
// Removed Auth0 Vue SDK - using Django server-side auth
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
// Removed Auth0 Vue SDK usage - Django handles auth completely
const authStore = useAuthStore();

const error = ref(null);

onMounted(async () => {
  try {
    console.log('Processing Auth0 callback with authorization code...');
    
    // Check for error in URL params first
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('error')) {
      throw new Error(`Auth0 Error: ${urlParams.get('error')} - ${urlParams.get('error_description')}`);
    }
    
    // Get authorization code from URL
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    
    if (!code) {
      throw new Error('No authorization code received from Auth0');
    }
    
    // Detect if this is a registration flow
    console.log('🔍 All localStorage items in callback:', Object.keys(localStorage));
    console.log('🔍 auth0_flow value in callback:', localStorage.getItem('auth0_flow'));
    const isRegistrationFlow = localStorage.getItem('auth0_flow') === 'registration';
    console.log(`Flow type detected: ${isRegistrationFlow ? 'registration' : 'login'}`);
    
    console.log('Got authorization code, sending to Django backend for token exchange...');
    
    // Send authorization code to Django for token exchange
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth0/exchange-code/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code,
        state: state,
        flow_type: isRegistrationFlow ? 'registration' : 'login'  // Tell backend the flow type
      })
    });

    const data = await response.json();
    
    // Handle payment required (402) status for registration
    if (response.status === 402) {
      console.log('🔄 Registration required for this user');
      
      if (isRegistrationFlow) {
        // User wanted to register, continue with registration
        console.log('✅ Continuing registration flow');
        
        // Store the Auth0 user info temporarily for registration completion
        sessionStorage.setItem('auth0_user_info', JSON.stringify({
          email: data.email,
          firstName: data.first_name,
          lastName: data.last_name,
          auth0_sub: data.auth0_sub
        }));
        
        // Clear the flow flag and redirect to registration step 2
        localStorage.removeItem('auth0_flow');
        router.push('/register?step=2');
      } else {
        // User tried to login but needs to complete registration
        console.log('❌ User tried to login but has no active subscription');
        localStorage.removeItem('auth0_flow');
        
        // Show error and redirect to login
        error.value = 'You need to complete your registration first. Please use the Register button.';
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      }
      return;
    }
    
    if (response.ok) {
      // Store tokens from Django
      authStore.setTokens({
        access: data.access,
        refresh: data.refresh
      });
      
      // Store user data
      if (data.user) {
        authStore.setUser(data.user);
      }
      
      console.log('✅ Django token exchange successful');
      
      // Handle different flows
      if (isRegistrationFlow) {
        console.log('🔄 Registration flow detected');
        
        // Check if this is an existing user trying to register again
        if (data.already_registered) {
          console.log('⚠️ Existing user with active subscription tried to register');
          localStorage.removeItem('auth0_flow');
          alert('You already have an account. You have been logged in.');
          router.push('/dashboard');
        } else if (data.registration_complete === false) {
          console.log('🔄 Registration incomplete, redirecting to step 2');
          localStorage.removeItem('auth0_flow');
          router.push('/register?step=2');
        } else if (data.is_new_user) {
          console.log('🔄 New user, redirecting to step 2');
          localStorage.removeItem('auth0_flow');
          router.push('/register?step=2');
        } else {
          console.log('✅ Registration complete, redirecting to dashboard');
          localStorage.removeItem('auth0_flow');
          router.push('/dashboard');
        }
      } else {
        console.log('✅ Login flow, redirecting to dashboard');
        router.push('/dashboard');
      }
    } else {
      throw new Error(data.message || 'Django token exchange failed');
    }
    
  } catch (err) {
    console.error('Auth0 callback error:', err);
    error.value = err.message || 'Authentication failed';
    
    // Clean up registration flow flag on error
    localStorage.removeItem('auth0_flow');
    
    // Redirect based on original intent
    const isRegistrationFlow = localStorage.getItem('auth0_flow') === 'registration';
    setTimeout(() => {
      router.push(isRegistrationFlow ? '/register' : '/login');
    }, 3000);
  }
});
</script>