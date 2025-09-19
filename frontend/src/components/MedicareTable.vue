<template>
  <div class="medicare-table">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading Medicare data...</span>
      </div>
      <p class="mt-2 text-muted">Loading Medicare overview data...</p>
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

            <!-- Medicare Columns -->
            <th colspan="4" class="text-center bg-danger text-white">Medicare</th>

            <!-- Indicators Column -->
            <th class="text-center bg-secondary text-white">Indicators</th>
          </tr>
          <tr style="background-color: #f8f9fa;">
            <!-- Demographics -->
            <th style="background-color: #f8f9fa;">Year</th>
            <th style="background-color: #f8f9fa;">{{ primaryName }} Age</th>
            <th v-if="hasSpouse" style="background-color: #f8f9fa;">{{ spouseName }} Age</th>

            <!-- Medicare -->
            <th>Part B</th>
            <th>Part D</th>
            <th>IRMAA Surcharge</th>
            <th class="border-end">Total Medicare</th>

            <!-- Indicators -->
            <th style="background-color: #f8f9fa;">
              <div class="d-flex justify-content-center align-items-center">
                <span class="me-2" title="IRMAA Bracket">ℹ️</span>
                <span title="Hold Harmless">🔒</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(year, idx) in tableData" :key="year.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(year, idx) }">
            <!-- Demographics -->
            <td>{{ year.year }}</td>
            <td>{{ year.primary_age || '-' }}</td>
            <td v-if="hasSpouse">{{ year.spouse_age || '-' }}</td>

            <!-- Medicare -->
            <td>{{ formatCurrency(year.part_b || 0) }}</td>
            <td>{{ formatCurrency(year.part_d || 0) }}</td>
            <td>{{ formatCurrency(year.irmaa_surcharge || 0) }}</td>
            <td class="border-end" style="position: relative;">
              {{ formatCurrency(year.total_medicare || 0) }}
              <span v-if="isIrmaaBracketHit(year, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)" title="IRMAA Information">
                ℹ️
              </span>
              <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                {{ getIrmaaBracketLabel(year) }}
              </div>
            </td>

            <!-- Indicators -->
            <td class="text-center">
              <span v-if="year.irmaa_bracket_number > 0" class="me-1" :title="`IRMAA Bracket ${year.irmaa_bracket_number}`">ℹ️</span>
              <span v-if="year.hold_harmless_applied" :title="`Hold Harmless Protection: Saved ${formatCurrency(year.hold_harmless_amount || 0)}`">🔒</span>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr style="font-weight: bold;">
            <td colspan="3"><strong>Total</strong></td>
            <td>{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.part_b || 0), 0)) }}</td>
            <td>{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.part_d || 0), 0)) }}</td>
            <td>{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.irmaa_surcharge || 0), 0)) }}</td>
            <td class="border-end">{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0)) }}</td>
            <td></td>
          </tr>
        </tfoot>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { apiService } from '@/services/api';

export default {
  name: 'MedicareTable',

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
    const openIrmaaTooltipIdx = ref(null);

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

    const isIrmaaBracketHit = (row, idx) => {
      // Returns true if this row's IRMAA bracket is different from the previous row
      const currentBracket = row.irmaa_bracket_number || 0;

      if (idx === 0) {
        // First row - show if in any bracket
        return currentBracket > 0;
      }

      // Check if bracket changed from previous row
      const prevRow = tableData.value[idx - 1];
      const prevBracket = prevRow?.irmaa_bracket_number || 0;

      // Show indicator if bracket number changed (either up or down)
      return currentBracket !== prevBracket;
    };

    const getIrmaaBracketLabel = (row) => {
      const magi = Number(row.magi);
      const bracketNum = row.irmaa_bracket_number || 0;
      const bracketThreshold = Number(row.irmaa_bracket_threshold);
      const year = row.year;

      const bracketLabels = {
        0: 'No IRMAA',
        1: 'IRMAA Bracket 1',
        2: 'IRMAA Bracket 2',
        3: 'IRMAA Bracket 3',
        4: 'IRMAA Bracket 4',
        5: 'IRMAA Bracket 5 (Highest)'
      };

      if (bracketNum > 0) {
        return `${bracketLabels[bracketNum] || `IRMAA Bracket ${bracketNum}`}: MAGI (${formatCurrency(magi)}) exceeds ${formatCurrency(bracketThreshold)} in ${year}`;
      } else {
        const firstThreshold = Number(row.irmaa_threshold);
        const difference = firstThreshold - magi;
        return `No IRMAA: ${formatCurrency(difference)} below first threshold of ${formatCurrency(firstThreshold)} in ${year}`;
      }
    };

    const toggleIrmaaTooltip = (idx) => {
      openIrmaaTooltipIdx.value = openIrmaaTooltipIdx.value === idx ? null : idx;
    };

    const fetchComprehensiveData = async () => {
      if (!props.scenarioId) {
        console.warn('No scenario ID provided, skipping Medicare data fetch');
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        const config = apiService.getConfig();
        const url = apiService.getUrl(`/api/scenarios/${props.scenarioId}/comprehensive-summary/`);

        console.log('Fetching Medicare data from:', url);
        const response = await axios.get(url, config);
        comprehensiveData.value = response.data;

        // Emit the data for parent component to use in graphs
        emit('data-loaded', response.data);
      } catch (err) {
        console.error('Error fetching Medicare data:', err);
        console.error('Request details:', {
          scenarioId: props.scenarioId,
          url: apiService.getUrl(`/api/scenarios/${props.scenarioId}/comprehensive-summary/`),
          error: err.response?.data || err.message
        });
        error.value = err.response?.data?.error || 'Failed to load Medicare data';
      } finally {
        loading.value = false;
      }
    };

    // Watch for scenario changes
    watch(() => props.scenarioId, (newId, oldId) => {
      if (newId && newId !== oldId) {
        fetchComprehensiveData();
      }
    });

    // Load data on mount (with slight delay to ensure props are available)
    onMounted(() => {
      // Use nextTick to ensure all props are properly set
      nextTick(() => {
        fetchComprehensiveData();
      });
    });

    return {
      loading,
      error,
      comprehensiveData,
      tableData,
      primaryName,
      spouseName,
      hasSpouse,
      openIrmaaTooltipIdx,
      formatCurrency,
      isIrmaaBracketHit,
      getIrmaaBracketLabel,
      toggleIrmaaTooltip
    };
  }
};
</script>

<style scoped>
.medicare-table {
  position: relative;
}

.irmaa-bracket-row {
  border-top: 2px solid #ff8000 !important;
}

.irmaa-info-icon {
  margin-left: 6px;
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}

.irmaa-popover {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  border: 1px solid #aaa;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 8px 12px;
  z-index: 10;
  font-size: 0.9em;
  max-width: 400px;
  white-space: normal;
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