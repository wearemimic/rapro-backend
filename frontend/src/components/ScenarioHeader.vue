<template>
  <div class="scenario-header">
    <!-- Page Title and Basic Info -->
    <div class="header-main">
      <div class="row align-items-center mb-4">
        <div class="col-md-8">
          <h1 class="page-title">Create New Scenario</h1>
          <p class="page-subtitle">Configure retirement planning parameters for your client</p>
        </div>
        <div class="col-md-4 text-end">
          <button type="button" class="btn btn-primary" @click="$emit('save')">
            <i class="bi bi-check-circle me-2"></i>Save Scenario
          </button>
        </div>
      </div>
    </div>

    <!-- Essential Settings Card -->
    <div class="card mb-4">
      <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
        <h5 class="card-title mb-0">
          <i class="bi bi-gear me-2"></i>Essential Settings
        </h5>
      </div>
      <div class="card-body">
        <div class="row g-3">
          <!-- Scenario Name -->
          <div class="col-md-6">
            <label class="form-label fw-semibold">Scenario Name</label>
            <input 
              v-model="localScenario.name" 
              type="text" 
              class="form-control" 
              placeholder="Enter scenario name"
              @input="$emit('update:scenario', localScenario)"
            />
          </div>
          
          <!-- Primary State -->
          <div class="col-md-6">
            <label class="form-label fw-semibold">State</label>
            <select 
              v-model="localScenario.primary_state" 
              class="form-select"
              @change="$emit('update:scenario', localScenario)"
            >
              <option value="">Select a state</option>
              <option v-for="state in states" :key="state.code" :value="state.code">
                {{ state.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Personal Information Cards -->
    <div class="row g-4 mb-4">
      <!-- Primary Client Card -->
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
            <h6 class="card-title mb-0" style="color: #fff;">
              <i class="bi bi-person me-2"></i>{{ primaryFirstName }}
            </h6>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-sm-6">
                <label class="form-label">Medicare Start Age</label>
                <select 
                  v-model.number="localScenario.primary_medicare_age" 
                  class="form-select"
                  @change="$emit('update:scenario', localScenario)"
                >
                  <option v-for="age in ageRange(62, 72)" :key="age" :value="age">
                    {{ age }}
                  </option>
                </select>
              </div>
              <div class="col-sm-6">
                <label class="form-label">Lifespan (Age)</label>
                <select 
                  v-model.number="localScenario.primary_lifespan" 
                  class="form-select"
                  @change="$emit('update:scenario', localScenario)"
                >
                  <option v-for="age in ageRange(70, 100)" :key="age" :value="age">
                    {{ age }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Spouse Card (if applicable) -->
      <div v-if="clientTaxStatus !== 'single'" class="col-md-6">
        <div class="card h-100">
          <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
            <h6 class="card-title mb-0" style="color: #fff;">
              <i class="bi bi-person me-2"></i>{{ spouseFirstName }}
            </h6>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-sm-6">
                <label class="form-label">Medicare Start Age</label>
                <select 
                  v-model.number="localScenario.spouse_medicare_age" 
                  class="form-select"
                  @change="$emit('update:scenario', localScenario)"
                >
                  <option v-for="age in ageRange(62, 72)" :key="age" :value="age">
                    {{ age }}
                  </option>
                </select>
              </div>
              <div class="col-sm-6">
                <label class="form-label">Lifespan (Age)</label>
                <select 
                  v-model.number="localScenario.spouse_lifespan" 
                  class="form-select"
                  @change="$emit('update:scenario', localScenario)"
                >
                  <option v-for="age in ageRange(70, 100)" :key="age" :value="age">
                    {{ age }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Options (Collapsible) -->
    <div class="card">
      <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
        <button 
          class="btn btn-link p-0 text-decoration-none d-flex align-items-center w-100"
          type="button"
          @click="showAdvanced = !showAdvanced"
          style="color: #fff !important;"
        >
          <i :class="['bi', showAdvanced ? 'bi-chevron-down' : 'bi-chevron-right', 'me-2']" style="color: #fff;"></i>
          <h6 class="mb-0" style="color: #fff;">Advanced Options</h6>
        </button>
      </div>
      <div v-show="showAdvanced" class="card-body">
        <div class="row g-4">
          <!-- Tax Settings -->
          <div class="col-md-6">
            <h6 class="text-muted mb-3">Tax Settings</h6>
            
            <div class="mb-3">
              <label class="form-label">Model Change in Taxes</label>
              <select 
                v-model="localScenario.model_tax_change" 
                class="form-select"
                @change="$emit('update:scenario', localScenario)"
              >
                <option value="">No Change</option>
                <option value="sunset_tcja">Sunset of TCJA (2026)</option>
                <option value="raise_top_bracket">Raise Top Bracket to 39.6%</option>
                <option value="lower_standard_deduction">Lower Standard Deduction</option>
                <option value="cap_itemized_deductions">Cap on Itemized Deductions</option>
              </select>
            </div>

            <div class="mb-3">
              <div class="form-check form-switch">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="localScenario.apply_standard_deduction"
                  @change="$emit('update:scenario', localScenario)"
                />
                <label class="form-check-label">Apply Standard Deductions</label>
              </div>
            </div>

            <div class="mb-3">
              <div class="form-check form-switch">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="localScenario.reduction_2030_ss"
                  @change="$emit('update:scenario', localScenario)"
                />
                <label class="form-check-label">2030 Reduction in SS</label>
              </div>
            </div>
          </div>

          <!-- Medicare Settings -->
          <div class="col-md-6">
            <h6 class="text-muted mb-3">Medicare Settings</h6>
            
            <div class="mb-3">
              <label class="form-label">Medicare Part B Inflation Rate</label>
              <select 
                v-model="localScenario.part_b_inflation_rate" 
                class="form-select"
                @change="$emit('update:scenario', localScenario)"
              >
                <option value="6">6%</option>
                <option value="7">7%</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Medicare Part D Inflation Rate</label>
              <select 
                v-model="localScenario.part_d_inflation_rate" 
                class="form-select"
                @change="$emit('update:scenario', localScenario)"
              >
                <option value="6">6%</option>
                <option value="7">7%</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  scenario: {
    type: Object,
    required: true
  },
  primaryFirstName: {
    type: String,
    default: 'Primary'
  },
  spouseFirstName: {
    type: String,
    default: 'Spouse'
  },
  clientTaxStatus: {
    type: String,
    default: 'single'
  }
})

const emit = defineEmits(['update:scenario', 'save'])

const showAdvanced = ref(false)
const localScenario = ref({ ...props.scenario })

// Watch for external changes to scenario
watch(() => props.scenario, (newVal) => {
  localScenario.value = { ...newVal }
}, { deep: true })

const states = [
  { code: 'AL', name: 'Alabama' },
  { code: 'AK', name: 'Alaska' },
  { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' },
  { code: 'CA', name: 'California' },
  { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' },
  { code: 'DE', name: 'Delaware' },
  { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' },
  { code: 'HI', name: 'Hawaii' },
  { code: 'ID', name: 'Idaho' },
  { code: 'IL', name: 'Illinois' },
  { code: 'IN', name: 'Indiana' },
  { code: 'IA', name: 'Iowa' },
  { code: 'KS', name: 'Kansas' },
  { code: 'KY', name: 'Kentucky' },
  { code: 'LA', name: 'Louisiana' },
  { code: 'ME', name: 'Maine' },
  { code: 'MD', name: 'Maryland' },
  { code: 'MA', name: 'Massachusetts' },
  { code: 'MI', name: 'Michigan' },
  { code: 'MN', name: 'Minnesota' },
  { code: 'MS', name: 'Mississippi' },
  { code: 'MO', name: 'Missouri' },
  { code: 'MT', name: 'Montana' },
  { code: 'NE', name: 'Nebraska' },
  { code: 'NV', name: 'Nevada' },
  { code: 'NH', name: 'New Hampshire' },
  { code: 'NJ', name: 'New Jersey' },
  { code: 'NM', name: 'New Mexico' },
  { code: 'NY', name: 'New York' },
  { code: 'NC', name: 'North Carolina' },
  { code: 'ND', name: 'North Dakota' },
  { code: 'OH', name: 'Ohio' },
  { code: 'OK', name: 'Oklahoma' },
  { code: 'OR', name: 'Oregon' },
  { code: 'PA', name: 'Pennsylvania' },
  { code: 'RI', name: 'Rhode Island' },
  { code: 'SC', name: 'South Carolina' },
  { code: 'SD', name: 'South Dakota' },
  { code: 'TN', name: 'Tennessee' },
  { code: 'TX', name: 'Texas' },
  { code: 'UT', name: 'Utah' },
  { code: 'VT', name: 'Vermont' },
  { code: 'VA', name: 'Virginia' },
  { code: 'WA', name: 'Washington' },
  { code: 'WV', name: 'West Virginia' },
  { code: 'WI', name: 'Wisconsin' },
  { code: 'WY', name: 'Wyoming' }
]

const ageRange = (start, end) => {
  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
}

// Header color from user's primary color
const headerColor = computed(() => {
  const authStore = useAuthStore();
  const user = authStore.user;
  return user && user.primary_color ? user.primary_color : '#377dff';
})
</script>

<style scoped>
.scenario-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.page-subtitle {
  color: #718096;
  margin-bottom: 0;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.card-title {
  color: #495057;
  font-weight: 600;
}

.form-label {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.375rem;
}

.fw-semibold {
  font-weight: 600;
}

.btn-link {
  color: #495057;
}

.btn-link:hover {
  color: #343a40;
}

.text-muted {
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>