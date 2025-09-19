<template>
  <div class="financial-overview-table">
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
      <table class="table table-hover">
        <thead class="thead-light">
          <tr>
            <th>Year</th>
            <th>Primary Age</th>
            <th v-if="hasSpouse">Spouse Age</th>
            <th>Gross Income</th>
            <th>AGI</th>
            <th>MAGI</th>
            <th>Tax Bracket</th>
            <th>Federal Tax</th>
            <th>Total Medicare</th>
            <th>Remaining Income</th>
            <th>Indicators</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(year, idx) in tableData" :key="year.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(year, idx) }">
            <td>{{ year.year }}</td>
            <td v-if="year.primary_age <= (Number(mortalityAge) || 90)">{{ year.primary_age }}</td>
            <td v-else></td>
            <td v-if="hasSpouse && year.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ year.spouse_age }}</td>
            <td v-else-if="hasSpouse"></td>
            <td>{{ formatCurrency(year.gross_income_total || 0) }}</td>
            <td>{{ formatCurrency(year.agi || 0) }}</td>
            <td>{{ formatCurrency(year.magi || 0) }}</td>
            <td>{{ year.tax_bracket || '-' }}</td>
            <td>{{ formatCurrency(year.federal_tax || 0) }}</td>
            <td>{{ formatCurrency(year.total_medicare || 0) }}</td>
            <td>{{ formatCurrency(calculateRemainingIncome(year)) }}</td>
            <td style="position: relative; text-align: center;">
              <span v-if="year.ss_decrease_applied" class="ss-decrease-icon" @click.stop="toggleSsDecreaseTooltip(idx)" title="Social Security Decrease">
                📉
              </span>
              <span v-if="isIrmaaBracketHit(year, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)" title="IRMAA Information" :style="{ marginLeft: year.ss_decrease_applied ? '5px' : '0' }">
                ℹ️
              </span>
              <span v-if="isHoldHarmlessProtected(year)" class="hold-harmless-icon" @click.stop="toggleHoldHarmlessTooltip(idx)" title="Hold Harmless Protection" :style="{ marginLeft: (year.ss_decrease_applied || isIrmaaBracketHit(year, idx)) ? '5px' : '0' }">
                🔒
              </span>
              <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                {{ getIrmaaBracketLabel(year) }}
              </div>
              <div v-if="openSsDecreaseTooltipIdx === idx" class="ss-decrease-popover">
                Social Security Decrease
              </div>
              <div v-if="openHoldHarmlessTooltipIdx === idx" class="hold-harmless-popover">
                Hold Harmless Protection: Social Security maintained at previous year's level. Without this protection, you would have received {{ formatCurrency(year.original_remaining_ss || 0) }} ({{ formatCurrency(year.hold_harmless_amount || 0) }} less).
              </div>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr style="font-weight: bold;">
            <td>Total</td>
            <td></td>
            <td v-if="hasSpouse"></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td>{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0)) }}</td>
            <td>{{ formatCurrency(tableData.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0)) }}</td>
            <td></td>
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
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { apiService } from '@/services/api';

export default {
  name: 'FinancialOverviewTable',

  props: {
    scenarioId: {
      type: [Number, String],
      required: true
    },
    client: {
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

    const calculateRemainingIncome = (year) => {
      const gross = parseFloat(year.gross_income_total || 0);
      const federalTax = parseFloat(year.federal_tax || 0);
      const totalMedicare = parseFloat(year.total_medicare || 0);
      return gross - federalTax - totalMedicare;
    };

    const isIrmaaBracketHit = (row, idx) => {
      return row.irmaa_bracket_number > 0;
    };

    const isHoldHarmlessProtected = (row) => {
      return row.hold_harmless_applied || row.hold_harmless_amount > 0;
    };

    const getIrmaaBracketLabel = (row) => {
      if (row.irmaa_bracket_number > 0) {
        return `IRMAA Bracket ${row.irmaa_bracket_number}`;
      }
      return '';
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
      hasSpouse,
      openIrmaaTooltipIdx,
      openSsDecreaseTooltipIdx,
      openHoldHarmlessTooltipIdx,
      formatCurrency,
      calculateRemainingIncome,
      isIrmaaBracketHit,
      isHoldHarmlessProtected,
      getIrmaaBracketLabel,
      toggleIrmaaTooltip,
      toggleSsDecreaseTooltip,
      toggleHoldHarmlessTooltip
    };
  }
};
</script>

<style scoped>
.irmaa-bracket-row {
  background-color: rgba(255, 193, 7, 0.1);
}

.ss-decrease-icon, .irmaa-info-icon, .hold-harmless-icon {
  cursor: pointer;
  font-size: 1.1em;
  margin: 0 2px;
}

.irmaa-popover, .ss-decrease-popover, .hold-harmless-popover {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-top: 5px;
}

.irmaa-popover::before, .ss-decrease-popover::before, .hold-harmless-popover::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid #333;
}

.hold-harmless-popover {
  width: 250px;
  white-space: normal;
}
</style>