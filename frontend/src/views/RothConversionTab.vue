<template>
  <div v-if="filteredAssets.length > 0">
    <!-- Section 1: Asset Selection Panel -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Asset Selection Panel</h5>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Owner</th>
                <th>Current Value</th>
                <th>Amount to Convert</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asset in filteredAssets" :key="asset.income_type || asset.id">
                <td>{{ asset.income_type || 'Unknown' }}</td>
                <td>{{ asset.owned_by || 'Unknown' }}</td>
                <td>${{ parseFloat(asset.current_asset_balance || 0).toFixed(2) }}</td>
                <td><input type="number" v-model="asset.amount_to_convert" :max="asset.current_asset_balance || 0" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Section 2: Conversion Schedule Parameters -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Conversion Schedule Parameters</h5>
        <div class="row">
          <div class="col-md-4">
            <label for="preRetirementIncome">Projected Pre-Retirement Household Income</label>
            <input type="number" id="preRetirementIncome" v-model="preRetirementIncome" class="form-control" />
          </div>
          <div class="col-md-4">
            <label for="conversionStartYear">Conversion Start Year</label>
            <select id="conversionStartYear" v-model="conversionStartYear" class="form-control">
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="rothGrowthRate">Roth Growth Rate (%)</label>
            <input type="number" id="rothGrowthRate" v-model="rothGrowthRate" class="form-control" />
          </div>
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
                <td>${{ parseFloat(row.gross_income || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.roth_conversion || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.taxable_income || 0).toFixed(2) }}</td>
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
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Lifetime Medicare Premiums</td>
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Lifetime IRMAA Surcharges</td>
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Net Lifetime Spendable Income</td>
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Final Roth IRA Balance</td>
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Total Net Assets at Mortality</td>
                <td>$0</td>
                <td>$0</td>
              </tr>
              <tr>
                <td>Average IRMAA Tier Hit</td>
                <td>Tier Level</td>
                <td>Tier Level</td>
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
export default {
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
      availableYears: this.generateAvailableYears(),
      conversionStartYear: new Date().getFullYear(),
      yearsToConvert: 0,
      rothGrowthRate: 0
    };
  },
  computed: {
    filteredAssets() {
      return this.assetDetails.filter(asset => {
        if (!asset || !asset.income_type) return false;
        const normalizedType = asset.income_type.trim().toLowerCase();
        console.log('Normalized Type:', normalizedType); // Log the normalized type
        return normalizedType === 'traditional_401k';
      });
    }
  },
  methods: {
    generateAvailableYears() {
      const currentYear = new Date().getFullYear();
      return Array.from({ length: 41 }, (_, i) => currentYear + i);
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

<style scoped>
input[type="range"] {
  width: 100%;
  background: transparent;
}

input[type="range"]::-webkit-slider-runnable-track {
  height: 8px;
  background: #ddd;
  border-radius: 5px;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #007bff;
  border-radius: 50%;
  cursor: pointer;
  margin-top: -4px; /* Center the thumb */
}

input[type="range"]::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #007bff;
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]::-moz-range-track {
  height: 8px;
  background: #ddd;
  border-radius: 5px;
}

datalist {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 0 10px;
}

datalist option {
  position: relative;
  text-align: center;
}

datalist option::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 10px;
  background: #ddd; /* Match the slider line color */
}
</style> 