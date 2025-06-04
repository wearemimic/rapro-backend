<template>
  <div class="p-6 max-w-7xl mx-auto">
    <div class="row" style="margin-top:20px;">
      <div class="col-sm-12"></div>
      <div class="card" style="max-width: 16rem;">
        <div class="card-body">
          <h3 class="card-title">Create New Scenario</h3>
          <div class="mb-3">
            <label class="block mb-1 font-medium">Scenario Name</label>
            <input v-model="scenario.name" type="text" class="input form-control" placeholder="Enter scenario name" />
          </div>
          <div class="mb-3">
            <label class="block mt-4 mb-1 font-medium">Description (Rich Text)</label>
            <textarea v-model="scenario.description"  class="form-control" placeholder="Textarea field" rows="4"></textarea>
          </div>
        </div>
      </div>
      <div class="card" style="max-width: 16rem;margin-left:10px;">
        <div class="card-body">
          <h3 class="card-title">Scenario Options</h3>
          <div class="mb-3">
            <label class="block mb-1 font-medium">Model Change in Taxes</label>
            <input class="js-toggle-switch form-check-input" type="checkbox"
           data-hs-toggle-switch-options='{
             "targetSelector": "#pricingCount1, #pricingCount2, #pricingCount3"
           }'>
          </div>
          <div class="mb-3">
            <label class="block mt-4 mb-1 font-medium">2030 Reduction in SS</label>
            <textarea v-model="scenario.description"  class="form-control" placeholder="Textarea field" rows="4"></textarea>
          </div>
        </div>
      </div>
      <div class="card" style="max-width: 16rem;margin-left:10px;">
        <div class="card-body">  
          <h3 class="text-lg font-semibold mb-2">Primary</h3>
          <label class="block mt-2">Retirement Age</label>
          <input v-model.number="scenario.primary_retirement_age" class="input" type="number" />
          <label class="block mt-2">Medicare Start Age</label>
          <input v-model.number="scenario.primary_medicare_age" class="input" type="number" />
          <label class="block mt-2">Lifespan (Age)</label>
          <input v-model.number="scenario.primary_lifespan" class="input" type="number" />
        </div>
      </div>
      <div v-if="clientTaxStatus !== 'single'" class="card" style="max-width: 16rem;margin-left:10px;">
        <div class="card-body">  
          <h3 class="text-lg font-semibold mb-2">Spouse</h3>
          <label class="block mt-2">Retirement Age</label>
          <input v-model.number="scenario.spouse_retirement_age" class="input" type="number" />
          <label class="block mt-2">Medicare Start Age</label>
          <input v-model.number="scenario.spouse_medicare_age" class="input" type="number" />
          <label class="block mt-2">Lifespan (Age)</label>
          <input v-model.number="scenario.spouse_lifespan" class="input" type="number" />
        </div>
      </div>
    </div>   

    <div class="row" style="margin-top:20px;">
      <div class="card" >
        <div class="card-body"> 
          <h3 class="card-title">Retirement Income Information</h3> 
          <select v-model="newIncome.income_type" class="input">
            <option disabled value="">Select income type</option>
            <option v-for="option in incomeTypes" :key="option" :value="option">{{ option }}</option>
          </select>
          <button class="btn mt-2" @click="addIncome">Add Income Product</button>

          <div v-for="(income, index) in scenario.income" :key="income.id" class="border p-4 mt-4 rounded shadow">
            <p class="font-medium">{{ income.income_type }}</p>
            <label class="block mt-2">Owner</label>
            <select v-model="income.owned_by" class="input">
              <option value="primary">{{ primaryFirstName }}</option>
              <option value="spouse">{{ spouseFirstName }}</option>
            </select>

            <template v-if="['401k', 'IRA', 'Roth IRA'].includes(income.income_type)">
              <label class="block mt-2">Current Balance</label>
              <input v-model.number="income.current_balance" class="input" type="number" />

              <label class="block mt-2">Monthly Contribution</label>
              <input v-model.number="income.monthly_contribution" class="input" type="number" />

              <label class="block mt-2">Growth Rate (%)</label>
              <input v-model.number="income.growth_rate" class="input" type="number" />
            </template>

            <label class="block mt-2">Start Age</label>
            <input v-model.number="income.start_age" class="input" type="number" />

            <label class="block mt-2">End Age</label>
            <input v-model.number="income.end_age" class="input" type="number" />

            <button class="btn mt-2 bg-red-500" @click="removeIncome(index)">Remove</button>
          </div>
        </div>
      </div>
    </div>
  

    <!-- Submit -->
    <button class="btn-primary" @click="submitScenario">Create Scenario</button>
    <button class="btn mt-2 ml-2" @click="router.push(`/clients/${clientId}`)">Cancel</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

console.log('Generated UUID:', uuidv4());

const route = useRoute();
const router = useRouter();
const clientId = route.params.id;

const primaryFirstName = ref('Primary');
const spouseFirstName = ref('Spouse');
const clientTaxStatus = ref('single');

const scenario = ref({
  name: '',
  description: '',
  primary_retirement_age: 65,
  primary_medicare_age: 65,
  primary_lifespan: 90,
  spouse_retirement_age: 65,
  spouse_medicare_age: 65,
  spouse_lifespan: 90,
  income: []
});

const incomeTypes = [
  '401k', 'IRA', 'Roth IRA', 'Annuity', 'Social Security Benefit',
  'Pension', 'Brokerage Account', 'Rental Income', 'Reverse Mortgage'
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

function removeIncome(index) {
  scenario.value.income.splice(index, 1);
}

async function submitScenario() {
  try {
    const response = await axios.post(`http://localhost:8000/api/clients/${clientId}/scenarios/create/`, scenario.value);
    router.push(`http://localhost:8000/clients/${clientId}/scenarios/${response.data.id}`);
  } catch (err) {
    console.error('Failed to create scenario:', err);
  }
}

onMounted(async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/clients/${clientId}/`);
    const client = response.data;
    if (!client || !client.first_name) {
      console.warn('Client data missing or incomplete:', client);
    }
    primaryFirstName.value = client.first_name ?? 'Primary';
    spouseFirstName.value = client.spouse_first_name ?? 'Spouse';
    clientTaxStatus.value = client.tax_status?.toLowerCase() ?? 'single';
  } catch (err) {
    if (err.response && err.response.status === 404) {
      console.error(`Client with ID ${clientId} not found (404).`);
    } else {
      console.error('Failed to load client data:', err);
    }
  }
});
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