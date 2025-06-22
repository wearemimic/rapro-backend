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
        <!-- Bar Chart -->
        <canvas id="financial_overview_chart" style="width: 100%; height: 300px !important;"></canvas>
        <!-- End Bar Chart -->
      </div>
      <!-- End Body -->
    </div>
    <!-- End Card -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-header card-header-content-between">
        <div v-if="scenarioResults.length" class="table-responsive mt-4">
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
              <tr v-for="row in scenarioResults" :key="row.year">
                <td>{{ row.year }}</td>
                <td v-if="row.primary_age <= 90">{{ row.primary_age }}</td>
                <td v-else></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= 90">{{ row.spouse_age }}</td>
                <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td>{{ formatCurrency(row.gross_income) }}</td>
                <td>{{ formatCurrency(row.agi) }}</td>
                <td>{{ formatCurrency(row.magi) }}</td>
                <td>{{ row.tax_bracket }}</td>
                <td>{{ formatCurrency(row.federal_tax) }}</td>
                <td>{{ formatCurrency(row.total_medicare) }}</td>
                <td>{{ formatCurrency(parseFloat(row.gross_income) - (parseFloat(row.federal_tax) + parseFloat(row.total_medicare))) }}</td>
              </tr>
            </tbody>
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
    }
  },
  data() {
    return {
      isDropdownOpen: {
        financial: false
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
    }
  }
};
</script> 