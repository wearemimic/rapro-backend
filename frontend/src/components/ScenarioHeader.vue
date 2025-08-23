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
      <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
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
          <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
            <h6 class="card-title mb-0">
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
          <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
            <h6 class="card-title mb-0">
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
      <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
        <button 
          class="btn btn-link p-0 text-decoration-none d-flex align-items-center w-100"
          type="button"
          @click="showAdvanced = !showAdvanced"
          style="color: #000000 !important;"
        >
          <i :class="['bi', showAdvanced ? 'bi-chevron-down' : 'bi-chevron-right', 'me-2']" style="color: #000000;"></i>
          <h6 class="mb-0" style="color: #000000;">Advanced Options</h6>
        </button>
      </div>
      <div v-show="showAdvanced" class="card-body">
        <div class="row g-4">
          <!-- Tax Settings -->
          <div class="col-md-6">
            <h6 class="text-muted mb-3">Tax Settings</h6>
            
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

            <!-- Deduction Fields (shown when Apply Standard Deductions is checked) -->
            <div v-show="localScenario.apply_standard_deduction">
              <div class="mb-3">
                <label class="form-label">
                  Federal Standard Deduction ($)
                  <i class="bi bi-info-circle ms-1" 
                     data-bs-toggle="tooltip" 
                     data-bs-placement="top" 
                     title="Auto-populated based on filing status, can be overridden"></i>
                </label>
                <input 
                  :value="formatCurrencyDisplay(localScenario.federal_standard_deduction || 0)"
                  @input="handleCurrencyInput($event, 'federal_standard_deduction')"
                  type="text"
                  class="form-control"
                  placeholder="Auto-populated from IRS table"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">
                  State Standard Deduction ($)
                  <i class="bi bi-info-circle ms-1" 
                     data-bs-toggle="tooltip" 
                     data-bs-placement="top" 
                     title="Additional state-level standard deduction"></i>
                </label>
                <input 
                  :value="formatCurrencyDisplay(localScenario.state_standard_deduction || 0)"
                  @input="handleCurrencyInput($event, 'state_standard_deduction')"
                  type="text"
                  class="form-control"
                  placeholder="Enter state deduction amount"
                />
              </div>

              <div class="mb-3">
                <label class="form-label">
                  Custom Annual Deduction ($)
                  <i class="bi bi-info-circle ms-1" 
                     data-bs-toggle="tooltip" 
                     data-bs-placement="top" 
                     title="Optional: Itemized deductions, business expenses, etc."></i>
                </label>
                <input 
                  :value="formatCurrencyDisplay(localScenario.custom_annual_deduction || 0)"
                  @input="handleCurrencyInput($event, 'custom_annual_deduction')"
                  type="text"
                  class="form-control"
                  placeholder="Additional itemized or special deductions"
                />
              </div>
              
              <div class="alert alert-info py-2 px-3">
                <small>
                  <strong>Total Deduction: {{ formatCurrencyDisplay(totalDeductions) }}</strong>
                  <br>
                  This amount will be subtracted from taxable income in calculations.
                </small>
              </div>
            </div>

          </div>

          <!-- Social Security Settings -->
          <div class="col-md-6">
            <h6 class="text-muted mb-3">Social Security Settings</h6>
            
            <div class="mb-3">
              <div class="form-check form-switch">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="localScenario.reduction_2030_ss"
                  @change="$emit('update:scenario', localScenario)"
                />
                <label class="form-check-label">2030 Social Security Adjustment</label>
              </div>
            </div>
            
            <!-- SS Adjustment Options (shown when toggle is checked) -->
            <div v-show="localScenario.reduction_2030_ss">
              <div class="row g-2 align-items-end">
                <div class="col-md-12 mb-2">
                  <small class="text-muted">
                    <strong>Decrease</strong> Social Security benefits starting in 2030 by:
                  </small>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label small">Type</label>
                  <select 
                    v-model="localScenario.ss_adjustment_type" 
                    class="form-select form-select-sm"
                    @change="$emit('update:scenario', localScenario)"
                  >
                    <option value="percentage">Percentage</option>
                    <option value="flat">Flat Amount</option>
                  </select>
                </div>
                
                <div class="col-md-6">
                  <label class="form-label small">
                    {{ localScenario.ss_adjustment_type === 'percentage' ? 'Percent (%)' : 'Amount ($)' }}
                  </label>
                  <input 
                    v-if="localScenario.ss_adjustment_type === 'percentage'"
                    v-model.number="localScenario.ss_adjustment_amount" 
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    class="form-control form-control-sm"
                    placeholder="e.g., 23"
                    @input="$emit('update:scenario', localScenario)"
                  />
                  <input 
                    v-else
                    :value="formatCurrencyDisplay(localScenario.ss_adjustment_amount || 0)"
                    @input="handleCurrencyInput($event, 'ss_adjustment_amount')"
                    type="text"
                    class="form-control form-control-sm"
                    placeholder="e.g., 5000"
                  />
                </div>
              </div>
              
              <div class="alert alert-warning py-1 px-2 mt-2">
                <small>
                  <strong>Summary:</strong> 
                  Decrease SS benefits by 
                  {{ localScenario.ss_adjustment_type === 'percentage' 
                    ? localScenario.ss_adjustment_amount + '%' 
                    : formatCurrencyDisplay(localScenario.ss_adjustment_amount || 0) }}
                  starting in 2030
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'
import { formatCurrencyDisplay } from '../utils/currencyFormatter'

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
const localScenario = ref({ 
  ...props.scenario,
  // Set defaults for SS adjustment fields if not present
  ss_adjustment_direction: props.scenario.ss_adjustment_direction || 'decrease',
  ss_adjustment_type: props.scenario.ss_adjustment_type || 'percentage',
  ss_adjustment_amount: props.scenario.ss_adjustment_amount || 23
})

// Computed property for total deductions
const totalDeductions = computed(() => {
  const federal = localScenario.value.federal_standard_deduction || 0
  const state = localScenario.value.state_standard_deduction || 0
  const custom = localScenario.value.custom_annual_deduction || 0
  return federal + state + custom
})

// Watch for external changes to scenario
watch(() => props.scenario, (newVal) => {
  localScenario.value = { 
    ...newVal,
    // Set defaults for SS adjustment fields if not present
    ss_adjustment_direction: newVal.ss_adjustment_direction || 'decrease',
    ss_adjustment_type: newVal.ss_adjustment_type || 'percentage',
    ss_adjustment_amount: newVal.ss_adjustment_amount || 23
  }
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

// Currency input handler
const handleCurrencyInput = (event, field) => {
  let value = event.target.value.replace(/[^0-9.]/g, '') // Remove non-numeric characters except decimal
  
  // Handle multiple decimals - only allow one
  const parts = value.split('.')
  if (parts.length > 2) {
    value = parts[0] + '.' + parts[1]
  }
  
  // Limit decimal places to 2
  if (parts[1] && parts[1].length > 2) {
    value = parts[0] + '.' + parts[1].slice(0, 2)
  }
  
  // Convert to number and update the scenario
  const numericValue = parseFloat(value) || 0
  localScenario.value[field] = numericValue
  
  // Update display with formatted currency
  event.target.value = formatCurrencyDisplay(numericValue)
  
  // Emit update
  emit('update:scenario', localScenario.value)
}

// Fetch federal standard deduction based on client tax status
const fetchFederalStandardDeduction = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    
    const response = await axios.get('http://localhost:8000/api/tax/federal-standard-deduction/', {
      params: {
        filing_status: props.clientTaxStatus
      },
      headers
    })
    
    if (response.data && response.data.deduction_amount) {
      localScenario.value.federal_standard_deduction = response.data.deduction_amount
      emit('update:scenario', localScenario.value)
    }
  } catch (error) {
    console.error('Error fetching federal standard deduction:', error.response?.data || error)
  }
}

// Watch for changes in client tax status to update standard deduction
watch(() => props.clientTaxStatus, () => {
  if (localScenario.value.apply_standard_deduction) {
    fetchFederalStandardDeduction()
  }
})

// Watch for changes in apply_standard_deduction toggle
watch(() => localScenario.value.apply_standard_deduction, (newValue) => {
  if (newValue) {
    fetchFederalStandardDeduction()
  }
})

// Fetch deduction when component mounts if apply_standard_deduction is already enabled
onMounted(() => {
  if (localScenario.value.apply_standard_deduction) {
    fetchFederalStandardDeduction()
  }
  
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })
})

// Removed headerColor computed property - using consistent light grey headers
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