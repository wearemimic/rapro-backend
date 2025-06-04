<template>
  <div class="p-6 max-w-7xl mx-auto">
    <h2 class="text-2xl font-semibold mb-4">Create New Scenario</h2>

    <!-- Scenario Basics -->
    <div class="mb-6">
      <label class="block mb-1 font-medium">Scenario Name</label>
      <input v-model="scenario.name" class="input" type="text" placeholder="Enter scenario name" />

      <label class="block mt-4 mb-1 font-medium">Retirement Age</label>
      <input v-model.number="scenario.retirement_age" class="input" type="number" />

      <label class="block mt-4 mb-1 font-medium">Medicare Start Age</label>
      <input v-model.number="scenario.medicare_age" class="input" type="number" />

      <label class="block mt-4 mb-1 font-medium">Lifespan (Age)</label>
      <input v-model.number="scenario.lifespan" class="input" type="number" />

      <label class="block mt-4 mb-1 font-medium">Description (Rich Text)</label>
      <textarea v-model="scenario.description" class="textarea"></textarea>
    </div>

    <!-- Income Inputs -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold mb-2">Retirement Income Information</h3>

      <select v-model="newIncome.income_type" class="input">
        <option disabled value="">Select income type</option>
        <option v-for="option in incomeTypes" :key="option" :value="option">{{ option }}</option>
      </select>

      <button class="btn mt-2" @click="addIncome">Add Income Product</button>

      <div v-for="(income, index) in scenario.income" :key="income.id" class="border p-4 mt-4 rounded shadow">
        <p class="font-medium">{{ income.income_type }}</p>
        <label class="block mt-2">Owner</label>
        <select v-model="income.owned_by" class="input">
          <option value="primary">Primary</option>
          <option value="spouse">Spouse</option>
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

    <!-- Submit -->
    <button class="btn-primary" @click="submitScenario">Create Scenario</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

console.log('Generated UUID:', uuidv4());

const route = useRoute();
const router = useRouter();
const clientId = route.params.id;

const scenario = ref({
  name: '',
  retirement_age: 65,
  medicare_age: 65,
  lifespan: 90,
  description: '',
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
    const response = await axios.post(`/api/clients/${clientId}/scenarios/create/`, scenario.value);
    router.push(`/clients/${clientId}/scenarios/${response.data.id}`);
  } catch (err) {
    console.error('Failed to create scenario:', err);
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