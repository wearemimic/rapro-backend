<template>
  <header id="header" class="navbar navbar-expand-lg navbar-fixed navbar-height navbar-container navbar-bordered" :style="{ backgroundColor: headerColor }">
    <div class="navbar-nav-wrap">
      <!-- Logo -->
      <a class="navbar-brand" href="#">
        <img v-if="hasCustomLogo" 
          style="height:30px;margin-left:20px;"
          :src="customLogoUrl"
          alt="Logo"
          @error="onLogoError"
        />
        <img v-else
          style="height:30px;margin-left:20px;"
          src="/assets/img/RAD-white-logo.png"
          alt="Logo"
        />
      </a>
      <!-- End Logo -->

      <div class="navbar-nav-wrap-content-end">
        <!-- Navbar -->
        <ul class="navbar-nav">
          <!-- Notifications -->
          <li class="nav-item dropdown">
            <a class="btn btn-ghost-secondary btn-icon" @click.prevent="toggleNotificationsDropdown" id="navbarNotificationsDropdown" role="button" :aria-expanded="notificationsDropdownOpen">
              <i class="bi-bell"></i>
            </a>
            <div class="dropdown-menu dropdown-menu-end navbar-dropdown-menu navbar-dropdown-menu-borderless" :class="{ 'show': notificationsDropdownOpen }" aria-labelledby="navbarNotificationsDropdown">
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
            <a class="nav-link dropdown-toggle" @click.prevent="toggleUserDropdown" id="navbarUserDropdown" role="button" :aria-expanded="userDropdownOpen">
              <span class="avatar avatar-sm avatar-circle bg-light text-dark fw-bold d-inline-flex align-items-center justify-content-center" style="width:32px;height:32px;font-size:1rem;">
                {{ userInitial }}
              </span>
              <span class="d-none d-sm-inline-block ms-2">{{ displayName }}</span>
            </a>
            <ul class="dropdown-menu" :class="{ 'show': userDropdownOpen }" aria-labelledby="navbarUserDropdown">
              <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
              <li><router-link class="dropdown-item" to="/billing">Billing</router-link></li>
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
import { computed, onMounted, ref, watch } from 'vue';
import { toast } from 'vue3-toastify'; // or whatever toast lib you're using
import 'vue3-toastify/dist/index.css';
import { API_CONFIG } from '@/config';

const authStore = useAuthStore();
const router = useRouter();

// Dropdown state management
const notificationsDropdownOpen = ref(false);
const userDropdownOpen = ref(false);

// Dropdown toggle functions
const toggleNotificationsDropdown = () => {
  notificationsDropdownOpen.value = !notificationsDropdownOpen.value;
  // Close user dropdown if open
  if (notificationsDropdownOpen.value) {
    userDropdownOpen.value = false;
  }
};

const toggleUserDropdown = () => {
  userDropdownOpen.value = !userDropdownOpen.value;
  // Close notifications dropdown if open
  if (userDropdownOpen.value) {
    notificationsDropdownOpen.value = false;
  }
};

// Close dropdowns when clicking outside
const closeDropdowns = () => {
  notificationsDropdownOpen.value = false;
  userDropdownOpen.value = false;
};

const displayName = computed(() => {
  const user = authStore.user;
  if (!user) return '';
  if (user.first_name || user.last_name) {
    return `${user.first_name || ''} ${user.last_name || ''}`.trim();
  }
  if (user.username) return user.username;
  if (user.email) return user.email;
  return '';
});

const userInitial = computed(() => {
  const user = authStore.user;
  if (user && user.first_name && user.first_name.length > 0) {
    return user.first_name[0].toUpperCase();
  }
  if (user && user.username && user.username.length > 0) {
    return user.username[0].toUpperCase();
  }
  if (user && user.email && user.email.length > 0) {
    return user.email[0].toUpperCase();
  }
  return '?';
});

const logoImg = ref(null);

// Cache-busting key that updates only when the logo changes
const logoCacheKey = ref(Date.now());

// Watch for changes to the logo and update the cache key
watch(
  () => authStore.user && authStore.user.logo,
  (newVal) => {
    logoCacheKey.value = Date.now();
    // Debug: Log when logo changes
    console.log('Logo changed:', newVal);
    console.log('hasCustomLogo:', hasCustomLogo.value);
    console.log('customLogoUrl:', customLogoUrl.value);
  }
);

// Watch for changes to the primary color
watch(
  () => authStore.user && authStore.user.primary_color,
  (newVal) => {
    console.log('Header color changed:', newVal);
  }
);

function onLogoError(event) {
  // fallback to default logo if image fails to load
  if (event && event.target) {
    event.target.src = '/assets/img/RAD-white-logo.png';
  }
}

// Check if user has a custom logo
const hasCustomLogo = computed(() => {
  const user = authStore.user;
  return user && typeof user.logo === 'string' && user.logo.trim() !== '';
});

// Generate the correct URL for the custom logo
const customLogoUrl = computed(() => {
  if (!hasCustomLogo.value) return '';
  
  const logo = authStore.user.logo;
  let url = '';
  
  if (logo.startsWith('http://') || logo.startsWith('https://')) {
    url = logo;
  } else if (logo.startsWith('/media/')) {
    url = `${API_CONFIG.BASE_URL}${logo}`;
  } else if (logo.startsWith('logos/')) {
    url = `${API_CONFIG.BASE_URL}/media/${logo}`;
  } else {
    url = `${API_CONFIG.BASE_URL}/media/${logo}`;
  }
  
  // Add cache-busting query param with a unique timestamp
  return `${url}?t=${logoCacheKey.value}`;
});

const logout = async () => {
  closeDropdowns(); // Close dropdown before logout
  await authStore.logout(); // calls the backend and clears token
  toast.success('You have been logged out.');
  router.push('/login');
};

onMounted(() => {
  // Debug: Log user and logo info on mount
  console.log('Header mounted, user:', authStore.user);
  console.log('Logo on mount:', authStore.user?.logo);
  console.log('hasCustomLogo:', hasCustomLogo.value);
  console.log('customLogoUrl:', customLogoUrl.value);
  console.log('localStorage user:', JSON.parse(localStorage.getItem('user')));
  
  authStore.fetchProfile();
  
  // Add click outside listener to close dropdowns
  document.addEventListener('click', (event) => {
    const header = document.getElementById('header');
    if (header && !header.contains(event.target)) {
      closeDropdowns();
    }
  });
});

// Header color computed property - only affects top navbar, not card headers
const headerColor = computed(() => {
  const user = authStore.user;
  return user && user.primary_color ? user.primary_color : '#377dff'; // Default blue
});
</script>
<style scoped>
.navbar-brand-logo {
  height: 40px;
}

.dropdown-menu {
  background-color: white;
}

.nav-link.dropdown-toggle {
  color: white;
}
</style>