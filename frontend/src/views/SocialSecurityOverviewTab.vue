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
            <tr v-for="row in filteredResults" :key="row.year">
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
      }
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