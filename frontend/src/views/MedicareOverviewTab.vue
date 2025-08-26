<template>
  <div>
    <!-- Medicare Chart and IRMAA Circle in Separate Cards -->
    <div class="row mb-3 mb-lg-5">
      <!-- Medicare Chart Card (2/3 width) -->
      <div class="col-lg-8 col-md-7 mb-3 mb-lg-0">
        <div class="card h-100">
          <div class="card-body">
            <div class="medicare-chart-container">
              <Graph 
                :data="chartData" 
                :options="chartOptions"
                :height="300"
                type="bar"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- IRMAA Circle Card (1/3 width) -->
      <div class="col-lg-4 col-md-5 mb-3 mb-lg-0">
        <div class="card h-100 d-flex flex-column justify-content-center align-items-center">
          <div class="card-body w-100">
            <h5 class="mb-4 text-center">IRMAA as percentage of Overall Cost</h5>
            <div class="circles-chart d-flex justify-content-center" style="padding-top:20px; min-height: 180px;">
              <div class="js-circle" id="circle-medicare"></div>
            </div>
            <div class="mt-4">
              <div class="row text-center">
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">Total Medicare Expense</small>
                  <strong class="text-primary fs-2">${{ (totalMedicareCost).toLocaleString() }}</strong>
                </div>
                <div class="col-6 mb-2">
                  <small class="text-muted d-block">IRMAA Surcharges</small>
                  <strong class="text-primary fs-2">${{ totalIrmaaSurcharge.toLocaleString() }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Medicare Costs Table Card -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <h5 class="mb-4">Medicare Costs</h5>
        <div class="row mb-3">
          <div class="col-md-4">
            <div class="border p-3 text-center">
              <strong>Mark age to opt in to Medicare</strong><br />
              <span>{{ client?.medicare_age || '65' }}</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="border p-3 text-center">
              <strong>Part B Inflation Rate:</strong><br />
              <span>{{ partBInflationRate }}%</span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="border p-3 text-center">
              <strong>Part D Inflation Rate:</strong><br />
              <span>{{ partDInflationRate }}%</span>
            </div>
          </div>
        </div>
        <div class="table-responsive">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Year</th>
                <th>Primary Age</th>
                <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
                <th>Part B</th>
                <th>Part D</th>
                <th>IRMAA Surcharge</th>
                <th>Total Medicare</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in filteredResults" :key="idx" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
                <td>{{ row.year }}</td>
                <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
                <td v-else></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
                <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td>${{ parseFloat(row.part_b || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.part_d || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.irmaa_surcharge || 0).toFixed(2) }}</td>
                <td style="position: relative;">
                  ${{ parseFloat(row.total_medicare || 0).toFixed(2) }}
                  <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                    ℹ️
                  </span>
                  <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                    IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight: bold;">
                <td colspan="2"><strong>Total</strong></td>
                <td>${{ filteredResults.reduce((total, row) => total + parseFloat(row.part_b || 0), 0).toFixed(2) }}</td>
                <td>${{ filteredResults.reduce((total, row) => total + parseFloat(row.part_d || 0), 0).toFixed(2) }}</td>
                <td>${{ filteredResults.reduce((total, row) => total + parseFloat(row.irmaa_surcharge || 0), 0).toFixed(2) }}</td>
                <td>${{ filteredResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0).toFixed(2) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Disclosures Card -->
    <DisclosuresCard />
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import Graph from '../components/Graph.vue';
import DisclosuresCard from '../components/DisclosuresCard.vue';

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
  components: {
    Graph,
    DisclosuresCard
  },
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
    },
    partBInflationRate: {
      type: Number,
      required: true
    },
    partDInflationRate: {
      type: Number,
      required: true
    },
    totalIrmaaSurcharge: {
      type: Number,
      required: true
    },
    totalMedicareCost: {
      type: Number,
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
        medicare: false
      },
      openIrmaaTooltipIdx: null
    };
  },
  computed: {
    filteredResults() {
      if (!this.scenarioResults || !Array.isArray(this.scenarioResults)) {
        return [];
      }
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
    },
    chartData() {
      if (!this.filteredResults || !this.filteredResults.length) {
        return { labels: [], datasets: [] };
      }

      const labels = this.filteredResults.map(row => row.year.toString());
      const datasets = [
        {
          type: 'bar',
          label: 'Part B',
          data: this.filteredResults.map(row => parseFloat(row.part_b || 0)),
          backgroundColor: '#377dff',
          stack: 'Stack 0',
          yAxisID: 'y'
        },
        {
          type: 'bar',
          label: 'Part D',
          data: this.filteredResults.map(row => parseFloat(row.part_d || 0)),
          backgroundColor: '#00c9db',
          stack: 'Stack 0',
          yAxisID: 'y'
        },
        {
          type: 'bar',
          label: 'IRMAA Surcharge',
          data: this.filteredResults.map(row => parseFloat(row.irmaa_surcharge || 0)),
          backgroundColor: '#ffc107',
          stack: 'Stack 0',
          yAxisID: 'y'
        }
      ];

      return { labels, datasets };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: true,
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
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            position: 'bottom'
          }
        }
      };
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
    initializeCircles() {
      this.$nextTick(() => {
        const maxRetries = 20;
        let retryCount = 0;
        const tryInit = () => {
          const CirclesGlobal = window.Circles;
          if (CirclesGlobal && typeof CirclesGlobal.create === 'function') {
            const circleElement = document.getElementById('circle-medicare');
            if (circleElement) {
              // Clear previous SVG if any
              circleElement.innerHTML = '';
              const irmaaPercentage = Math.round((this.totalIrmaaSurcharge / this.totalMedicareCost) * 100);
              let circleColor = '#377dff';
              if (irmaaPercentage > 50) {
                circleColor = '#ff0000';
              } else if (irmaaPercentage > 25) {
                circleColor = '#ffa500';
              } else if (irmaaPercentage > 15) {
                circleColor = '#ffff00';
              } else {
                circleColor = '#00ff00';
              }
              CirclesGlobal.create({
                id: 'circle-medicare',
                value: irmaaPercentage,
                maxValue: 100,
                width: 20,
                radius: 70,
                text: function(value) { return value + '%'; },
                colors: ['#f0f0f0', circleColor],
                duration: 400,
                wrpClass: 'circles-wrp',
                textClass: 'circles-text',
                styleWrapper: true,
                styleText: true
              });
            }
          } else if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(tryInit, 100);
          }
        };
        tryInit();
      });
    },
    isIrmaaBracketHit(row, idx) {
      // Returns true if this row's MAGI crosses into a new IRMAA bracket
      const currentBracket = row.irmaa_bracket_number || 0;
      
      if (currentBracket > 0) {
        // We're in an IRMAA bracket
        if (idx === 0) {
          // First row - show if in any bracket
          return true;
        }
        
        // Check if bracket changed from previous row
        const prevRow = this.filteredResults[idx - 1];
        const prevBracket = prevRow?.irmaa_bracket_number || 0;
        
        // Show indicator if bracket number changed
        return currentBracket !== prevBracket;
      }
      
      return false;
    },
    getIrmaaBracketLabel(row) {
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
        return `${bracketLabels[bracketNum] || `IRMAA Bracket ${bracketNum}`}: MAGI (${this.formatCurrency(magi)}) exceeds ${this.formatCurrency(bracketThreshold)} in ${year}`;
      } else {
        const firstThreshold = Number(row.irmaa_threshold);
        const difference = firstThreshold - magi;
        return `No IRMAA: ${this.formatCurrency(difference)} below first threshold of ${this.formatCurrency(firstThreshold)} in ${year}`;
      }
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
    this.initializeCircles();
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  watch: {
    scenarioResults: {
      handler() {
        this.$nextTick(() => {
          this.initializeCircles();
        });
      },
      deep: true
    }
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
.js-circle {
  min-width: 160px;
  min-height: 160px;
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.medicare-chart-container {
  width: 100%;
  height: 300px;
  min-height: 300px;
  max-height: 300px;
  position: relative;
}
</style> 