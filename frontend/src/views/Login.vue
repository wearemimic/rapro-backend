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
                @click="showEmbeddedEmailLogin"
              >
                Continue with Email
              </button>
            </div>
            
            <!-- Embedded Auth0 Email Login -->
            <div v-if="showEmailLogin" class="mt-4 p-4 border rounded">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">Sign in with Email</h5>
                <button type="button" class="btn-close" @click="showEmailLogin = false"></button>
              </div>
              <div class="text-center mb-3">
                <div class="btn-group" role="group">
                  <input type="radio" class="btn-check" name="authMode" id="loginMode" v-model="authMode" value="login" autocomplete="off">
                  <label class="btn btn-outline-primary" for="loginMode">Sign In</label>
                  
                  <input type="radio" class="btn-check" name="authMode" id="registerMode" v-model="authMode" value="register" autocomplete="off">
                  <label class="btn btn-outline-primary" for="registerMode">Sign Up</label>
                </div>
              </div>
              <div id="auth0-lock-container"></div>
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

<style scoped>
/* Hide Auth0 branding and customize embedded login */
#auth0-lock-container >>> .auth0-lock-header-logo,
#auth0-lock-container >>> .auth0-lock-header-avatar,
#auth0-lock-container >>> .auth0-lock-header,
#auth0-lock-container >>> .auth0-lock-badge-bottom {
  display: none !important;
}

/* Hide signup-related elements */
#auth0-lock-container >>> .auth0-lock-sign-up-terms,
#auth0-lock-container >>> .auth0-lock-alternative-link,
#auth0-lock-container >>> .auth0-lock-alternative,
#auth0-lock-container >>> [data-auth0-lock-action="sign-up"],
#auth0-lock-container >>> .auth0-lock-tabs,
#auth0-lock-container >>> .auth0-lock-tab {
  display: none !important;
}

/* Customize login button - remove icon and set text */
#auth0-lock-container >>> .auth0-lock-submit .auth0-lock-submit-label::before {
  display: none !important;  /* Hide any icon */
}

#auth0-lock-container >>> .auth0-lock-submit .auth0-lock-submit-label {
  background-image: none !important;  /* Remove background icon */
}

#auth0-lock-container >>> .auth0-lock-submit {
  background-image: none !important;  /* Remove button icon */
}

#auth0-lock-container >>> .auth0-lock-submit::before {
  display: none !important;  /* Hide pseudo-element icons */
}

#auth0-lock-container >>> .auth0-lock {
  box-shadow: none !important;
  border: 1px solid #e7eaf3;
}

#auth0-lock-container >>> .auth0-lock-widget {
  box-shadow: none !important;
}

#auth0-lock-container >>> .auth0-lock-form {
  padding-top: 10px !important;
}
</style>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { clearAuthData, initAuthState, storeAuthState } from '@/utils/authHelper';
// Removed Auth0 Vue SDK import - using Django backend endpoints

const router = useRouter();
const authStore = useAuthStore();
// Removed Auth0 Vue SDK usage - using Django backend endpoints

const email = ref('');
const password = ref('');
const showLegacyLogin = ref(false); // Can be toggled based on environment or user role
const showEmailLogin = ref(false);
const authMode = ref('login'); // 'login' or 'register'
let auth0Lock = null;

// Frontend Auth0 login - redirect to Auth0 from frontend, callback to frontend
const loginWithGoogle = () => {
  console.log('🔍 Starting Google login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = 'http://localhost:3000/auth/callback';
  
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

const showEmbeddedEmailLogin = () => {
  // Set login flow in localStorage (will be updated based on authMode)
  localStorage.setItem('auth0_flow', 'login');
  showEmailLogin.value = true;
  
  // Dynamically load Auth0 Lock if not already loaded
  if (!window.Auth0Lock) {
    const script = document.createElement('script');
    script.src = 'https://cdn.auth0.com/js/lock/11.32.2/lock.min.js';
    script.onload = initAuth0Lock;
    document.head.appendChild(script);
  } else {
    initAuth0Lock();
  }
};

const initAuth0Lock = () => {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  
  // Update localStorage based on current authMode
  localStorage.setItem('auth0_flow', authMode.value === 'register' ? 'registration' : 'login');
  
  const isRegistrationMode = authMode.value === 'register';
  
  auth0Lock = new window.Auth0Lock(clientId, domain, {
    container: 'auth0-lock-container',
    auth: {
      redirectUrl: 'http://localhost:3000/auth/callback',
      responseType: 'code',
      params: {
        scope: 'openid profile email',
        state: isRegistrationMode ? 'registration' : 'login'
      }
    },
    allowedConnections: ['Username-Password-Authentication'],
    socialButtonStyle: 'small',
    allowSignUp: isRegistrationMode,  // Enable signup for registration mode
    allowForgotPassword: !isRegistrationMode,  // Hide forgot password for registration
    initialScreen: isRegistrationMode ? 'signUp' : 'login',  // Set initial screen based on mode
    languageDictionary: {
      title: '',
      signUpTerms: '',  // Hide signup terms
      databaseAlternativeSignUpInstructions: '',  // Hide signup instructions
      loginSubmitLabel: isRegistrationMode ? 'Sign Up' : 'Sign In',
      signUpSubmitLabel: 'Sign Up',
      loginLabel: isRegistrationMode ? 'Sign Up' : 'Sign In'
    },
    theme: {
      primaryColor: '#377dff',
      logo: '',  // Hide Auth0 logo
      labeledSubmitButton: false
    },
    avatar: null,
    closable: false,
    focusInput: true,
    gravatar: false,
    usernameStyle: 'email'
  });
  
  auth0Lock.on('authenticated', (authResult) => {
    console.log('Auth0 Lock authentication successful:', authResult);
    // The callback will be handled by our existing Auth0CallbackSimple.vue
    const stateParam = isRegistrationMode ? 'registration' : 'login';
    window.location.href = `http://localhost:3000/auth/callback?code=${authResult.accessToken}&state=${stateParam}`;
  });
  
  auth0Lock.show();
};

const loginWithEmail = () => {
  // Fallback to redirect method if embedded fails
  console.log('🔍 Starting email-only login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = 'http://localhost:3000/auth/callback';
  
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: callbackUrl,
    scope: 'openid profile email',
    state: 'login',
    prompt: 'login',
    connection: 'Username-Password-Authentication',
    screen_hint: 'login'
  });
  
  window.location.href = `https://${domain}/authorize?${params.toString()}`;
};

const loginWithFacebook = () => {
  console.log('🔵 Starting Facebook login from frontend');
  // Set login flow in localStorage
  localStorage.setItem('auth0_flow', 'login');
  
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const callbackUrl = 'http://localhost:3000/auth/callback';
  
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
  const callbackUrl = 'http://localhost:3000/auth/callback';
  
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
