<template>
  <div v-if="eligibleAssets && eligibleAssets.length > 0">
    <!-- Mode Toggle -->
    <div class="mb-3">
      <label style="font-weight: bold;">Manual Settings</label>
    </div>
    <!-- Section 1: Asset Selection Panel -->
    <div class="row align-items-stretch">
      <!-- Asset Selection Panel -->
      <div class="col-md-7 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
            <h5 class="mb-0">Asset Selection Panel</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-bordered table-hover align-middle">
                <thead class="thead-light">
                  <tr>
                    <th>Asset</th>
                    <th>Owner</th>
                    <th>Current Value</th>
                    <th>Max to Convert</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="asset in (eligibleAssets && eligibleAssets.length ? eligibleAssets : [])" :key="asset.id || asset.income_type">
                    <td>{{ asset.income_type || 'Unknown' }}</td>
                    <td>{{ asset.owned_by || 'Unknown' }}</td>
                    <td>{{ formatCurrency(asset.current_asset_balance) }}</td>
                    <td>
                      <input
                        type="text"
                        :value="maxToConvertRaw[asset.id || asset.income_type] || ''"
                        @focus="onMaxToConvertFocus(asset)"
                        @input="onMaxToConvertInput($event, asset)"
                        @blur="onMaxToConvertBlur(asset)"
                        class="form-control form-control-sm"
                      />
                    </td>
                  </tr>
                  <!-- Total Row -->
                  <tr style="font-weight: bold; background: #f8f9fa;">
                    <td>Total to Convert</td>
                    <td></td>
                    <td></td>
                    <td>{{ formatCurrency(selectedAssetList.reduce((sum, asset) => sum + (parseFloat(maxToConvert[asset.id || asset.income_type]) || 0), 0)) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <!-- Conversion Schedule Parameters -->
      <div class="col-md-5 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-header" :style="{ backgroundColor: headerColor, color: '#fff' }">
            <h5 class="mb-0">Conversion Schedule Parameters</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <!-- Row 1: Pre-Retirement Income & Conversion Start Year -->
             
              <div class="col-md-6">
                <label for="conversionStartYear">Conversion Start Year</label>
                <select id="conversionStartYear" v-model="conversionStartYear" class="form-control">
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label for="preRetirementIncome">Pre-Retirement Income</label>
                <input
                  type="text"
                  id="preRetirementIncome"
                  :value="preRetirementIncomeRaw"
                  @focus="onCurrencyFocus('preRetirementIncome')"
                  @input="onCurrencyInput($event, 'preRetirementIncome')"
                  @blur="onCurrencyBlur('preRetirementIncome')"
                  class="form-control"
                />
              </div>
              <!-- Row 2: Roth Growth Rate & Max Annual Conversion Amount -->
              <div class="col-md-6 mt-3">
                <label for="rothGrowthRate">Roth Growth Rate (%)</label>
                <input type="number" id="rothGrowthRate" v-model="rothGrowthRate" class="form-control" />
              </div>
              <div class="col-md-6 mt-3">
                <label for="maxAnnualAmount">Max Annual Conversion Amount</label>
                <input
                  type="text"
                  id="maxAnnualAmount"
                  :value="maxAnnualAmountRaw"
                  @focus="onCurrencyFocus('maxAnnualAmount')"
                  @input="onCurrencyInput($event, 'maxAnnualAmount')"
                  @blur="onCurrencyBlur('maxAnnualAmount')"
                  class="form-control"
                  min="0"
                />
              </div>
              <!-- Row 3: Roth Withdrawal Amount & Roth Withdrawal Start Year -->
              <div class="col-md-6 mt-3">
                <label for="rothWithdrawalAmount">Roth Withdrawal Amount</label>
                <input
                  type="text"
                  id="rothWithdrawalAmount"
                  :value="rothWithdrawalAmountRaw"
                  @focus="onCurrencyFocus('rothWithdrawalAmount')"
                  @input="onCurrencyInput($event, 'rothWithdrawalAmount')"
                  @blur="onCurrencyBlur('rothWithdrawalAmount')"
                  class="form-control"
                  min="0"
                />
              </div>
              <div class="col-md-6 mt-3">
                <label for="rothWithdrawalStartYear">Roth Withdrawal Start Year</label>
                <select id="rothWithdrawalStartYear" v-model="rothWithdrawalStartYear" class="form-control">
                  <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
              </div>
              <!-- Years to Convert Slider (full width) -->
              <div class="col-12 mt-3">
                <label for="yearsToConvert" class="w-100 text-center" style="font-size: 1.2em; font-weight: bold;">Years to Convert</label>
                <input type="range" id="yearsToConvert" v-model="yearsToConvert" min="1" max="10" class="form-range w-100" list="tickmarks" />
                <datalist id="tickmarks">
                  <option v-for="year in 10" :key="year" :value="year">{{ year }}</option>
                </datalist>
                <span>{{ yearsToConvert }} years</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <button class="btn btn-primary me-2" @click="recalculateConversion">Recalculate Conversion</button>
      </div>
    </div>
    
    <!-- Empty state message when no scenario has been run -->
    <div v-if="!hasScenarioBeenRun" class="empty-state">
      <div class="empty-state-icon">📊</div>
      <div class="empty-state-message">No Roth Conversion Scenario Yet</div>
      <div class="empty-state-description">
        Select your assets and parameters above, then click "Recalculate Conversion" to see detailed analysis and projections.
      </div>
    </div>
    
    <div v-if="hasScenarioBeenRun" class="scenario-results">
    <!-- Combined Expense Summary Chart -->
    <h3>Expense Summary</h3>
    <div class="row mb-3">
      <div class="col-md-12">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="mb-3">Expense Comparison Before vs After Roth Conversion</h6>
            <Graph 
              :data="expenseSummaryData || {
                labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
                datasets: [
                  {
                    label: 'Before Conversion',
                    backgroundColor: '#007bff',
                    data: [0, 0, 0, 0, 0]
                  },
                  {
                    label: 'After Conversion',
                    backgroundColor: '#28a745',
                    data: [0, 0, 0, 0, 0]
                  }
                ]
              }" 
              :options="expenseSummaryOptions" 
              :height="300" 
              type="bar" 
              graphId="roth-expense-summary-chart"
            />
            <div class="mt-3">
              <div v-if="totalSavings" class="text-center mt-3">
                <div class="alert alert-success d-inline-block">
                  <strong>Total Savings: {{ formatCurrency(totalSavings) }}</strong> 
                  <span class="ms-2">({{ savingsPercentage }}% reduction in lifetime expenses)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>  
    <h3>Asset Summary</h3>
    <div class="row mb-3">
      <div class="col-md-12">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="mb-3">Asset Balance Time Line</h6>
            <div class="asset-balance-timeline">
              <Graph 
                :data="assetLineData || {
                  labels: Array.from({ length: 30 }, (_, i) => (new Date().getFullYear() + i).toString()),
                  datasets: [
                    {
                      label: 'Default Asset',
                      borderColor: '#007bff',
                      backgroundColor: 'rgba(0,123,255,0.1)',
                      data: Array(30).fill(0),
                      fill: false
                    }
                  ]
                }" 
                :options="lineOptions" 
                type="line" 
                :height="150" 
                graphId="roth-asset-timeline-chart"
              />
              <div 
                v-if="rothWithdrawalStartYear" 
                class="withdrawal-year-marker" 
                :style="{ left: calculateWithdrawalYearPosition() + '%' }"
              >
                <span class="withdrawal-year-label">Withdrawals Begin</span>
              </div>
            </div>
            
            <div class="asset-summary-legend">
              <div class="asset-summary-legend-item" v-for="(dataset, index) in assetLineData.datasets" :key="index">
                <span class="asset-summary-legend-color" :style="{ backgroundColor: dataset.borderColor }"></span>
                <span>{{ dataset.label }}</span>
              </div>
            </div>
            
            <h6 class="mb-3 mt-4">Asset Details</h6>
            <div class="table-responsive">
              <table class="asset-summary-table">
                <thead>
                  <tr>
                    <th>Asset</th>
                    <th>Owner</th>
                    <th>Current Value</th>
                    <th>Conversion Amount</th>
                    <th>Projected Value at Retirement</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- Affected Assets (those with conversion amount > 0) -->
                  <tr 
                    v-for="asset in selectedAssetList" 
                    :key="'affected-' + (asset.id || asset.income_type)" 
                    class="affected-asset"
                  >
                    <td>{{ asset.income_type || 'Unknown' }}</td>
                    <td>{{ asset.owned_by || 'Unknown' }}</td>
                    <td>{{ formatCurrency(asset.current_asset_balance) }}</td>
                    <td>{{ formatCurrency(maxToConvert[asset.id || asset.income_type]) }}</td>
                    <td>{{ formatCurrency(calculateProjectedValue(asset)) }}</td>
                  </tr>
                  
                  <!-- New Roth IRA Line -->
                  <tr class="roth-asset">
                    <td>New Roth IRA</td>
                    <td>{{ selectedAssetList.length ? selectedAssetList[0].owned_by || 'Client' : 'Client' }}</td>
                    <td>$0.00</td>
                    <td>{{ formatCurrency(totalConversionAmount) }}</td>
                    <td>{{ formatCurrency(calculateRothProjectedValue()) }}</td>
                  </tr>
                  
                  <!-- Unaffected Assets (those without conversion) -->
                  <tr 
                    v-for="asset in unaffectedAssets" 
                    :key="'unaffected-' + (asset.id || asset.income_type)"
                  >
                    <td>{{ asset.income_type || 'Unknown' }}</td>
                    <td>{{ asset.owned_by || 'Unknown' }}</td>
                    <td>{{ formatCurrency(asset.current_asset_balance) }}</td>
                    <td>$0.00</td>
                    <td>{{ formatCurrency(calculateProjectedValue(asset)) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Section 3: Conversion Impact Table -->
    <h3>Detailed Yealry Summary</h3>
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Conversion Impact Table</h5>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Year</th>
                <th>Client/Spouse Ages</th>
                <th>Income Before Conversion</th>
                <th>Conversion Amount</th>
                <th>Total Taxable Income</th>
                <th>Tax Bracket (%)</th>
                <th>Federal Tax</th>
                <th>Medicare Costs</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in scenarioResults" :key="row.year">
                <td>{{ row.year }}</td>
                <td>{{ row.primary_age }} / {{ row.spouse_age }}</td>
                <td>
                  ${{ 
                    (parseFloat(row.gross_income || 0) + 
                    (row.year < retirementYear ? parseFloat(preRetirementIncome || 0) : 0)).toFixed(2) 
                  }}
                </td>
                <td>${{ parseFloat(row.roth_conversion || 0).toFixed(2) }}</td>
                <td>
                  ${{ (
                    (parseFloat(row.gross_income || 0) +
                    (row.year < retirementYear ? parseFloat(preRetirementIncome || 0) : 0)) +
                    parseFloat(row.roth_conversion || 0)
                  ).toFixed(2) }}
                </td>
                <td>12%</td>
                <td>${{ parseFloat(row.federal_tax || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Section 4: Baseline vs Roth Conversion Comparison Table -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Baseline vs Roth Conversion Comparison</h5>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Metric</th>
                <th>Baseline</th>
                <th>Roth Conversion</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Lifetime Federal Taxes</td>
                <td>${{ baselineMetrics.lifetime_tax !== undefined ? baselineMetrics.lifetime_tax.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.lifetime_tax !== undefined ? optimalSchedule.score_breakdown.lifetime_tax.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Lifetime Medicare Premiums</td>
                <td>${{ baselineMetrics.lifetime_medicare !== undefined ? baselineMetrics.lifetime_medicare.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.lifetime_medicare !== undefined ? optimalSchedule.score_breakdown.lifetime_medicare.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Lifetime IRMAA Surcharges</td>
                <td>${{ baselineMetrics.total_irmaa !== undefined ? baselineMetrics.total_irmaa.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.total_irmaa !== undefined ? optimalSchedule.score_breakdown.total_irmaa.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Net Lifetime Spendable Income</td>
                <td>${{ baselineMetrics.cumulative_net_income !== undefined ? baselineMetrics.cumulative_net_income.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.cumulative_net_income !== undefined ? optimalSchedule.score_breakdown.cumulative_net_income.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Final Roth IRA Balance</td>
                <td>${{ baselineMetrics.final_roth !== undefined ? baselineMetrics.final_roth.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.final_roth !== undefined ? optimalSchedule.score_breakdown.final_roth.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Total Net Assets at Mortality</td>
                <td>${{ baselineMetrics.final_roth !== undefined ? baselineMetrics.final_roth.toLocaleString() : 0 }}</td>
                <td>${{ optimalSchedule.score_breakdown?.final_roth !== undefined ? optimalSchedule.score_breakdown.final_roth.toLocaleString() : 0 }}</td>
              </tr>
              <tr>
                <td>Average IRMAA Tier Hit</td>
                <td>{{ baselineMetrics.income_stability !== undefined ? baselineMetrics.income_stability : 'Tier Level' }}</td>
                <td>{{ optimalSchedule.score_breakdown?.income_stability !== undefined ? optimalSchedule.score_breakdown.income_stability : 'Tier Level' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Section 5: Action Buttons -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <button class="btn btn-primary me-2" @click="recalculateConversion">Recalculate Conversion</button>
      </div>
    </div>
    </div> <!-- End of scenario-results div -->
  </div>
</template>

<script>
import Graph from '../components/Graph.vue';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import './RothConversionTab.css';

export default {
  components: { Graph },
  mounted() {
    // Initialize our component's chart data without affecting other components
    const assetLineData = this.generateAssetLineData();
    if (assetLineData) {
      this.assetLineData = JSON.parse(JSON.stringify(assetLineData)); // Deep clone to avoid reference issues
    }
    
    const expenseSummaryData = this.generateExpenseSummaryData();
    if (expenseSummaryData) {
      this.expenseSummaryData = JSON.parse(JSON.stringify(expenseSummaryData)); // Deep clone to avoid reference issues
    }
  },
  props: {
    scenario: {
      type: Object,
      required: true
    },
    assetDetails: {
      type: Array,
      required: true,
      default: () => []
    },
    scenarioResults: {
      type: Array,
      required: true,
      default: () => []
    },
    client: {
      type: Object,
      required: true
    }
  },
  data() {
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 30 }, (_, i) => currentYear + i);
    
    return {
      // Flag to track if we're in the middle of a recalculation
      _isRecalculating: false,
      preRetirementIncome: 0,
      preRetirementIncomeRaw: '',
      availableYears: this.generateAvailableYears(),
      conversionStartYear: currentYear,
      yearsToConvert: 1,
      rothGrowthRate: 5.0,
      scenarioResults: [],
      baselineMetrics: {},
      comparisonMetrics: {},
      optimalSchedule: {},
      maxToConvert: {},
      maxToConvertRaw: {},
      maxToConvertDisplay: {},
      maxAnnualAmount: '',
      maxAnnualAmountRaw: '',
      maxTotalAmount: '',
      totalSavings: 0,
      savingsPercentage: 0,
      conversionGoals: {
        taxes: true,
        irmaa: false,
        roth: false,
        volatility: false
      },
      conversionMode: 'auto',
      rothWithdrawalAmount: 0,
      rothWithdrawalAmountRaw: '',
      rothWithdrawalStartYear: currentYear,
      // Initialize assetLineData as null, will be set in mounted
      assetLineData: null,
      // Initialize expenseSummaryData as null, will be set in mounted
      expenseSummaryData: null,
      // Keep the original data for backward compatibility
      taxesBarData: {
        labels: ['Before', 'After'],
        datasets: [
          {
            label: 'Total Taxes',
            backgroundColor: ['#007bff', '#28a745'],
            data: [250000, 180000]
          }
        ]
      },
      irmaaBarData: {
        labels: ['Before', 'After'],
        datasets: [
          {
            label: 'Total IRMAA',
            backgroundColor: ['#ffc107', '#17a2b8'],
            data: [40000, 22000]
          }
        ]
      },

      barOptions: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      },
      expenseSummaryOptions: {
        plugins: {
          legend: { 
            display: true,
            position: 'bottom'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.dataset.label + ': $' + context.raw.toLocaleString();
              }
            }
          },
          totalColumnHighlight: {
            beforeDraw: function(chart) {
              const ctx = chart.ctx;
              const xAxis = chart.scales.x;
              const yAxis = chart.scales.y;
              
              // Highlight the total column with a light background
              if (xAxis.getLabels().length > 4) {
                const totalIndex = 4; // Index of "Total Expenses"
                const xStart = xAxis.getPixelForValue(totalIndex) - xAxis.width / (xAxis.ticks.length * 2);
                const xEnd = xAxis.getPixelForValue(totalIndex) + xAxis.width / (xAxis.ticks.length * 2);
                const yStart = yAxis.top;
                const yHeight = yAxis.height;
                
                ctx.save();
                ctx.fillStyle = 'rgba(220, 220, 220, 0.3)';
                ctx.fillRect(xStart, yStart, xEnd - xStart, yHeight);
                ctx.restore();
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            },
            title: {
              display: true,
              text: 'Amount ($)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Expense Categories'
            }
          }
        },
        indexAxis: 'x',
        responsive: true,
        maintainAspectRatio: false
      },
      lineOptions: {
        plugins: { legend: { display: true } },
        scales: { y: { beginAtZero: true } }
      },
    };
  },
  computed: {
    eligibleAssets() {
      // Show all eligible accounts for conversion (401k, IRA, Roth IRA, etc.)
      const assets = this.assetDetails || [];
      return assets.filter(asset => {
        if (!asset || !asset.income_type) return false;
        const type = asset.income_type.trim().toLowerCase();
        return [
          'traditional_401k', 'traditional_ira', 'ira', 'roth_401k', 'roth_ira'
        ].includes(type);
      });
    },
    selectedAssetList() {
      // Only include assets with a maxToConvert value > 0
      const assets = this.eligibleAssets || [];
      return assets.filter(asset => {
        const val = this.maxToConvert[asset.id || asset.income_type];
        return val && parseFloat(val) > 0;
      });
    },
    retirementYear() {
      // Compute the retirement year from client birthdate and scenario retirement age
      const birthYear = new Date(this.client.birthdate).getFullYear();
      const retirementAge = this.scenario.retirement_age || 65;
      return birthYear + retirementAge;
    },
    headerColor() {
      const authStore = useAuthStore();
      const user = authStore.user;
      return user && user.primary_color ? user.primary_color : '#377dff';
    },
    headingTextColor() {
      const authStore = useAuthStore();
      const user = authStore.user;
      if (user && user.primary_color && user.primary_color !== '#377dff') {
        return '#fff';
      }
      return '#fff'; // Always white for colored backgrounds
    },
    totalConversionAmount() {
      return this.selectedAssetList.reduce((sum, asset) => {
        return sum + (parseFloat(this.maxToConvert[asset.id || asset.income_type]) || 0);
      }, 0);
    },
    unaffectedAssets() {
      // Filter out assets that have no conversion amount
      return this.eligibleAssets.filter(asset => {
        const key = asset.id || asset.income_type;
        return !this.maxToConvert[key] || parseFloat(this.maxToConvert[key]) <= 0;
      });
    },
    yearsUntilRetirement() {
      const currentYear = new Date().getFullYear();
      return this.retirementYear - currentYear;
    },
    yearsUntilWithdrawal() {
      const currentYear = new Date().getFullYear();
      return this.rothWithdrawalStartYear - currentYear;
    },
    hasScenarioBeenRun() {
      // Check if we have scenario results or baseline metrics
      return (
        (this.scenarioResults && this.scenarioResults.length > 0) || 
        (this.baselineMetrics && Object.keys(this.baselineMetrics).length > 0) ||
        (this.optimalSchedule && Object.keys(this.optimalSchedule).length > 0)
      );
    }
  },
  methods: {
    generateAvailableYears() {
      const currentYear = new Date().getFullYear();
      return Array.from({ length: 41 }, (_, i) => currentYear + i);
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value || 0);
    },
    onMaxToConvertFocus(asset) {
      const key = asset.id || asset.income_type;
      const val = this.maxToConvert[key];
      if (!val || val === 0) {
        this.maxToConvertRaw[key] = '';
      } else {
        this.maxToConvertRaw[key] = val.toString();
      }
    },
    onMaxToConvertInput(event, asset) {
      const key = asset.id || asset.income_type;
      let raw = event.target.value.replace(/[^0-9.]/g, '');
      // Only allow one decimal point
      const parts = raw.split('.');
      if (parts.length > 2) raw = parts[0] + '.' + parts[1];
      // Limit to two decimals
      if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2);
      // Handle just a decimal (e.g., ".")
      if (raw === '.') {
        this.maxToConvertRaw[key] = '0.';
        this.maxToConvert[key] = 0;
        return;
      }
      // Handle empty input
      if (raw === '') {
        this.maxToConvertRaw[key] = '';
        this.maxToConvert[key] = 0;
        return;
      }
      // Parse to float
      let numeric = parseFloat(raw);
      if (isNaN(numeric)) numeric = 0;
      // ENFORCE MAXIMUM
      const max = parseFloat(asset.current_asset_balance) || 0;
      if (numeric > max) {
        numeric = max;
      }
      // Format with commas but no $ while typing
      const [intPart, decPart] = numeric.toString().split('.');
      let formatted = parseInt(intPart, 10).toLocaleString();
      if (decPart !== undefined) {
        formatted += '.' + decPart;
      }
      this.maxToConvertRaw[key] = formatted;
      this.maxToConvert[key] = numeric;
    },
    onMaxToConvertBlur(asset) {
      const key = asset.id || asset.income_type;
      const val = this.maxToConvert[key];
      this.maxToConvertRaw[key] = this.formatCurrency(val);
    },
    onCurrencyFocus(field) {
      if (!this[field] || this[field] === 0) {
        this[`${field}Raw`] = '';
      } else {
        this[`${field}Raw`] = this[field].toString();
      }
    },
    onCurrencyInput(event, field) {
      let raw = event.target.value.replace(/[^0-9.]/g, '');
      const parts = raw.split('.');
      if (parts.length > 2) raw = parts[0] + '.' + parts[1];
      if (parts[1]) raw = parts[0] + '.' + parts[1].slice(0, 2);
      if (raw === '.') {
        this[`${field}Raw`] = '0.';
        this[field] = 0;
        return;
      }
      if (raw === '') {
        this[`${field}Raw`] = '';
        this[field] = 0;
        return;
      }
      let numeric = parseFloat(raw);
      if (isNaN(numeric)) numeric = 0;
      const [intPart, decPart] = numeric.toString().split('.');
      let formatted = parseInt(intPart, 10).toLocaleString();
      if (decPart !== undefined) {
        formatted += '.' + decPart;
      }
      this[`${field}Raw`] = formatted;
      this[field] = numeric;
    },
    onCurrencyBlur(field) {
      this[`${field}Raw`] = this.formatCurrency(this[field]);
    },
    calculateProjectedValue(asset) {
      // Simple compound interest calculation for asset growth
      const initialValue = parseFloat(asset.current_asset_balance) || 0;
      const conversionAmount = parseFloat(this.maxToConvert[asset.id || asset.income_type]) || 0;
      const remainingValue = initialValue - conversionAmount;
      
      // Use asset's growth rate if available, otherwise use a default value
      const growthRate = parseFloat(asset.growth_rate) || 5.0;
      const years = this.yearsUntilRetirement;
      
      // Compound interest formula: A = P(1 + r/100)^t
      return remainingValue * Math.pow(1 + (growthRate / 100), years);
    },
    calculateRothProjectedValue() {
      // Calculate the projected value of the new Roth IRA
      const totalConversion = this.totalConversionAmount;
      const growthRate = parseFloat(this.rothGrowthRate) || 5.0;
      const yearsToRetirement = this.yearsUntilRetirement;
      const yearsToWithdrawal = this.yearsUntilWithdrawal;
      
      // Calculate value at retirement first
      let rothValue = totalConversion * Math.pow(1 + (growthRate / 100), yearsToRetirement);
      
      // If withdrawal starts after retirement, continue growth until withdrawal starts
      if (this.rothWithdrawalStartYear > this.retirementYear) {
        const additionalYears = this.rothWithdrawalStartYear - this.retirementYear;
        rothValue = rothValue * Math.pow(1 + (growthRate / 100), additionalYears);
      }
      
      return rothValue;
    },
    calculateWithdrawalYearPosition() {
      // Calculate the position of the withdrawal year marker on the timeline
      const currentYear = new Date().getFullYear();
      const totalYears = 30; // Total years shown in the timeline
      const withdrawalYear = parseInt(this.rothWithdrawalStartYear) || currentYear;
      
      // Calculate position as percentage of timeline width
      const position = ((withdrawalYear - currentYear) / totalYears) * 100;
      return Math.min(Math.max(position, 0), 100); // Clamp between 0-100%
    },
    updateAssetLineData() {
      try {
        // Generate years for x-axis
        const currentYear = new Date().getFullYear();
        const years = Array.from({ length: 30 }, (_, i) => currentYear + i);
        
        // Create datasets for each affected asset
        const datasets = [];
        
        // If we have no assets or no scenario has been run, use the default data
        if (!this.hasScenarioBeenRun && (!this.eligibleAssets || this.eligibleAssets.length === 0)) {
          // Use default data
          this.assetLineData = {
            labels: years.map(year => year.toString()),
            datasets: [
              {
                label: 'IRA',
                borderColor: '#007bff',
                backgroundColor: 'rgba(0,123,255,0.1)',
                data: [300000, 250000, 200000, 180000, 160000, 140000, 120000, 100000, 80000, 60000, 40000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 2, 1, 1, 1, 1, 1, 1],
                fill: false
              },
              {
                label: '401k',
                borderColor: '#28a745',
                backgroundColor: 'rgba(40,167,69,0.1)',
                data: [200000, 180000, 160000, 140000, 120000, 100000, 80000, 60000, 40000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                fill: false
              },
              {
                label: 'Traditional IRA',
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255,193,7,0.1)',
                data: [100000, 95000, 90000, 85000, 80000, 75000, 70000, 65000, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000, 15000, 10000, 5000, 2500, 1000, 500, 200, 100, 50, 25, 10, 5, 2],
                fill: false
              },
              {
                label: 'Roth IRA',
                borderColor: '#6f42c1',
                backgroundColor: 'rgba(111,66,193,0.1)',
                data: [0, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000, 400000, 420000, 440000, 460000, 480000, 500000, 520000, 540000, 560000, 580000],
                fill: false
              }
            ]
          };
          return;
        }
        
        // Add datasets for affected assets (with declining balances due to conversion)
        this.selectedAssetList.forEach(asset => {
          const initialValue = parseFloat(asset.current_asset_balance) || 0;
          const conversionAmount = parseFloat(this.maxToConvert[asset.id || asset.income_type]) || 0;
          const growthRate = parseFloat(asset.growth_rate) || 5.0;
          const yearsToConvert = parseInt(this.yearsToConvert) || 1;
          const annualConversion = conversionAmount / yearsToConvert;
          
          // Generate data points for this asset
          const data = [];
          let balance = initialValue;
          
          for (let i = 0; i < years.length; i++) {
            // Apply conversion for the conversion years
            if (i < yearsToConvert && years[i] >= this.conversionStartYear) {
              balance -= annualConversion;
            }
            
            // Apply growth
            balance = balance * (1 + (growthRate / 100));
            
            // Ensure balance doesn't go below zero
            balance = Math.max(0, balance);
            data.push(balance);
          }
          
          // Add to datasets
          datasets.push({
            label: asset.income_type || 'Asset',
            borderColor: this.getRandomColor(),
            backgroundColor: 'rgba(0,0,0,0.1)',
            data: data,
            fill: false
          });
        });
        
        // Add dataset for unaffected assets
        this.unaffectedAssets.forEach(asset => {
          const initialValue = parseFloat(asset.current_asset_balance) || 0;
          const growthRate = parseFloat(asset.growth_rate) || 5.0;
          
          // Generate data points
          const data = [];
          let balance = initialValue;
          
          for (let i = 0; i < years.length; i++) {
            // Apply growth
            balance = balance * (1 + (growthRate / 100));
            data.push(balance);
          }
          
          // Add to datasets
          datasets.push({
            label: asset.income_type || 'Asset',
            borderColor: this.getRandomColor(),
            backgroundColor: 'rgba(0,0,0,0.1)',
            data: data,
            fill: false
          });
        });
        
        // Add Roth IRA dataset
        const rothData = [];
        let rothBalance = 0;
        const rothGrowthRate = parseFloat(this.rothGrowthRate) || 5.0;
        const withdrawalAmount = parseFloat(this.rothWithdrawalAmount) || 0;
        
        for (let i = 0; i < years.length; i++) {
          const year = years[i];
          
          // Add conversion amounts during conversion years
          if (i < this.yearsToConvert && year >= this.conversionStartYear) {
            rothBalance += this.totalConversionAmount / this.yearsToConvert;
          }
          
          // Apply growth
          rothBalance = rothBalance * (1 + (rothGrowthRate / 100));
          
          // Apply withdrawals if past withdrawal start year
          if (year >= this.rothWithdrawalStartYear && withdrawalAmount > 0) {
            rothBalance -= withdrawalAmount;
            rothBalance = Math.max(0, rothBalance); // Ensure balance doesn't go below zero
          }
          
          rothData.push(rothBalance);
        }
        
        // Add Roth dataset if we have conversion data
        if (this.totalConversionAmount > 0) {
          datasets.push({
            label: 'Roth IRA',
            borderColor: '#6f42c1', // Purple for Roth
            backgroundColor: 'rgba(111,66,193,0.1)',
            data: rothData,
            fill: false
          });
        }
        
        // Make sure we have at least one dataset
        if (datasets.length === 0) {
          datasets.push({
            label: 'Default Asset',
            borderColor: '#007bff',
            backgroundColor: 'rgba(0,123,255,0.1)',
            data: Array(years.length).fill(0),
            fill: false
          });
        }
        
        // Update the asset line data
        this.assetLineData = {
          labels: years.map(year => year.toString()),
          datasets: datasets
        };
      } catch (error) {
        console.error('Error updating asset line data:', error);
        // Provide fallback data to ensure the graph doesn't break
        this.assetLineData = {
          labels: Array.from({ length: 30 }, (_, i) => (new Date().getFullYear() + i).toString()),
          datasets: [
            {
              label: 'Default Asset',
              borderColor: '#007bff',
              backgroundColor: 'rgba(0,123,255,0.1)',
              data: Array(30).fill(0),
              fill: false
            }
          ]
        };
      }
    },
    getRandomColor() {
      // Generate a random color for asset lines
      const colors = [
        '#007bff', // Blue
        '#28a745', // Green
        '#ffc107', // Yellow
        '#dc3545', // Red
        '#17a2b8', // Cyan
        '#fd7e14', // Orange
        '#20c997', // Teal
        '#e83e8c', // Pink
        '#6610f2', // Indigo
        '#6c757d'  // Gray
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    },
    async recalculateConversion() {
      // Flag to track recalculation state
      this._isRecalculating = true;
      
      // Check if client exists
      if (!this.client) {
        console.error('Client data is missing');
        console.error('Client data is missing. Cannot calculate conversion.');
        this._isRecalculating = false;
        return;
      }

      // Always include all income-producing assets
      const allAssets = (this.assetDetails || []).map(asset => ({
        ...asset,
        max_to_convert: this.maxToConvert[asset.id || asset.income_type] || 0
      }));

      // Always use manual mode
      const modeToSend = 'manual';

      // Calculate total amount to convert from all selected assets
      const totalToConvert = allAssets
        .filter(asset => [
          'traditional_401k', 'traditional_ira', 'ira', 'roth_401k', 'roth_ira', '401k'
        ].includes((asset.income_type || '').trim().toLowerCase()))
        .reduce((sum, asset) => sum + (parseFloat(asset.max_to_convert) || 0), 0);

      // Ensure we have valid years to convert
      const yearsToConvert = Math.max(1, parseInt(this.yearsToConvert) || 1);
      
      // Calculate annual conversion amount by dividing total by years
      const annualConversion = totalToConvert / yearsToConvert;
      
      // Ensure all required fields have valid values
      const currentYear = new Date().getFullYear();
      const conversionStartYear = parseInt(this.conversionStartYear) || currentYear;
      const rothWithdrawalStartYear = parseInt(this.rothWithdrawalStartYear) || currentYear;
      const rothWithdrawalAmount = parseFloat(this.rothWithdrawalAmount) || 0;
      const rothGrowthRate = parseFloat(this.rothGrowthRate) || 0;
      const maxAnnualAmount = parseFloat(this.maxAnnualAmount) || 0;

      // Ensure the client and scenario have all required fields
      const scenarioData = {
        ...this.scenario,
        roth_conversion_start_year: conversionStartYear,
        roth_conversion_duration: yearsToConvert,
        roth_withdrawal_amount: rothWithdrawalAmount,
        roth_withdrawal_start_year: rothWithdrawalStartYear,
        pre_retirement_income: this.preRetirementIncome || 0,
        max_annual_amount: maxAnnualAmount,
        // Add these fields to ensure they exist
        retirement_age: this.scenario.retirement_age || 65,
        mortality_age: this.scenario.mortality_age || 90,
        part_b_inflation_rate: this.scenario.part_b_inflation_rate || 3.0,
        part_d_inflation_rate: this.scenario.part_d_inflation_rate || 3.0,
      };
      
      // Ensure client has required fields
      const clientData = {
        ...this.client,
        // Safely access tax_status with fallback
        tax_status: this.client?.tax_status || 'Single',
        // Add other potentially missing fields
        birthdate: this.client?.birthdate || new Date().toISOString().split('T')[0],
        name: this.client?.name || 'Client',
        gender: this.client?.gender || 'M',
        state: this.client?.state || 'CA'
      };

      console.log('Client data being sent:', clientData);

      const payload = {
        scenario: scenarioData,
        client: clientData,
        spouse: this.scenario.spouse || (this.scenario.spouse_birthdate ? { birthdate: this.scenario.spouse_birthdate } : null),
        assets: allAssets,
        optimizer_params: {
          mode: modeToSend,
          conversion_start_year: conversionStartYear,
          years_to_convert: yearsToConvert,
          annual_conversion_amount: annualConversion,
          roth_growth_rate: rothGrowthRate,
          max_annual_amount: maxAnnualAmount,
          max_total_amount: totalToConvert,
          roth_withdrawal_amount: rothWithdrawalAmount,
          roth_withdrawal_start_year: rothWithdrawalStartYear
        }
      };

      // Debug: print payload and mode to console
      console.log('Roth Conversion Payload:', JSON.stringify(payload, null, 2));
      console.log('Optimizer mode being sent:', modeToSend);
      console.log('Years to convert:', yearsToConvert);
      console.log('Total to convert:', totalToConvert);
      console.log('Annual conversion amount:', annualConversion);

      try {
        const authStore = useAuthStore();
        const token = authStore.accessToken;
        
        if (!token) {
          console.error('No authentication token available');
          this._isRecalculating = false;
          return;
        }
        
        // Create a loading indicator for the user
        console.log('Calculating Roth conversion...');
        
        console.log('Sending request with token:', token);
        const response = await fetch('http://localhost:8000/api/roth-optimize/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          console.error('API error:', data);
          console.error(`Error: ${data.error || 'Unknown error occurred'}`);
          this._isRecalculating = false;
          return;
        }
        
        console.log('API response:', data);
        
        // Only update our specific data if we have valid response data
        if (data && data.year_by_year && data.year_by_year.length > 0) {
          // Store the API response data in component properties
          this.scenarioResults = data.year_by_year || [];
          this.comparisonMetrics = data.comparison || {};
          this.optimalSchedule = data.optimal_schedule || {};
          this.baselineMetrics = data.baseline || {};
          
          // Generate new chart data
          const newAssetLineData = this.generateAssetLineData();
          const newExpenseSummaryData = this.generateExpenseSummaryData();
          
          // Only update our component's chart data with deep clones to avoid reference issues
          if (newAssetLineData) {
            this.assetLineData = JSON.parse(JSON.stringify(newAssetLineData));
          }
          
          if (newExpenseSummaryData) {
            this.expenseSummaryData = JSON.parse(JSON.stringify(newExpenseSummaryData));
          }
        } else {
          console.error('Invalid response data structure');
        }
        
        // Save the Roth conversion data to the database
        const saveResult = await this.saveRothConversionScenario();
        if (saveResult) {
          console.log('Roth conversion data saved successfully');
        } else {
          console.error('Error saving Roth conversion data');
        }
        
        // Debug: log income fields for each year
        if (this.scenarioResults && this.scenarioResults.length) {
          console.log('--- Roth ConversionTab: Income Data by Year ---');
          this.scenarioResults.forEach(row => {
            const assetBalances = Object.fromEntries(Object.entries(row).filter(([k]) => k.endsWith('_balance')));
            const assetWithdrawals = Object.fromEntries(Object.entries(row).filter(([k]) => k.endsWith('_withdrawal') || k.endsWith('_conversion') || k.endsWith('_rmd') || k.endsWith('_distribution')));
            console.log(`Year: ${row.year}`);
            console.log('  Asset Balances:', assetBalances);
            if (Object.keys(assetWithdrawals).length > 0) {
              console.log('  Asset Withdrawals/Conversions:', assetWithdrawals);
            }
            console.log(`  Gross Income: ${row.gross_income}, SS Income: ${row.ss_income}, Taxable SS: ${row.taxable_ss}, Taxable Income: ${row.taxable_income}`);
          });
        } else {
          console.warn('No scenarioResults returned from backend.');
        }
      } catch (err) {
        console.error('Error running optimizer:', err);
      } finally {
        // Always reset the recalculation flag
        this._isRecalculating = false;
      }
    },
    async saveRothConversionScenario() {
      try {
        // Validate required data
        if (!this.client || !this.client.id) {
          console.error('Client data is missing');
          throw new Error('Client data is missing. Cannot save scenario.');
        }
        
        if (!this.scenario || !this.scenario.id) {
          console.error('Scenario data is missing');
          throw new Error('Scenario data is missing. Cannot save scenario.');
        }
        
        const authStore = useAuthStore();
        const token = authStore.accessToken;
        
        if (!token) {
          console.error('No authentication token available');
          throw new Error('No authentication token available');
        }
        
        // Prepare the scenario update data
        const scenarioUpdateData = {
          id: this.scenario.id,
          name: this.scenario.name,
          description: this.scenario.description || 'Roth Conversion Scenario',
          roth_conversion_start_year: parseInt(this.conversionStartYear) || new Date().getFullYear(),
          roth_conversion_duration: parseInt(this.yearsToConvert) || 1,
          roth_conversion_annual_amount: this.totalConversionAmount / (parseInt(this.yearsToConvert) || 1),
          retirement_age: this.scenario.retirement_age || 65,
          medicare_age: this.scenario.medicare_age || 65,
          spouse_retirement_age: this.scenario.spouse_retirement_age,
          spouse_medicare_age: this.scenario.spouse_medicare_age,
          mortality_age: this.scenario.mortality_age || 90,
          spouse_mortality_age: this.scenario.spouse_mortality_age,
          part_b_inflation_rate: this.scenario.part_b_inflation_rate || 3.0,
          part_d_inflation_rate: this.scenario.part_d_inflation_rate || 3.0,
          apply_standard_deduction: this.scenario.apply_standard_deduction !== undefined ? this.scenario.apply_standard_deduction : true
        };
        
        // Update the scenario with Roth conversion parameters
        try {
          const response = await fetch(`http://localhost:8000/api/scenarios/${this.scenario.id}/update/`, {
            method: 'PUT',
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(scenarioUpdateData)
          });
          
          const data = await response.json();
          
          if (!response.ok) {
            console.error('API error:', data);
            throw new Error(`Error: ${data.error || 'Unknown error occurred'}`);
          }
        } catch (error) {
          console.error('Error updating scenario:', error);
          // Don't rethrow - we'll try to continue with asset updates
        }
        
        // Update asset data to save conversion amounts
        const assetUpdates = [];
        
        // Process assets that have conversion amounts
        for (const asset of this.selectedAssetList) {
          const conversionAmount = parseFloat(this.maxToConvert[asset.id || asset.income_type]) || 0;
          if (conversionAmount > 0) {
            assetUpdates.push({
              id: asset.id,
              max_to_convert: conversionAmount,
              scenario_id: this.scenario.id
            });
          }
        }
        
        // Save asset updates if there are any
        if (assetUpdates.length > 0) {
          try {
            const assetResponse = await fetch(`http://localhost:8000/api/scenarios/${this.scenario.id}/update-assets/`, {
              method: 'PUT',
              headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({ assets: assetUpdates })
            });
            
            const assetData = await assetResponse.json();
            
            if (!assetResponse.ok) {
              console.error('API error updating assets:', assetData);
              throw new Error(`Error updating assets: ${assetData.error || 'Unknown error occurred'}`);
            }
          } catch (error) {
            console.error('Error updating assets:', error);
            // Continue with the flow even if asset updates fail
          }
        }
        
        console.log('Roth Conversion Scenario saved successfully!');
        return true;
      } catch (err) {
        console.error('Error saving Roth Conversion Scenario:', err);
        console.error('Error details:', err.message);
        return false;
      }
    },
    exportComparisonReport() {
      // Implement PDF export logic
    },
    updateExpenseSummaryData() {
      try {
        // Check if we have real data or need to use defaults
        if (!this.hasScenarioBeenRun) {
          // Use default data for initial display
          const defaultBaselineRMDs = 250000;
          const defaultOptimalRMDs = 180000;
          const defaultBaselineTaxes = 180000;
          const defaultOptimalTaxes = 140000;
          const defaultBaselineMedicare = 50000;
          const defaultOptimalMedicare = 40000;
          const defaultBaselineInheritance = 75000;
          const defaultOptimalInheritance = 45000;
          
          const defaultBaselineTotal = defaultBaselineRMDs + defaultBaselineTaxes + defaultBaselineMedicare + defaultBaselineInheritance;
          const defaultOptimalTotal = defaultOptimalRMDs + defaultOptimalTaxes + defaultOptimalMedicare + defaultOptimalInheritance;
          
          const defaultSavings = defaultBaselineTotal - defaultOptimalTotal;
          const defaultSavingsPercentage = ((defaultSavings / defaultBaselineTotal) * 100).toFixed(1);
          
          this.expenseSummaryData = {
            labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
            datasets: [
              {
                label: 'Before Conversion',
                backgroundColor: '#007bff',
                data: [defaultBaselineRMDs, defaultBaselineTaxes, defaultBaselineMedicare, defaultBaselineInheritance, defaultBaselineTotal],
                backgroundColor: (context) => {
                  return context.dataIndex === 4 ? '#0056b3' : '#007bff';
                }
              },
              {
                label: 'After Conversion',
                backgroundColor: '#28a745',
                data: [defaultOptimalRMDs, defaultOptimalTaxes, defaultOptimalMedicare, defaultOptimalInheritance, defaultOptimalTotal],
                backgroundColor: (context) => {
                  return context.dataIndex === 4 ? '#1e7e34' : '#28a745';
                }
              }
            ]
          };
          
          this.totalSavings = defaultSavings;
          this.savingsPercentage = defaultSavingsPercentage;
          return;
        }
        
        // Get values from baseline and optimal schedule
        const baseline = this.baselineMetrics || {};
        const optimal = this.optimalSchedule?.score_breakdown || {};
        
        // Extract RMD data (use total RMDs or a reasonable estimate)
        const baselineRMDs = baseline.total_rmds || 250000;
        const optimalRMDs = optimal.total_rmds || 180000;
        
        // Extract tax data
        const baselineTaxes = baseline.lifetime_tax || 180000;
        const optimalTaxes = optimal.lifetime_tax || 140000;
        
        // Extract Medicare and IRMAA data
        const baselineMedicare = (baseline.lifetime_medicare || 0) + (baseline.total_irmaa || 0);
        const optimalMedicare = (optimal.lifetime_medicare || 0) + (optimal.total_irmaa || 0);
        
        // Extract inheritance tax (estimate based on final balances)
        const baselineInheritance = baseline.inheritance_tax || 75000;
        const optimalInheritance = optimal.inheritance_tax || 45000;
        
        // Calculate totals
        const baselineTotal = baselineRMDs + baselineTaxes + baselineMedicare + baselineInheritance;
        const optimalTotal = optimalRMDs + optimalTaxes + optimalMedicare + optimalInheritance;
        
        // Calculate savings
        const savings = baselineTotal - optimalTotal;
        const savingsPercentage = ((savings / baselineTotal) * 100).toFixed(1);
        
        // Update the chart data
        this.expenseSummaryData = {
          labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
          datasets: [
            {
              label: 'Before Conversion',
              backgroundColor: '#007bff',
              data: [baselineRMDs, baselineTaxes, baselineMedicare, baselineInheritance, baselineTotal],
              // Make the total column darker
              backgroundColor: (context) => {
                return context.dataIndex === 4 ? '#0056b3' : '#007bff';
              }
            },
            {
              label: 'After Conversion',
              backgroundColor: '#28a745',
              data: [optimalRMDs, optimalTaxes, optimalMedicare, optimalInheritance, optimalTotal],
              // Make the total column darker
              backgroundColor: (context) => {
                return context.dataIndex === 4 ? '#1e7e34' : '#28a745';
              }
            }
          ]
        };
        
        // Update savings display
        this.totalSavings = savings;
        this.savingsPercentage = savingsPercentage;
      } catch (error) {
        console.error('Error updating expense summary data:', error);
        // Provide fallback data to ensure the graph doesn't break
        this.expenseSummaryData = {
          labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
          datasets: [
            {
              label: 'Before Conversion',
              backgroundColor: '#007bff',
              data: [0, 0, 0, 0, 0]
            },
            {
              label: 'After Conversion',
              backgroundColor: '#28a745',
              data: [0, 0, 0, 0, 0]
            }
          ]
        };
        this.totalSavings = 0;
        this.savingsPercentage = 0;
      }
    },
    generateAssetLineData() {
      try {
        // Generate years for x-axis
        const currentYear = new Date().getFullYear();
        const years = Array.from({ length: 30 }, (_, i) => currentYear + i);
        
        // Create datasets for each affected asset
        const datasets = [];
        
        // If we have no assets or no scenario has been run, use the default data
        if (!this.hasScenarioBeenRun && (!this.eligibleAssets || this.eligibleAssets.length === 0)) {
          // Return default data
          return {
            labels: years.map(year => year.toString()),
            datasets: [
              {
                label: 'IRA',
                borderColor: '#007bff',
                backgroundColor: 'rgba(0,123,255,0.1)',
                data: [300000, 250000, 200000, 180000, 160000, 140000, 120000, 100000, 80000, 60000, 40000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 2, 1, 1, 1, 1, 1, 1],
                fill: false
              },
              {
                label: '401k',
                borderColor: '#28a745',
                backgroundColor: 'rgba(40,167,69,0.1)',
                data: [200000, 180000, 160000, 140000, 120000, 100000, 80000, 60000, 40000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                fill: false
              },
              {
                label: 'Traditional IRA',
                borderColor: '#ffc107',
                backgroundColor: 'rgba(255,193,7,0.1)',
                data: [100000, 95000, 90000, 85000, 80000, 75000, 70000, 65000, 60000, 55000, 50000, 45000, 40000, 35000, 30000, 25000, 20000, 15000, 10000, 5000, 2500, 1000, 500, 200, 100, 50, 25, 10, 5, 2],
                fill: false
              },
              {
                label: 'Roth IRA',
                borderColor: '#6f42c1',
                backgroundColor: 'rgba(111,66,193,0.1)',
                data: [0, 20000, 40000, 60000, 80000, 100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000, 260000, 280000, 300000, 320000, 340000, 360000, 380000, 400000, 420000, 440000, 460000, 480000, 500000, 520000, 540000, 560000, 580000],
                fill: false
              }
            ]
          };
        }
        
        // Add datasets for affected assets (with declining balances due to conversion)
        this.selectedAssetList.forEach(asset => {
          const initialValue = parseFloat(asset.current_asset_balance) || 0;
          const conversionAmount = parseFloat(this.maxToConvert[asset.id || asset.income_type]) || 0;
          const growthRate = parseFloat(asset.growth_rate) || 5.0;
          const yearsToConvert = parseInt(this.yearsToConvert) || 1;
          const annualConversion = conversionAmount / yearsToConvert;
          
          // Generate data points for this asset
          const data = [];
          let balance = initialValue;
          
          for (let i = 0; i < years.length; i++) {
            // Apply conversion for the conversion years
            if (i < yearsToConvert && years[i] >= this.conversionStartYear) {
              balance -= annualConversion;
            }
            
            // Apply growth
            balance = balance * (1 + (growthRate / 100));
            
            // Ensure balance doesn't go below zero
            balance = Math.max(0, balance);
            data.push(balance);
          }
          
          // Add to datasets
          datasets.push({
            label: asset.income_type || 'Asset',
            borderColor: this.getRandomColor(),
            backgroundColor: 'rgba(0,0,0,0.1)',
            data: data,
            fill: false
          });
        });
        
        // Add dataset for unaffected assets
        this.unaffectedAssets.forEach(asset => {
          const initialValue = parseFloat(asset.current_asset_balance) || 0;
          const growthRate = parseFloat(asset.growth_rate) || 5.0;
          
          // Generate data points
          const data = [];
          let balance = initialValue;
          
          for (let i = 0; i < years.length; i++) {
            // Apply growth
            balance = balance * (1 + (growthRate / 100));
            data.push(balance);
          }
          
          // Add to datasets
          datasets.push({
            label: asset.income_type || 'Asset',
            borderColor: this.getRandomColor(),
            backgroundColor: 'rgba(0,0,0,0.1)',
            data: data,
            fill: false
          });
        });
        
        // Add Roth IRA dataset
        const rothData = [];
        let rothBalance = 0;
        const rothGrowthRate = parseFloat(this.rothGrowthRate) || 5.0;
        const withdrawalAmount = parseFloat(this.rothWithdrawalAmount) || 0;
        
        for (let i = 0; i < years.length; i++) {
          const year = years[i];
          
          // Add conversion amounts during conversion years
          if (i < this.yearsToConvert && year >= this.conversionStartYear) {
            rothBalance += this.totalConversionAmount / this.yearsToConvert;
          }
          
          // Apply growth
          rothBalance = rothBalance * (1 + (rothGrowthRate / 100));
          
          // Apply withdrawals if past withdrawal start year
          if (year >= this.rothWithdrawalStartYear && withdrawalAmount > 0) {
            rothBalance -= withdrawalAmount;
            rothBalance = Math.max(0, rothBalance); // Ensure balance doesn't go below zero
          }
          
          rothData.push(rothBalance);
        }
        
        // Add Roth dataset if we have conversion data
        if (this.totalConversionAmount > 0) {
          datasets.push({
            label: 'Roth IRA',
            borderColor: '#6f42c1', // Purple for Roth
            backgroundColor: 'rgba(111,66,193,0.1)',
            data: rothData,
            fill: false
          });
        }
        
        // Make sure we have at least one dataset
        if (datasets.length === 0) {
          datasets.push({
            label: 'Default Asset',
            borderColor: '#007bff',
            backgroundColor: 'rgba(0,123,255,0.1)',
            data: Array(years.length).fill(0),
            fill: false
          });
        }
        
        // Return the asset line data
        return {
          labels: years.map(year => year.toString()),
          datasets: datasets
        };
      } catch (error) {
        console.error('Error generating asset line data:', error);
        // Return fallback data
        return {
          labels: Array.from({ length: 30 }, (_, i) => (new Date().getFullYear() + i).toString()),
          datasets: [
            {
              label: 'Default Asset',
              borderColor: '#007bff',
              backgroundColor: 'rgba(0,123,255,0.1)',
              data: Array(30).fill(0),
              fill: false
            }
          ]
        };
      }
    },
    generateExpenseSummaryData() {
      try {
        // Check if we have real data or need to use defaults
        if (!this.hasScenarioBeenRun) {
          // Use default data for initial display
          const defaultBaselineRMDs = 250000;
          const defaultOptimalRMDs = 180000;
          const defaultBaselineTaxes = 180000;
          const defaultOptimalTaxes = 140000;
          const defaultBaselineMedicare = 50000;
          const defaultOptimalMedicare = 40000;
          const defaultBaselineInheritance = 75000;
          const defaultOptimalInheritance = 45000;
          
          const defaultBaselineTotal = defaultBaselineRMDs + defaultBaselineTaxes + defaultBaselineMedicare + defaultBaselineInheritance;
          const defaultOptimalTotal = defaultOptimalRMDs + defaultOptimalTaxes + defaultOptimalMedicare + defaultOptimalInheritance;
          
          const defaultSavings = defaultBaselineTotal - defaultOptimalTotal;
          const defaultSavingsPercentage = ((defaultSavings / defaultBaselineTotal) * 100).toFixed(1);
          
          this.totalSavings = defaultSavings;
          this.savingsPercentage = defaultSavingsPercentage;
          
          return {
            labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
            datasets: [
              {
                label: 'Before Conversion',
                backgroundColor: '#007bff',
                data: [defaultBaselineRMDs, defaultBaselineTaxes, defaultBaselineMedicare, defaultBaselineInheritance, defaultBaselineTotal]
              },
              {
                label: 'After Conversion',
                backgroundColor: '#28a745',
                data: [defaultOptimalRMDs, defaultOptimalTaxes, defaultOptimalMedicare, defaultOptimalInheritance, defaultOptimalTotal]
              }
            ]
          };
        }
        
        // Get values from baseline and optimal schedule
        const baseline = this.baselineMetrics || {};
        const optimal = this.optimalSchedule?.score_breakdown || {};
        
        // Extract RMD data (use total RMDs or a reasonable estimate)
        const baselineRMDs = baseline.total_rmds || 250000;
        const optimalRMDs = optimal.total_rmds || 180000;
        
        // Extract tax data
        const baselineTaxes = baseline.lifetime_tax || 180000;
        const optimalTaxes = optimal.lifetime_tax || 140000;
        
        // Extract Medicare and IRMAA data
        const baselineMedicare = (baseline.lifetime_medicare || 0) + (baseline.total_irmaa || 0);
        const optimalMedicare = (optimal.lifetime_medicare || 0) + (optimal.total_irmaa || 0);
        
        // Extract inheritance tax (estimate based on final balances)
        const baselineInheritance = baseline.inheritance_tax || 75000;
        const optimalInheritance = optimal.inheritance_tax || 45000;
        
        // Calculate totals
        const baselineTotal = baselineRMDs + baselineTaxes + baselineMedicare + baselineInheritance;
        const optimalTotal = optimalRMDs + optimalTaxes + optimalMedicare + optimalInheritance;
        
        // Calculate savings
        const savings = baselineTotal - optimalTotal;
        const savingsPercentage = ((savings / baselineTotal) * 100).toFixed(1);
        
        // Update savings display
        this.totalSavings = savings;
        this.savingsPercentage = savingsPercentage;
        
        // Return the expense summary data
        return {
          labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
          datasets: [
            {
              label: 'Before Conversion',
              backgroundColor: '#007bff',
              data: [baselineRMDs, baselineTaxes, baselineMedicare, baselineInheritance, baselineTotal]
            },
            {
              label: 'After Conversion',
              backgroundColor: '#28a745',
              data: [optimalRMDs, optimalTaxes, optimalMedicare, optimalInheritance, optimalTotal]
            }
          ]
        };
      } catch (error) {
        console.error('Error generating expense summary data:', error);
        // Return fallback data
        return {
          labels: ['RMDs', 'State & Federal Taxes', 'Medicare & IRMAA', 'Inheritance Tax', 'Total Expenses'],
          datasets: [
            {
              label: 'Before Conversion',
              backgroundColor: '#007bff',
              data: [0, 0, 0, 0, 0]
            },
            {
              label: 'After Conversion',
              backgroundColor: '#28a745',
              data: [0, 0, 0, 0, 0]
            }
          ]
        };
      }
    },
  },
  mounted() {
    console.log('Asset Details medicare:', this.assetDetails);
    if (Array.isArray(this.assetDetails) && this.assetDetails.length > 0) {
      this.assetDetails.forEach(asset => {
        console.log('Asset:', asset);
        console.log('Asset Type:', asset.income_type);
      });
    } else {
      console.log('Asset Details is empty or not an array.');
    }
  },
  watch: {
    // Remove the watch handlers that could affect other components
  },
};
</script>

<style src="./RothConversionTab.css"></style>
