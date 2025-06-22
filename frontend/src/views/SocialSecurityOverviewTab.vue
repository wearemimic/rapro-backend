<template>
  <div>
    <!-- Card for Graph -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <Graph :data="ssChartData" :options="ssChartOptions" type="bar" :height="300" />
      </div>
    </div>
    <!-- End Card for Graph -->
    <!-- Card for Table -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <table class="table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Primary Age</th>
              <th>Social Security Benefit</th>
              <th>Total Medicare</th>
              <th>SSI Taxed</th>
              <th>Remaining SSI</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in scenarioResults" :key="row.year">
              <td>{{ row.year }}</td>
              <td>{{ row.primary_age }}</td>
              <td>${{ parseFloat(row.ss_income || 0).toFixed(2) }}</td>
              <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
              <td>${{ parseFloat(row.ssi_taxed || 0).toFixed(2) }}</td>
              <td class="bg-success text-white">${{ (parseFloat(row.ss_income || 0) - parseFloat(row.total_medicare || 0)).toFixed(2) }}</td>
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
import Graph from '../components/Graph.vue';

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

export default {
  components: { Graph },
  props: {
    scenarioResults: {
      type: Array,
      required: true
    },
    client: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isDropdownOpen: {
        socialSecurity: false
      }
    };
  },
  computed: {
    ssChartData() {
      const years = this.scenarioResults.map(row => row.year);
      const ssIncome = this.scenarioResults.map(row => parseFloat(row.ss_income || 0));
      const totalMedicare = this.scenarioResults.map(row => parseFloat(row.total_medicare || 0));
      const remainingSSI = this.scenarioResults.map(row => {
        const ss = parseFloat(row.ss_income || 0);
        const med = parseFloat(row.total_medicare || 0);
        return ss - med;
      });
      return {
        labels: years,
        datasets: [
          // Bar for Medicare
          {
            type: 'bar',
            label: 'Total Medicare',
            backgroundColor: '#28a745',
            data: totalMedicare,
            order: 2
          },
          // Lines
          {
            type: 'line',
            label: 'Social Security Benefit',
            borderColor: '#007bff',
            backgroundColor: 'rgba(0,123,255,0.1)',
            data: ssIncome,
            fill: false,
            yAxisID: 'y',
            order: 1
          },
          {
            type: 'line',
            label: 'Remaining SSI',
            borderColor: '#6f42c1',
            backgroundColor: 'rgba(111,66,193,0.1)',
            data: remainingSSI,
            fill: false,
            yAxisID: 'y',
            order: 1
          }
        ]
      };
    },
    ssChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true }
        },
        scales: {
          x: { stacked: false },
          y: { stacked: false, beginAtZero: true }
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
    }
  }
};
</script> 