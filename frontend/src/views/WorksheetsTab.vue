<template>
  <div>
    <div class="row">
      <div class="col-sm-6 col-xl-6 mb-3 mb-xl-6">
        <div class="card mb-3 mb-lg-5">
          <div class="card-body">
            <Graph :data="breakevenLineData" type="line" :height="300" />
          </div>
        </div>
        <div class="card mt-3 mb-lg-5">
          <div class="card-body">
            <h5 class="mb-4">Social Security Claim Comparison</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Age</th>
                    <th>Monthly Amount</th>
                    <th>Total Lifetime Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(benefit, age) in benefitByAge" :key="age">
                    <td>{{ age }}</td>
                    <td>${{ (benefit / 12).toFixed(2) }}</td>
                    <td>
                      ${{ 
                        (
                          Array.from({ length: client?.mortality_age - age + 1 }, (_, i) =>
                            (benefit * Math.pow(1 + socialSecurityCola / 100, i))
                          ).reduce((acc, val) => acc + val, 0)
                        ).toFixed(2) 
                      }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-xl-6 mb-3 mb-xl-6">
        <div class="card mb-3 mb-lg-5">
          <div class="card-body">
          </div>
        </div>
        <div class="card mt-3 mb-lg-5">
          <div class="card-body">
            <h5 class="mb-4">Social Security Claim Comparison</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Age</th>
                    <th>Monthly Amount</th>
                    <th>Total Lifetime Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(benefit, age) in benefitByAge" :key="age">
                    <td>{{ age }}</td>
                    <td>${{ (benefit / 12).toFixed(2) }}</td>
                    <td>
                      ${{ 
                        (
                          Array.from({ length: client?.mortality_age - age + 1 }, (_, i) =>
                            (benefit * Math.pow(1 + socialSecurityCola / 100, i))
                          ).reduce((acc, val) => acc + val, 0)
                        ).toFixed(2) 
                      }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="dropdown">
      <button type="button" class="btn btn-white btn-sm dropdown-toggle" @click="toggleDropdown('worksheets')" :aria-expanded="isDropdownOpen.worksheets">
        <i class="bi-download me-2"></i> Export
      </button>
      <div class="dropdown-menu dropdown-menu-sm-end" :class="{ show: isDropdownOpen.worksheets }" aria-labelledby="usersExportDropdown">
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
    },
    benefitByAge: {
      type: Object,
      required: true
    },
    socialSecurityCola: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      isDropdownOpen: {
        worksheets: false
      }
    };
  },
  computed: {
    breakevenLineData() {
      return {
        labels: Object.keys(this.benefitByAge),
        datasets: [
          {
            label: 'Monthly Amount',
            borderColor: '#007bff',
            backgroundColor: 'rgba(0,123,255,0.1)',
            data: Object.values(this.benefitByAge).map(val => val / 12),
            fill: false
          },
          {
            label: 'Total Lifetime Value',
            borderColor: '#28a745',
            backgroundColor: 'rgba(40,167,69,0.1)',
            data: Object.values(this.benefitByAge),
            fill: false
          }
        ]
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