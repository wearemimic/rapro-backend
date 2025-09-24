<template>
  <div v-if="showMigration" class="auth-migration-notice">
    <div class="alert alert-info d-flex align-items-center" role="alert">
      <i class="bi bi-shield-check me-3 fs-4"></i>
      <div class="flex-grow-1">
        <h6 class="alert-heading mb-1">🔒 Security Upgrade Required</h6>
        <p class="mb-2 small">
          We've upgraded our security to use secure, httpOnly cookies instead of localStorage.
          This prevents XSS attacks and keeps your account safer.
        </p>
        <button
          v-if="!migrating"
          @click="performMigration"
          class="btn btn-sm btn-primary me-2"
        >
          <i class="bi bi-arrow-clockwise me-1"></i>
          Upgrade Security Now
        </button>
        <button
          v-if="!migrating"
          @click="dismissMigration"
          class="btn btn-sm btn-outline-secondary"
        >
          Skip for Now
        </button>
        <div v-if="migrating" class="text-primary small">
          <i class="bi bi-arrow-clockwise spin me-1"></i>
          Upgrading security...
        </div>
      </div>
      <button
        v-if="!migrating"
        type="button"
        class="btn-close"
        @click="dismissMigration"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCookieAuthStore } from '@/stores/cookieAuth'
import { toast } from 'vue3-toastify'

const cookieAuthStore = useCookieAuthStore()

const migrating = ref(false)
const dismissed = ref(false)

const showMigration = computed(() => {
  return cookieAuthStore.migrationNeeded && !dismissed.value && !cookieAuthStore.migrationAttempted
})

async function performMigration() {
  migrating.value = true

  try {
    await cookieAuthStore.migrateToSecureAuth()

    toast.success('Security upgrade successful! 🔒', {
      position: 'top-right',
      timeout: 5000
    })

    // Auto-dismiss after successful migration
    setTimeout(() => {
      dismissed.value = true
    }, 2000)

  } catch (error) {
    console.error('Migration failed:', error)

    toast.error('Security upgrade failed. Please try logging in again.', {
      position: 'top-right',
      timeout: 5000
    })

    dismissed.value = true
  } finally {
    migrating.value = false
  }
}

function dismissMigration() {
  dismissed.value = true

  // Show info about manual migration
  toast.info('You can upgrade security anytime by logging out and back in.', {
    position: 'top-right',
    timeout: 3000
  })
}

onMounted(() => {
  // Check if migration is needed
  cookieAuthStore.checkMigration()
})
</script>

<style scoped>
.auth-migration-notice {
  position: fixed;
  top: 70px;
  right: 20px;
  z-index: 1050;
  max-width: 400px;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.alert-info {
  background-color: #e3f2fd;
  border-color: #1976d2;
  color: #0d47a1;
}

@media (max-width: 576px) {
  .auth-migration-notice {
    top: 10px;
    left: 10px;
    right: 10px;
    max-width: none;
  }
}
</style>