<template>
  <div>
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Types of Income in Scenario</h5>
        <ul>
          <li v-for="incomeType in incomeFields" :key="incomeType">
            {{ incomeType }}
            <Graph :data="getGraphData(incomeType)" />
          </li>
        </ul>
      </div>
    </div>
    
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Assets in Scenario</h5>
        <ul>
          <li v-for="asset in assetDetails" :key="asset.id" class="asset-details">
            <div>
              <div v-for="(value, key) in asset" :key="key">
                <strong>{{ key }}:</strong> {{ value }}
              </div>
              <pre style="background:#f8f9fa; border:1px solid #eee; padding:8px; margin-top:8px;">{{ asset }}</pre>
            </div>
            <Graph :data="getGraphData(asset.income_type)" style="height: 50px;" />
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
      }
      // Find the asset for this incomeType
      const asset = this.assetDetails.find(a => {
        if (!a.income_type) return false;
        const lower = a.income_type.toLowerCase();
        if (normalizedType === '401k') return lower.includes('401k');
        if (normalizedType === 'ira') return lower.includes('ira');
        return false;
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
      // Simulate each year
      let balance = startBalance;
      const balances = [];
      const withdrawals = [];
      for (let age = currentAge; age <= endAge; age++) {
        // Pre-retirement: accumulate
        if (age < withdrawalStartAge) {
          balance += annualContribution;
        }
        // Growth
        balance *= (1 + growthRate);
        // Withdrawals (if in withdrawal phase)
        let withdrawal = 0;
        if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
          withdrawal = annualWithdrawal;
          if (balance < withdrawal) withdrawal = balance;
          balance -= withdrawal;
        }
        // RMDs (if age >= rmdStartAge)
        if (age >= rmdStartAge && balance > 0) {
          // IRS Uniform Lifetime Table divisor for RMDs (approximate)
          const rmdDivisor = Math.max(27.4 - (age - 72), 1.9); // 27.4 at 73, 26.5 at 74, ...
          const rmd = balance / rmdDivisor;
          if (rmd > withdrawal) {
            const extraRmd = rmd - withdrawal;
            if (balance < extraRmd) balance = 0;
            else balance -= extraRmd;
            withdrawal = rmd;
          }
        }
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