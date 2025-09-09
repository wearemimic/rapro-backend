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
                          <option v-for="age in getAgeOptions(income.income_type)" :key="age" :value="age">{{ age }}</option>
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
                        <input v-model.number="income.rate_of_return" type="number" class="form-control" />
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
                          <option v-for="age in getAgeOptions(income.income_type)" :key="age" :value="age">{{ age }}</option>
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
                          <option v-for="age in getAgeOptions(income.income_type)" :key="age" :value="age">{{ age }}</option>
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
              <button class="btn btn-primary" @click="addNewInvestment">
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
                    <th class="text-center" style="width: 140px;">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="investment in group" :key="investment.id">
                    <td>{{ investment.owned_by === 'primary' ? primaryFirstName : spouseFirstName }}</td>
                    <td>{{ investment.investment_name || investment.income_name }}</td>
                    <td>{{ formatCurrencyDisplay(investment.current_balance || 0) }}</td>
                    <td>{{ investment.rate_of_return ? investment.rate_of_return.toFixed(1) : '0' }}%</td>
                    <td>{{ investment.start_age }}</td>
                    <td>{{ investment.end_age }}</td>
                    <td class="text-center">
                      <div class="btn-group" role="group">
                        <button 
                          class="btn btn-sm btn-outline-primary" 
                          @click="editInvestment(investment)"
                          title="Edit Investment"
                        >
                          <i class="bi bi-pencil"></i> Edit
                        </button>
                        <button 
                          class="btn btn-sm btn-outline-danger" 
                          @click="removeInvestmentById(investment.id)"
                          title="Remove Investment"
                        >
                          <i class="bi bi-trash"></i> Remove
                        </button>
                      </div>
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
              <select v-model="scenario.part_b_inflation_rate" class="form-control">
                <option v-for="rate in medicareInflationRates" :key="rate.period" :value="rate.part_b_rate.toString()">
                  {{ rate.description }} ({{ rate.part_b_rate }}%)
                </option>
                <option value="custom">Custom Inflation Rate</option>
              </select>
              <input v-if="scenario.part_b_inflation_rate === 'custom'" 
                     v-model="customPartBRate" 
                     @input="scenario.part_b_inflation_rate = customPartBRate"
                     type="number" 
                     step="0.1" 
                     class="form-control mt-2" 
                     placeholder="Enter custom rate (%)" />
            </td>
          </tr>
          <tr>
            <td><input type="checkbox" class="form-check-input" checked /></td>
            <td>Medicare Part D</td>
            <td>$0</td>
            <td>
              <select v-model="scenario.part_d_inflation_rate" class="form-control">
                <option v-for="rate in medicareInflationRates" :key="rate.period" :value="rate.part_d_rate.toString()">
                  {{ rate.description }} ({{ rate.part_d_rate }}%)
                </option>
                <option value="custom">Custom Inflation Rate</option>
              </select>
              <input v-if="scenario.part_d_inflation_rate === 'custom'" 
                     v-model="customPartDRate" 
                     @input="scenario.part_d_inflation_rate = customPartDRate"
                     type="number" 
                     step="0.1" 
                     class="form-control mt-2" 
                     placeholder="Enter custom rate (%)" />
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
  :editing-investment="editingInvestment"
  :show="showInvestmentModal"
  @save="handleInvestmentSave"
  @cancel="cancelInvestmentEdit"
/>


</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { API_CONFIG } from '@/config';
import { v4 as uuidv4 } from 'uuid';
import InvestmentModal from '../components/InvestmentModal.vue';
import ScenarioHeader from '../components/ScenarioHeader.vue';
import { useAuthStore } from '../stores/auth';
import { createCurrencyHandlers, formatCurrency, formatCurrencyDisplay } from '../utils/currencyFormatter';

const route = useRoute();
const router = useRouter();
const clientId = route.params.id;

// Check if we're in edit mode
const isEditMode = computed(() => !!route.query.edit);

const primaryFirstName = ref('Primary');
const spouseFirstName = ref('Spouse');
const clientTaxStatus = ref('single');
const clientData = ref(null);
const editingInvestment = ref(null);
const medicareInflationRates = ref([]);
const customPartBRate = ref('');
const customPartDRate = ref('');

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
  
  // Set appropriate start age based on income type
  let defaultStartAge = 65;
  if (['Wages', 'Rental_Income', 'Other'].includes(newIncome.value.income_type)) {
    defaultStartAge = youngestCurrentAge.value;
  }
  
  scenario.value.income.push({
    id: uuidv4(),
    income_type: newIncome.value.income_type,
    owned_by: 'primary',
    start_age: defaultStartAge,
    end_age: 90,
    current_balance: 0,
    monthly_contribution: 0,
    rate_of_return: null
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
  
  // Check if birth date is valid
  if (isNaN(birth.getTime())) {
    console.warn('ScenarioCreate: Invalid birthdate detected:', birthdate);
    return 65; // Return default age for invalid dates
  }
  
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  
  // Debug log for negative ages
  if (age < 0) {
    console.warn('ScenarioCreate: Negative age calculated:', {
      birthdate,
      today: today.toISOString(),
      birth: birth.toISOString(),
      calculatedAge: age
    });
    return 65; // Return reasonable default for negative ages
  }
  
  // Cap age to reasonable bounds
  if (age > 120) {
    console.warn('ScenarioCreate: Unreasonably high age calculated:', age, 'for birthdate:', birthdate);
    return 65;
  }
  
  return age;
};

const primaryCurrentAge = computed(() => {
  const age = clientData.value?.birthdate ? calculateAge(clientData.value.birthdate) : 65;
  console.log('ScenarioCreate: Primary age calculation:', {
    birthdate: clientData.value?.birthdate,
    calculatedAge: age,
    clientData: clientData.value ? 'loaded' : 'not loaded'
  });
  return age;
});

const spouseCurrentAge = computed(() => {
  const age = clientData.value?.spouse?.birthdate ? calculateAge(clientData.value.spouse.birthdate) : 65;
  console.log('ScenarioCreate: Spouse age calculation:', {
    birthdate: clientData.value?.spouse?.birthdate,
    calculatedAge: age,
    hasSpouse: !!clientData.value?.spouse
  });
  return age;
});

// Calculate the youngest person's current age (for income types that should start from current age)
const youngestCurrentAge = computed(() => {
  if (isSingle.value) {
    return primaryCurrentAge.value;
  }
  return Math.min(primaryCurrentAge.value, spouseCurrentAge.value);
});

// Dynamic age options based on income type
const getAgeOptions = (incomeType, startAge = null) => {
  let minAge, maxAge;
  
  if (['Wages', 'Rental_Income', 'Other'].includes(incomeType)) {
    // For these income types, start from current age of youngest person
    minAge = startAge || youngestCurrentAge.value;
    maxAge = 100;
  } else {
    // For other income types (social security, pension, etc.), use standard retirement age range
    minAge = 62;
    maxAge = 100;
  }
  
  const ageRange = maxAge - minAge + 1;
  return Array.from({ length: ageRange }, (_, i) => minAge + i);
};

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
function handleInvestmentSave(investmentData) {
  // Growth rate is already in percentage format, no conversion needed
  
  if (investmentData.isEdit) {
    // Update existing investment
    const index = scenario.value.investments.findIndex(inv => inv.id === investmentData.id);
    if (index !== -1) {
      // Remove the isEdit flag before storing
      delete investmentData.isEdit;
      scenario.value.investments[index] = investmentData;
    }
    // Clear editing state
    editingInvestment.value = null;
  } else {
    // Add new investment
    delete investmentData.isEdit; // Remove the flag
    scenario.value.investments.push(investmentData);
  }
  
  // Close the modal
  showInvestmentModal.value = false;
}

function removeInvestmentById(id) {
  scenario.value.investments = scenario.value.investments.filter(investment => investment.id !== id);
}

// Load client data function
async function loadClientData() {
  if (clientData.value) return; // Already loaded
  
  try {
    const response = await axios.get(`${API_CONFIG.API_URL}/clients/${clientId}/`);
    const client = response.data;
    clientData.value = client;
    console.log('ScenarioCreate: Client data loaded for age calculations:', {
      birthdate: client?.birthdate,
      spouseBirthdate: client?.spouse?.birthdate
    });
  } catch (error) {
    console.error('Error loading client data:', error);
  }
}

// Load Medicare inflation rates function
async function loadMedicareInflationRates() {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_CONFIG.API_URL}/medicare/inflation-rates/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    medicareInflationRates.value = response.data.inflation_rates;
    console.log('ScenarioCreate: Medicare inflation rates loaded:', medicareInflationRates.value);
  } catch (error) {
    console.error('Error loading Medicare inflation rates:', error);
    // Set fallback rates if API fails
    medicareInflationRates.value = [
      { period: '1_year', description: 'Last 1 year', part_b_rate: 5.9, part_d_rate: 3.5 },
      { period: '5_years', description: 'Last 5 years', part_b_rate: 6.8, part_d_rate: 4.2 },
      { period: '10_years', description: 'Last 10 years', part_b_rate: 4.9, part_d_rate: 3.8 },
      { period: 'inception', description: 'From inception', part_b_rate: 4.3, part_d_rate: 3.7 }
    ];
  }
}

// Modal visibility state
const showInvestmentModal = ref(false);

async function addNewInvestment() {
  // Clear any existing editing state to ensure modal opens in add mode
  editingInvestment.value = null;
  
  // Ensure client data is loaded before opening modal
  if (!clientData.value) {
    console.log('ScenarioCreate: Loading client data before opening investment modal');
    await loadClientData();
  }
  
  // Show the modal
  showInvestmentModal.value = true;
}

function cancelInvestmentEdit() {
  // Clear the editing state when user cancels
  editingInvestment.value = null;
  // Close the modal
  showInvestmentModal.value = false;
}

function editInvestment(investment) {
  // Set the investment being edited - this will trigger the modal to populate
  editingInvestment.value = investment;
  
  // Show the modal
  showInvestmentModal.value = true;
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
      sanitized.rate_of_return = parseFloat(row.rate_of_return || 0) / 100; // Convert percentage to decimal for backend rate_of_return field
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
      federal_standard_deduction: scenario.value.federal_standard_deduction,
      state_standard_deduction: scenario.value.state_standard_deduction,
      custom_annual_deduction: scenario.value.custom_annual_deduction,
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
      console.log("💰 INCOME_EDIT: URL:", `${API_CONFIG.API_URL}/scenarios/${isEditMode}/update/`);
      
      try {
        response = await axios.put(
          `${API_CONFIG.API_URL}/scenarios/${isEditMode}/update/`,
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
        `${API_CONFIG.API_URL}/clients/${clientId}/scenarios/create/`,
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
    // Load client data and Medicare inflation rates concurrently
    await Promise.all([
      loadClientData(),
      loadMedicareInflationRates()
    ]);
    const client = clientData.value;
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
    const response = await axios.get(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/edit/?mode=duplicate`, { headers });
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
      rate_of_return: (item.rate_of_return || item.growth_rate) * 100, // Convert decimal to percentage for display
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
    const response = await axios.get(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/edit/?mode=edit`, { headers });
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
      rate_of_return: (item.rate_of_return || item.growth_rate) * 100, // Convert decimal to percentage for display
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
  console.log('🔙 handleCancel called');
  console.log('route.query:', route.query);
  console.log('route.params:', route.params);
  console.log('clientId:', clientId);
  
  try {
    // Check if we're editing by looking at route query params first
    const editId = route.query.edit;
    
    if (editId) {
      // If we have an edit query param, go back to that scenario's detail page
      const targetUrl = `/clients/${clientId}/scenarios/detail/${editId}`;
      console.log('🔙 Cancel from edit mode, navigating to:', targetUrl);
      router.push(targetUrl).then(() => {
        console.log('✅ Navigation successful');
      }).catch(err => {
        console.error('❌ Navigation failed:', err);
      });
    } else if (scenario.value.id) {
      // Fallback: if scenario has an ID, go back to that scenario's detail page
      const targetUrl = `/clients/${clientId}/scenarios/detail/${scenario.value.id}`;
      console.log('🔙 Cancel with scenario ID, navigating to:', targetUrl);
      router.push(targetUrl).then(() => {
        console.log('✅ Navigation successful');
      }).catch(err => {
        console.error('❌ Navigation failed:', err);
      });
    } else {
      // If creating a new scenario (including duplication), go back to client page
      const targetUrl = `/clients/${clientId}`;
      console.log('🔙 Cancel from create mode, navigating to:', targetUrl);
      router.push(targetUrl).then(() => {
        console.log('✅ Navigation successful');
      }).catch(err => {
        console.error('❌ Navigation failed:', err);
      });
    }
  } catch (error) {
    console.error('🔙 Error in handleCancel:', error);
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