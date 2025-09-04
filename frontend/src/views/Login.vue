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
                @click="loginWithGoogle"
              >
                <img src="/assets/svg/brands/google-icon.svg" class="me-2" width="20" alt="Google">
                Continue with Google
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                @click="loginWithFacebook"
              >
                <img src="/assets/svg/brands/facebook-icon.svg" class="me-2" width="20" alt="Facebook">
                Continue with Facebook
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-primary btn-lg d-flex justify-content-center align-items-center"
                @click="loginWithApple"
              >
                <img src="/assets/svg/brands/apple.svg.png" class="me-2" width="20" alt="Apple">
                Continue with Apple
              </button>
              
              <button 
                type="button" 
                class="btn btn-outline-secondary btn-lg"
                @click="loginWithEmail"
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
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { clearAuthData, initAuthState, storeAuthState } from '@/utils/authHelper';
import { API_CONFIG } from '@/config';
// Removed Auth0 Vue SDK import - using Django backend endpoints

const router = useRouter();
const authStore = useAuthStore();
// Removed Auth0 Vue SDK usage - using Django backend endpoints

const email = ref('');
const password = ref('');
const showLegacyLogin = ref(false); // Can be toggled based on environment or user role
// Removed embedded Auth0 Lock - using redirect approach

// Frontend Auth0 login - redirect to Auth0 from frontend, callback to frontend
const loginWithGoogle = () => {
  console.log('🔍 Starting Google login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = `${API_CONFIG.FRONTEND_URL}/auth/callback`;
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'openid profile email',
    connection: 'google-oauth2',
    state: 'login',
    prompt: 'login'
  });
  
  window.location.href = `https://${domain}/authorize?${params.toString()}`;
};


const loginWithEmail = () => {
  console.log('🔍 Starting email-only login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = `${API_CONFIG.FRONTEND_URL}/auth/callback`;
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'openid profile email',
    state: 'login',
    prompt: 'login',
    connection: 'Username-Password-Authentication',
    screen_hint: 'login',
    // Add custom branding parameters
    ui_locales: 'en',
    login_hint: '', // Could pre-fill email if needed
  });
  
  window.location.href = `https://${domain}/authorize?${params.toString()}`;
};

const loginWithFacebook = () => {
  console.log('🔵 Starting Facebook login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = `${API_CONFIG.FRONTEND_URL}/auth/callback`;
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'openid profile email',
    connection: 'facebook-oauth2',
    state: 'login',
    prompt: 'login'
  });
  
  window.location.href = `https://${domain}/authorize?${params.toString()}`;
};

const loginWithApple = () => {
  console.log('🔵 Starting Apple login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = `${API_CONFIG.FRONTEND_URL}/auth/callback`;
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'openid profile email',
    connection: 'apple',
    state: 'login',
    prompt: 'login'
  });
  
  window.location.href = `https://${domain}/authorize?${params.toString()}`;
};

const handleLegacyLogin = async () => {
  try {
    // Call traditional login endpoint directly for legacy users
    const response = await fetch(`${API_CONFIG.API_URL}/login/`, {
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
