<template>
  <div>
    <!-- Card -->
    <div class="card mb-3 mb-lg-5" >
      <!-- Header -->
      <div class="card-header card-header-content-between">
        <!-- <h6 class="card-subtitle mb-0">Project budget: <span class="h3 ms-sm-2">$150,000.00 USD</span></h6> -->

        <!-- Dropdown -->
        <div class="dropdown">
          <button type="button" class="btn btn-white btn-sm dropdown-toggle" @click="toggleDropdown('financial')" :aria-expanded="isDropdownOpen.financial">
            <i class="bi-download me-2"></i> Export
          </button>

          <div class="dropdown-menu dropdown-menu-sm-end" :class="{ show: isDropdownOpen.financial }" aria-labelledby="usersExportDropdown">
            <span class="dropdown-header">Export Options</span>
            <a id="export-excel" class="dropdown-item" href="javascript:;" @click="exportGraphAndDataToExcel">
              <img class="avatar avatar-xss avatar-4x3 me-2" src="/assets/svg/brands/excel-icon.svg" alt="Image Description">
              Export graph and table to Excel
            </a>
            <a id="export-pdf" class="dropdown-item" href="javascript:;" @click="exportGraphAndDataToPDF">
              <img class="avatar avatar-xss avatar-4x3 me-2" src="/assets/svg/brands/pdf-icon.svg" alt="Image Description">
              Export graph and data to PDF
            </a>
            <a id="export-graph" class="dropdown-item" href="javascript:;">
              Export graph only
            </a>
            <a id="export-csv" class="dropdown-item" href="javascript:;" @click="exportTableToCSV">
              <img class="avatar avatar-xss avatar-4x3 me-2" src="/assets/svg/components/placeholder-csv-format.svg" alt="Image Description">
              Export table only as CSV
            </a>
          </div>
        </div>
        <!-- End Dropdown -->
      </div>
      <!-- End Header -->

      <!-- Body -->
      <div class="card-body">
        <!-- Mixed Line/Bar Chart -->
        <canvas id="financialOverviewChart" style="width: 100%; height: 300px !important;"></canvas>
        <!-- End Mixed Chart -->
      </div>
      <!-- End Body -->
    </div>
    <!-- End Card -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-header card-header-content-between">
        <div v-if="filteredResults.length" class="table-responsive mt-4">
          <table class="table table-hover">
            <thead class="thead-light">
              <tr>
                <th>Year</th>
                <th>Primary Age</th>
                <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
                <th>Gross Income</th>
                <th>AGI</th>
                <th>MAGI</th>
                <th>Tax Bracket</th>
                <th>Federal Tax</th>
                <th>Total Medicare</th>
                <th>Remaining Income</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in filteredResults" :key="row.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
                <td>{{ row.year }}</td>
                <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
                <td v-else></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
                <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td>{{ formatCurrency(row.gross_income) }}</td>
                <td>{{ formatCurrency(row.agi) }}</td>
                <td>{{ formatCurrency(row.magi) }}</td>
                <td>{{ row.tax_bracket }}</td>
                <td>{{ formatCurrency(row.federal_tax) }}</td>
                <td style="position: relative;">
                  {{ formatCurrency(row.total_medicare) }}
                  <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                    ℹ️
                  </span>
                  <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                    IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
                  </div>
                </td>
                <td>{{ formatCurrency(parseFloat(row.gross_income) - (parseFloat(row.federal_tax) + parseFloat(row.total_medicare))) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight: bold;">
                <td>Total</td>
                <td></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>{{ formatCurrency(filteredResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0)) }}</td>
                <td>{{ formatCurrency(filteredResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0)) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { Chart } from 'chart.js';

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
  // No Graph component needed
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    filteredResults: {
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
        financial: false
      },
      openIrmaaTooltipIdx: null,
      chartInstance: null
    };
  },
  computed: {
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
  watch: {
    filteredResults: {
      handler(newResults) {
        this.renderFinancialChart(newResults);
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    renderFinancialChart(results) {
      if (!results || results.length === 0) return;
      // Destroy previous chart instance if exists
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      // Extract years for labels
      const years = results.map(row => row.year);
      // Build datasets: lines for income, stacked bars for tax/medicare
      const datasets = [
        {
          type: 'line',
          label: 'Gross Income',
          data: results.map(row => parseFloat(row.gross_income) || 0),
          borderColor: '#4285f4',
          backgroundColor: 'rgba(66,133,244,0.1)',
          borderWidth: 2,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 2,
          order: 1
        },
        {
          type: 'line',
          label: 'Net Income',
          data: results.map(row => {
            const gross = parseFloat(row.gross_income) || 0;
            const tax = parseFloat(row.federal_tax) || 0;
            const medicare = parseFloat(row.total_medicare) || 0;
            return gross - tax - medicare;
          }),
          borderColor: '#34a853',
          backgroundColor: 'rgba(52,168,83,0.1)',
          borderWidth: 2,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 2,
          order: 1
        },
        {
          type: 'bar',
          label: 'Federal Tax',
          data: results.map(row => parseFloat(row.federal_tax) || 0),
          backgroundColor: '#ea4335',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        },
        {
          type: 'bar',
          label: 'Medicare',
          data: results.map(row => parseFloat(row.total_medicare) || 0),
          backgroundColor: '#fbbc05',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        }
      ];
      const ctx = document.getElementById('financialOverviewChart');
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Year'
              }
            },
            y: {
              stacked: true,
              title: {
                display: true,
                text: 'Amount ($)'
              },
              ticks: {
                beginAtZero: true,
                callback: function(value) {
                  return '$' + value.toLocaleString();
                }
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          },
          interaction: {
            mode: 'index',
            intersect: false
          }
        }
      });
    },
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
      // Returns true if this row's MAGI crosses into a new IRMAA bracket compared to the previous row
      const magi = Number(row.magi);
      const thresholds = this.irmaaThresholds;
      if (idx === 0) {
        // First row: highlight if above first threshold
        return thresholds.some(t => magi >= t);
      }
      const prevMagi = Number(this.filteredResults[idx - 1]?.magi);
      // Find the bracket index for current and previous
      const getBracket = (m) => thresholds.findIndex(t => m < t);
      const currBracket = getBracket(magi);
      const prevBracket = getBracket(prevMagi);
      // If the bracket index decreases, we've crossed up into a new bracket
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
    if (this.filteredResults && this.filteredResults.length) {
      this.renderFinancialChart(this.filteredResults);
    }
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  },
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
</style> 