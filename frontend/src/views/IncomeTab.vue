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
                <template v-else-if="asset.income_type === 'Qualified' || asset.income_type === 'Non-Qualified'">
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div><strong>Asset Type:</strong> {{ asset.income_type }}</div>
                  <div><strong>Starting Balance:</strong> ${{ parseFloat(asset.current_asset_balance || 0).toLocaleString() }}</div>
                  <div><strong>Monthly Contribution:</strong> ${{ parseFloat(asset.monthly_contribution || 0).toLocaleString() }}</div>
                  <div><strong>Growth Rate:</strong> {{ (parseFloat(asset.rate_of_return || 0) * 100).toFixed(2) }}%</div>
                  <div><strong>Withdrawal Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>Withdrawal End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                  <div><strong>Monthly Withdrawal:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div v-if="asset.income_type === 'Qualified'" style="color: orange;">
                    <strong>RMDs Required:</strong> Starting at age 73
                  </div>
                  <div v-if="getProjectedBalance(asset)" style="color: green; font-weight: bold;">
                    <strong>Projected Balance at Retirement:</strong> ${{ getProjectedBalance(asset).toLocaleString() }}
                  </div>
                </template>
                <template v-else>
                  <div><strong>Owner:</strong> {{ asset.owned_by }}</div>
                  <div v-if="asset.current_asset_balance"><strong>Balance:</strong> ${{ parseFloat(asset.current_asset_balance || 0).toLocaleString() }}</div>
                  <div><strong>Monthly Amount:</strong> ${{ parseFloat(asset.monthly_amount || 0).toLocaleString() }}</div>
                  <div><strong>Start Age:</strong> {{ asset.age_to_begin_withdrawal }}</div>
                  <div><strong>End Age:</strong> {{ asset.age_to_end_withdrawal }}</div>
                  <div v-if="asset.rate_of_return"><strong>Growth Rate:</strong> {{ (parseFloat(asset.rate_of_return || 0) * 100).toFixed(2) }}%</div>
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
      // Find the asset for this incomeType
      const asset = this.assetDetails.find(a => a.income_type === incomeType);
      if (!asset) return {};
      
      // Get client's actual current age from birthdate
      const birthYear = new Date(this.scenario?.client?.birthdate).getFullYear();
      const currentYear = new Date().getFullYear();
      let actualCurrentAge = currentYear - birthYear;
      
      console.log(`Client birthdate: ${this.scenario?.client?.birthdate}, Birth year: ${birthYear}, Current age: ${actualCurrentAge}`);
      
      // If we couldn't get the birthdate, use a fallback
      if (!birthYear || isNaN(actualCurrentAge)) {
        actualCurrentAge = 50; // Fallback value based on common scenario
        console.warn('Could not determine client age from birthdate, using fallback age:', actualCurrentAge);
      }
      
      // Get scenario ages
      const endAge = this.scenario?.mortality_age || 90;
      const retirementAge = this.scenario?.retirement_age || 65;
      const rmdStartAge = 73; // SECURE Act 2.0 default
      
      // Asset fields
      const startBalance = parseFloat(asset.current_asset_balance || 0);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const growthRate = parseFloat(asset.rate_of_return || 0) / 100;
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || retirementAge);
      const withdrawalEndAge = parseInt(asset.age_to_end_withdrawal || endAge);
      const annualWithdrawal = parseFloat(asset.monthly_amount || 0) * 12;

      // Qualified/Non-Qualified: handle investment accounts with balances
      if (incomeType === 'Qualified' || incomeType === 'Non-Qualified' || startBalance > 0) {
        console.log(`Retirement account data:`, {
          type: asset.income_type,
          currentAge: actualCurrentAge,
          retirementAge: withdrawalStartAge,
          startBalance,
          monthlyContribution,
          growthRate: growthRate * 100 + '%'
        });
        
        // Calculate the actual projection
        const balances = [];
        const withdrawals = [];
        const contributions = [];
        const labels = [];
        
        // Start with the current balance at current age
        let currentBalance = startBalance;
        
        // Generate data points for each year from current age to end age
        for (let age = actualCurrentAge; age <= endAge; age++) {
          labels.push(age);
          
          // Debugging
          if (age === actualCurrentAge) {
            console.log(`Initial balance at age ${age}: $${currentBalance.toFixed(2)}`);
          }
          
          // Pre-retirement phase: apply contributions and growth
          if (age < withdrawalStartAge) {
            // Add contribution for this year
            const yearlyContribution = annualContribution;
            contributions.push(yearlyContribution);
            
            // Apply contribution
            currentBalance += yearlyContribution;
            
            // Apply growth
            currentBalance *= (1 + growthRate);
            
            // Store balance and zero withdrawal
            balances.push(parseFloat(currentBalance.toFixed(2)));
            withdrawals.push(0);
            
            // Debug log at specific intervals
            if (age === actualCurrentAge || age === actualCurrentAge + 5 || age === withdrawalStartAge - 1) {
              console.log(`Age ${age}: Balance after contribution and growth: $${currentBalance.toFixed(2)}`);
            }
          } 
          // Retirement phase: apply withdrawals and growth
          else {
            // No more contributions
            contributions.push(0);
            
            // Calculate RMD if applicable (only for Qualified accounts)
            let rmd = 0;
            if (age >= rmdStartAge && asset.income_type === 'Qualified') {
              const rmdTable = {
                72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0,
                79: 21.1, 80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0,
                86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8,
                93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4,
                101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9, 105: 4.5, 106: 4.2, 107: 3.9,
                108: 3.7, 109: 3.4, 110: 3.1, 111: 2.9, 112: 2.6, 113: 2.4, 114: 2.1, 115: 1.9
              };
              
              const divisor = rmdTable[age] || (age > 115 ? 1.9 : 27.4);
              rmd = currentBalance / divisor;
              
              if (age === rmdStartAge) {
                console.log(`Age ${age}: First RMD calculation: $${rmd.toFixed(2)} (balance: $${currentBalance.toFixed(2)}, divisor: ${divisor})`);
              }
            }
            
            // Calculate withdrawal amount (greater of specified withdrawal or RMD)
            let withdrawal = annualWithdrawal;
            if (rmd > withdrawal) {
              withdrawal = rmd;
            }
            
            // Don't withdraw more than available
            if (withdrawal > currentBalance) {
              withdrawal = currentBalance;
            }
            
            // Apply withdrawal
            currentBalance -= withdrawal;
            withdrawals.push(parseFloat(withdrawal.toFixed(2)));
            
            // Apply growth to remaining balance
            currentBalance *= (1 + growthRate);
            
            // Store balance
            balances.push(parseFloat(currentBalance.toFixed(2)));
            
            // Debug log at key points
            if (age === withdrawalStartAge || age === rmdStartAge || age === endAge) {
              console.log(`Age ${age}: Withdrawal: $${withdrawal.toFixed(2)}, Balance after withdrawal and growth: $${currentBalance.toFixed(2)}`);
            }
          }
        }
        
        // Log final dataset
        console.log(`Final projection generated: ${labels.length} data points from age ${actualCurrentAge} to ${endAge}`);
        console.log(`Balance at retirement age (${withdrawalStartAge}): $${balances[withdrawalStartAge - actualCurrentAge].toLocaleString()}`);
        
        return {
          labels,
          datasets: [
            {
              label: 'Balance',
              data: balances,
              borderColor: 'green',
              backgroundColor: 'rgba(0, 128, 0, 0.1)',
              fill: true
            },
            {
              label: 'Withdrawals',
              data: withdrawals,
              borderColor: 'red',
              backgroundColor: 'rgba(255, 0, 0, 0.1)',
              fill: true
            },
            {
              label: 'Contributions',
              data: contributions,
              borderColor: 'blue',
              backgroundColor: 'rgba(0, 0, 255, 0.1)',
              fill: true
            }
          ]
        };
      }
      // Social Security: payout graph only
      if (incomeType === 'social_security') {
        const cola = parseFloat(asset.cola || 0) / 100;
        const payouts = [];
        const labels = [];
        
        // Monthly amount adjusted annually by COLA
        const monthlyAmount = parseFloat(asset.monthly_amount || 0);
        const annualAmount = monthlyAmount * 12;
        
        let payout = annualAmount;
        
        // We'll simulate from their actual current age
        for (let age = actualCurrentAge; age <= endAge; age++) {
          labels.push(age);
          
          // Check if we're in the eligible age range for benefits
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            payouts.push(parseFloat(payout.toFixed(2)));
            
            // Apply COLA for next year
            payout *= (1 + cola);
          } else {
            payouts.push(0);
          }
        }
        
        return {
          labels,
          datasets: [
            {
              label: 'Social Security Benefits',
              data: payouts,
              borderColor: '#1877F2',
              backgroundColor: 'rgba(24, 119, 242, 0.1)',
              fill: true
            }
          ]
        };
      }
      // Other types: simple payout graph if monthly_amount is present
      if (annualWithdrawal > 0) {
        const payouts = [];
        const labels = [];
        
        // We'll simulate from their actual current age
        for (let age = actualCurrentAge; age <= endAge; age++) {
          labels.push(age);
          
          // Check if we're in the eligible age range for payouts
          if (age >= withdrawalStartAge && age <= withdrawalEndAge) {
            // Apply COLA adjustment if applicable
            let yearlyPayout = annualWithdrawal;
            if (asset.cola) {
              const cola = parseFloat(asset.cola || 0) / 100;
              const yearsWithCola = age - withdrawalStartAge;
              yearlyPayout *= Math.pow(1 + cola, yearsWithCola);
            }
            
            payouts.push(parseFloat(yearlyPayout.toFixed(2)));
          } else {
            payouts.push(0);
          }
        }
        
        // Choose appropriate color based on income type
        let borderColor = '#8959A8'; // Default purple
        let backgroundColor = 'rgba(137, 89, 168, 0.1)';
        
        if (normalizedType === 'pension') {
          borderColor = '#5B8C5A'; // Green for pension
          backgroundColor = 'rgba(91, 140, 90, 0.1)';
        } else if (normalizedType === 'annuity') {
          borderColor = '#D89614'; // Gold for annuity
          backgroundColor = 'rgba(216, 150, 20, 0.1)';
        } else if (normalizedType === 'rental_income') {
          borderColor = '#E15759'; // Red for rental
          backgroundColor = 'rgba(225, 87, 89, 0.1)';
        }
        
        return {
          labels,
          datasets: [
            {
              label: `${asset.income_type.replace(/_/g, ' ')} Income`,
              data: payouts,
              borderColor: borderColor,
              backgroundColor: backgroundColor,
              fill: true
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
    },
    getProjectedBalance(asset) {
      // Only calculate for retirement accounts
      if (!['Traditional_401k', 'Roth_401k', 'Traditional_IRA', 'Roth_IRA'].includes(asset.income_type)) {
        return null;
      }
      
      // Get the necessary data
      const startBalance = parseFloat(asset.current_asset_balance || 0);
      const monthlyContribution = parseFloat(asset.monthly_contribution || 0);
      const annualContribution = monthlyContribution * 12;
      const growthRate = parseFloat(asset.rate_of_return || 0) / 100;
      const withdrawalStartAge = parseInt(asset.age_to_begin_withdrawal || 65);
      
      // Get the client's actual current age
      const birthYear = new Date(this.scenario?.client?.birthdate).getFullYear();
      if (!birthYear) return null;
      
      const currentYear = new Date().getFullYear();
      const actualCurrentAge = currentYear - birthYear;
      
      // Calculate years until retirement
      const yearsToRetirement = withdrawalStartAge - actualCurrentAge;
      if (yearsToRetirement <= 0) return startBalance; // Already at or past retirement
      
      // Calculate projected balance at retirement
      let projectedBalance = startBalance;
      for (let i = 0; i < yearsToRetirement; i++) {
        projectedBalance += annualContribution;
        projectedBalance *= (1 + growthRate);
      }
      
      return parseFloat(projectedBalance.toFixed(2));
    }
  }
};
</script> 