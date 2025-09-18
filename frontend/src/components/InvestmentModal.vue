<template>
  <div 
    v-if="show"
    class="modal d-block" 
    tabindex="-1" 
    style="background-color: rgba(0, 0, 0, 0.5);"
  >
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="investmentModalLabel">
            <i class="bi bi-question-circle" style="margin-right: 8px;"></i>
            {{ isEditMode ? 'Edit Investment' : 'Add Investment' }}
          </h5>
          <button type="button" class="btn-close" @click="cancelEdit" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p class="text-muted mb-4">Provide personal financial investment information for the case.</p>
          
          <div class="row mb-3">
            <div class="col-md-6">
              <label class="form-label fw-bold">Account Owner</label>
              <select v-model="investment.owned_by" class="form-control">
                <option value="primary">{{ primaryFirstName }}</option>
                <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-bold">Account Type</label>
              <select v-model="investment.income_type" class="form-control">
                <option value="">Select account type</option>
                <option value="Qualified">Qualified</option>
                <option value="Non-Qualified">Non-Qualified</option>
                <option value="Roth">Roth</option>
                <option value="Inherited Traditional Spouse">Inherited Traditional Spouse</option>
                <option value="Inherited Roth Spouse">Inherited Roth Spouse</option>
                <option value="Inherited Traditional Non-Spouse">Inherited Traditional Non-Spouse</option>
                <option value="Inherited Roth Non-Spouse">Inherited Roth Non-Spouse</option>
              </select>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-3">
              <label class="form-label fw-bold">Investment Name</label>
              <input 
                v-model="investment.investment_name" 
                type="text" 
                class="form-control" 
                placeholder="401K"
              />
            </div>
            <div class="col-md-3">
              <label class="form-label fw-bold">Current Balance</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input 
                  :value="currentBalanceDisplay"
                  @input="onCurrentBalanceInput"
                  @focus="onCurrentBalanceFocus"
                  @blur="onCurrentBalanceBlur"
                  type="text" 
                  class="form-control" 
                  placeholder="500,000"
                />
              </div>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-bold">Age Asset Established</label>
              <select v-model.number="investment.age_established" class="form-control">
                <option :value="null">Select age</option>
                <option v-for="age in availableEstablishedAges" :key="age" :value="age">
                  {{ age }}
                </option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-bold">Est. Rate of Return</label>
              <div class="input-group">
                <input 
                  v-model.number="investment.rate_of_return" 
                  type="number" 
                  class="form-control" 
                  placeholder="6"
                  step="0.1"
                />
                <span class="input-group-text">%</span>
              </div>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-md-4">
              <label class="form-label fw-bold">Age to Begin Withdrawals</label>
              <select v-model.number="investment.age_start_taking" class="form-control">
                <option v-for="age in availableStartAges" :key="age" :value="age">
                  {{ age }}
                </option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-bold">Age to End Withdrawals</label>
              <select v-model.number="investment.age_stop_taking" class="form-control">
                <option v-for="age in availableEndAges" :key="age" :value="age">
                  {{ age }}
                </option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-bold">Minimum Monthly Withdrawal</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input 
                  :value="monthlyWithdrawalDisplay"
                  @input="onMonthlyWithdrawalInput"
                  @focus="onMonthlyWithdrawalFocus"
                  @blur="onMonthlyWithdrawalBlur"
                  type="text" 
                  class="form-control" 
                  placeholder="2,500"
                />
              </div>
            </div>
          </div>

          <div class="row mb-3">
            <div class="col-12">
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  v-model="investment.is_contributing" 
                  id="contributingCheck"
                />
                <label class="form-check-label fw-bold" for="contributingCheck">
                  Are you currently contributing to this investment?
                </label>
              </div>
            </div>
          </div>

          <div v-if="investment.is_contributing">
            <p class="text-muted mb-3">Please provide your annual contribution amount.</p>
            
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label fw-bold">Annual Contribution Amount</label>
                <div class="input-group">
                  <span class="input-group-text">$</span>
                  <input 
                    :value="annualContributionDisplay"
                    @input="onAnnualContributionInput"
                    @focus="onAnnualContributionFocus"
                    @blur="onAnnualContributionBlur"
                    type="text" 
                    class="form-control" 
                    placeholder="25,000"
                  />
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label fw-bold">Employer Contribution Match</label>
                <div class="input-group">
                  <input 
                    v-model.number="investment.employer_match" 
                    type="number" 
                    class="form-control" 
                    placeholder="0"
                    step="0.1"
                  />
                  <span class="input-group-text">%</span>
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold">Age Last Year of Contribution</label>
                <select v-model.number="investment.age_last_contribution" class="form-control">
                  <option :value="null">Not specified</option>
                  <option v-for="age in availableContributionEndAges" :key="age" :value="age">
                    {{ age }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="cancelEdit">Cancel</button>
          <button type="button" class="btn btn-primary" @click="saveInvestment">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  primaryFirstName: {
    type: String,
    default: 'Primary'
  },
  spouseFirstName: {
    type: String, 
    default: 'Spouse'
  },
  primaryLifespan: {
    type: Number,
    default: 90
  },
  spouseLifespan: {
    type: Number,
    default: 90
  },
  isSingle: {
    type: Boolean,
    default: false
  },
  primaryCurrentAge: {
    type: Number,
    default: 45
  },
  spouseCurrentAge: {
    type: Number,
    default: 45
  },
  editingInvestment: {
    type: Object,
    default: null
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'cancel'])

// Computed property to determine if we're in edit mode
const isEditMode = computed(() => props.editingInvestment !== null)

const investment = ref({
  owned_by: 'primary',
  income_type: '',
  investment_name: '',
  current_balance: null,
  age_established: null,
  rate_of_return: null,
  age_start_taking: 65,
  age_stop_taking: 95,
  monthly_withdrawal_amount: null,
  is_contributing: false,
  annual_contribution_amount: null,
  annual_contribution_percentage: null,
  employer_match: null,
  age_last_contribution: null
})

// For formatted display
const currentBalanceDisplay = ref('')
const monthlyWithdrawalDisplay = ref('')
const annualContributionDisplay = ref('')

// Computed properties for age ranges
const currentLifespan = computed(() => {
  return investment.value.owned_by === 'primary' ? props.primaryLifespan : props.spouseLifespan
})

const availableEstablishedAges = computed(() => {
  // Age when asset was established - typically from 18 to current retirement age
  const ages = []
  for (let age = 18; age <= currentLifespan.value; age++) {
    ages.push(age)
  }
  return ages
})

const availableStartAges = computed(() => {
  // Start ages from 50 to the owner's lifespan
  const ages = []
  for (let age = 50; age <= currentLifespan.value; age++) {
    ages.push(age)
  }
  return ages
})

const availableEndAges = computed(() => {
  // End ages from start age (if selected) to the owner's lifespan
  const startAge = investment.value.age_start_taking || 50
  const ages = []
  for (let age = startAge; age <= currentLifespan.value; age++) {
    ages.push(age)
  }
  return ages
})

const availableContributionEndAges = computed(() => {
  // Contribution end ages from current age to retirement age (typically 65-70)
  const ages = []
  let currentAge = investment.value.owned_by === 'spouse' ? props.spouseCurrentAge : props.primaryCurrentAge
  
  // Debug: Always log the age calculation details
  console.log('InvestmentModal: Age calculation debug:', {
    currentAge,
    primaryCurrentAge: props.primaryCurrentAge,
    spouseCurrentAge: props.spouseCurrentAge,
    owned_by: investment.value.owned_by,
    currentLifespan: currentLifespan.value
  })
  
  // Validate currentAge is a valid positive number and not the default fallback
  if (typeof currentAge !== 'number' || isNaN(currentAge) || currentAge < 0) {
    console.warn('InvestmentModal: Invalid current age, using fallback:', {
      receivedAge: currentAge,
      primaryCurrentAge: props.primaryCurrentAge,
      spouseCurrentAge: props.spouseCurrentAge,
      owned_by: investment.value.owned_by
    })
    currentAge = 45 // Use reasonable default instead of invalid values
  }
  
  // If we're getting the default 65 age, it likely means client data isn't loaded yet
  // So use a more reasonable starting age for contribution planning
  if (currentAge === 65) {
    console.info('InvestmentModal: Received default age 65, using 45 for contribution planning')
    currentAge = 45
  }
  
  // Ensure we have valid minimum and maximum ages
  const minAge = Math.max(currentAge, 18) // Minimum 18 years old
  const maxAge = Math.min(currentLifespan.value || 90, 80)
  
  console.log('InvestmentModal: Final age range:', { minAge, maxAge, currentAge })
  
  // Only generate age options if we have valid ages
  if (minAge <= maxAge && minAge > 0) {
    for (let age = minAge; age <= maxAge; age++) {
      ages.push(age)
    }
  } else {
    // Fallback range if calculation fails
    console.warn('InvestmentModal: Invalid age range, using fallback:', { minAge, maxAge, currentAge })
    for (let age = 25; age <= 80; age++) {
      ages.push(age)
    }
  }
  
  console.log('InvestmentModal: Generated ages:', ages.slice(0, 5), '...', ages.slice(-5))
  
  return ages
})

const resetForm = () => {
  investment.value = {
    owned_by: 'primary',
    income_type: '',
    investment_name: '',
    current_balance: null,
    age_established: null,
    rate_of_return: null,
    age_start_taking: 65,
    age_stop_taking: 95,
    monthly_withdrawal_amount: null,
    is_contributing: false,
    annual_contribution_amount: null,
    annual_contribution_percentage: null,
    employer_match: null,
    age_last_contribution: null
  }
  currentBalanceDisplay.value = ''
  monthlyWithdrawalDisplay.value = ''
  annualContributionDisplay.value = ''
}

// Watch for changes to editingInvestment to populate form
watch(() => props.editingInvestment, (newValue) => {
  if (newValue) {
    // Populate form with existing investment data
    console.log('InvestmentModal: Loading investment for edit:', newValue);
    console.log('InvestmentModal: rate_of_return from parent:', newValue.rate_of_return);
    investment.value = {
      owned_by: newValue.owned_by || 'primary',
      income_type: newValue.income_type || '',
      investment_name: newValue.investment_name || newValue.income_name || '',
      current_balance: newValue.current_balance || newValue.current_asset_balance || null,
      age_established: newValue.age_established || null,
      rate_of_return: newValue.rate_of_return !== null && newValue.rate_of_return !== undefined ? newValue.rate_of_return * 100 : 0, // Convert rate_of_return from decimal to percentage for display
      age_start_taking: newValue.start_age || newValue.age_to_begin_withdrawal || 65,
      age_stop_taking: newValue.end_age || newValue.age_to_end_withdrawal || 95,
      monthly_withdrawal_amount: newValue.withdrawal_amount || newValue.monthly_amount || null,
      is_contributing: newValue.is_contributing || false,
      annual_contribution_amount: newValue.monthly_contribution ? newValue.monthly_contribution * 12 : null,
      annual_contribution_percentage: newValue.contribution_percentage || null,
      employer_match: newValue.employer_match || null,
      age_last_contribution: newValue.age_last_contribution || null
    }
    
    // Update display values
    currentBalanceDisplay.value = investment.value.current_balance ? formatCurrency(investment.value.current_balance) : ''
    monthlyWithdrawalDisplay.value = investment.value.monthly_withdrawal_amount ? new Intl.NumberFormat('en-US').format(investment.value.monthly_withdrawal_amount) : ''
    annualContributionDisplay.value = investment.value.annual_contribution_amount ? new Intl.NumberFormat('en-US').format(investment.value.annual_contribution_amount) : ''
  } else {
    resetForm()
  }
}, { immediate: true })

// Currency formatting functions
const formatCurrency = (value) => {
  if (!value || value === 0) return '0'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value)
}

const onCurrentBalanceFocus = () => {
  // Show raw number on focus
  currentBalanceDisplay.value = investment.value.current_balance ? investment.value.current_balance.toString() : ''
}

const onCurrentBalanceInput = (event) => {
  // Remove non-numeric characters except decimal
  let raw = event.target.value.replace(/[^0-9.]/g, '')
  
  // Handle multiple decimals
  const parts = raw.split('.')
  if (parts.length > 2) raw = parts[0] + '.' + parts[1]
  
  // Limit decimal places to 2
  if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2)
  
  // Handle edge cases
  if (raw === '.') {
    currentBalanceDisplay.value = '0.'
    investment.value.current_balance = 0
    return
  }
  
  if (raw === '') {
    currentBalanceDisplay.value = ''
    investment.value.current_balance = null
    return
  }
  
  // Parse numeric value
  let numeric = parseFloat(raw)
  if (isNaN(numeric)) numeric = 0
  
  // Format with commas for display
  const [intPart, decPart] = numeric.toString().split('.')
  let formatted = parseInt(intPart, 10).toLocaleString()
  if (decPart !== undefined) {
    formatted += '.' + decPart
  }
  
  currentBalanceDisplay.value = formatted
  investment.value.current_balance = numeric
}

const onCurrentBalanceBlur = () => {
  // Format as currency on blur
  if (investment.value.current_balance) {
    currentBalanceDisplay.value = formatCurrency(investment.value.current_balance)
  }
}

// Monthly Withdrawal Amount formatting
const onMonthlyWithdrawalFocus = () => {
  monthlyWithdrawalDisplay.value = investment.value.monthly_withdrawal_amount ? investment.value.monthly_withdrawal_amount.toString() : ''
}

const onMonthlyWithdrawalInput = (event) => {
  let raw = event.target.value.replace(/[^0-9.]/g, '')
  const parts = raw.split('.')
  if (parts.length > 2) raw = parts[0] + '.' + parts[1]
  if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2)
  
  if (raw === '.') {
    monthlyWithdrawalDisplay.value = '0.'
    investment.value.monthly_withdrawal_amount = 0
    return
  }
  
  if (raw === '') {
    monthlyWithdrawalDisplay.value = ''
    investment.value.monthly_withdrawal_amount = null
    return
  }
  
  let numeric = parseFloat(raw)
  if (isNaN(numeric)) numeric = 0
  
  const [intPart, decPart] = numeric.toString().split('.')
  let formatted = parseInt(intPart, 10).toLocaleString()
  if (decPart !== undefined) {
    formatted += '.' + decPart
  }
  
  monthlyWithdrawalDisplay.value = formatted
  investment.value.monthly_withdrawal_amount = numeric
}

const onMonthlyWithdrawalBlur = () => {
  if (investment.value.monthly_withdrawal_amount) {
    monthlyWithdrawalDisplay.value = new Intl.NumberFormat('en-US').format(investment.value.monthly_withdrawal_amount)
  }
}

// Annual Contribution Amount formatting
const onAnnualContributionFocus = () => {
  annualContributionDisplay.value = investment.value.annual_contribution_amount ? investment.value.annual_contribution_amount.toString() : ''
}

const onAnnualContributionInput = (event) => {
  let raw = event.target.value.replace(/[^0-9.]/g, '')
  const parts = raw.split('.')
  if (parts.length > 2) raw = parts[0] + '.' + parts[1]
  if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2)
  
  if (raw === '.') {
    annualContributionDisplay.value = '0.'
    investment.value.annual_contribution_amount = 0
    return
  }
  
  if (raw === '') {
    annualContributionDisplay.value = ''
    investment.value.annual_contribution_amount = null
    return
  }
  
  let numeric = parseFloat(raw)
  if (isNaN(numeric)) numeric = 0
  
  const [intPart, decPart] = numeric.toString().split('.')
  let formatted = parseInt(intPart, 10).toLocaleString()
  if (decPart !== undefined) {
    formatted += '.' + decPart
  }
  
  annualContributionDisplay.value = formatted
  investment.value.annual_contribution_amount = numeric
}

const onAnnualContributionBlur = () => {
  if (investment.value.annual_contribution_amount) {
    annualContributionDisplay.value = new Intl.NumberFormat('en-US').format(investment.value.annual_contribution_amount)
  }
}

const saveInvestment = () => {
  if (!investment.value.income_type || !investment.value.investment_name) {
    alert('Please fill in required fields')
    return
  }

  // Debug: Log the rate of return before conversion
  console.log('InvestmentModal: rate_of_return before save:', investment.value.rate_of_return)

  // Convert to the format expected by the backend
  const investmentData = {
    id: isEditMode.value ? props.editingInvestment.id : (Date.now() + Math.random()), // Preserve ID when editing
    income_type: investment.value.income_type,
    income_name: investment.value.investment_name,  // For backend compatibility
    investment_name: investment.value.investment_name,  // For frontend display
    owned_by: investment.value.owned_by,
    current_balance: investment.value.current_balance || 0,
    age_established: investment.value.age_established,
    rate_of_return: investment.value.rate_of_return ? investment.value.rate_of_return / 100 : 0, // Convert percentage to decimal for backend
    monthly_contribution: investment.value.is_contributing ? 
      (investment.value.annual_contribution_amount ? investment.value.annual_contribution_amount / 12 : 0) : 0,
    contribution_percentage: investment.value.annual_contribution_percentage || 0,
    employer_match: investment.value.employer_match || 0,
    age_last_contribution: investment.value.age_last_contribution,
    start_age: investment.value.age_start_taking || 65,
    end_age: investment.value.age_stop_taking || 95,
    withdrawal_amount: investment.value.monthly_withdrawal_amount || 0,
    isEdit: isEditMode.value // Flag to indicate this is an edit
  }

  // Debug: Log the converted rate of return
  console.log('InvestmentModal: investmentData being saved:', investmentData)

  emit('save', investmentData)

  // Reset form
  resetForm()
}

const cancelEdit = () => {
  // Emit cancel event so parent can clear editing state and close modal
  emit('cancel')
  resetForm()
}

// Expose resetForm for parent component if needed
defineExpose({
  resetForm
})
</script>

<style scoped>
.form-label {
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.fw-bold {
  font-weight: 600;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  background-color: #4c63d2;
  border-color: #4c63d2;
}

.btn-primary:hover {
  background-color: #3b51c7;
  border-color: #3b51c7;
}
</style>