<template>
  <div class="container py-5">
    <h1>Auth0 Callback Debug</h1>
    <div class="alert alert-info">
      <strong>Current URL:</strong> {{ currentUrl }}
    </div>
    
    <div class="alert alert-warning">
      <strong>URL Search Params:</strong>
      <pre>{{ urlSearchParams }}</pre>
    </div>
    
    <div class="alert alert-secondary">
      <strong>URL Hash:</strong> {{ urlHash }}
    </div>
    
    <div class="alert alert-primary">
      <strong>localStorage Auth Flow:</strong> {{ authFlow }}
    </div>
    
    <div class="alert alert-success">
      <strong>Auth0 Plugin State:</strong>
      <pre>{{ auth0State }}</pre>
    </div>
    
    <button @click="manualHandleCallback" class="btn btn-primary me-2">
      Manual Handle Callback
    </button>
    
    <button @click="forceRedirectToLogin" class="btn btn-secondary">
      Force Redirect to Login
    </button>
    
    <div v-if="debugLog.length > 0" class="mt-4">
      <h3>Debug Log:</h3>
      <div class="alert alert-light">
        <pre>{{ debugLog.join('\n') }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const { handleRedirectCallback, getAccessTokenSilently, user, isAuthenticated, isLoading, error: auth0Error } = useAuth0();

const currentUrl = ref(window.location.href);
const urlSearchParams = ref({});
const urlHash = ref(window.location.hash);
const authFlow = ref('');
const auth0State = ref({});
const debugLog = ref([]);

const addLog = (message) => {
  debugLog.value.push(`${new Date().toISOString()}: ${message}`);
};

onMounted(() => {
  addLog('CallbackDebug component mounted');
  
  // Parse URL params
  const params = new URLSearchParams(window.location.search);
  urlSearchParams.value = Object.fromEntries(params.entries());
  
  // Get auth flow from localStorage
  authFlow.value = localStorage.getItem('auth0_flow') || 'Not set';
  
  // Get Auth0 state
  auth0State.value = {
    isLoading: isLoading.value,
    isAuthenticated: isAuthenticated.value,
    hasUser: !!user.value,
    userEmail: user.value?.email || 'No user',
    error: auth0Error.value?.message || 'No error'
  };
  
  addLog(`URL has code: ${params.has('code')}`);
  addLog(`URL has state: ${params.has('state')}`);
  addLog(`URL has error: ${params.has('error')}`);
});

const manualHandleCallback = async () => {
  addLog('Starting manual callback handling...');
  
  try {
    const result = await handleRedirectCallback();
    addLog(`Callback result: ${JSON.stringify(result)}`);
    
    // Wait for Auth0 to update
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    addLog(`Auth0 state after callback: isAuthenticated=${isAuthenticated.value}, hasUser=${!!user.value}`);
    
    if (isAuthenticated.value) {
      const accessToken = await getAccessTokenSilently();
      addLog('Got access token from Auth0');
      
      const success = await authStore.loginWithAuth0(accessToken);
      addLog(`Backend login success: ${success}`);
      
      if (success) {
        addLog('Redirecting to dashboard...');
        router.push('/dashboard');
      }
    } else {
      addLog('Not authenticated after callback');
    }
  } catch (error) {
    addLog(`Error: ${error.message}`);
  }
};

const forceRedirectToLogin = () => {
  addLog('Forcing redirect to login...');
  router.push('/login');
};
</script>