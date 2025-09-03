<template>
  <main id="content" role="main" class="main login-main">
    <div class="container py-5 py-sm-7">
      <div class="mx-auto" style="max-width: 30rem;">
        <div class="text-center mb-4">
          <img src="/assets/img/RAD-white-logo.png" style="height:50px;margin-bottom:20px;" alt="Logo">
        </div>
        <div class="card card-lg mb-5">
          <div class="card-body text-center">
            <div v-if="loading" class="mb-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <h3 class="mt-3">Completing Authentication...</h3>
              <p class="text-muted">Please wait while we sign you in.</p>
            </div>
            
            <div v-else-if="error" class="mb-4">
              <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Authentication Error</h4>
                <p>{{ error }}</p>
                <hr>
                <p class="mb-0">
                  <a href="/login" class="btn btn-outline-danger">Back to Login</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(true);
const error = ref('');

onMounted(async () => {
  try {
    // Get tokens from URL parameters (Django will pass them)
    const urlParams = new URLSearchParams(window.location.search);
    const access = urlParams.get('access_token');
    const refresh = urlParams.get('refresh_token');
    const userParam = urlParams.get('user');
    
    if (!access || !refresh) {
      throw new Error('Missing authentication tokens');
    }
    
    // Parse user data if provided
    let user = null;
    if (userParam) {
      try {
        user = JSON.parse(decodeURIComponent(userParam));
      } catch (e) {
        console.warn('Could not parse user data:', e);
      }
    }
    
    // Store tokens and user in auth store
    authStore.setTokens({ access, refresh });
    if (user) {
      authStore.setUser(user);
    }
    
    // Clear URL parameters for security
    window.history.replaceState({}, document.title, window.location.pathname);
    
    // Redirect to dashboard
    router.push('/dashboard');
    
  } catch (err) {
    console.error('Auth0 success handling error:', err);
    error.value = err.message || 'Authentication failed';
    loading.value = false;
  }
});
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