<template>
  <div 
    v-if="authStore.originalUser" 
    class="impersonation-banner alert alert-warning alert-dismissible m-0 rounded-0 border-0 border-bottom"
    role="alert"
    style="z-index: 9999; position: relative;"
  >
    <div class="container-fluid d-flex align-items-center justify-content-between">
      <div class="d-flex align-items-center">
        <i class="bi-person-check-fill me-2"></i>
        <span class="fw-bold">
          🎭 You are impersonating: {{ authStore.impersonatedUser?.email }}
        </span>
        <span class="ms-2 text-muted">
          (Admin: {{ authStore.realAdminUser?.email }})
        </span>
      </div>
      
      <div class="d-flex align-items-center gap-2">
        <small class="text-muted">
          Session: {{ sessionId }}
        </small>
        <button 
          @click="endImpersonation"
          class="btn btn-sm btn-outline-warning"
          type="button"
        >
          <i class="bi-x-circle me-1"></i>
          End Impersonation
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

export default {
  name: 'ImpersonationBanner',
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    
    const sessionId = computed(() => {
      return authStore.impersonationSessionInfo?.session_id?.toString().substring(0, 8) || 'Unknown';
    });
    
    const endImpersonation = async () => {
      try {
        const confirmed = confirm(
          `Are you sure you want to end the impersonation session for ${authStore.impersonatedUser?.email}?\n\n` +
          `You will be returned to your admin account.`
        );
        
        if (confirmed) {
          await authStore.endImpersonation();
          
          // Redirect back to admin users page
          router.push('/admin/users');
          
          alert(`✅ Impersonation session ended. You are now back to your admin account (${authStore.user?.email}).`);
        }
      } catch (error) {
        console.error('Failed to end impersonation:', error);
        alert('⚠️ Failed to end impersonation session, but you have been returned to your admin account.');
        
        // Force redirect to admin even if backend call failed
        router.push('/admin/users');
      }
    };
    
    return {
      authStore,
      sessionId,
      endImpersonation
    };
  }
};
</script>

<style scoped>
.impersonation-banner {
  position: sticky;
  top: 0;
  z-index: 1030;
  background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
  border-left: 4px solid #f39c12 !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.impersonation-banner .alert-dismissible {
  padding-right: 1rem;
}

.impersonation-banner i {
  color: #f39c12;
}
</style>