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
// import { useAuth0 } from '@auth0/auth0-vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
// Auth0 Vue plugin is temporarily disabled for debugging
// const { getAccessTokenSilently, user, isAuthenticated, isLoading, error: auth0Error } = useAuth0();
const authStore = useAuthStore();

// Mock the Auth0 values for now
const isLoading = ref(false);
const isAuthenticated = ref(false);
const user = ref(null);
const auth0Error = ref(null);

const error = ref(null);
const debug = ref(false);
const debugInfo = ref({});
const showSignupLink = ref(false);

onMounted(async () => {
  console.log('🚀 Auth0Callback component mounted');
  console.log('🚀 Current URL:', window.location.href);
  console.log('🚀 URL params:', window.location.search);
  
  // Wait for Auth0 to finish loading
  if (!isLoading.value) {
    console.log('🚀 Auth0 not loading, handling authentication immediately');
    await handleAuth0Authentication();
  } else {
    console.log('🚀 Auth0 is loading, waiting...');
    // Set up a watcher for isLoading
    const checkAuth = setInterval(() => {
      if (!isLoading.value) {
        console.log('🚀 Auth0 finished loading, handling authentication');
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
    const error = urlParams.get('error');
    const errorDescription = urlParams.get('error_description');
    
    // Check for Auth0 errors in URL parameters
    if (error) {
      throw new Error(`Auth0 Error: ${error} - ${errorDescription || 'Unknown error'}`);
    }
    
    // Verify state parameter for CSRF protection
    const storedState = sessionStorage.getItem('auth0_state');
    
    // Only validate state if we have both state in URL and stored state
    if (authCode && state && storedState) {
      if (state !== storedState) {
        console.error('❌ State parameter mismatch - possible CSRF attack');
        console.error('URL state:', state);
        console.error('Stored state:', storedState);
        sessionStorage.removeItem('auth0_state');
        sessionStorage.removeItem('auth0_nonce');
        throw new Error('Authentication failed: Invalid state parameter. Please try logging in again.');
      } else {
        console.log('✅ State parameter verified successfully');
        sessionStorage.removeItem('auth0_state');
        sessionStorage.removeItem('auth0_nonce');
      }
    } else if (authCode && !state && storedState) {
      // Auth0 didn't return a state, but we have one stored - might be an issue
      console.warn('⚠️ No state parameter in callback but expected one');
      sessionStorage.removeItem('auth0_state');
      sessionStorage.removeItem('auth0_nonce');
    } else if (authCode && !state && !storedState) {
      // No state validation needed - might be a direct Auth0 redirect
      console.log('ℹ️ No state parameter validation (direct Auth0 redirect)');
    }
    
    debugInfo.value = {
      isLoading: isLoading.value,
      isAuthenticated: isAuthenticated.value,
      hasUser: !!user.value,
      auth0Error: auth0Error.value,
      userEmail: user.value?.email,
      emailVerified: user.value?.email_verified,
      authCode: authCode ? `${authCode.substring(0, 10)}...` : null,
      hasState: !!state,
      hasStoredState: !!storedState,
      stateValid: state === storedState,
      timestamp: new Date().toISOString()
    };

    console.log('Auth0 Debug Info:', debugInfo.value);

    // Check for Auth0 errors from the SDK
    if (auth0Error.value) {
      throw new Error(`Auth0 Error: ${auth0Error.value.message || auth0Error.value}`);
    }

    // If we have an authorization code but Auth0 Vue plugin hasn't processed it yet
    if (authCode && !isAuthenticated.value) {
      console.log('🔄 Found authorization code, processing manually...');
      
      // Exchange authorization code via our backend (secure)
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      const callbackUrl = import.meta.env.VITE_AUTH0_CALLBACK_URL || 'http://localhost:3000/auth/callback';
      
      const tokenResponse = await fetch(`${apiUrl}/auth0/exchange-code/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: authCode,
          redirect_uri: callbackUrl
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

    // Skip Auth0 Vue plugin check since it's disabled
    // if (isAuthenticated.value && user.value) {
    //   console.log('User authenticated via Auth0 Vue plugin, getting access token...');
    //   
    //   // Get the access token
    //   const accessToken = await getAccessTokenSilently();
    //   console.log('Access token obtained, length:', accessToken?.length);
    //   
    //   // Exchange Auth0 token for our backend token
    //   console.log('Attempting backend token exchange...');
    //   const success = await authStore.loginWithAuth0(accessToken);
    //   
    //   if (success) {
    //     console.log('Backend token exchange successful');
    //     router.push('/dashboard');
    //   } else {
    //     throw new Error('Backend token exchange failed');
    //   }
    // } else 
    if (!authCode) {
      // No auth code means we might be coming back from Auth0 without proper params
      console.warn('⚠️ No authorization code in callback URL');
      console.log('URL params:', window.location.search);
      
      // Check if this is just a page refresh or direct access
      if (!window.location.search || window.location.search === '?') {
        console.log('Direct access to callback page, redirecting to login');
        router.push('/login');
        return;
      }
      
      throw new Error(`No authentication data found: isAuthenticated=${isAuthenticated.value}, hasUser=${!!user.value}, authCode=${!!authCode}`);
    }
  } catch (err) {
    console.error('❌ Error handling Auth0 authentication:', err);
    console.error('❌ Full error details:', {
      message: err.message,
      stack: err.stack,
      debugInfo: debugInfo.value
    });
    error.value = err.message || 'Authentication failed';
    
    // Show error for a few seconds, then redirect
    setTimeout(() => {
      router.push('/login');
    }, 5000);
  }
};
</script> 