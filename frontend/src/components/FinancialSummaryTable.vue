<template>
  <div class="financial-summary-table">
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
    <div v-else-if="tableData && tableData.length > 0" class="table-responsive">
      <table class="table table-hover table-sm">
        <thead class="thead-light" style="position: sticky; top: 0; z-index: 20;">
          <tr>
            <!-- Demographics Columns -->
            <th colspan="3" class="text-center bg-info text-white">Demographics</th>

            <!-- Tax Columns -->
            <th colspan="5" class="text-center bg-warning">Taxes</th>

            <!-- Medicare Columns -->
            <th colspan="1" class="text-center bg-danger text-white">Medicare</th>

            <!-- Net Income Columns -->
            <th colspan="4" class="text-center bg-primary text-white">Net Income</th>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <!-- Demographics -->
            <th style="background-color: #f8f9fa;">Year</th>
            <th style="background-color: #f8f9fa;">{{ primaryName }} Age</th>
            <th v-if="hasSpouse" style="background-color: #f8f9fa;">{{ spouseName }} Age</th>

            <!-- Taxes -->
            <th>AGI</th>
            <th>MAGI</th>
            <th>Taxable Income</th>
            <th>Federal Tax</th>
            <th class="border-end">State Tax</th>

            <!-- Medicare -->
            <th class="border-end">Total Medicare</th>

            <!-- Net Income -->
            <th>Gross Income</th>
            <th>After Tax</th>
            <th>After Medicare</th>
            <th>Remaining</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="year in tableData" :key="year.year">
            <!-- Demographics -->
            <td>{{ year.year }}</td>
            <td>{{ year.primary_age || '-' }}</td>
            <td v-if="hasSpouse">{{ year.spouse_age || '-' }}</td>

            <!-- Taxes -->
            <td>{{ formatCurrency(year.agi || 0) }}</td>
            <td>{{ formatCurrency(year.magi || 0) }}</td>
            <td>{{ formatCurrency(year.taxable_income || 0) }}</td>
            <td>{{ formatCurrency(year.federal_tax || 0) }}</td>
            <td class="border-end">{{ formatCurrency(year.state_tax || 0) }}</td>

            <!-- Medicare -->
            <td class="border-end">{{ formatCurrency(year.total_medicare || 0) }}</td>

            <!-- Net Income -->
            <td>{{ formatCurrency(year.gross_income_total || 0) }}</td>
            <td>{{ formatCurrency(year.after_tax_income || 0) }}</td>
            <td>{{ formatCurrency(year.after_medicare_income || 0) }}</td>
            <td class="fw-bold">{{ formatCurrency(year.remaining_income || 0) }}</td>
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
  name: 'FinancialSummaryTable',

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
.financial-summary-table {
  position: relative;
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

/* Badge styles */
.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>