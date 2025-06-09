<template>
  <header id="header" class="navbar navbar-expand-lg navbar-fixed navbar-height navbar-container navbar-bordered" style="background-color:#377dff;">
    <div class="navbar-nav-wrap">
      <!-- Logo -->
      <a class="navbar-brand" href="#">
        <img style="height:30px;margin-left:30px;" src="/assets/img/logo.png" alt="Logo">
      </a>
      <!-- End Logo -->

      <div class="navbar-nav-wrap-content-end">
        <!-- Navbar -->
        <ul class="navbar-nav">
          <!-- Notifications -->
          <li class="nav-item dropdown">
            <a class="btn btn-ghost-secondary btn-icon" href="#" id="navbarNotificationsDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi-bell"></i>
              <span class="btn-status btn-sm-status btn-status-danger"></span>
            </a>
            <div class="dropdown-menu dropdown-menu-end navbar-dropdown-menu navbar-dropdown-menu-borderless" aria-labelledby="navbarNotificationsDropdown">
              <div class="dropdown-header d-flex align-items-center">
                <h5 class="dropdown-header-title mb-0">Notifications</h5>
              </div>
              <div class="dropdown-item">
                <span class="text-body">You have 3 new messages</span>
              </div>
            </div>
          </li>
          <!-- End Notifications -->

          <!-- User Profile -->
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarUserDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <img class="avatar avatar-sm avatar-circle" src="/assets/img/160x160/img1.jpg" alt="User">
              <span class="d-none d-sm-inline-block">John Doe</span>
            </a>
            <ul class="dropdown-menu" aria-labelledby="navbarUserDropdown">
              <li><a class="dropdown-item" href="./profile">Profile</a></li>
              <li><a class="dropdown-item" href="#">Settings</a></li>
              <li><hr class="dropdown-divider"></li>
              <li><button class="dropdown-item" @click="logout">Logout</button></li>
            </ul>
          </li>
          <!-- End User Profile -->
        </ul>
        <!-- End Navbar -->
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Header'
};
</script>
<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { toast } from 'vue3-toastify'; // or whatever toast lib you're using
import 'vue3-toastify/dist/index.css';

const authStore = useAuthStore();
const router = useRouter();

const logout = async () => {
  await authStore.logout(); // calls the backend and clears token
  toast.success('You have been logged out.');
  router.push('/login');
};
</script>
<style scoped>
.navbar-brand-logo {
  height: 40px;
}
</style>