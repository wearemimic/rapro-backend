<template>
  <div v-if="showDebug" class="token-debug-panel">
    <div class="debug-header">
      <small>Token Status (DEV)</small>
      <button @click="toggleDebug" class="btn btn-sm btn-link">×</button>
    </div>
    <div class="debug-content">
      <div class="status-item" :class="{ 'text-danger': !authStore.isAuthenticated }">
        Auth: {{ authStore.isAuthenticated ? 'Yes' : 'No' }}
      </div>
      <div class="status-item" :class="{ 'text-warning': expiresInMinutes < 10, 'text-danger': expiresInMinutes < 5 }">
        Expires: {{ expiresInMinutes }}m
      </div>
      <div class="status-item" :class="{ 'text-warning': authStore.isRefreshing }">
        Refreshing: {{ authStore.isRefreshing ? 'Yes' : 'No' }}
      </div>
      <div class="status-item">
        Attempts: {{ authStore.refreshAttempts }}/{{ authStore.maxRefreshAttempts }}
      </div>
    </div>
  </div>
  <div v-else class="token-debug-trigger">
    <button @click="toggleDebug" class="btn btn-sm btn-outline-secondary" title="Show token debug info">
      🔑
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showDebug = ref(false)
const updateInterval = ref(null)

const expiresInMinutes = computed(() => {
  return authStore.tokenExpirationMinutes
})

const toggleDebug = () => {
  showDebug.value = !showDebug.value
}

onMounted(() => {
  // Update every 30 seconds
  updateInterval.value = setInterval(() => {
    // Force reactivity update
  }, 30000)
})

onUnmounted(() => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})
</script>

<style scoped>
.token-debug-panel {
  position: fixed;
  top: 100px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 5px;
  font-size: 12px;
  z-index: 9999;
  min-width: 200px;
}

.token-debug-trigger {
  position: fixed;
  top: 100px;
  right: 20px;
  z-index: 9999;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 4px;
}

.debug-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-item {
  font-family: monospace;
}

.text-warning {
  color: #ffc107 !important;
}

.text-danger {
  color: #dc3545 !important;
}

.btn-link {
  color: white;
  text-decoration: none;
  padding: 0;
  border: none;
  background: none;
}
</style>