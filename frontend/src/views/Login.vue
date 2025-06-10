<template>
  <main id="content" role="main" class="main">
    <div class="container py-5 py-sm-7">
      <div class="mx-auto" style="max-width: 30rem;">
        <!-- Card -->
        <div class="text-center mb-4">
          <img src="/assets/img/logo.png" style="height:50px;margin-bottom:20px;" alt="Logo">
        </div>
        <div class="card card-lg mb-5">
          <div class="card-body">
            <!-- Form -->
            <form @submit.prevent="handleLogin()">
              <div class="text-center">
                <div class="mb-5">
                  <h1 class="display-5">Sign in</h1>
                  <p>Don't have an account yet? <a href="/register">Sign up here</a></p>
                </div>
              </div>

              <!-- Form Group -->
              <div class="mb-4">
                <label class="form-label" for="email">Your email</label>
                <input type="email" class="form-control form-control-lg" v-model="email" required>
              </div>
              <!-- End Form Group -->

              <!-- Form Group -->
              <div class="mb-4">
                <label class="form-label" for="password">Password</label>
                <input type="password" class="form-control form-control-lg" v-model="password" required>
              </div>
              <!-- End Form Group -->

              <!-- Checkbox -->
              <div class="d-flex justify-content-between align-items-center mb-4">
                <div class="form-check">
                  <input type="checkbox" class="form-check-input" id="rememberMe">
                  <label class="form-check-label" for="rememberMe">Remember me</label>
                </div>
              </div>
              <!-- End Checkbox -->

              <div class="d-grid">
                <button type="submit" class="btn btn-primary btn-lg">Sign in</button>
              </div>
            </form>
            <!-- End Form -->
          </div>
        </div>
        <!-- End Card -->
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');

const handleLogin = async () => {
  try {
    const success = await authStore.login({ email: email.value, password: password.value });
    if (success) {
      router.push('/dashboard');
    } else {
      alert('Login failed. Please check your credentials.');
    }
  } catch (error) {
    console.error('Login error:', error);
    alert('An error occurred during login.');
  }
};
</script>

<style scoped>
.main {
  background-color: #f9fafb;
  min-height: 100vh;
  display: flex;
  align-items: center;
}
</style>
