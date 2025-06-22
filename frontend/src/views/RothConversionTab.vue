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
          <div class="card-body">
            <h5 class="mb-4">Asset Selection Panel</h5>
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
          <div class="card-body">
            <h5 class="mb-4">Conversion Schedule Parameters</h5>
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
        <button class="btn btn-success me-2" @click="saveRothConversionScenario">Save Roth Conversion Scenario</button>
        <button class="btn btn-secondary" @click="exportComparisonReport">Export Comparison Report (PDF)</button>
      </div>
    </div>
    <!-- Row of three cards: 1/4, 1/4, 1/2 width -->
    <div class="row mb-3">
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="mb-3">Taxes Before and After Conversion</h6>
            <Graph :data="taxesBarData" :options="barOptions" type="bar" :height="150" />
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="mb-3">IRMAA Before and After</h6>
            <Graph :data="irmaaBarData" :options="barOptions" type="bar" :height="150" />
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="mb-3">Asset Balance Time Line</h6>
            <Graph :data="assetLineData" :options="lineOptions" type="line" :height="150" />
          </div>
        </div>
      </div>
    </div>
    <!-- Section 3: Conversion Impact Table -->
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
        <button class="btn btn-success me-2" @click="saveRothConversionScenario">Save Roth Conversion Scenario</button>
        <button class="btn btn-secondary" @click="exportComparisonReport">Export Comparison Report (PDF)</button>
      </div>
    </div>
  </div>
</template>

<script>
import Graph from '../components/Graph.vue';

export default {
  components: { Graph },
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
    return {
      preRetirementIncome: 0,
      preRetirementIncomeRaw: '',
      availableYears: this.generateAvailableYears(),
      conversionStartYear: new Date().getFullYear(),
      yearsToConvert: 0,
      rothGrowthRate: 0,
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
      conversionGoals: {
        taxes: true,
        irmaa: false,
        roth: false,
        volatility: false
      },
      conversionMode: 'auto',
      rothWithdrawalAmount: 0,
      rothWithdrawalAmountRaw: '',
      rothWithdrawalStartYear: new Date().getFullYear(),
      // Dummy chart data for cards
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
      assetLineData: {
        labels: Array.from({ length: 30 }, (_, i) => `Year ${i + 1}`),
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
      },
      barOptions: {
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
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
    async recalculateConversion() {
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

      const payload = {
        scenario: {
          ...this.scenario,
          roth_conversion_start_year: this.conversionStartYear,
          roth_conversion_duration: yearsToConvert,
          roth_withdrawal_amount: this.rothWithdrawalAmount,
          roth_withdrawal_start_year: this.rothWithdrawalStartYear,
          pre_retirement_income: this.preRetirementIncome,
          max_annual_amount: this.maxAnnualAmount,
        },
        client: this.client,
        spouse: this.scenario.spouse || (this.scenario.spouse_birthdate ? { birthdate: this.scenario.spouse_birthdate } : null),
        assets: allAssets,
        optimizer_params: {
          mode: modeToSend,
          conversion_start_year: this.conversionStartYear,
          years_to_convert: yearsToConvert,
          annual_conversion_amount: annualConversion,
          roth_growth_rate: this.rothGrowthRate,
          max_annual_amount: this.maxAnnualAmount,
          max_total_amount: totalToConvert,
          roth_withdrawal_amount: this.rothWithdrawalAmount,
          roth_withdrawal_start_year: this.rothWithdrawalStartYear
        }
      };

      // Debug: print payload and mode to console
      console.log('Roth Conversion Payload:', JSON.stringify(payload, null, 2));
      console.log('Optimizer mode being sent:', modeToSend);
      console.log('Years to convert:', yearsToConvert);
      console.log('Total to convert:', totalToConvert);
      console.log('Annual conversion amount:', annualConversion);

      try {
        const response = await fetch('http://localhost:8000/api/roth-optimize/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        this.scenarioResults = data.year_by_year || [];
        this.comparisonMetrics = data.comparison || {};
        this.optimalSchedule = data.optimal_schedule || {};
        this.baselineMetrics = data.baseline || {};
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
      }
    },
    saveRothConversionScenario() {
      // Implement save logic
    },
    exportComparisonReport() {
      // Implement PDF export logic
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
    assetDetails(newVal) {
      console.log('Updated Asset Details:', newVal);
      if (Array.isArray(newVal) && newVal.length > 0) {
        newVal.forEach(asset => {
          console.log('Asset:', asset);
          console.log('Asset Type:', asset.income_type);
        });
      } else {
        console.log('Asset Details is empty or not an array.');
      }
    }
  },
};
</script>

<style src="./RothConversionTab.css"></style>
