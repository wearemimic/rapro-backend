<template>
<main id="content" role="main" class="main">
    <!-- Content -->
    <div class="content container-fluid">
      <!-- Page Header -->
      <div class="page-header">
        <div class="d-flex mb-3">
          <div class="flex-grow-1 ms-4">
            <div class="row">
              <div class="col-lg mb-3 mb-lg-0">
                
                <h1 class="page-header-title">{{ scenario ? scenario.name : 'Scenario Detail' }}</h1>

                <div class="row align-items-center">
                  <div class="col-auto">
                    <span>Client:</span>
                    <router-link v-if="client" :to="{ name: 'ClientDetail', params: { id: client.id } }">
                      {{ formatClientName(client) }}
                    </router-link>
                    <span v-else>Loading...</span>
                  </div>
                  <!-- End Col -->

                  <div class="col-auto">
                    <div class="row align-items-center g-0">
                      
                      <!-- End Flatpickr -->
                    </div>
                  </div>

                  <!-- End Col -->
                </div>
                <!-- End Row -->
              </div>
              <!-- End Col -->

              <div class="col-lg-auto d-flex align-items-center">
                <div class="d-flex align-items-center me-3">
                  <label for="scenarioSelect" class="form-label mb-0 me-2" style="white-space: nowrap;">Switch Scenario</label>
                  <select id="scenarioSelect" class="form-select" v-model="selectedScenarioId" @change="onScenarioChange">
                    <option v-for="s in scenarios" :value="s.id" :key="s.id">{{ s.name }}</option>
                  </select>
                </div>
                <!-- New Scenario Dropdown -->
                <div class="d-flex align-items-center">
                  <div class="dropdown">
                    <button class="btn btn-primary dropdown-toggle" type="button" id="newScenarioDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                      New Scenario
                    </button>
                    <ul class="dropdown-menu" aria-labelledby="newScenarioDropdown">
                      <li><a class="dropdown-item" href="#" @click="createScenario('scratch')">From Scratch</a></li>
                      <li><a class="dropdown-item" href="#" @click="createScenario('duplicate')">Duplicate This Scenario</a></li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <!-- End Row -->
          </div>
        </div>
        <!-- End Media -->

        <!-- Nav -->
        <!-- Nav -->
        <div class="js-nav-scroller hs-nav-scroller-horizontal">
          <span class="hs-nav-scroller-arrow-prev" style="display: none;">
            <a class="hs-nav-scroller-arrow-link" href="javascript:;">
              <i class="bi-chevron-left"></i>
            </a>
          </span>

          <span class="hs-nav-scroller-arrow-next" style="display: none;">
            <a class="hs-nav-scroller-arrow-link" href="javascript:;">
              <i class="bi-chevron-right"></i>
            </a>
          </span>

          <ScenarioMetrics :total-federal-taxes="totalFederalTaxes" :total-medicare-costs="totalMedicareCosts" />

          <ul class="nav nav-tabs page-header-tabs" id="projectsTab" role="tablist">
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'financial' }"
                href="#"
                @click.prevent="activeTab = 'financial'; $nextTick(() => initializeChartJS())"
              >Financial Overview</a>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'socialSecurity' }"
                href="#"
                @click.prevent="activeTab = 'socialSecurity'"
              >Social Security Overview</a>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'medicare' }"
                href="#"
                @click.prevent="activeTab = 'medicare'"
              >Medicare Overview</a>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'income' }"
                href="#"
                @click.prevent="activeTab = 'income'"
              >Income</a>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'rothConversion' }"
                href="#"
                @click.prevent="activeTab = 'rothConversion'"
              >Roth Conversion</a>
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'worksheets' }"
                href="#"
                @click.prevent="activeTab = 'worksheets'"
              >Social Security Worksheets</a>
            </li>
          </ul>
          <div class="tab-content mt-4">
            <div v-if="activeTab === 'financial'" class="tab-pane active" style="margin-top:50px;">
              <FinancialOverviewTab :scenario-results="scenarioResults" :client="client" />
            </div>
            <div v-show="activeTab === 'socialSecurity'" class="tab-pane active" style="margin-top:50px;">
              <SocialSecurityOverviewTab :scenario-results="scenarioResults" :client="client" />
            </div>
            <div v-show="activeTab === 'medicare'" class="tab-pane active" style="margin-top:50px;">
              <MedicareOverviewTab :scenario-results="scenarioResults" :client="client" :partBInflationRate="partBInflationRate" :partDInflationRate="partDInflationRate" :totalIrmaaSurcharge="totalIrmaaSurcharge" :totalMedicareCost="totalMedicareCost" />
            </div>
            <div v-show="activeTab === 'income'" class="tab-pane active" style="margin-top:50px;">
              <IncomeTab :scenario="scenario" :assetDetails="assetDetails" />
            </div>
            <div v-show="activeTab === 'rothConversion'" class="tab-pane active" style="margin-top:50px;">
              <RothConversionTab :scenario="scenario" :assetDetails="assetDetails" :scenarioResults="scenarioResults" />
            </div>
            <div v-show="activeTab === 'worksheets'" class="tab-pane active" style="margin-top:50px;">
              <WorksheetsTab :scenarioResults="scenarioResults" :client="client" :benefitByAge="benefitByAge" :socialSecurityCola="socialSecurityCola" :medicareCosts="scenarioResults" />
            </div>
          </div>
        </div>
        <!-- End Nav -->
      </div>
      <!-- End Page Header -->
    </div>
    <!-- End Content -->

    <!-- Footer -->

    <div class="footer">
      <div class="row justify-content-between align-items-center">
        <div class="col">
          <p class="fs-6 mb-0">&copy; Front. <span class="d-none d-sm-inline-block">2022 Htmlstream.</span></p>
        </div>
        <!-- End Col -->

        <div class="col-auto">
          <div class="d-flex justify-content-end">
            <!-- List Separator -->
            <ul class="list-inline list-separator">
              <li class="list-inline-item">
                <a class="list-separator-link" href="#">FAQ</a>
              </li>

              <li class="list-inline-item">
                <a class="list-separator-link" href="#">License</a>
              </li>

              <li class="list-inline-item">
                <!-- Keyboard Shortcuts Toggle -->
                <button class="btn btn-ghost-secondary btn btn-icon btn-ghost-secondary rounded-circle" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasKeyboardShortcuts" aria-controls="offcanvasKeyboardShortcuts">
                  <i class="bi-command"></i>
                </button>
                <!-- End Keyboard Shortcuts Toggle -->
              </li>
            </ul>
            <!-- End List Separator -->
          </div>
        </div>
        <!-- End Col -->
      </div>
      <!-- End Row -->
    </div>

    <!-- End Footer -->
  </main>
</template>

<script>
import axios from 'axios'
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { mapActions } from 'vuex';

import {
  Chart,
  LineController,
  LineElement,
  BarController,
  BarElement,
  PointElement,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale
} from 'chart.js';

import FinancialOverviewTab from './FinancialOverviewTab.vue';
import SocialSecurityOverviewTab from './SocialSecurityOverviewTab.vue';
import MedicareOverviewTab from './MedicareOverviewTab.vue';
import IncomeTab from './IncomeTab.vue';
import RothConversionTab from './RothConversionTab.vue';
import WorksheetsTab from './WorksheetsTab.vue';
import ScenarioMetrics from './ScenarioMetrics.vue';

Chart.register(
  LineController,
  LineElement,
  BarController,
  BarElement,
  PointElement,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  CategoryScale
);

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
  components: {
    FinancialOverviewTab,
    SocialSecurityOverviewTab,
    MedicareOverviewTab,
    IncomeTab,
    RothConversionTab,
    WorksheetsTab,
    ScenarioMetrics
  },
  data() {
    return {
      scenario: null,
      scenarios: [],
      selectedScenarioId: null,
      client: null,
      scenarioResults: [],
      activeTab: 'financial',
      partBInflationRate: 7.42,
      partDInflationRate: 6.73,
      breakevenChartInstance: null,
      socialSecurityCola: 0,
      benefitByAge: {
        62: 37800,
        63: 40776,
        64: 43740,
        65: 47256,
        66: 50496,
        67: 54000,
        68: 58320,
        69: 62640,
        70: 66960,
      },
      isDropdownOpen: {
        financial: false,
        socialSecurity: false,
        medicare: false,
        worksheets: false
      },
      preRetirementIncome: 0,
      availableYears: [],
      conversionStartYear: null,
      yearsToConvert: 0,
      rothGrowthRate: 0,
      assetDetails: [],
    };
  },
  mounted() {
    // Ensure activeTab is set to 'financial' on mount
    this.activeTab = 'financial';
    // Fetch the client and scenarios, select scenario by id
    const clientId = this.$route.params.id;
    axios.get(`http://localhost:8000/api/clients/${clientId}/`, { headers })
      .then(response => {
        this.client = response.data;
        this.scenarios = response.data.scenarios || [];
        const scenarioId = this.$route.params.scenarioid;
        this.scenario = this.scenarios.find(s => s.id === parseInt(scenarioId));
        this.selectedScenarioId = this.scenario?.id || null;
        this.initPlugins();
        this.initializeCircles();
        this.fetchScenarioData();
        this.fetchAssetDetails();
        console.log('Client Tax Status:', this.client?.tax_status);
        console.log('Scenarios:', this.scenarios);
        console.log('Selected Scenario:', this.scenario);
      })
      .catch(error => {
        console.error('Error loading client and scenario:', error);
      });

    // Add event listener for clicks outside the dropdown
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    ...mapActions(['fetchScenarioData']),
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    },
    downloadTable(format) {
      const rows = this.scenarioResults;
      if (!rows.length) return;

      const headers = ['Year', 'Primary Age', 'Spouse Age', 'Gross Income', 'Taxable Income', 'Tax Bracket', 'Federal Tax', 'Total Medicare', 'Remaining Income'];
      const data = rows.map(row => [
        row.year,
        row.primary_age <= 90 ? row.primary_age : '',
        this.client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= 90 ? row.spouse_age : '',
        row.gross_income,
        row.taxable_income,
        '12%',
        row.federal_tax,
        row.total_medicare,
        (parseFloat(row.gross_income) - (parseFloat(row.federal_tax) + parseFloat(row.total_medicare))).toFixed(2)
      ]);

      const csvContent = [headers.join(','), ...data.map(r => r.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: format === 'excel' ? 'application/vnd.ms-excel' : 'text/csv' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `scenario-data.${format === 'excel' ? 'xls' : 'csv'}`;
      link.click();
    },
    initPlugins() {
      this.initializeFlatpickr();
      this.initializeChartJS();
      this.initializeCircles(); 
    },
    initializeFlatpickr() {
      if (window.HSCore?.components?.HSFlatpickr) {
        window.HSCore.components.HSFlatpickr.init('.js-flatpickr')
      }
    },
    initializeChartJS() {
      this.$nextTick(() => {
        const ctx = document.getElementById(
          this.activeTab === 'worksheets' ? 'breakevenChart' :
          this.activeTab === 'medicare' ? 'medicareChart' :
          this.activeTab === 'socialSecurity' ? 'socialSecurityChart' :
          'financial_overview_chart'
        );
        console.log('Canvas Context:', ctx); // Log the canvas context
        if (ctx && this.scenarioResults.length) {
          if (this.chartInstance) {
            this.chartInstance.destroy();
          }

          const datasets = this.activeTab === 'worksheets' ? [
            ...Object.entries(this.benefitByAge).map(([age, benefit], i) => {
              const label = `Age ${age}`;
              const data = [];
              let cumulativeIncome = 0;
              const startYear = 62 + (age - 62);
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
                tension: 0.3,
                yAxisID: 'y'
              };
            })
          ] : this.activeTab === 'socialSecurity' ? [
            {
              type: 'line',
              label: 'SSI Benefit',
              data: this.scenarioResults.map(row => parseFloat(row.ss_income || 0)),
              borderColor: "#377dff",
              backgroundColor: "rgba(55, 125, 255, 0.1)",
              borderWidth: 2,
              tension: 0.3,
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'Remaining SSI Benefit',
              data: this.scenarioResults.map(row => {
                const ssiBenefit = parseFloat(row.ss_income || 0);
                const medicareExpense = parseFloat(row.total_medicare || 0);
                const remainingSSI = ssiBenefit - medicareExpense;
                return remainingSSI;
              }),
              borderColor: "#00c9db",
              backgroundColor: "rgba(0, 201, 219, 0.1)",
              borderWidth: 2,
              tension: 0.3,
              yAxisID: 'y'
            },
            {
              type: 'bar',
              label: 'Medicare Expense',
              data: this.scenarioResults.map(row => parseFloat(row.total_medicare || 0)),
              backgroundColor: "#ffc107",
              stack: 'Stack 0',
              yAxisID: 'y'
            }
          ] : this.activeTab === 'medicare' ? [
            {
              type: 'bar',
              label: 'Part B',
              data: this.scenarioResults.map(row => parseFloat(row.part_b || 0)),
              backgroundColor: '#377dff',
              stack: 'Stack 0',
              yAxisID: 'y'
            },
            {
              type: 'bar',
              label: 'Part D',
              data: this.scenarioResults.map(row => parseFloat(row.part_d || 0)),
              backgroundColor: '#00c9db',
              stack: 'Stack 0',
              yAxisID: 'y'
            },
            {
              type: 'bar',
              label: 'IRMAA Surcharge',
              data: this.scenarioResults.map(row => parseFloat(row.irmaa_surcharge || 0)),
              backgroundColor: '#ffc107',
              stack: 'Stack 0',
              yAxisID: 'y'
            }
          ] : [
            {
              type: 'line',
              label: 'Total Income',
              data: this.scenarioResults.map(row => parseFloat(row.gross_income)),
              borderColor: "#377dff",
              backgroundColor: "rgba(55, 125, 255, 0.1)",
              borderWidth: 2,
              tension: 0.3,
              yAxisID: 'y'
            },
            {
              type: 'line',
              label: 'Remaining Income',
              data: this.scenarioResults.map(row => {
                const gross = parseFloat(row.gross_income);
                const tax = parseFloat(row.federal_tax);
                const medicare = parseFloat(row.total_medicare);
                const remaining = gross - (tax + medicare);
                return parseFloat(remaining.toFixed(2));
              }),
              borderColor: "#00c9db",
              backgroundColor: "rgba(0, 201, 219, 0.1)",
              borderWidth: 2,
              tension: 0.3,
              yAxisID: 'y'
            },
            {
              type: 'bar',
              label: 'Federal Tax',
              data: this.scenarioResults.map(row => parseFloat(row.federal_tax)),
              backgroundColor: "#ff6b6b",
              stack: 'Stack 0',
              yAxisID: 'y'
            },
            {
              type: 'bar',
              label: 'Total Medicare',
              data: this.scenarioResults.map(row => parseFloat(row.total_medicare)),
              backgroundColor: "#ffc107",
              stack: 'Stack 0',
              yAxisID: 'y'
            }
          ];

          this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
              labels: this.scenarioResults.map(row => row.year.toString()),
              datasets: datasets
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: {
                  stacked: this.activeTab === 'medicare',
                  title: {
                    display: true,
                    text: 'Year'
                  }
                },
                y: {
                  stacked: this.activeTab === 'medicare',
                  title: {
                    display: true,
                    text: 'Amount ($)'
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
                legend: {
                  position: 'bottom'
                }
              }
            }
          });
        } else {
          // If scenarioResults is empty, clear the chart
          if (this.chartInstance) {
            this.chartInstance.destroy();
          }
        }
      });
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
            document.querySelectorAll('.js-circle').forEach((el) => {
              console.log('Found circle element:', el);
              if (!el.dataset.initialized) {
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
                  id: el.id,
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
                el.dataset.initialized = true;
              }
            });
          } else if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(tryInit, 100);
          } else {
            console.error('Failed to initialize Circles.js after multiple attempts.');
          }
        };

        tryInit();
      });
    },
    fetchScenariosForClient() {
      // Use clientId from route params (not from scenario.client)
      const clientId = this.$route.params.id;
      if (clientId) {
        axios.get(`http://localhost:8000/api/clients/${clientId}/`, { headers })
          .then(response => {
            this.client = response.data;
            this.scenarios = response.data.scenarios || [];
            if (this.scenario) {
              this.selectedScenarioId = this.scenario.id;
            }
          })
          .catch(error => {
            console.error('Error loading scenarios for client:', error);
          });
      }
    },
    onScenarioChange() {
      // Navigate using both clientId and scenarioid to match new route structure
      this.$router.push({ name: 'ScenarioDetail', params: { clientId: this.$route.params.id, scenarioid: this.selectedScenarioId } });
    },
    fetchScenarioData() {
      const scenarioId = this.$route.params.scenarioid;
      axios.get(`http://localhost:8000/api/scenarios/${scenarioId}/calculate/`, { headers })
        .then(response => {
          if (response.data && response.data.length) {
            this.scenarioResults = response.data;
            console.log('API Response:', response.data); // Log the API response
            console.log('Scenario Results:', this.scenarioResults); // Log scenario results
            // Re-initialize chart with new data
            this.initializeChartJS();
          } else {
            console.warn('No data received for scenarioResults');
          }
        })
        .catch(error => {
          console.error("Error loading scenario data:", error);
        });
    },
    toggleDropdown(tab) {
      // Close all dropdowns first
      for (const key in this.isDropdownOpen) {
        if (key !== tab) {
          this.isDropdownOpen[key] = false;
        }
      }
      // Toggle the selected dropdown
      this.isDropdownOpen[tab] = !this.isDropdownOpen[tab];
    },
    handleClickOutside(event) {
      console.log('handleClickOutside triggered');
      const dropdowns = {
        financial: this.$refs.financialDropdown,
        socialSecurity: this.$refs.socialSecurityDropdown,
        medicare: this.$refs.medicareDropdown,
        worksheets: this.$refs.worksheetsDropdown
      };

      for (const [tab, dropdown] of Object.entries(dropdowns)) {
        if (dropdown) {
          console.log(`Checking dropdown for tab: ${tab}`);
          console.log(`Dropdown contains event target: ${dropdown.contains(event.target)}`);
          console.log(`Dropdown open state before: ${this.isDropdownOpen[tab]}`);
          if (!dropdown.contains(event.target) && this.isDropdownOpen[tab]) {
            console.log(`Closing dropdown for tab: ${tab}`);
            this.isDropdownOpen[tab] = false;
          }
          console.log(`Dropdown open state after: ${this.isDropdownOpen[tab]}`);
        }
      }
    },
    exportGraphAndDataToPDF() {
      console.log('Exporting graph and data to PDF...');
      const doc = new jsPDF();
      let canvasId, tableData;

      // Determine which graph and table to export based on the active tab
      if (this.activeTab === 'financial') {
        canvasId = 'financial_overview_chart';
        tableData = this.scenarioResults;
      } else if (this.activeTab === 'socialSecurity') {
        canvasId = 'socialSecurityChart';
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          social_security_benefit: row.ss_income,
          total_medicare: row.total_medicare,
          ssi_taxed: row.ssi_taxed,
          remaining_ssi: row.remaining_ssi
        }));
      } else if (this.activeTab === 'medicare') {
        canvasId = 'medicareChart';
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          gross_income: row.gross_income,
          medicare_income: row.medicare_income,
          part_b: row.part_b,
          part_d: row.part_d,
          total_medicare: row.total_medicare
        }));
      } else if (this.activeTab === 'worksheets') {
        canvasId = 'breakevenChart';
        tableData = this.benefitByAge;
      }

      // Capture the graph as an image
      const canvas = document.getElementById(canvasId);
      if (canvas) {
        const imgData = canvas.toDataURL('image/png');
        doc.addImage(imgData, 'PNG', 10, 10, 180, 80); // Adjust the position and size as needed
      }

      // Add the table data
      const headers = Object.keys(tableData[0]).map(key => key.replace(/_/g, ' ').toUpperCase());
      const data = tableData.map(row => Object.values(row));

      doc.autoTable({
        head: [headers],
        body: data,
        startY: 100 // Adjust the start position as needed
      });

      doc.save(`${this.activeTab}-graph-and-data.pdf`);
    },
    exportGraphAndDataToExcel() {
      let tableData;

      if (this.activeTab === 'financial') {
        tableData = this.scenarioResults;
      } else if (this.activeTab === 'socialSecurity') {
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          social_security_benefit: row.ss_income,
          total_medicare: row.total_medicare,
          ssi_taxed: row.ssi_taxed,
          remaining_ssi: row.remaining_ssi
        }));
      } else if (this.activeTab === 'medicare') {
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          gross_income: row.gross_income,
          medicare_income: row.medicare_income,
          part_b: row.part_b,
          part_d: row.part_d,
          total_medicare: row.total_medicare
        }));
      } else if (this.activeTab === 'worksheets') {
        tableData = this.benefitByAge;
      }

      const ws = XLSX.utils.json_to_sheet(tableData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Scenario Data');
      XLSX.writeFile(wb, `${this.activeTab}-scenario-data.xlsx`);
    },
    exportTableToCSV() {
      console.log('Exporting table to CSV...');
      let tableData;

      if (this.activeTab === 'financial') {
        tableData = this.scenarioResults;
      } else if (this.activeTab === 'socialSecurity') {
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          social_security_benefit: row.ss_income,
          total_medicare: row.total_medicare,
          ssi_taxed: row.ssi_taxed,
          remaining_ssi: row.remaining_ssi
        }));
      } else if (this.activeTab === 'medicare') {
        tableData = this.scenarioResults.map(row => ({
          year: row.year,
          primary_age: row.primary_age,
          gross_income: row.gross_income,
          medicare_income: row.medicare_income,
          part_b: row.part_b,
          part_d: row.part_d,
          total_medicare: row.total_medicare
        }));
      } else if (this.activeTab === 'worksheets') {
        tableData = this.benefitByAge;
      }

      const headers = Object.keys(tableData[0]).map(key => key.replace(/_/g, ' ').toUpperCase());
      const data = tableData.map(row => Object.values(row));
      const csvContent = [headers.join(','), ...data.map(r => r.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${this.activeTab}-scenario-data.csv`;
      link.click();
    },
    formatClientName(client) {
      if (!client) return '';
      const firstName = client.first_name || '';
      const lastName = client.last_name || '';
      const spouseName = client.spouse_name || '';
      if (spouseName) {
        return `${firstName} and ${spouseName} ${lastName}`;
      }
      return `${firstName} ${lastName}`;
    },
    fetchAssetDetails() {
      const scenarioId = this.$route.params.scenarioid;
      axios.get(`http://localhost:8000/api/scenarios/${scenarioId}/assets/`, { headers })
        .then(response => {
          this.assetDetails = response.data;
          console.log('Asset Details:', this.assetDetails);
        })
        .catch(error => {
          console.error('Error fetching asset details:', error);
        });
    },
  },
  computed: {
    incomeFields() {
      if (!this.scenarioResults.length) return [];

      const firstRow = this.scenarioResults[0];
      const knownKeys = [
        'year', 'primary_age', 'spouse_age', 'gross_income', 'taxable_income', 
        'federal_tax', 'total_medicare', 'remaining_ssi', 'social_security_benefit',
        'part_b', 'part_d', 'medicare_income'
      ];

      // List any field that seems to represent income but is not excluded
      return Object.keys(firstRow)
        .filter(key => key.includes('income') && !knownKeys.includes(key));
    },
    totalFederalTaxes() {
      return this.scenarioResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0).toFixed(2);
    },
    totalMedicareCosts() {
      return this.scenarioResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0).toFixed(2);
    },
    totalIrmaaSurcharge() {
      return parseFloat(this.scenarioResults.reduce((total, row) => total + (parseFloat(row.irmaa_surcharge || 0)), 0).toFixed(2));
    },
    totalMedicareCost() {
      return parseFloat(this.scenarioResults.reduce((total, row) => total + (parseFloat(row.total_medicare || 0)), 0).toFixed(2));
    },
  },
  watch: {
    scenarioResults: {
      handler() {
        this.$nextTick(() => {
          this.initializeCircles();
        });
      },
      deep: true
    },
    activeTab(newVal) {
      console.log('Active tab changed to:', newVal);
      if (['socialSecurity', 'medicare', 'worksheets'].includes(newVal)) {
        console.log('🔍 Debug - scenarioResults:', this.scenarioResults);
        if (this.scenarioResults.length) {
          console.log('🔍 Debug - First row year:', this.scenarioResults[0].year);
          this.initializeChartJS();
        } else {
          console.warn(`⚠️ scenarioResults is empty when switching to ${newVal} tab`);
          this.fetchScenarioData();
        }
      }
    },
    '$route.params.scenarioid': {
      immediate: true,
      handler(newVal) {
        const scenarioId = parseInt(newVal);
        this.scenario = this.scenarios.find(s => s.id === scenarioId);
        this.selectedScenarioId = scenarioId;
        this.fetchScenarioData();
      }
    },
  }
};
</script>

<style>
.equal-height-row {
  display: flex;
  flex-wrap: wrap;
}

.equal-height-row > .col {
  display: flex;
  flex-direction: column;
}

.circles-chart-content {
  text-align: center;
  line-height: 1;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(0%, 0%);
}
</style>
