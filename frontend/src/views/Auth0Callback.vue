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
        <div class="d-flex gap-2">
          <router-link to="/login" class="btn btn-secondary">Back to Login</router-link>
          <router-link v-if="showSignupLink" to="/register" class="btn btn-primary">Sign Up Now</router-link>
        </div>
      </div>
      <h3 v-if="!error">Processing your authentication...</h3>
      <p v-if="!error">Please wait while we log you in.</p>
      <div v-if="debug" class="mt-4 text-start">
        <h5>Debug Information:</h5>
        <pre>{{ debugInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth0 } from '@auth0/auth0-vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const { getAccessTokenSilently, user, isAuthenticated, isLoading, error: auth0Error } = useAuth0();
const authStore = useAuthStore();

const error = ref(null);
const debug = ref(false);
const debugInfo = ref({});
const showSignupLink = ref(false);

onMounted(async () => {
  // Wait for Auth0 to finish loading
  if (!isLoading.value) {
    await handleAuth0Authentication();
  } else {
    // Set up a watcher for isLoading
    const checkAuth = setInterval(() => {
      if (!isLoading.value) {
        handleAuth0Authentication();
        clearInterval(checkAuth);
      }
    }, 100);
  }
});

const handleAuth0Authentication = async () => {
  try {
    // Enable debug mode in development
    debug.value = import.meta.env.MODE === 'development';
    
    // Check if we have an authorization code in the URL (from direct Auth0 redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const authCode = urlParams.get('code');
    const state = urlParams.get('state');
    
    debugInfo.value = {
      isLoading: isLoading.value,
      isAuthenticated: isAuthenticated.value,
      hasUser: !!user.value,
      auth0Error: auth0Error.value,
      userEmail: user.value?.email,
      emailVerified: user.value?.email_verified,
      authCode: authCode ? `${authCode.substring(0, 10)}...` : null,
      hasState: !!state,
      timestamp: new Date().toISOString()
    };

    console.log('Auth0 Debug Info:', debugInfo.value);

    // Check for Auth0 errors first
    if (auth0Error.value) {
      throw new Error(`Auth0 Error: ${auth0Error.value.message || auth0Error.value}`);
    }

    // If we have an authorization code but Auth0 Vue plugin hasn't processed it yet
    if (authCode && !isAuthenticated.value) {
      console.log('🔄 Found authorization code, processing manually...');
      
      // Exchange authorization code via our backend (secure)
      const tokenResponse = await fetch(`http://localhost:8000/api/auth0/exchange-code/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: authCode,
          redirect_uri: 'http://localhost:3000/auth/callback'
        })
      });
      
      const result = await tokenResponse.json();
      console.log('🔍 Token exchange response status:', tokenResponse.status);
      console.log('🔍 Response.ok:', tokenResponse.ok);
      console.log('🔍 Backend response:', result);
      
      // Handle 202 status (registration incomplete) first, before checking response.ok
      if (tokenResponse.status === 202 && result.code === 'REGISTRATION_INCOMPLETE') {
        console.log('🔄 User authenticated but registration incomplete (202 response)');
        
        // Redirect to complete registration regardless of original flow
        localStorage.setItem('auth0_flow', 'registration');
        router.push('/register?step=2');
        return;
      }
      
      if (!tokenResponse.ok) {
        console.log('❌ Token exchange failed with status:', tokenResponse.status);
        throw new Error(`Token exchange failed: ${tokenResponse.status} - ${result.message || 'Unknown error'}`);
      }
      
      console.log('✅ Token exchange successful via backend');
      
      // Backend should return our JWT tokens directly
      if (result.access && result.user) {
        authStore.setTokens({ access: result.access, refresh: result.refresh });
        authStore.setUser(result.user);
        console.log('✅ User logged in successfully');
        
        // Check if this was a registration flow
        const isRegistration = localStorage.getItem('auth0_flow') === 'registration';
        localStorage.removeItem('auth0_flow');
        
        if (isRegistration) {
          console.log('🔄 Registration flow detected, redirecting to registration step 2');
          router.push('/register?step=2');
        } else {
          console.log('🔄 Login flow detected, redirecting to dashboard');
          router.push('/dashboard');
        }
        return;
      } else {
        console.error('❌ Unexpected response format:', result);
        console.error('❌ Missing access token:', !result.access);
        console.error('❌ Missing user:', !result.user);
        throw new Error(`Invalid response from backend token exchange. Response: ${JSON.stringify(result)}`);
      }
    }

    // Check if user is authenticated with Auth0 Vue plugin
    if (isAuthenticated.value && user.value) {
      console.log('User authenticated via Auth0 Vue plugin, getting access token...');
      
      // Get the access token
      const accessToken = await getAccessTokenSilently();
      console.log('Access token obtained, length:', accessToken?.length);
      
      // Exchange Auth0 token for our backend token
      console.log('Attempting backend token exchange...');
      const success = await authStore.loginWithAuth0(accessToken);
      
      if (success) {
        console.log('Backend token exchange successful');
        router.push('/dashboard');
      } else {
        throw new Error('Backend token exchange failed');
      }
    } else if (!authCode) {
      throw new Error(`No authentication data found: isAuthenticated=${isAuthenticated.value}, hasUser=${!!user.value}, authCode=${!!authCode}`);
    }
  } catch (err) {
    console.error('Error handling Auth0 authentication:', err);
    error.value = err.message || 'Authentication failed';
    
    // Show error for a few seconds, then redirect
    setTimeout(() => {
      router.push('/login');
    }, 5000);
  }
};
</script> 