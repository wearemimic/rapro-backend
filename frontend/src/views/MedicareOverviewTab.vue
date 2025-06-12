<template>
  <div>
    <!-- Medicare Chart Card -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <div class="dropdown">
          <button type="button" class="btn btn-white btn-sm dropdown-toggle" @click="toggleDropdown('medicare')" :aria-expanded="isDropdownOpen.medicare">
            <i class="bi-download me-2"></i> Export
          </button>
          <div class="dropdown-menu dropdown-menu-sm-end" :class="{ show: isDropdownOpen.medicare }" aria-labelledby="usersExportDropdown">
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
        <div class="row" style="margin-top:20px;">
          <div class="col-sm-8 h-100">
            <canvas id="medicareChart" style="width: 100%; height: 300px;"></canvas>
          </div>
          <div class="col-sm-4 h-100">
            <h5 class="mb-4" style="text-align:center;">IRMAA as percentage of Overall Cost </h5>
            <div class="circles-chart" style="padding-top:20px;">
              <div class="js-circle" id="circle-medicare" data-hs-circles-options='{
                "value": {{ totalIrmaaSurcharge }},
                "maxValue": {{ totalMedicareCost }},
                "duration": 2000,
                "isViewportInit": true,
                "radius": 80,
                "width": 20,
                "fgStrokeLinecap": "round",
                "textColor": "#377dff"
              }'>
              </div>
            </div>
            <div class="card-body">
              <h4 style="text-align:center;margin-top:20px;">Base Premium: ${{ (totalMedicareCost - totalIrmaaSurcharge).toFixed(2) }}</h4>
              <h4 style="text-align:center;">IRMAA Surcharges: ${{ totalIrmaaSurcharge }}</h4>
            </div>
          </div>
        </div>
      </div>
    </div>
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
              <tr v-for="(row, index) in scenarioResults" :key="index">
                <td>{{ row.year }}</td>
                <td>{{ row.primary_age }}</td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single'">{{ row.spouse_age }}</td>
                <td>${{ parseFloat(row.part_b || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.part_d || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.irmaa_surcharge || 0).toFixed(2) }}</td>
                <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight: bold;">
                <td colspan="2"><strong>Total</strong></td>
                <td>${{ scenarioResults.reduce((total, row) => total + parseFloat(row.part_b || 0), 0).toFixed(2) }}</td>
                <td>${{ scenarioResults.reduce((total, row) => total + parseFloat(row.part_d || 0), 0).toFixed(2) }}</td>
                <td>${{ scenarioResults.reduce((total, row) => total + parseFloat(row.irmaa_surcharge || 0), 0).toFixed(2) }}</td>
                <td>${{ scenarioResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0).toFixed(2) }}</td>
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

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

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
    }
  },
  data() {
    return {
      isDropdownOpen: {
        medicare: false
      }
    };
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
        console.log('Initializing Circles...');
        console.log('Total IRMAA Surcharge:', this.totalIrmaaSurcharge);
        console.log('Total Medicare Cost:', this.totalMedicareCost);

        const maxRetries = 20;
        let retryCount = 0;
        const tryInit = () => {
          const CirclesGlobal = window.Circles;
          if (CirclesGlobal && typeof CirclesGlobal.create === 'function') {
            console.log('Circles.js is ready.');
            const circleElement = document.getElementById('circle-medicare');
            if (circleElement) {
              console.log('Circle element found:', circleElement);
              const irmaaPercentage = Math.round((this.totalIrmaaSurcharge / this.totalMedicareCost) * 100);
              let circleColor = '#377dff'; // Default color

              // Determine color based on IRMAA percentage
              if (irmaaPercentage > 50) {
                circleColor = '#ff0000'; // Red for percentages above 50
              } else if (irmaaPercentage > 25) {
                circleColor = '#ffa500'; // Orange for percentages between 25 and 50
              } else if (irmaaPercentage > 15) {
                circleColor = '#ffff00'; // Yellow for percentages between 15 and 25
              } else {
                circleColor = '#00ff00'; // Green for percentages below 15
              }

              console.log('IRMAA Percentage:', irmaaPercentage, 'Circle Color:', circleColor);

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
            } else {
              console.error('Circle element not found.');
            }
          } else if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(tryInit, 100);
          } else {
            console.error('Failed to initialize Circles.js after multiple attempts.');
          }
        };

        tryInit();
      });
    }
  }
};
</script> 