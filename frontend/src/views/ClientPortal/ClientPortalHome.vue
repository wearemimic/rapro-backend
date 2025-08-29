<template>
  <div class="client-portal">
    <!-- Header -->
    <header class="portal-header bg-primary text-white py-3 mb-4">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h4 class="mb-0">
              <i class="bi bi-person-circle me-2"></i>
              Welcome, {{ clientName }}
            </h4>
          </div>
          <div class="col-md-6 text-end">
            <button class="btn btn-light btn-sm me-2" @click="refreshData">
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
            <button class="btn btn-outline-light btn-sm" @click="logout">
              <i class="bi bi-box-arrow-right me-1"></i>
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar Navigation -->
        <div class="col-md-3">
          <div class="card">
            <div class="card-body p-0">
              <nav class="portal-nav">
                <ul class="nav nav-pills flex-column">
                  <li class="nav-item">
                    <router-link 
                      :to="{ name: 'client-portal-dashboard' }"
                      class="nav-link"
                      active-class="active"
                    >
                      <i class="bi bi-speedometer2 me-2"></i>
                      Dashboard
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      :to="{ name: 'client-portal-documents' }"
                      class="nav-link"
                      active-class="active"
                    >
                      <i class="bi bi-folder me-2"></i>
                      My Documents
                      <span v-if="documentCount > 0" class="badge bg-secondary ms-auto">
                        {{ documentCount }}
                      </span>
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      :to="{ name: 'client-portal-messages' }"
                      class="nav-link"
                      active-class="active"
                    >
                      <i class="bi bi-chat-dots me-2"></i>
                      Messages
                      <span v-if="unreadMessages > 0" class="badge bg-danger ms-auto">
                        {{ unreadMessages }}
                      </span>
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      :to="{ name: 'client-portal-appointments' }"
                      class="nav-link"
                      active-class="active"
                    >
                      <i class="bi bi-calendar-event me-2"></i>
                      Appointments
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      :to="{ name: 'client-portal-scenarios' }"
                      class="nav-link"
                      active-class="active"
                    >
                      <i class="bi bi-graph-up me-2"></i>
                      My Scenarios
                    </router-link>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="col-md-9">
          <router-view 
            :client="client"
            :document-count="documentCount"
            :unread-messages="unreadMessages"
            @document-count-updated="documentCount = $event"
            @messages-updated="unreadMessages = $event"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useClientStore } from '@/stores/clientStore.js'

const router = useRouter()
const authStore = useAuthStore()
const clientStore = useClientStore()

// State
const client = ref(null)
const documentCount = ref(0)
const unreadMessages = ref(0)
const loading = ref(false)

// Computed
const clientName = computed(() => {
  return client.value ? `${client.value.first_name} ${client.value.last_name}` : 'Client'
})

// Methods
const loadClientData = async () => {
  loading.value = true
  try {
    // Get current user's client profile
    const user = authStore.user
    if (user && user.client_id) {
      client.value = await clientStore.getClient(user.client_id)
    }
  } catch (error) {
    console.error('Failed to load client data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await loadClientData()
  // Trigger refresh in child components via route change
  router.go(0)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

// Lifecycle
onMounted(() => {
  loadClientData()
})
</script>

<style scoped>
.client-portal {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.portal-header {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.portal-nav .nav-link {
  color: #495057;
  border-radius: 0;
  border-bottom: 1px solid #dee2e6;
  padding: 12px 16px;
  display: flex;
  align-items: center;
}

.portal-nav .nav-link:last-child {
  border-bottom: none;
}

.portal-nav .nav-link:hover {
  background-color: #f8f9fa;
}

.portal-nav .nav-link.active {
  background-color: #007bff;
  color: white;
}

.portal-nav .nav-link.active:hover {
  background-color: #0056b3;
}

.badge {
  font-size: 0.7rem;
}
</style>