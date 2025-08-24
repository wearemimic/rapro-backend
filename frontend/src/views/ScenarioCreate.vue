<template>
  <div class="p-6 max-w-7xl mx-auto" style="margin-top: 80px;">
    <ScenarioHeader 
      v-model:scenario="scenario"
      :primary-first-name="primaryFirstName"
      :spouse-first-name="spouseFirstName"
      :client-tax-status="clientTaxStatus"
      :is-edit-mode="isEditMode"
      @save="submitScenario"
    />

    <div class="card">
      <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
        <h5 class="mb-0" style="color: #000000 !important;">
          <i class="bi bi-cash-coin me-2"></i>Retirement Income Information
        </h5>
      </div>
        <div class="card-body"> 
          <div class="row mb-3">
            <div class="col-auto">
              <select v-model="newIncome.income_type" class="form-select" style="width: auto;">
                <option disabled value="">Select income type</option>
                <option
                  v-for="option in incomeTypes"
                  :key="option"
                  :value="option"
                >{{ option.replace(/_/g, ' ') }}</option>
              </select>
            </div>
            <div class="col-auto">
              <button class="btn btn-primary" @click="addIncome">
                <i class="bi bi-plus-circle me-2"></i>Add Income Product
              </button>
            </div>
          </div>

          <div v-for="(group, type) in groupedIncome" :key="type" class="mt-5">
            <h5 class="font-semibold text-lg mb-3">{{ type }}</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead class="thead-light">
                  <tr>
                    <template v-if="type === 'Wages' || type === 'Reverse_Mortgage'">
                      <th>Owner</th>
                      <th>Amount per Month</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'social_security'">
                      <th>Owner</th>
                      <th>Amount at FRA</th>
                      <th>Start Age</th>
                      <th>COLA %</th>
                      <th>Actual Benefit Amount</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Life_Insurance'">
                      <th>Owner</th>
                      <th>Monthly Loan Amount</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Pension'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>COLA %</th>
                      <th>Start Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Annuity'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>% Taxable</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="['Roth_IRA', 'Traditional_IRA', 'Roth_401k', 'Traditional_401k'].includes(type)">
                      <th>Owner</th>
                      <th>Current Balance</th>
                      <th>Monthly Contribution</th>
                      <th>Growth Rate (%)</th>
                      <th>Start Age</th>
                      <th>Monthly Withdrawal</th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Brokerage_Account'">
                      <th>Owner</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th colspan="2"></th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else-if="type === 'Rental_Income'">
                      <th>Owner</th>
                      <th>Monthly Income</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th colspan="1"></th>
                      <th class="text-center" style="width: 90px;">Action</th>
                    </template>
                    <template v-else>
                      <th v-if="type === 'other_taxable_income'">Title</th>
                      <th>Owner</th>
                      <th>Monthly Amount</th>
                      <th>Start Age</th>
                      <th>End Age</th>
                      <th style="width: 90px;">Action</th>
                    </template>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="income in group" :key="income.id">

                    <!-- Wages / Reverse Mortgage -->
                    <tr v-if="['Wages', 'Reverse_Mortgage'].includes(income.income_type)">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td>
                        <input 
                          :value="formatCurrencyInput(income.amount_per_month)"
                          @input="onCurrencyInput($event, income, 'amount_per_month')"
                          @blur="onCurrencyBlur($event, income, 'amount_per_month')"
                          type="text" 
                          class="form-control"
                          placeholder="5,000"
                        />
                      </td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Social Security -->
                    <tr v-else-if="income.income_type === 'social_security'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td>
                        <input 
                          :value="formatCurrencyInput(income.amount_at_fra)"
                          @input="onCurrencyInput($event, income, 'amount_at_fra')"
                          @blur="onCurrencyBlur($event, income, 'amount_at_fra')"
                          type="text" 
                          class="form-control"
                          placeholder="3,500"
                        />
                      </td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control" placeholder="Start Age" @change="checkMedicareAdjustment(income)">
                          <option v-for="age in Array.from({ length: 9 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td><input v-model.number="income.cola" type="number" class="form-control" placeholder="COLA %" /></td>
                      <td>{{ calculateSocialSecurityBenefit(income.amount_at_fra, income.start_age) }}</td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Life Insurance -->
                    <tr v-else-if="income.income_type === 'Life_Insurance'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.loan_amount" type="number" class="form-control" placeholder="Monthly Loan" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Pension -->
                    <tr v-else-if="income.income_type === 'Pension'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td><input v-model.number="income.cola" type="number" class="form-control" placeholder="COLA %" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Annuity -->
                    <tr v-else-if="income.income_type === 'Annuity'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td><input v-model.number="income.percent_taxable" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Retirement Accounts -->
                    <tr v-else-if="['Roth_IRA', 'Traditional_IRA', 'Roth_401k', 'Traditional_401k'].includes(income.income_type)">
                      <td>
                        <select v-model="income.owned_by" class="form-control">
                          <option value="primary">{{ primaryFirstName }}</option>
                          <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                        </select>
                      </td>
                      <td>
                        <input 
                          :value="formatCurrencyInput(income.current_balance)"
                          @input="onCurrencyInput($event, income, 'current_balance')"
                          @blur="onCurrencyBlur($event, income, 'current_balance')"
                          type="text" 
                          class="form-control"
                          placeholder="500,000"
                        />
                      </td>
                      <td>
                        <input 
                          :value="formatCurrencyInput(income.monthly_contribution)"
                          @input="onCurrencyInput($event, income, 'monthly_contribution')"
                          @blur="onCurrencyBlur($event, income, 'monthly_contribution')"
                          type="text" 
                          class="form-control"
                          placeholder="2,500"
                        />
                      </td>
                      <td>
                        <input v-model.number="income.growth_rate" type="number" class="form-control" />
                      </td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <input v-model.number="income.withdrawal_amount" type="number" class="form-control" placeholder="Monthly Withdrawal" />
                      </td>
                      <td class="text-end" style="width: 90px;">
                        <button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button>
                      </td>
                    </tr>

                    <!-- Brokerage -->
                    <tr v-else-if="income.income_type === 'Brokerage_Account'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td colspan="2"></td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Rental Income -->
                    <tr v-else-if="income.income_type === 'Rental_Income'">
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td colspan="1"></td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                    <!-- Other Taxable Income -->
                    <tr v-else>
                      <td v-if="type === 'other_taxable_income'"><input v-model="income.title" class="form-control" placeholder="Income Title" /></td>
                      <td><select v-model="income.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select></td>
                      <td><input v-model.number="income.amount_per_month" type="number" class="form-control" /></td>
                      <td>
                        <select v-model.number="income.start_age" class="form-control">
                          <option v-for="age in Array.from({ length: 39 }, (_, i) => 62 + i)" :key="age" :value="age">{{ age }}</option>
                        </select>
                      </td>
                      <td>
                        <select v-model.number="income.end_age" class="form-control">
                          <option
                            v-for="age in Array.from({ length: (income.owned_by === 'primary' ? scenario.primary_lifespan - 62 + 1 : scenario.spouse_lifespan - 62 + 1) }, (_, i) => 62 + i)"
                            :key="age"
                            :value="age"
                          >
                            {{ age }}
                          </option>
                        </select>
                      </td>
                      <td class="text-end" style="width: 90px;"><button class="btn btn-sm btn-danger" @click="removeIncomeById(income.id)">Remove</button></td>
                    </tr>

                  </template>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

    <!-- Investment Accounts Section -->
    <div class="card" style="margin-top:40px;">
      <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
        <h5 class="mb-0" style="color: #000000 !important;">
          <i class="bi bi-piggy-bank me-2"></i>Investment Accounts
        </h5>
      </div>
      <div class="card-body">
          <div class="row mb-3">
            <div class="col-auto">
              <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#investmentModal">
                <i class="bi bi-plus-circle me-2"></i>Add Investment Account
              </button>
            </div>
          </div>

          <div v-for="(group, type) in groupedInvestments" :key="type" class="mt-4">
            <h5 class="font-semibold text-lg mb-3">{{ type }}</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead class="thead-light">
                  <tr>
                    <th>Owner</th>
                    <th>Investment Name</th>
                    <th>Current Balance</th>
                    <th>Rate of Return</th>
                    <th>Age Start Taking</th>
                    <th>Age Stop Taking</th>
                    <th class="text-center" style="width: 90px;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="investment in group" :key="investment.id">
                    <td>
                      <select v-model="investment.owned_by" class="form-control">
                        <option value="primary">{{ primaryFirstName }}</option>
                        <option v-if="!isSingle" value="spouse">{{ spouseFirstName }}</option>
                      </select>
                    </td>
                    <td>
                      <input v-model="investment.investment_name" type="text" class="form-control" />
                    </td>
                    <td>
                      <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input v-model.number="investment.current_balance" type="number" class="form-control" />
                      </div>
                    </td>
                    <td>
                      <div class="input-group">
                        <input v-model.number="investment.growth_rate" type="number" class="form-control" step="0.01" />
                        <span class="input-group-text">%</span>
                      </div>
                    </td>
                    <td>
                      <input v-model.number="investment.start_age" type="number" class="form-control" />
                    </td>
                    <td>
                      <input v-model.number="investment.end_age" type="number" class="form-control" />
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-danger" @click="removeInvestmentById(investment.id)">Remove</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

        <div class="card" style="margin-top:40px;">
      <div class="card-header" style="background-color: #f8f9fa !important; color: #000000 !important; border-bottom: 1px solid #dee2e6;">
        <h5 class="mb-0" style="color: #000000 !important;">
          <i class="bi bi-shield-plus me-2"></i>Coverage Information (Cost per Individual)
        </h5>
      </div>
      <div class="card-body">
      <p class="text-muted">Please choose the types of coverage you would like to have in retirement. Note Part B is mandatory, also the associated costs are per individual.</p>
      <table class="table table-bordered mt-3">
        <thead class="thead-light">
          <tr>
            <th></th>
            <th>Coverage</th>
            <th>Current Base Monthly Premium</th>
            <th>Choose the Expected Inflation Rate</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td></td>
            <td>Medicare Part B</td>
            <td>$185.00</td>
            <td>
              <select class="form-control">
                <option>Average Historical Inflation (7.42%)</option>
                <option>Custom Inflation Rate</option>
              </select>
            </td>
          </tr>
          <tr>
            <td><input type="checkbox" class="form-check-input" checked /></td>
            <td>Medicare Part D</td>
            <td>$0</td>
            <td>
              <select class="form-control">
                <option>Average Historical Inflation (6.73%)</option>
                <option>Custom Inflation Rate</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

    <!-- Submit -->
    <button class="btn btn-primary" @click="submitScenario" style="margin:10px 10px 0px 0px;">
      {{ isEditMode ? 'Save Scenario' : 'Create Scenario' }}
    </button>
    <button class="btn btn-secondary" @click="handleCancel" style="margin-top:10px;">Cancel</button>
  </div>

<!-- Medicare Modal -->
<div v-if="showMedicareModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0, 0, 0, 0.5);">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content shadow-lg border-0">
      <div class="modal-header bg-light">
        <h5 class="modal-title">Adjust Medicare Start Age</h5>
        <button type="button" class="btn-close" @click="showMedicareModal = false" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <p>
          You've selected age {{ medicareModalData.suggestedAge }} for
          {{ medicareModalData.isPrimary ? primaryFirstName : spouseFirstName }}'s Social Security benefits,
          but their Medicare start age is different.
        </p>
        <p>Would you like to update their Medicare start age to match?</p>
      </div>
      <div class="modal-footer bg-light">
        <button class="btn btn-secondary" @click="showMedicareModal = false">Cancel</button>
        <button class="btn btn-primary" @click="handleMedicareAdjustment">Yes, Update</button>
      </div>
    </div>
  </div>
</div>

<InvestmentModal 
  :primary-first-name="primaryFirstName" 
  :spouse-first-name="spouseFirstName"
  :primary-lifespan="scenario.primary_lifespan"
  :spouse-lifespan="scenario.spouse_lifespan"
  :is-single="isSingle"
  :primary-current-age="primaryCurrentAge"
  :spouse-current-age="spouseCurrentAge"
  @save="addInvestment"
/>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import InvestmentModal from '../components/InvestmentModal.vue';
import ScenarioHeader from '../components/ScenarioHeader.vue';
import { useAuthStore } from '../stores/auth';
import { createCurrencyHandlers, formatCurrency } from '../utils/currencyFormatter';

const route = useRoute();
const router = useRouter();
const clientId = route.params.id;

// Check if we're in edit mode
const isEditMode = computed(() => !!route.query.edit);

const primaryFirstName = ref('Primary');
const spouseFirstName = ref('Spouse');
const clientTaxStatus = ref('single');
const clientData = ref(null);

const scenario = ref({
  name: '',
  description: '',
  primary_retirement_age: 65,
  primary_medicare_age: 65,
  primary_lifespan: 90,
  spouse_retirement_age: 65,
  spouse_medicare_age: 65,
  spouse_lifespan: 90,
  income: [],
  investments: [],
  model_tax_change: '',
  reduction_2030_ss: false,
  ss_adjustment_year: 2030,
  ss_adjustment_direction: 'decrease',
  ss_adjustment_type: 'percentage', 
  ss_adjustment_amount: 23,
  apply_standard_deduction: false,
  primary_blind: false,
  spouse_blind: false,
  is_dependent: false,
  part_b_inflation_rate: '6',
  part_d_inflation_rate: '6',
  primary_state: '',
});

const incomeTypes = [
  'social_security',
  'Pension',
  'Wages',
  'Rental_Income',
  'Other'
];

const newIncome = ref({ income_type: '' });

function addIncome() {
  if (!newIncome.value.income_type) return;
  scenario.value.income.push({
    id: uuidv4(),
    income_type: newIncome.value.income_type,
    owned_by: 'primary',
    start_age: 65,
    end_age: 90,
    current_balance: 0,
    monthly_contribution: 0,
    growth_rate: 0
  });
  newIncome.value.income_type = '';
}

// Remove by id for grouped income
function removeIncomeById(id) {
  scenario.value.income = scenario.value.income.filter(income => income.id !== id);
}

// Check if client is single
const isSingle = computed(() => {
  return clientTaxStatus.value === 'single';
});

// Calculate current ages from birthdates
const calculateAge = (birthdate) => {
  if (!birthdate) return 65; // Default age
  const today = new Date();
  const birth = new Date(birthdate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
};

const primaryCurrentAge = computed(() => {
  return clientData.value?.birthdate ? calculateAge(clientData.value.birthdate) : 65;
});

const spouseCurrentAge = computed(() => {
  return clientData.value?.spouse?.birthdate ? calculateAge(clientData.value.spouse.birthdate) : 65;
});

// Currency formatting methods
const formatCurrencyInput = (value) => {
  if (!value || value === 0) return '';
  return new Intl.NumberFormat('en-US').format(value);
};

const parseCurrencyInput = (value) => {
  if (!value) return 0;
  return parseFloat(value.toString().replace(/,/g, '')) || 0;
};

const onCurrencyInput = (event, object, field) => {
  // Remove non-numeric characters except decimal
  let raw = event.target.value.replace(/[^0-9.]/g, '');
  
  // Handle multiple decimals
  const parts = raw.split('.');
  if (parts.length > 2) raw = parts[0] + '.' + parts[1];
  
  // Limit decimal places to 2
  if (parts[1] && parts[1].length > 2) {
    raw = parts[0] + '.' + parts[1].slice(0, 2);
  }
  
  if (raw === '') {
    object[field] = 0;
    event.target.value = '';
    return;
  }
  
  const numericValue = parseFloat(raw) || 0;
  object[field] = numericValue;
  
  // Format display with commas
  event.target.value = formatCurrencyInput(numericValue);
};

const onCurrencyBlur = (event, object, field) => {
  const value = object[field] || 0;
  event.target.value = formatCurrencyInput(value);
};

// Group income products by type
const groupedIncome = computed(() => {
  return scenario.value.income.reduce((acc, item) => {
    if (!acc[item.income_type]) acc[item.income_type] = [];
    acc[item.income_type].push(item);
    return acc;
  }, {});
});

// Investment functions
function addInvestment(investmentData) {
  // Convert growth_rate back to percentage for display
  investmentData.growth_rate = investmentData.growth_rate * 100;
  scenario.value.investments.push(investmentData);
}

function removeInvestmentById(id) {
  scenario.value.investments = scenario.value.investments.filter(investment => investment.id !== id);
}

// Group investments by type
const groupedInvestments = computed(() => {
  return scenario.value.investments.reduce((acc, item) => {
    if (!acc[item.income_type]) acc[item.income_type] = [];
    acc[item.income_type].push(item);
    return acc;
  }, {});
});

// Removed headerColor computed property - using consistent light grey headers

async function submitScenario() {
  try {
    console.log('💰 INCOME_EDIT: submitScenario called');
    console.log('💰 INCOME_EDIT: scenario.value.income:', scenario.value.income);
    console.log('💰 INCOME_EDIT: route.query:', route.query);
    
    // Validate scenario name and provide fallback if blank
    if (!scenario.value.name || scenario.value.name.trim() === "") {
      const timestamp = new Date().getTime();
      scenario.value.name = `Scenario ${timestamp}`;
    }

    // Clean and map income sources for API payload
    const incomeSources = scenario.value.income;
    const cleanedIncomeSources = incomeSources.map(row => {
      const sanitized = { ...row };
      // Ensure fields match expected database schema
      sanitized.owned_by = row.owned_by;
      sanitized.income_type = row.income_type;
      sanitized.income_name = row.title || row.income_type.replace(/_/g, ' ');
      sanitized.current_asset_balance = parseFloat(row.current_balance || 0).toFixed(2);
      sanitized.monthly_amount = parseFloat(row.withdrawal_amount || row.amount_at_fra || row.amount_per_month || row.loan_amount || 0).toFixed(2);
      sanitized.monthly_contribution = parseFloat(row.monthly_contribution || 0).toFixed(2);
      sanitized.age_to_begin_withdrawal = row.start_age;
      sanitized.age_to_end_withdrawal = row.end_age;
      sanitized.rate_of_return = parseFloat(row.growth_rate || 0).toFixed(4);
      sanitized.cola = parseFloat(row.cola || 0).toFixed(2);
      sanitized.exclusion_ratio = parseFloat(row.exclusion_ratio || row.percent_taxable || 0).toFixed(4);
      sanitized.tax_rate = parseFloat(row.tax_rate || 0).toFixed(4);
      return sanitized;
    });

    // Clean and map investment sources for API payload
    const investments = scenario.value.investments;
    const cleanedInvestments = investments.map(row => {
      const sanitized = { ...row };
      // Ensure fields match expected database schema
      sanitized.owned_by = row.owned_by;
      sanitized.income_type = row.income_type;
      sanitized.income_name = row.income_name;
      sanitized.current_asset_balance = parseFloat(row.current_balance || 0).toFixed(2);
      sanitized.monthly_amount = parseFloat(row.withdrawal_amount || 0).toFixed(2); // Monthly withdrawal amount
      sanitized.monthly_contribution = parseFloat(row.monthly_contribution || 0).toFixed(2);
      sanitized.age_to_begin_withdrawal = row.start_age;
      sanitized.age_to_end_withdrawal = row.end_age;
      sanitized.rate_of_return = (parseFloat(row.growth_rate || 0) / 100).toFixed(4); // Convert percentage to decimal
      sanitized.cola = 0;
      sanitized.exclusion_ratio = 0;
      sanitized.tax_rate = 0;
      return sanitized;
    });

    // Combine income and investment sources
    const allIncomeSources = [...cleanedIncomeSources, ...cleanedInvestments];

    // Debug log of payload before submission
    const payload = {
      client: clientId,
      name: scenario.value.name,
      description: scenario.value.description,
      primary_retirement_age: scenario.value.primary_retirement_age,
      primary_medicare_age: scenario.value.primary_medicare_age,
      mortality_age: scenario.value.primary_lifespan,
      spouse_retirement_age: scenario.value.spouse_retirement_age,
      spouse_medicare_age: scenario.value.spouse_medicare_age,
      spouse_mortality_age: scenario.value.spouse_lifespan,
      income_sources: allIncomeSources,
      model_tax_change: scenario.value.model_tax_change,
      reduction_2030_ss: scenario.value.reduction_2030_ss,
      ss_adjustment_year: scenario.value.ss_adjustment_year,
      ss_adjustment_direction: scenario.value.ss_adjustment_direction,
      ss_adjustment_type: scenario.value.ss_adjustment_type,
      ss_adjustment_amount: scenario.value.ss_adjustment_amount,
      apply_standard_deduction: scenario.value.apply_standard_deduction,
      primary_blind: scenario.value.primary_blind,
      spouse_blind: scenario.value.spouse_blind,
      is_dependent: scenario.value.is_dependent,
      part_b_inflation_rate: scenario.value.part_b_inflation_rate,
      part_d_inflation_rate: scenario.value.part_d_inflation_rate,
      primary_state: scenario.value.primary_state,
    };
    console.log("🚀 Payload to submit:", payload);
    
    // Check if we're editing an existing scenario or creating/duplicating a new one
    const isEditMode = route.query.edit; // Only true edit mode updates existing scenario
    const isDuplicateMode = route.query.duplicate; // Duplicate mode creates new scenario
    let response;
    
    if (isEditMode) {
      // Update existing scenario - only in edit mode
      console.log("💰 INCOME_EDIT: Updating existing scenario with ID:", isEditMode);
      console.log("💰 INCOME_EDIT: About to make PUT request with payload:", payload);
      console.log("💰 INCOME_EDIT: URL:", `http://localhost:8000/api/scenarios/${isEditMode}/update/`);
      
      try {
        response = await axios.put(
          `http://localhost:8000/api/scenarios/${isEditMode}/update/`,
          payload
        );
        console.log("💰 INCOME_EDIT: ✅ PUT request successful:", response.data);
      } catch (error) {
        console.error("💰 INCOME_EDIT: ❌ PUT request failed:", error);
        console.error("💰 INCOME_EDIT: ❌ Error response:", error.response?.data);
        throw error;
      }
    } else {
      // Create new scenario - for both new creation and duplicate mode
      if (isDuplicateMode) {
        console.log("📋 Creating new scenario from duplicate of:", isDuplicateMode);
      } else {
        console.log("✨ Creating new scenario from scratch");
      }
      response = await axios.post(
        `http://localhost:8000/api/clients/${clientId}/scenarios/create/`,
        payload
      );
    }
    
    router.push(`/clients/${clientId}/scenarios/detail/${response.data.id}`);
  } catch (error) {
    console.error('❌ Error saving scenario:', error);
    console.error('❌ Response data:', error.response?.data);
    
    // Log specific income_sources errors
    if (error.response?.data?.income_sources) {
      console.error('❌ Income sources errors:', error.response.data.income_sources);
      error.response.data.income_sources.forEach((err, index) => {
        if (err && typeof err === 'object') {
          console.error(`❌ Income source ${index} errors:`, err);
        }
      });
    }
    
    console.error('❌ Status:', error.response?.status);
    console.error('❌ Full error response:', error.response);
    
    // Show more detailed error message
    let errorMessage = 'Failed to create scenario.\n\n';
    if (error.response?.data?.income_sources) {
      errorMessage += 'Income source errors:\n';
      error.response.data.income_sources.forEach((err, index) => {
        if (err && typeof err === 'object') {
          errorMessage += `- Income ${index + 1}: ${JSON.stringify(err)}\n`;
        }
      });
    }
    alert(errorMessage);
  }
}

onMounted(async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/clients/${clientId}/`);
    const client = response.data;
    clientData.value = client; // Store client data for age calculations
    if (!client || !client.first_name) {
      console.warn('Client data missing or incomplete:', client);
    }
    primaryFirstName.value = client.first_name ?? 'Primary';
    spouseFirstName.value = client.spouse?.first_name?.trim() || 'Spouse';
    clientTaxStatus.value = client.tax_status?.toLowerCase() ?? 'single';

    // Check if we're duplicating or editing a scenario
    const duplicateId = route.query.duplicate;
    const editId = route.query.edit;
    
    if (duplicateId) {
      await loadScenarioForDuplication(duplicateId);
    } else if (editId) {
      await loadScenarioForEditing(editId);
    }
  } catch (err) {
    if (err.response && err.response.status === 404) {
      console.error(`Client with ID ${clientId} not found (404).`);
    } else {
      console.error('Failed to load client data:', err);
    }
  }
});

async function loadScenarioForDuplication(scenarioId) {
  try {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };
    const response = await axios.get(`http://localhost:8000/api/scenarios/${scenarioId}/detail/?mode=duplicate`, { headers });
    const scenarioData = response.data;
    
    // Define investment account types
    const investmentTypes = ['Qualified', 'Non-Qualified', 'Roth', 'Inherited Traditional Spouse', 'Inherited Roth Spouse', 'Inherited Traditional Non-Spouse', 'Inherited Roth Non-Spouse'];
    
    // Separate income sources and investments
    const allIncomeSources = scenarioData.income || [];
    const rawInvestments = allIncomeSources.filter(item => investmentTypes.includes(item.income_type));
    const incomeSources = allIncomeSources.filter(item => !investmentTypes.includes(item.income_type));
    
    // Debug: Log raw investment data to see what fields are available
    console.log('Raw investment data from backend:', rawInvestments);
    
    // Map investment fields properly for frontend compatibility  
    const investments = rawInvestments.map(item => ({
      ...item,
      investment_name: item.income_name || item.investment_name || '', // Don't fall back to income_type
      current_balance: item.current_asset_balance || item.current_balance || 0,
      start_age: item.age_to_begin_withdrawal || item.start_age || 65,
      end_age: item.age_to_end_withdrawal || item.end_age || 95,
      growth_rate: item.rate_of_return || item.growth_rate || 0.06,
      withdrawal_amount: item.monthly_amount || item.withdrawal_amount || 0
    }));
    
    // Prefill the scenario object with properly separated data
    scenario.value = {
      ...scenario.value,
      ...scenarioData,
      income: incomeSources,
      investments: investments
    };
    
    console.log('Loaded scenario data for duplication:', scenarioData);
  } catch (error) {
    console.error('Failed to load scenario for duplication:', error);
    alert('Failed to load scenario data for duplication. Please try again.');
  }
}

async function loadScenarioForEditing(scenarioId) {
  try {
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };
    const response = await axios.get(`http://localhost:8000/api/scenarios/${scenarioId}/detail/?mode=edit`, { headers });
    const scenarioData = response.data;
    
    // Define investment account types
    const investmentTypes = ['Qualified', 'Non-Qualified', 'Roth', 'Inherited Traditional Spouse', 'Inherited Roth Spouse', 'Inherited Traditional Non-Spouse', 'Inherited Roth Non-Spouse'];
    
    // Separate income sources and investments
    const allIncomeSources = scenarioData.income || [];
    const rawInvestments = allIncomeSources.filter(item => investmentTypes.includes(item.income_type));
    const incomeSources = allIncomeSources.filter(item => !investmentTypes.includes(item.income_type));
    
    // Map investment fields properly for frontend compatibility  
    const investments = rawInvestments.map(item => ({
      ...item,
      investment_name: item.income_name || item.investment_name || '', // Don't fall back to income_type
      current_balance: item.current_asset_balance || item.current_balance || 0,
      start_age: item.age_to_begin_withdrawal || item.start_age || 65,
      end_age: item.age_to_end_withdrawal || item.end_age || 95,
      growth_rate: item.rate_of_return || item.growth_rate || 0.06,
      withdrawal_amount: item.monthly_amount || item.withdrawal_amount || 0
    }));
    
    // Prefill the scenario object with properly separated data for editing
    scenario.value = {
      ...scenario.value,
      ...scenarioData,
      // Keep the original ID for editing (unlike duplication)
      id: scenarioData.id,
      income: incomeSources,
      investments: investments
    };
    
    console.log('Loaded scenario data for editing:', scenarioData);
  } catch (error) {
    console.error('Failed to load scenario for editing:', error);
    alert('Failed to load scenario data for editing. Please try again.');
  }
}

function handleCancel() {
  // Check if we're editing by looking at route query params first
  const editId = route.query.edit;
  
  if (editId) {
    // If we have an edit query param, go back to that scenario's detail page
    console.log('🔙 Cancel from edit mode, returning to scenario:', editId);
    router.push(`/clients/${clientId}/scenarios/detail/${editId}`);
  } else if (scenario.value.id) {
    // Fallback: if scenario has an ID, go back to that scenario's detail page
    console.log('🔙 Cancel with scenario ID, returning to scenario:', scenario.value.id);
    router.push(`/clients/${clientId}/scenarios/detail/${scenario.value.id}`);
  } else {
    // If creating a new scenario (including duplication), go back to client page
    console.log('🔙 Cancel from create mode, returning to client page');
    router.push(`/clients/${clientId}`);
  }
}

function calculateSocialSecurityBenefit(amountAtFRA, startAge) {
  if (!amountAtFRA || !startAge) return '';
  const FRA = 67;
  const monthlyAdjustment = 0.0067;
  let adjustmentFactor = 1;

  if (startAge < FRA) {
    const monthsEarly = (FRA - startAge) * 12;
    adjustmentFactor -= monthsEarly * monthlyAdjustment;
  } else if (startAge > FRA) {
    const monthsDelayed = (startAge - FRA) * 12;
    adjustmentFactor += monthsDelayed * 0.0067; // Delayed credit
  }

  adjustmentFactor = Math.max(0.7, Math.min(adjustmentFactor, 1.24));
  return (amountAtFRA * adjustmentFactor).toFixed(2);
}

// Medicare Modal State and Functions
const showMedicareModal = ref(false);
const medicareModalData = ref({
  isPrimary: true,
  suggestedAge: 65
});

function handleMedicareAdjustment() {
  const { isPrimary, suggestedAge } = medicareModalData.value;
  if (isPrimary) {
    scenario.value.primary_medicare_age = suggestedAge;
  } else {
    scenario.value.spouse_medicare_age = suggestedAge;
  }
  showMedicareModal.value = false;
}

function checkMedicareAdjustment(income) {
  if (income.income_type !== 'Social Security') return;

  const isPrimary = income.owned_by === 'primary';
  const selectedSSAge = income.start_age;
  const medicareAge = isPrimary ? scenario.value.primary_medicare_age : scenario.value.spouse_medicare_age;

  if (selectedSSAge !== medicareAge) {
    medicareModalData.value = {
      isPrimary,
      suggestedAge: selectedSSAge
    };
    showMedicareModal.value = true;
  }
}
</script>

<style scoped>
.input {
  @apply w-full border border-gray-300 rounded px-3 py-2 mt-1;
}
.textarea {
  @apply w-full border border-gray-300 rounded px-3 py-2 h-24 mt-1;
}
.btn {
  @apply bg-gray-600 text-white px-4 py-2 rounded;
}
.btn-primary {
  @apply bg-blue-600 text-white px-6 py-2 rounded mt-4;
}
</style>