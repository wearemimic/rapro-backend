<template>
  <div class="row mt-4">
    <div class="col-12">
      <div class="card">
        <div class="card-header" style="background-color: #f8f9fa; border-bottom: 1px solid #dee2e6;">
          <h5 class="mb-0">
            <i class="bi bi-shield-check me-2"></i>Important Disclosures
          </h5>
        </div>
        <div class="card-body">
          <!-- Custom Disclosure (if exists) -->
          <div v-if="customDisclosure" class="mb-3">
            <h6 class="text-muted mb-2">{{ companyName || 'Company' }} Disclosure:</h6>
            <p class="mb-0" style="white-space: pre-wrap;">{{ customDisclosure }}</p>
            <hr class="my-3">
          </div>
          
          <!-- Default RetirementAdvisorPro Disclosure -->
          <div>
            <h6 class="text-muted mb-2">RetirementAdvisorPro Disclosure:</h6>
            <p class="mb-0 small" style="line-height: 1.6;">
              {{ defaultDisclosure }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  showCustom: {
    type: Boolean,
    default: true
  }
})

const authStore = useAuthStore()
const customDisclosure = ref('')
const companyName = ref('')

// Default RetirementAdvisorPro disclosure text
const defaultDisclosure = `This analysis is provided for informational purposes only and should not be considered as personalized investment advice. All investments involve risk, including the potential loss of principal. Past performance does not guarantee future results. The projections and calculations presented are hypothetical in nature and do not reflect actual investment results and are not guarantees of future performance. Tax implications and strategies should be discussed with a qualified tax professional. RetirementAdvisorPro does not provide legal or tax advice. Please consult with appropriate professionals before making any financial decisions. The information provided is believed to be accurate but is not guaranteed. Market conditions can change rapidly and unexpectedly. Regular review and updates of your retirement plan are recommended.`

onMounted(async () => {
  // Load custom disclosure from user profile if available
  if (props.showCustom && authStore.user) {
    try {
      // This will be populated from the user's profile data
      customDisclosure.value = authStore.user.custom_disclosure || ''
      companyName.value = authStore.user.company_name || ''
    } catch (error) {
      console.error('Error loading custom disclosure:', error)
    }
  }
})
</script>

<style scoped>
.card {
  border: 1px solid #dee2e6;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header {
  font-weight: 600;
}

hr {
  border-top: 1px solid #dee2e6;
}
</style>