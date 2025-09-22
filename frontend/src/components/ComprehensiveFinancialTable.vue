<template>
  <div class="comprehensive-financial-table">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading comprehensive data...</span>
      </div>
      <p class="mt-2 text-muted">Loading comprehensive financial summary...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Table Content -->
    <div v-else-if="tableData && tableData.length > 0" class="table-responsive" style="overflow-x: auto;">
      <table class="table table-hover table-sm" style="min-width: 1400px;">
        <thead class="thead-light" style="position: sticky; top: 0; z-index: 20;">
          <tr>
            <!-- Demographics Columns (Sticky) -->
            <th :colspan="hasSpouse ? 3 : 2" class="text-center bg-info text-white">Demographics</th>

            <!-- Income Sources Columns -->
            <th v-if="incomeSourceColumns.length > 0" :colspan="incomeSourceColumns.length" class="text-center bg-success text-white">
              Income Sources
            </th>

            <!-- Asset Balances Columns -->
            <th v-if="assetBalanceColumns.length > 0" :colspan="assetBalanceColumns.length" class="text-center bg-success text-white">
              Asset Balances
            </th>

            <!-- RMD Columns -->
            <th colspan="2" class="text-center bg-success text-white">RMDs</th>

            <!-- Tax Columns -->
            <th colspan="7" class="text-center bg-warning">Taxes</th>

            <!-- Medicare Columns -->
            <th colspan="5" class="text-center bg-danger text-white">Medicare/IRMAA</th>

            <!-- Net Income Columns -->
            <th colspan="4" class="text-center bg-primary text-white">Net Income</th>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <!-- Demographics -->
            <th style="position: sticky; left: 0; z-index: 10; background-color: #f8f9fa;">Year</th>
            <th style="background-color: #f8f9fa;">{{ primaryName }} Age</th>
            <th v-if="hasSpouse" style="background-color: #f8f9fa;">{{ spouseName }} Age</th>

            <!-- Income Sources -->
            <th v-for="source in incomeSourceColumns" :key="`income-${source.id}`">
              {{ source.name }}
            </th>

            <!-- Asset Balances -->
            <th v-for="asset in assetBalanceColumns" :key="`balance-${asset.id}`">
              {{ asset.name }}
            </th>

            <!-- RMDs -->
            <th>RMD Required</th>
            <th class="border-end">RMD Total</th>

            <!-- Taxes -->
            <th>AGI</th>
            <th>MAGI</th>
            <th>Taxable Income</th>
            <th>Federal Tax</th>
            <th>State Tax</th>
            <th>Marginal Rate</th>
            <th class="border-end">Effective Rate</th>

            <!-- Medicare -->
            <th>Part B</th>
            <th>Part D</th>
            <th>IRMAA</th>
            <th>Bracket</th>
            <th class="border-end">Total Medicare</th>

            <!-- Net Income -->
            <th>Gross Income</th>
            <th>After Tax</th>
            <th>After Medicare</th>
            <th class="sticky-column fw-bold" style="position: sticky; right: 0; z-index: 10; background-color: #f8f9fa;">
              Remaining
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="year in tableData" :key="year.year">
            <!-- Demographics -->
            <td style="position: sticky; left: 0; background-color: white; z-index: 5;">{{ year.year }}</td>
            <td>{{ year.primary_age || '-' }}</td>
            <td v-if="hasSpouse">{{ year.spouse_age || '-' }}</td>

            <!-- Income Sources -->
            <td v-for="source in incomeSourceColumns" :key="`income-${source.id}-${year.year}`">
              {{ formatCurrency(year.income_by_source?.[source.id] || 0) }}
            </td>

            <!-- Asset Balances -->
            <td v-for="asset in assetBalanceColumns" :key="`balance-${asset.id}-${year.year}`">
              {{ formatCurrency(year.asset_balances?.[asset.id] || 0) }}
            </td>

            <!-- RMDs -->
            <td>
              <span v-if="Object.keys(year.rmd_required || {}).length > 0" class="text-danger">
                {{ formatCurrency(Object.values(year.rmd_required).reduce((a, b) => a + b, 0)) }}
              </span>
              <span v-else>-</span>
            </td>
            <td class="border-end">{{ formatCurrency(year.rmd_total || 0) }}</td>

            <!-- Taxes -->
            <td>{{ formatCurrency(year.agi || 0) }}</td>
            <td>{{ formatCurrency(year.magi || 0) }}</td>
            <td>{{ formatCurrency(year.taxable_income || 0) }}</td>
            <td>{{ formatCurrency(year.federal_tax || 0) }}</td>
            <td>{{ formatCurrency(year.state_tax || 0) }}</td>
            <td>{{ year.marginal_rate || 0 }}%</td>
            <td class="border-end">{{ year.effective_rate || 0 }}%</td>

            <!-- Medicare -->
            <td>{{ formatCurrency(year.part_b || 0) }}</td>
            <td>{{ formatCurrency(year.part_d || 0) }}</td>
            <td>
              <span v-if="year.irmaa_surcharge > 0" class="text-warning">
                {{ formatCurrency(year.irmaa_surcharge) }}
              </span>
              <span v-else>-</span>
            </td>
            <td>
              <span v-if="year.irmaa_bracket_number > 0" class="badge bg-warning text-dark">
                {{ year.irmaa_bracket_number }}
              </span>
              <span v-else>-</span>
            </td>
            <td class="border-end">{{ formatCurrency(year.total_medicare || 0) }}</td>

            <!-- Net Income -->
            <td>{{ formatCurrency(year.gross_income_total || 0) }}</td>
            <td>{{ formatCurrency(year.after_tax_income || 0) }}</td>
            <td>{{ formatCurrency(year.after_medicare_income || 0) }}</td>
            <td class="sticky-column fw-bold" style="position: sticky; right: 0; background-color: #f8f9fa; z-index: 5;">
              {{ formatCurrency(year.remaining_income || 0) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-table fs-1 text-muted"></i>
      <p class="mt-2 text-muted">No data available</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { apiService } from '@/services/api';

export default {
  name: 'ComprehensiveFinancialTable',

  props: {
    scenarioId: {
      type: [Number, String],
      required: true
    },
    client: {
      type: Object,
      default: () => ({})
    }
  },

  setup(props) {
    // Reactive state
    const loading = ref(false);
    const error = ref(null);
    const comprehensiveData = ref(null);

    // Computed properties
    const tableData = computed(() => {
      return comprehensiveData.value?.years || [];
    });

    const primaryName = computed(() => {
      return props.client?.first_name || 'Primary';
    });

    const spouseName = computed(() => {
      return props.client?.spouse?.first_name || 'Spouse';
    });

    const hasSpouse = computed(() => {
      const taxStatus = props.client?.tax_status?.toLowerCase();
      return taxStatus && taxStatus !== 'single';
    });

    // Dynamic column generation based on actual data
    const incomeSourceColumns = computed(() => {
      if (!tableData.value.length) return [];

      const firstYear = tableData.value[0];
      const sources = [];

      if (firstYear.income_by_source) {
        // Get all unique income source IDs from all years
        const allSourceIds = new Set();
        tableData.value.forEach(year => {
          if (year.income_by_source) {
            Object.keys(year.income_by_source).forEach(id => allSourceIds.add(id));
          }
        });

        // Get names from comprehensive data if available
        const incomeNames = comprehensiveData.value?.income_source_names || {};

        // Create column definitions
        allSourceIds.forEach(id => {
          // Try to get the name from the metadata
          let name = incomeNames[id];
          if (!name) {
            // Fallback to default names if not in metadata
            name = `Income ${id}`;
          } else {
            // Capitalize properly
            name = name.split(' ').map(word =>
              word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');
          }

          sources.push({
            id: id,
            name: name
          });
        });
      }

      return sources;
    });

    const assetBalanceColumns = computed(() => {
      if (!tableData.value.length) return [];

      const firstYear = tableData.value[0];
      const assets = [];

      if (firstYear.asset_balances) {
        // Get all unique asset IDs - but only for actual assets with balances
        const allAssetIds = new Set();
        tableData.value.forEach(year => {
          if (year.asset_balances) {
            Object.keys(year.asset_balances).forEach(id => {
              // Only add if it has a non-zero balance (filters out income-only sources)
              if (year.asset_balances[id] > 0) {
                allAssetIds.add(id);
              }
            });
          }
        });

        // Get names from comprehensive data if available
        const assetNames = comprehensiveData.value?.asset_names || {};

        // Create column definitions - only for real assets
        allAssetIds.forEach(id => {
          // Get the name from the metadata (backend already filters income-only types)
          let name = assetNames[id];
          if (name) {
            // Capitalize properly
            name = name.split(' ').map(word =>
              word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');

            assets.push({
              id: id,
              name: name
            });
          }
        });
      }

      return assets;
    });

    // Methods
    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '-';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    };

    const fetchComprehensiveData = async () => {
      loading.value = true;
      error.value = null;

      try {
        const config = apiService.getConfig();
        const url = apiService.getUrl(`/api/scenarios/${props.scenarioId}/comprehensive-summary/`);

        const response = await axios.get(url, config);
        comprehensiveData.value = response.data;
      } catch (err) {
        console.error('Error fetching comprehensive data:', err);
        error.value = err.response?.data?.error || 'Failed to load comprehensive financial summary';
      } finally {
        loading.value = false;
      }
    };

    // Watch for scenario changes
    watch(() => props.scenarioId, () => {
      fetchComprehensiveData();
    });

    // Load data on mount
    onMounted(() => {
      fetchComprehensiveData();
    });

    return {
      loading,
      error,
      comprehensiveData,
      tableData,
      primaryName,
      spouseName,
      hasSpouse,
      incomeSourceColumns,
      assetBalanceColumns,
      formatCurrency
    };
  }
};
</script>

<style scoped>
.comprehensive-financial-table {
  position: relative;
}

.sticky-column {
  position: sticky;
  background-color: #f8f9fa;
  font-weight: 500;
}

/* Keep Bootstrap color classes intact */
.table thead tr:first-child th {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.table thead tr:nth-child(2) th {
  border-bottom: 1px solid #dee2e6;
  font-weight: 600;
  font-size: 0.875rem;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
  font-size: 0.875rem;
  white-space: nowrap;
  vertical-align: middle;
}

.table td {
  font-size: 0.875rem;
  white-space: nowrap;
  vertical-align: middle;
}

.table-responsive {
  max-height: 600px;
  overflow: auto;
}

/* Zebra striping */
.table tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Hover effect */
.table tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

/* Border styles for section separation */
.border-end {
  border-right: 2px solid #dee2e6 !important;
}

/* Sticky styling enhancements */
.sticky-column {
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}

/* Badge styles */
.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>