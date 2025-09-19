<template>
  <div class="financial-comprehensive-table">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading comprehensive data...</span>
      </div>
      <p class="mt-2 text-muted">Loading financial overview data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Table Content -->
    <div v-else-if="tableData && tableData.length > 0" class="table-responsive" style="overflow-x: auto;">
      <table class="table table-hover table-sm" style="min-width: 1100px;">
        <thead class="thead-light" style="position: sticky; top: 0; z-index: 20;">
          <tr>
            <!-- Demographics Columns (Sticky) -->
            <th colspan="3" class="text-center bg-info text-white">Demographics</th>

            <!-- Financial Columns -->
            <th colspan="4" class="text-center bg-success text-white">Income & Tax Info</th>

            <!-- Medicare Columns -->
            <th colspan="2" class="text-center bg-danger text-white">Medicare</th>

            <!-- Net Income Columns -->
            <th colspan="2" class="text-center bg-primary text-white">Net Income</th>

            <!-- Indicators Column -->
            <th class="text-center bg-secondary text-white">Indicators</th>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <!-- Demographics -->
            <th style="position: sticky; left: 0; z-index: 10; background-color: #f8f9fa;">Year</th>
            <th style="background-color: #f8f9fa;">{{ primaryName }} Age</th>
            <th v-if="hasSpouse" style="background-color: #f8f9fa;">{{ spouseName }} Age</th>

            <!-- Financial Info -->
            <th>Gross Income</th>
            <th>AGI</th>
            <th>MAGI</th>
            <th class="border-end">Federal Tax</th>

            <!-- Medicare -->
            <th>Total Medicare</th>
            <th class="border-end">IRMAA Bracket</th>

            <!-- Net Income -->
            <th>After Tax</th>
            <th class="border-end">Remaining</th>

            <!-- Indicators -->
            <th class="sticky-column" style="position: sticky; right: 0; z-index: 10; background-color: #f8f9fa;">
              <div class="d-flex justify-content-center align-items-center">
                <span class="me-2" title="SS Decrease">📉</span>
                <span class="me-2" title="IRMAA Bracket">ℹ️</span>
                <span title="Hold Harmless">🔒</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="year in tableData" :key="year.year">
            <!-- Demographics -->
            <td style="position: sticky; left: 0; background-color: white; z-index: 5;">{{ year.year }}</td>
            <td>{{ year.primary_age || '-' }}</td>
            <td v-if="hasSpouse">{{ year.spouse_age || '-' }}</td>

            <!-- Financial Info -->
            <td>{{ formatCurrency(year.gross_income_total || 0) }}</td>
            <td>{{ formatCurrency(year.agi || 0) }}</td>
            <td>{{ formatCurrency(year.magi || 0) }}</td>
            <td class="border-end">{{ formatCurrency(year.federal_tax || 0) }}</td>

            <!-- Medicare -->
            <td>{{ formatCurrency(year.total_medicare || 0) }}</td>
            <td class="border-end">
              <span v-if="year.irmaa_bracket_number > 0" class="badge bg-warning text-dark">
                {{ year.irmaa_bracket_number }}
              </span>
              <span v-else>-</span>
            </td>

            <!-- Net Income -->
            <td>{{ formatCurrency(year.after_tax_income || 0) }}</td>
            <td class="border-end fw-bold">{{ formatCurrency(year.remaining_income || 0) }}</td>

            <!-- Indicators -->
            <td class="sticky-column text-center" style="position: sticky; right: 0; background-color: white; z-index: 5;">
              <span v-if="year.ss_decrease_applied" class="me-1" title="Social Security Decrease Applied">📉</span>
              <span v-if="year.irmaa_bracket_number > 0" class="me-1" :title="`IRMAA Bracket ${year.irmaa_bracket_number}`">ℹ️</span>
              <span v-if="year.hold_harmless_applied" :title="`Hold Harmless Protection: Saved ${formatCurrency(year.hold_harmless_amount || 0)}`">🔒</span>
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
  name: 'FinancialComprehensiveTable',

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

  emits: ['data-loaded'],

  setup(props, { emit }) {
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

        // Emit the data for parent component to use in graphs
        emit('data-loaded', response.data);
      } catch (err) {
        console.error('Error fetching comprehensive data:', err);
        error.value = err.response?.data?.error || 'Failed to load financial overview data';
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
      formatCurrency
    };
  }
};
</script>

<style scoped>
.financial-comprehensive-table {
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

/* Indicator styles */
.sticky-column span {
  cursor: help;
  font-size: 1.1rem;
}

.sticky-column span:hover {
  transform: scale(1.2);
  transition: transform 0.2s;
}
</style>