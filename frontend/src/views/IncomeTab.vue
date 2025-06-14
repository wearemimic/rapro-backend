<template>
  <div>
    
    
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Assets in Scenario</h5>
        <ul>
          <li v-for="asset in assetDetails" :key="asset.id" class="asset-details" style="margin-bottom: 2rem;">
            <div>
              <h5 style="margin-bottom: 0.5rem; text-transform: capitalize;">{{ asset.income_type.replace(/_/g, ' ') }}</h5>
              <div style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
                <template v-if="asset.income_type === 'social_security'">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Amount at FRA:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>COLA %:</strong> {{ asset.cola }}</div>
                </template>
                <template v-else-if="['Traditional_401k', 'Roth_401k', 'Traditional_IRA', 'Roth_IRA'].includes(asset.income_type)">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Current Balance:</strong> ${{ parseFloat(asset.current_asset_balance || 0).toLocaleString() }}</div>
                  <div><strong>Monthly Contribution:</strong> ${{ parseFloat(asset.monthly_contribution || 0).toLocaleString() }}</div>
                  <div><strong>Growth Rate (%):</strong> {{ asset.rate_of_return }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>Monthly Withdrawal:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                </template>
                <template v-else-if="asset.income_type === 'Pension'">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Monthly Income:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>COLA %:</strong> {{ asset.cola }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                </template>
                <template v-else-if="asset.income_type === 'Annuity'">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Monthly Income:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>% Taxable:</strong> {{ asset.tax_rate }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                </template>
                <template v-else-if="asset.income_type === 'Rental_Income'">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Monthly Income:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                </template>
                <template v-else-if="['Wages', 'Reverse_Mortgage'].includes(asset.income_type)">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Amount per Month:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                </template>
                <template v-else>
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Monthly Amount:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                </template>
              </div>
            </div>
            <Graph :data="getGraphData(asset.income_type)" :height="200" />
          </li>
        </ul>
      </div>
    </div>

  </div>
</template>

<script>
import Graph from '../components/Graph.vue';

export default {
  components: {
    Graph
  },
  props: {
    scenario: {
      type: Object,
      required: true
    },
    assetDetails: {
      type: Array,
      required: true
    },
    scenarioResults: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      preRetirementIncome: 0,
      availableYears: [],
      conversionStartYear: null,
      yearsToConvert: 0,
      rothGrowthRate: 0
    };
  },
  computed: {
    incomeFields() {
      if (!this.scenarioResults || !this.scenarioResults.length) return [];

      const firstRow = this.scenarioResults[0];
      const knownKeys = [
        'year', 'primary_age', 'spouse_age', 'gross_income', 'taxable_income', 
        'federal_tax', 'total_medicare', 'remaining_ssi', 'social_security_benefit',
        'part_b', 'part_d', 'medicare_income'
      ];

      // List any field that seems to represent income but is not excluded
      return Object.keys(firstRow)
        .filter(key => key.includes('income') && !knownKeys.includes(key));
    }
  },
  methods: {
    getGraphData(incomeType) {
      // Normalize incomeType for retirement accounts
      let normalizedType = incomeType;
      if (typeof incomeType === 'string') {
        const lower = incomeType.toLowerCase();
        if (lower.includes('401k')) normalizedType = '401k';
        else if (lower.includes('ira')) normalizedType = 'ira';
        else if (lower.includes('social_security')) normalizedType = 'social_security';
      }
      // Find the asset for this incomeType
      const asset = this.assetDetails.find(a => {
        if (!a.income_type) return false;
        const lower = a.income_type.toLowerCase();
        if (normalizedType === '401k') return lower.includes('401k');
        if (normalizedType === 'ira') return lower.includes('ira');
        if (normalizedType === 'social_security') return lower.includes('social_security');
        return lower === normalizedType;
      });
      if (!asset) return {};
      // Get scenario ages
      const currentAge = 65; // TODO: Replace with actual current age if available
      const endAge = this.scenario?.primary_lifespan || 90;
      const retirementAge = this.scenario?.primary_retirement_age || 65;
      const rmdStartAge = 73; // SECURE Act 2.0 default
      // Asset fields
      const startBalance = parseFloat(asset.current_asset_balance || 0);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const growthRate = parseFloat(asset.rate_of_return || 0) / 100;
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || retirementAge);
      const withdrawalEndAge = parseInt(asset.age_to_end_withdrawal || endAge);
      const annualWithdrawal = parseFloat(asset.monthly_amount || 0) * 12;
      // Social Security: payout graph only
      if (normalizedType === 'social_security') {
        const cola = parseFloat(asset.cola || 0) / 100;
        const payouts = [];
        const labels = [];
        let payout = annualWithdrawal;
        for (let age = currentAge; age <= endAge; age++) {
          labels.push(age);
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            payouts.push(parseFloat(payout.toFixed(2)));
            payout *= (1 + cola);
          } else {
            payouts.push(0);
          }
        }
        return {
          labels,
          datasets: [
            {
              label: 'Annual Payout',
              data: payouts,
              borderColor: 'blue',
              fill: false
            }
          ]
        };
      }
      // 401k/IRA: keep current logic
      if (normalizedType === '401k' || normalizedType === 'ira') {
        let balance = startBalance;
        const balances = [];
        const withdrawals = [];
        for (let age = currentAge; age <= endAge; age++) {
          // Pre-retirement: accumulate
          if (age < withdrawalStartAge) {
            balance += annualContribution;
            balance *= (1 + growthRate);
            balances.push(Math.max(balance, 0));
            withdrawals.push(0);
            continue;
          }
          // Calculate RMD if applicable
          let rmd = 0;
          if (age >= rmdStartAge && balance > 0) {
            const rmdDivisor = Math.max(27.4 - (age - 72), 1.9);
            rmd = balance / rmdDivisor;
          }
          // Calculate withdrawal: greater of annualWithdrawal or RMD (if RMD applies)
          let withdrawal = annualWithdrawal;
          if (rmd > withdrawal) {
            withdrawal = rmd;
          }
          // Don't withdraw more than the balance
          if (withdrawal > balance) {
            withdrawal = balance;
          }
          // Deduct withdrawal, then grow remaining balance
          balance -= withdrawal;
          balance = Math.max(balance, 0);
          balance *= (1 + growthRate);
          balances.push(Math.max(balance, 0));
          withdrawals.push(withdrawal);
        }
        const labels = Array.from({length: endAge - currentAge + 1}, (_, i) => currentAge + i);
        return {
          labels,
          datasets: [
            {
              label: 'Balance',
              data: balances,
              borderColor: 'green',
              fill: false
            },
            {
              label: 'Withdrawals',
              data: withdrawals,
              borderColor: 'red',
              fill: false
            }
          ]
        };
      }
      // Other types: simple payout graph if monthly_amount is present
      if (annualWithdrawal > 0) {
        const payouts = [];
        const labels = [];
        for (let age = currentAge; age <= endAge; age++) {
          labels.push(age);
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            payouts.push(annualWithdrawal);
          } else {
            payouts.push(0);
          }
        }
        return {
          labels,
          datasets: [
            {
              label: 'Annual Payout',
              data: payouts,
              borderColor: 'purple',
              fill: false
            }
          ]
        };
      }
      // Default: empty
      return {};
    },
    recalculateConversion() {
      // Implement recalculation logic
    },
    saveRothConversionScenario() {
      // Implement save logic
    },
    exportComparisonReport() {
      // Implement PDF export logic
    }
  }
};
</script> 