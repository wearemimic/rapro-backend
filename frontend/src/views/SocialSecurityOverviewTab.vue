<template>
  <div>
    <!-- Row for Graph and Insights -->
    <div class="row mb-3 mb-lg-5">
      <!-- Graph Card (2/3 width) -->
      <div class="col-lg-8">
        <div class="card h-100">
          <div class="card-body">
            <canvas id="socialSecurityChart" style="width: 100%; height: 300px !important;"></canvas>
          </div>
        </div>
      </div>
      <!-- Insights Card (1/3 width) -->
      <div class="col-lg-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Insights</h5>
            <div>
              <!-- Placeholder for insights content -->
              <p>Add insights here...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Row for Graph and Insights -->
    <!-- Card for Table -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <table class="table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Primary Age</th>
              <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
              <th>Social Security Benefit</th>
              <th>Total Medicare</th>
              <th>SSI Taxed</th>
              <th>Remaining SSI</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in filteredResults" :key="row.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
              <td>{{ row.year }}</td>
              <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
              <td v-else></td>
              <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
              <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
              <td>
                <span v-if="client?.tax_status?.toLowerCase() !== 'single'">
                  ${{ parseFloat(row.ss_income || 0).toFixed(2) }} /
                  <span v-if="row.ss_income_spouse !== undefined">${{ parseFloat(row.ss_income_spouse || 0).toFixed(2) }}</span>
                  <span v-else>N/A</span>
                </span>
                <span v-else>
                  ${{ parseFloat(row.ss_income || 0).toFixed(2) }}
                </span>
              </td>
              <td style="position: relative;">
                ${{ parseFloat(row.total_medicare || 0).toFixed(2) }}
                <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                  ℹ️
                </span>
                <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                  IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
                </div>
              </td>
              <td>${{ parseFloat(row.ssi_taxed || 0).toFixed(2) }}</td>
              <td :class="{ 'cell-negative': (parseFloat(row.ss_income || 0) - parseFloat(row.total_medicare || 0)) < 0 }">
                ${{ (parseFloat(row.ss_income || 0) - parseFloat(row.total_medicare || 0)).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- End Card for Table -->
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

const IRMAA_THRESHOLDS = {
  'single': [
    106000, 133000, 167000, 200000, 500000
  ],
  'married filing jointly': [
    212000, 266000, 334000, 400000, 750000
  ],
  'married filing separately': [
    106000, 394000
  ]
};
const IRMAA_LABELS = {
  'single': [
    '≤ $106,000',
    '$106,001 – $133,000',
    '$133,001 – $167,000',
    '$167,001 – $200,000',
    '$200,001 – $500,000',
    '>$500,000'
  ],
  'married filing jointly': [
    '≤ $212,000',
    '$212,001 – $266,000',
    '$266,001 – $334,000',
    '$334,001 – $400,000',
    '$400,001 – $750,000',
    '>$750,000'
  ],
  'married filing separately': [
    '≤ $106,000',
    '$106,001 – $394,000',
    '>$394,000'
  ]
};

export default {
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
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
  data() {
    return {
      isDropdownOpen: {
        socialSecurity: false
      },
      openIrmaaTooltipIdx: null
    };
  },
  computed: {
    filteredResults() {
      const mortalityAge = Number(this.mortalityAge) || 90;
      const spouseMortalityAge = Number(this.spouseMortalityAge) || 90;
      const isSingle = this.client?.tax_status?.toLowerCase() === 'single';
      const maxAge = isSingle ? mortalityAge : Math.max(mortalityAge, spouseMortalityAge);
      return this.scenarioResults.filter(row => {
        if (isSingle) {
          return row.primary_age <= mortalityAge;
        } else {
          return (row.primary_age <= maxAge || (row.spouse_age && row.spouse_age <= maxAge));
        }
      });
    },
    irmaaThresholds() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_THRESHOLDS) {
        return IRMAA_THRESHOLDS[status];
      }
      return IRMAA_THRESHOLDS['single'];
    },
    irmaaLabels() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_LABELS) {
        return IRMAA_LABELS[status];
      }
      return IRMAA_LABELS['single'];
    }
  },
  methods: {
    toggleDropdown(tab) {
      this.isDropdownOpen[tab] = !this.isDropdownOpen[tab];
    },
    exportGraphAndDataToPDF() {
      // Implement PDF export logic
    },
    exportGraphAndDataToExcel() {
      // Implement Excel export logic
    },
    exportTableToCSV() {
      // Implement CSV export logic
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    },
    isIrmaaBracketHit(row, idx) {
      const magi = Number(row.magi);
      const thresholds = this.irmaaThresholds;
      if (idx === 0) {
        return thresholds.some(t => magi >= t);
      }
      const prevMagi = Number(this.filteredResults[idx - 1]?.magi);
      const getBracket = (m) => thresholds.findIndex(t => m < t);
      const currBracket = getBracket(magi);
      const prevBracket = getBracket(prevMagi);
      return currBracket !== prevBracket;
    },
    getIrmaaBracketLabel(row) {
      const magi = Number(row.magi);
      const thresholds = this.irmaaThresholds;
      const labels = this.irmaaLabels;
      for (let i = 0; i < thresholds.length; i++) {
        if (magi <= thresholds[i]) {
          return labels[i];
        }
      }
      return labels[labels.length - 1];
    },
    toggleIrmaaTooltip(idx) {
      this.openIrmaaTooltipIdx = this.openIrmaaTooltipIdx === idx ? null : idx;
    },
    closeIrmaaTooltip() {
      this.openIrmaaTooltipIdx = null;
    },
    handleClickOutside(event) {
      if (!event.target.closest('.irmaa-info-icon') && !event.target.closest('.irmaa-popover')) {
        this.closeIrmaaTooltip();
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
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
  padding: 6px 12px;
  z-index: 10;
  font-size: 0.95em;
  white-space: nowrap;
}
.text-danger {
  color: #c0392b !important;
}
.cell-negative {
  background: #ec4836 !important;
  color: #fff !important;
}
</style> 