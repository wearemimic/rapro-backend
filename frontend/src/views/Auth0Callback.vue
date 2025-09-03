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
          <router-link to="/register" class="btn btn-primary">Sign Up Now</router-link>
        </div>
      </div>
      <h3 v-if="!error">Processing your authentication...</h3>
      <p v-if="!error">Please wait while we log you in.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth0 } from '@auth0/auth0-vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const { handleRedirectCallback, getAccessTokenSilently, user, isAuthenticated, isLoading, error: auth0Error } = useAuth0();
const authStore = useAuthStore();

const error = ref(null);

onMounted(async () => {
  console.log('🚀 Auth0Callback component mounted');
  console.log('🚀 Current URL:', window.location.href);
  console.log('🚀 URL Search params:', window.location.search);
  console.log('🚀 URL Hash:', window.location.hash);
  
  try {
    // Check if we have Auth0 callback params
    const urlParams = new URLSearchParams(window.location.search);
    const hasCode = urlParams.has('code');
    const hasError = urlParams.has('error');
    const hasState = urlParams.has('state');
    
    console.log('🚀 URL Params analysis:', {
      hasCode,
      hasError,
      hasState,
      code: hasCode ? urlParams.get('code')?.substring(0, 10) + '...' : null,
      error: hasError ? urlParams.get('error') : null,
      state: hasState ? urlParams.get('state')?.substring(0, 10) + '...' : null,
      allParams: Object.fromEntries(urlParams.entries())
    });
    
    // Check Auth0 plugin state
    console.log('🚀 Auth0 Plugin State on mount:', {
      isLoading: isLoading.value,
      isAuthenticated: isAuthenticated.value,
      hasUser: !!user.value,
      auth0Error: auth0Error.value?.message || 'None'
    });
    
    if (hasError) {
      const errorMsg = urlParams.get('error');
      const errorDesc = urlParams.get('error_description');
      console.error('❌ Auth0 returned error in callback:', { errorMsg, errorDesc });
      throw new Error(`Auth0 Error: ${errorMsg} - ${errorDesc || 'Unknown error'}`);
    }
    
    // If we have code and state, try the Auth0 SDK callback handling first
    if (hasCode && hasState) {
      console.log('🔄 Attempting Auth0 SDK callback handling...');
      
      try {
        // Try the Auth0 SDK handleRedirectCallback
        const result = await handleRedirectCallback();
        console.log('🚀 Auth0 SDK callback processed successfully:', result);
        
        // Wait for Auth0 to update its state
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log('🔍 Auth0 state after SDK callback:', {
          isAuthenticated: isAuthenticated.value,
          isLoading: isLoading.value,
          hasUser: !!user.value,
          userEmail: user.value?.email || 'No user',
          auth0Error: auth0Error.value?.message || 'None'
        });
        
        if (isAuthenticated.value && user.value) {
          console.log('✅ Auth0 SDK authentication successful');
          
          // Get the Auth0 access token
          const accessToken = await getAccessTokenSilently();
          console.log('✅ Got Auth0 access token');
          
          // Exchange Auth0 token for our backend token
          console.log('🔄 Exchanging Auth0 token for backend token...');
          const success = await authStore.loginWithAuth0(accessToken);
          
          if (success) {
            console.log('✅ Backend authentication successful');
            const target = result?.appState?.target || '/dashboard';
            console.log(`✅ Redirecting to ${target}`);
            router.push(target);
            return;
          } else {
            console.error('❌ Backend authentication failed');
            throw new Error('Backend authentication failed');
          }
        } else {
          console.warn('⚠️ Auth0 SDK callback succeeded but user not authenticated');
          throw new Error('Auth0 callback succeeded but user not authenticated');
        }
      } catch (sdkError) {
        console.warn('⚠️ Auth0 SDK callback failed:', sdkError.message);
        
        // If the SDK fails due to state validation but we have valid code/state,
        // it might be a configuration issue. Try to proceed anyway.
        if (sdkError.message.includes('Invalid state')) {
          console.log('🔄 SDK failed due to state validation, but we have valid callback parameters');
          console.log('🔄 This usually means Auth0 configuration was changed mid-flight');
          console.log('🔄 Redirecting to login to start fresh...');
          
          // Clear any stale Auth0 state
          localStorage.removeItem('auth0_flow');
          
          // Redirect to login with a fresh start
          router.push('/login?error=state_mismatch');
          return;
        } else {
          // Re-throw other errors
          throw sdkError;
        }
      }
    }
    
    if (hasCode) {
      console.log('🚀 Processing Auth0 callback...');
      
      // Let Auth0 Vue plugin handle the callback
      const result = await handleRedirectCallback();
      console.log('🚀 Callback processed, result:', result);
      
      // Wait longer for Auth0 to update its state (increased from 500ms to 1000ms)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check if authenticated with more detailed logging
      console.log('🔍 Auth0 state after callback:', {
        isAuthenticated: isAuthenticated.value,
        isLoading: isLoading.value,
        hasUser: !!user.value,
        userEmail: user.value?.email,
        auth0Error: auth0Error.value
      });
      
      if (!isAuthenticated.value) {
        console.error('❌ Authentication failed - Auth0 state not authenticated');
        if (auth0Error.value) {
          throw new Error(`Auth0 Error: ${auth0Error.value.message}`);
        }
        throw new Error('Authentication failed - not authenticated after callback');
      }
      
      console.log('✅ User authenticated:', user.value?.email);
      
      // Get the Auth0 access token with retry logic
      let accessToken;
      let retries = 3;
      while (retries > 0) {
        try {
          accessToken = await getAccessTokenSilently();
          console.log('✅ Got Auth0 access token');
          break;
        } catch (tokenError) {
          retries--;
          console.warn(`⚠️ Failed to get access token, ${retries} retries left:`, tokenError.message);
          if (retries === 0) {
            throw new Error(`Failed to get Auth0 access token: ${tokenError.message}`);
          }
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }
      
      // Exchange Auth0 token for our backend token
      console.log('🔄 Exchanging Auth0 token for backend token...');
      const success = await authStore.loginWithAuth0(accessToken);
      
      if (success) {
        console.log('✅ Backend authentication successful');
        
        // Check if we came from registration or login
        const flow = localStorage.getItem('auth0_flow') || 'login';
        localStorage.removeItem('auth0_flow');
        
        // Get the target from appState if available
        const target = result?.appState?.target || '/dashboard';
        
        console.log(`✅ Redirecting to ${target} after ${flow}`);
        router.push(target);
      } else {
        console.error('❌ Backend authentication failed - check auth store logs');
        throw new Error('Backend authentication failed - please check the console for details');
      }
    } else {
      // No callback params - shouldn't happen
      console.warn('⚠️ No callback parameters found');
      router.push('/login');
    }
  } catch (err) {
    console.error('❌ Error in Auth0 callback:', err);
    error.value = err.message || 'Authentication failed';
    
    // Redirect to login after showing error
    setTimeout(() => {
      router.push('/login');
    }, 3000);
  }
});
</script>