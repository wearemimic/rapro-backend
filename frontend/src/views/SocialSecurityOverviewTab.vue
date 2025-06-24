<template>
  <div>
    <!-- Card for Graph -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-body">
        <canvas id="socialSecurityChart" style="width: 100%; height: 300px !important;"></canvas>
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
            <tr v-for="row in filteredResults" :key="row.year">
              <td>{{ row.year }}</td>
              <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
              <td v-else></td>
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
      const maxAge = Math.max(mortalityAge, spouseMortalityAge);
      return this.scenarioResults.filter(row => {
        return (row.primary_age <= maxAge || (row.spouse_age && row.spouse_age <= maxAge));
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