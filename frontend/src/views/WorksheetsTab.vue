<template>
  <div>
    <div class="row">
      <div class="col-sm-6 col-xl-6 mb-3 mb-xl-6">
        <div class="card mb-3 mb-lg-5">
          <div class="card-body">
            <h5 class="mb-4">Social Security Breakeven</h5>
            <div style="height: 300px">
              <Graph 
                :data="breakevenChartData" 
                :options="breakevenChartOptions"
                :height="300"
              />
            </div>
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
            <h5 class="mb-4">Medicare-Adjusted Social Security Breakeven</h5>
            <div style="height: 300px">
              <Graph 
                :data="medicareAdjustedBreakevenChartData" 
                :options="medicareAdjustedBreakevenChartOptions"
                :height="300"
              />
            </div>
          </div>
        </div>
        <div class="card mt-3 mb-lg-5">
          <div class="card-body">
            <h5 class="mb-4">Medicare-Adjusted Social Security Comparison</h5>
            <div class="table-responsive">
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Age</th>
                    <th>Monthly Amount</th>
                    <th>Medicare Costs</th>
                    <th>Net Monthly Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(benefit, age) in benefitByAge" :key="age">
                    <td>{{ age }}</td>
                    <td>${{ (benefit / 12).toFixed(2) }}</td>
                    <td>${{ getAverageMedicareCostByAge(age).toFixed(2) }}</td>
                    <td>${{ ((benefit / 12) - getAverageMedicareCostByAge(age)).toFixed(2) }}</td>
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
  components: {
    Graph
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
    benefitByAge: {
      type: Object,
      required: true
    },
    socialSecurityCola: {
      type: Number,
      required: true
    },
    medicareCosts: {
      type: Array,
      default: () => []
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
    breakevenChartData() {
      const datasets = Object.entries(this.benefitByAge).map(([age, benefit], i) => {
        const label = `Age ${age}`;
        const data = [];
        let cumulativeIncome = 0;
        const startYear = 62 + (parseInt(age) - 62);
        
        for (let year = 62; year <= 90; year++) {
          if (year >= startYear) {
            cumulativeIncome += benefit;
            data.push(cumulativeIncome);
          } else {
            data.push(null);
          }
        }
        
        return {
          type: 'line',
          label,
          data,
          borderColor: `hsl(${(i * 40) % 360}, 70%, 50%)`,
          backgroundColor: `hsla(${(i * 40) % 360}, 70%, 50%, 0.1)`,
          borderWidth: 2,
          tension: 0.3
        };
      });
      
      return {
        labels: Array.from({ length: 29 }, (_, i) => (62 + i).toString()),
        datasets
      };
    },
    breakevenChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Age'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Cumulative Social Security ($)'
            },
            ticks: {
              beginAtZero: true
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: true,
            text: 'Social Security Breakeven Analysis'
          },
          legend: {
            position: 'bottom'
          }
        }
      };
    },
    medicareAdjustedBreakevenChartData() {
      const datasets = Object.entries(this.benefitByAge).map(([age, benefit], i) => {
        const label = `Age ${age}`;
        const data = [];
        let cumulativeIncome = 0;
        const startYear = 62 + (parseInt(age) - 62);
        
        for (let year = 62; year <= 90; year++) {
          if (year >= startYear) {
            // Find Medicare costs for this year
            const medicareCost = this.getMedicareCostForAge(year);
            const adjustedBenefit = benefit - (medicareCost * 12); // Annual adjusted benefit
            
            cumulativeIncome += adjustedBenefit;
            data.push(cumulativeIncome);
          } else {
            data.push(null);
          }
        }
        
        return {
          type: 'line',
          label,
          data,
          borderColor: `hsl(${(i * 40) % 360}, 70%, 50%)`,
          backgroundColor: `hsla(${(i * 40) % 360}, 70%, 50%, 0.1)`,
          borderWidth: 2,
          tension: 0.3
        };
      });
      
      return {
        labels: Array.from({ length: 29 }, (_, i) => (62 + i).toString()),
        datasets
      };
    },
    medicareAdjustedBreakevenChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Age'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Cumulative Net Social Security ($)'
            },
            ticks: {
              beginAtZero: true
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: true,
            text: 'Medicare-Adjusted Social Security Breakeven Analysis'
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
    getAverageMedicareCostByAge(age) {
      // Find all scenario results where primary_age matches the given age
      const matchingYears = this.medicareCosts.filter(year => year.primary_age === parseInt(age));
      
      // If no matching years, return 0
      if (matchingYears.length === 0) return 0;
      
      // Calculate the average monthly Medicare cost
      const totalMedicareCost = matchingYears.reduce((sum, year) => sum + parseFloat(year.total_medicare || 0), 0);
      return totalMedicareCost / matchingYears.length / 12; // Monthly cost
    },
    getMedicareCostForAge(age) {
      // Find the Medicare cost for the given age
      const matchingYear = this.medicareCosts.find(year => year.primary_age === parseInt(age));
      return matchingYear ? parseFloat(matchingYear.total_medicare || 0) : 0;
    }
  }
};
</script> 