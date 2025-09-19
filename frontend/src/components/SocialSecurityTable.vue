<template>
  <div class="social-security-table">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading Social Security data...</span>
      </div>
      <p class="mt-2 text-muted">Loading Social Security overview data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- Table Content -->
    <div v-else-if="tableData && tableData.length > 0" class="table-responsive">
      <table class="table table-hover">
        <thead class="thead-light">
          <tr>
            <th>Year</th>
            <th>Primary Age</th>
            <th v-if="hasSpouse">Spouse Age</th>
            <th>Primary SSI Benefit</th>
            <th v-if="hasSpouse">Spouse SSI Benefit</th>
            <th v-if="hasSsDecrease">SS Decrease</th>
            <th>Total Medicare</th>
            <th>SSI Taxed</th>
            <th>Remaining SSI</th>
            <th>Indicators</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in tableData" :key="row.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
            <td>{{ row.year }}</td>
            <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
            <td v-else></td>
            <td v-if="hasSpouse && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
            <td v-else-if="hasSpouse"></td>
            <td>{{ formatCurrency(row.ss_income_primary_gross || 0) }}</td>
            <td v-if="hasSpouse">{{ formatCurrency(row.ss_income_spouse_gross || 0) }}</td>
            <td v-if="hasSsDecrease" class="text-danger">{{ formatCurrency(getSsDecreaseAmount(row)) }}</td>
            <td style="position: relative;">
              {{ formatCurrency(row.total_medicare || 0) }}
              <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                ℹ️
              </span>
              <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
              </div>
            </td>
            <td>{{ formatCurrency(row.ssi_taxed || 0) }}</td>
            <td :class="{ 'cell-negative': getRemainingSSI(row) < 0 }">
              {{ formatCurrency(getRemainingSSI(row)) }}
            </td>
            <td style="position: relative; text-align: center;">
              <span v-if="row.ss_decrease_applied" class="ss-decrease-icon" @click.stop="toggleSsDecreaseTooltip(idx)" title="Social Security Decrease">
                📉
              </span>
              <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon-table" @click.stop="toggleIrmaaTooltip(idx)" title="IRMAA Information" :style="{ marginLeft: row.ss_decrease_applied ? '5px' : '0' }">
                ℹ️
              </span>
              <span v-if="isHoldHarmlessProtected(row)" class="hold-harmless-icon" @click.stop="toggleHoldHarmlessTooltip(idx)" title="Hold Harmless Protection" :style="{ marginLeft: (row.ss_decrease_applied || isIrmaaBracketHit(row, idx)) ? '5px' : '0' }">
                🔒
              </span>
              <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                {{ getIrmaaBracketLabel(row) }}
              </div>
              <div v-if="openSsDecreaseTooltipIdx === idx" class="ss-decrease-popover">
                Social Security {{ reductionPercentage }}% reduction applied starting {{ row.year }}
              </div>
              <div v-if="openHoldHarmlessTooltipIdx === idx" class="hold-harmless-popover">
                Hold Harmless Protection: Social Security maintained at previous year's level. Without this protection, you would have received {{ formatCurrency(row.original_remaining_ss || 0) }} ({{ formatCurrency(row.hold_harmless_amount || 0) }} less).
              </div>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { apiService } from '@/services/api';

export default {
  name: 'SocialSecurityTable',

  props: {
    scenarioId: {
      type: [Number, String],
      required: true
    },
    client: {
      type: Object,
      default: () => ({})
    },
    scenario: {
      type: Object,
      default: () => ({})
    },
    mortalityAge: {
      type: [Number, String],
      required: false
    },
    spouseMortalityAge: {
      type: [Number, String],
      required: false
    }
  },

  emits: ['data-loaded'],

  setup(props, { emit }) {
    // Reactive state
    const loading = ref(false);
    const error = ref(null);
    const comprehensiveData = ref(null);
    const openIrmaaTooltipIdx = ref(null);
    const openSsDecreaseTooltipIdx = ref(null);
    const openHoldHarmlessTooltipIdx = ref(null);

    // Computed properties
    const tableData = computed(() => {
      return comprehensiveData.value?.years || [];
    });

    const hasSpouse = computed(() => {
      const taxStatus = props.client?.tax_status?.toLowerCase();
      return taxStatus && taxStatus !== 'single';
    });

    const hasSsDecrease = computed(() => {
      // Check if any row has SS decrease applied
      return tableData.value && tableData.value.some(row => row.ss_decrease_applied);
    });

    const reductionPercentage = computed(() => {
      return props.scenario?.ss_adjustment_amount || 23;
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
      openSsDecreaseTooltipIdx.value = null;
      openHoldHarmlessTooltipIdx.value = null;
    };

    const toggleSsDecreaseTooltip = (idx) => {
      openSsDecreaseTooltipIdx.value = openSsDecreaseTooltipIdx.value === idx ? null : idx;
      openIrmaaTooltipIdx.value = null;
      openHoldHarmlessTooltipIdx.value = null;
    };

    const toggleHoldHarmlessTooltip = (idx) => {
      openHoldHarmlessTooltipIdx.value = openHoldHarmlessTooltipIdx.value === idx ? null : idx;
      openIrmaaTooltipIdx.value = null;
      openSsDecreaseTooltipIdx.value = null;
    };

    const isHoldHarmlessProtected = (row) => {
      return row.hold_harmless_protected === true;
    };

    const getSsDecreaseAmount = (row) => {
      if (!row.ss_decrease_applied) {
        return 0;
      }
      return parseFloat(row.ss_decrease_amount || 0);
    };

    const getRemainingSSI = (row) => {
      // Use backend calculation that includes Hold Harmless adjustments
      if (row.remaining_ss !== undefined) {
        return parseFloat(row.remaining_ss);
      }

      // Fallback calculation if remaining_ss not available
      const primarySSI = parseFloat(row.ss_income_primary_gross || 0);
      const spouseSSI = parseFloat(row.ss_income_spouse_gross || 0);
      const totalSSI = primarySSI + spouseSSI;
      const ssDecrease = getSsDecreaseAmount(row);
      const medicare = parseFloat(row.total_medicare || 0);

      return totalSSI - ssDecrease - medicare;
    };

    const fetchComprehensiveData = async () => {
      if (!props.scenarioId) {
        console.warn('No scenario ID provided, skipping Social Security data fetch');
        return;
      }

      loading.value = true;
      error.value = null;

      try {
        const config = apiService.getConfig();
        const url = apiService.getUrl(`/api/scenarios/${props.scenarioId}/comprehensive-summary/`);

        console.log('Fetching Social Security data from:', url);
        const response = await axios.get(url, config);
        comprehensiveData.value = response.data;

        // Emit the data for parent component to use in graphs
        emit('data-loaded', response.data);
      } catch (err) {
        console.error('Error fetching Social Security data:', err);
        console.error('Request details:', {
          scenarioId: props.scenarioId,
          url: apiService.getUrl(`/api/scenarios/${props.scenarioId}/comprehensive-summary/`),
          error: err.response?.data || err.message
        });
        error.value = err.response?.data?.error || 'Failed to load Social Security data';
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
      hasSpouse,
      hasSsDecrease,
      reductionPercentage,
      openIrmaaTooltipIdx,
      openSsDecreaseTooltipIdx,
      openHoldHarmlessTooltipIdx,
      formatCurrency,
      isIrmaaBracketHit,
      getIrmaaBracketLabel,
      toggleIrmaaTooltip,
      toggleSsDecreaseTooltip,
      toggleHoldHarmlessTooltip,
      isHoldHarmlessProtected,
      getSsDecreaseAmount,
      getRemainingSSI
    };
  }
};
</script>

<style scoped>
.social-security-table {
  position: relative;
}

.irmaa-bracket-row {
  border-top: 2px solid #ff8000 !important;
}

.irmaa-info-icon,
.irmaa-info-icon-table {
  margin-left: 6px;
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}

.ss-decrease-icon {
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}

.hold-harmless-icon {
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}

.irmaa-popover,
.ss-decrease-popover,
.hold-harmless-popover {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  border: 1px solid #aaa;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 6px 12px;
  z-index: 10;
  font-size: 0.95em;
  white-space: nowrap;
}

.ss-decrease-popover {
  background: #fff9e6;
  border-color: #ffc107;
}

.hold-harmless-popover {
  background: #f0f8ff;
  border-color: #007bff;
  max-width: 300px;
  white-space: normal;
}

.text-danger {
  color: #c0392b !important;
}

.cell-negative {
  background: #ec4836 !important;
  color: #fff !important;
}

/* Zebra striping */
.table tbody tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Hover effect */
.table tbody tr:hover {
  background-color: rgba(0, 123, 255, 0.1);
}
</style>