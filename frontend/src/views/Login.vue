<template>
  <main id="content" role="main" class="main login-main">
    <div class="container py-5 py-sm-7">
      <div class="mx-auto" style="max-width: 30rem;">
        <!-- Card -->
        <div class="text-center mb-4">
          <img src="/assets/img/RAD-white-logo.png" style="height:50px;margin-bottom:20px;" alt="Logo">
        </div>
        <div class="card card-lg mb-5">
          <div class="card-body">
            <div class="text-center">
              <div class="mb-5">
                <h1 class="display-5">Sign in</h1>
                <p>Don't have an account yet? <a href="/register">Sign up here</a></p>
              </div>
            </div>
           
            
            <!-- Primary Auth0 Login Buttons -->
            <div class="d-grid gap-2 mb-4">
              <button 
                type="button" 
                class="btn btn-primary btn-lg d-flex justify-content-center align-items-center"
                @click="() => { console.log('🔵 Google button clicked'); loginWithAuth0('google'); }"
                style="cursor: pointer; pointer-events: auto;"
              >
                <img src="/assets/svg/brands/google-icon.svg" class="me-2" width="20" alt="Google">
                Continue with Google
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                @click="() => { console.log('🔵 Facebook button clicked'); loginWithAuth0('facebook-oauth2'); }"
              >
                <img src="/assets/svg/brands/facebook-icon.svg" class="me-2" width="20" alt="Facebook">
                Continue with Facebook
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                @click="() => { console.log('🔵 Apple button clicked'); loginWithAuth0('apple'); }"
              >
                <img src="/assets/svg/brands/apple.svg.png" class="me-2" width="20" alt="Apple">
                Continue with Apple
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-secondary btn-lg"
                @click="() => { console.log('🔵 Email button clicked'); loginWithAuth0(); }"
              >
                Continue with Email
              </button>
            </div>
            
            <!-- Legacy Login Form (Collapsed) -->
            <div class="text-center">
              <button 
                type="button" 
                class="btn btn-link btn-sm text-muted"
                data-bs-toggle="collapse" 
                data-bs-target="#legacyLogin"
                v-if="showLegacyLogin"
              >
                Use legacy login instead
              </button>
            </div>
            
            <div class="collapse" id="legacyLogin">
              <div class="border-top pt-4 mt-3">
                <div class="alert alert-warning" role="alert">
                  <strong>Note:</strong> Legacy email/password login is deprecated. Please use one of the options above for better security.
                </div>
                
                <form @submit.prevent="handleLegacyLogin()">
                  <!-- Form Group -->
                  <div class="mb-3">
                    <label class="form-label" for="email">Your email</label>
                    <input type="email" class="form-control" v-model="email" required>
                  </div>
                  
                  <!-- Form Group -->
                  <div class="mb-3">
                    <label class="form-label" for="password">Password</label>
                    <input type="password" class="form-control" v-model="password" required>
                  </div>
                  
                  <div class="d-grid">
                    <button type="submit" class="btn btn-outline-secondary">Sign in with Legacy Account</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
        <!-- End Card -->
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useAuth0 } from '@auth0/auth0-vue';

const router = useRouter();
const authStore = useAuthStore();
const { loginWithRedirect, getAccessTokenSilently, user, isAuthenticated, isLoading } = useAuth0();

const email = ref('');
const password = ref('');
const showLegacyLogin = ref(false); // Can be toggled based on environment or user role

onMounted(async () => {
  console.log('🔧 Login component mounted');
  console.log('🔧 Auth0 state:', {
    isLoading: isLoading.value,
    isAuthenticated: isAuthenticated.value,
    hasUser: !!user.value,
    loginWithRedirect: !!loginWithRedirect
  });
  
  // Check if user is authenticated with Auth0
  if (isAuthenticated.value && user.value) {
    try {
      // Get the access token
      const accessToken = await getAccessTokenSilently();
      
      // Exchange Auth0 token for our backend token
      const success = await authStore.loginWithAuth0(accessToken);
      
      if (success) {
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Error handling Auth0 authentication:', error);
    }
  }
});

const handleLegacyLogin = async () => {
  try {
    // Call traditional login endpoint directly for legacy users
    const response = await fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    });

    if (response.ok) {
      const data = await response.json();
      authStore.setTokens({ access: data.access, refresh: data.refresh });
      authStore.setUser(data.user);
      router.push('/dashboard');
    } else {
      alert('Login failed. Please check your credentials.');
    }
  } catch (error) {
    console.error('Legacy login error:', error);
    alert('An error occurred during login.');
  }
};

const testAuth0Direct = () => {
  console.log('🔬 Testing Auth0 direct redirect...');
  
  const authUrl = `https://genai-030069804226358743.us.auth0.com/authorize?` +
    `client_id=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw&` +
    `response_type=code&` +
    `redirect_uri=http://localhost:3000/auth/callback&` +
    `scope=openid profile email&` +
    `connection=google-oauth2`;
  
  console.log('🔬 Redirecting to:', authUrl);
  window.location.href = authUrl;
};

const loginWithAuth0 = async (connection) => {
  console.log('🔵 loginWithAuth0 called with connection:', connection);
  
  try {
    // Store that this is a login flow (not registration)
    localStorage.setItem('auth0_flow', 'login');
    console.log('🔄 Set auth0_flow to login');
    
    // For now, use the direct method since Auth0 Vue plugin has issues
    console.log('🔄 Using direct Auth0 redirect method...');
    
    // Map common connection names to Auth0 connection names
    const connectionMap = {
      'google': 'google-oauth2',
      'facebook': 'facebook',
      'apple': 'apple'
    };
    
    const actualConnection = connectionMap[connection] || connection;
    console.log(`🔵 Using connection: ${connection} -> ${actualConnection}`);
    
    let authUrl = `https://genai-030069804226358743.us.auth0.com/authorize?` +
      `client_id=MS2O3usgLl8btDkPNwO6i0ZzC4LxR0Jw&` +
      `response_type=code&` +
      `redirect_uri=http://localhost:3000/auth/callback&` +
      `scope=openid profile email`;
    
    // Add connection if specified
    if (actualConnection) {
      authUrl += `&connection=${actualConnection}`;
    } else {
      // For email login, we need to show the Auth0 login page
      // Adding prompt=login forces Auth0 to show the login screen
      authUrl += `&prompt=login`;
    }
    
    console.log('🔵 Redirecting to:', authUrl);
    window.location.href = authUrl;
    
  } catch (error) {
    console.error('❌ Auth0 login error:', error);
    alert(`Auth0 login failed: ${error.message}`);
  }
};
</script>

<style scoped>
.login-main {
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
</style>
