<template>
<main id="content" role="main" class="main">
    <!-- Content -->
    <div class="content container-fluid">
      <!-- Page Header -->
      <div class="page-header">
        <div class="d-flex mb-3">
          <!-- Avatar -->
          <!-- <div class="flex-shrink-0">
            <div class="avatar avatar-lg avatar-4x3">
              <img class="avatar-img" src="./assets/svg/brands/guideline-icon.svg" alt="Image Description">
            </div>
          </div> -->
          <!-- End Avatar -->

          <div class="flex-grow-1 ms-4">
            <div class="row">
              <div class="col-lg mb-3 mb-lg-0">
                
                <h1 class="page-header-title">{{ scenario ? scenario.name : 'Scenario Detail' }}</h1>

                <div class="row align-items-center">
                  <div class="col-auto">
                    <span>Client:</span>
                    <a href="#">< Client Name(s) ></a>
                  </div>
                  <!-- End Col -->

                  <div class="col-auto">
                    <div class="row align-items-center g-0">
                      <div class="col-auto">Due date:</div>

                      <!-- Flatpickr -->
                      <div class="col flatpickr-custom-position-fix-sm-down">
                        <div id="projectDeadlineFlatpickr" class="js-flatpickr flatpickr-custom flatpickr-custom-borderless input-group input-group-sm" data-hs-flatpickr-options='{
                                "appendTo": "#projectDeadlineFlatpickr",
                                "dateFormat": "d/m/Y",
                                "wrap": true
                              }'>
                          <input type="text" class="flatpickr-custom-form-control form-control" placeholder="Select dates" data-input value="29/06/2020">
                          
                        </div>
                      </div>
                      <!-- End Flatpickr -->
                    </div>
                  </div>

                  <!-- End Col -->
                </div>
                <!-- End Row -->
              </div>
              <!-- End Col -->

              <div class="col-lg-auto">
                <div class="mb-3">
                  <label for="scenarioSelect" class="form-label">Switch Scenario</label>
                  <select id="scenarioSelect" class="form-select" v-model="selectedScenarioId" @change="onScenarioChange">
                    <option v-for="s in scenarios" :value="s.id" :key="s.id">{{ s.name }}</option>
                  </select>
                </div>
              </div>
              <!-- End Col -->
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

          <div class="row">
        <div class="col-sm-6 col-xl-4 mb-3 mb-xl-6">
          <!-- Card -->
          <div class="card card-sm h-100">
            <div class="card-body">
              <div class="row">
                <div class="col">
                  <!-- Media -->
                  <div class="d-flex">
                    <div class="flex-shrink-0">
                      <i class="bi-receipt nav-icon"></i>
                    </div>

                    <div class="flex-grow-1 ms-3">
                      <h4 class="mb-1">Total Taxes</h4>
                    </div>
                  </div>
                  <!-- End Media -->
                </div>
                <!-- End Col -->

                <div class="col-auto">
                  <!-- Circle -->
                  <div class="circles-chart">
                    <div class="js-circle" id="circle-taxes" data-hs-circles-options='{
                           "value": 54,
                           "maxValue": 100,
                           "duration": 500,
                           "isViewportInit": true,
                           "radius": 25,
                           "width": 7,
                           "fgStrokeLinecap": "round",
                           "textFontSize": 14,
                           "additionalText": "%",
                           "textClass": "circles-chart-content",
                           "textColor": "#377dff"
                         }'></div>
                  </div>
                  <!-- End Circle -->
                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-xl-4 mb-3 mb-xl-6">
          <!-- Card -->
          <div class="card card-sm h-100">
            <div class="card-body">
              <div class="row">
                <div class="col">
                  <!-- Media -->
                  <div class="d-flex">
                    <div class="flex-shrink-0">
                      <i class="bi-bar-chart nav-icon"></i>
                    </div>

                    <div class="flex-grow-1 ms-3">
                      <h4 class="mb-1">Total Medicare Costs</h4>
                    </div>
                  </div>
                  <!-- End Media -->
                </div>
                <!-- End Col -->

                <div class="col-auto">
                  <!-- Circle -->
                  <div class="circles-chart">
                    <div class="js-circle" id="circle-medicare" data-hs-circles-options='{
                           "value": 80,
                           "maxValue": 100,
                           "duration": 2000,
                           "isViewportInit": true,
                           "radius": 25,
                           "width": 3,
                           "fgStrokeLinecap": "round",
                           "textFontSize": 14,
                           "additionalText": "%",
                           "textClass": "circles-chart-content",
                           "textColor": "#377dff"
                         }'></div>
                  </div>
                  <!-- End Circle -->
                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        <div class="col-sm-6 col-xl-4 mb-3 mb-xl-6">
          <!-- Card -->
          <div class="card card-sm h-100">
            <div class="card-body">
              <div class="row">
                <div class="col">
                  <!-- Media -->
                  <div class="d-flex">
                    <div class="flex-shrink-0">
                      <i class="bi-check2-circle nav-icon"></i>
                    </div>

                    <div class="flex-grow-1 ms-3">
                      <h4 class="mb-1">Total Medicare Out Of Pocket</h4>
                      <span class="d-block">79 <span class="badge bg-soft-dark text-dark rounded-pill ms-1">+4 today</span></span>
                    </div>
                  </div>
                  <!-- End Media -->
                </div>
                <!-- End Col -->

                <div class="col-auto">
                  <!-- Circle -->
                  <div class="circles-chart">
                    <div class="js-circle" id="circle-outofpocket" data-hs-circles-options='{
                           "value": 67,
                           "maxValue": 100,
                           "duration": 2000,
                           "isViewportInit": true,
                           "radius": 25,
                           "width": 3,
                           "fgStrokeLinecap": "round",
                           "textFontSize": 14,
                           "additionalText": "%",
                           "textClass": "circles-chart-content",
                           "textColor": "#377dff"
                         }'></div>
                  </div>
                  <!-- End Circle -->
                </div>
                <!-- End Col -->
              </div>
              <!-- End Row -->
            </div>
          </div>
          <!-- End Card -->
        </div>

        
      </div>
      <!-- End Row -->

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
            <div v-if="activeTab === 'financial'" class="tab-pane active">
              <!-- Card -->
              <div class="card mb-3 mb-lg-5" >
                <!-- Header -->
                <div class="card-header card-header-content-between">
                  <!-- <h6 class="card-subtitle mb-0">Project budget: <span class="h3 ms-sm-2">$150,000.00 USD</span></h6> -->

                  <!-- Dropdown -->
                  <div class="dropdown">
                    <button type="button" class="btn btn-white btn-sm dropdown-toggle" id="usersExportDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                      <i class="bi-download me-2"></i> Export
                    </button>

                    <div class="dropdown-menu dropdown-menu-sm-end" aria-labelledby="usersExportDropdown">
                      <span class="dropdown-header">Options</span>
                      <a id="export-copy" class="dropdown-item" href="javascript:;">
                        <img class="avatar avatar-xss avatar-4x3 me-2" src="./assets/svg/illustrations/copy-icon.svg" alt="Image Description">
                        Copy
                      </a>
                      <a id="export-print" class="dropdown-item" href="javascript:;">
                        <img class="avatar avatar-xss avatar-4x3 me-2" src="./assets/svg/illustrations/print-icon.svg" alt="Image Description">
                        Print
                      </a>
                      <div class="dropdown-divider"></div>
                      <span class="dropdown-header">Download options</span>
                      <a id="export-excel" class="dropdown-item" href="javascript:;">
                        <img class="avatar avatar-xss avatar-4x3 me-2" src="./assets/svg/brands/excel-icon.svg" alt="Image Description">
                        Excel
                      </a>
                      <a id="export-csv" class="dropdown-item" href="javascript:;">
                        <img class="avatar avatar-xss avatar-4x3 me-2" src="./assets/svg/components/placeholder-csv-format.svg" alt="Image Description">
                        .CSV
                      </a>
                      <a id="export-pdf" class="dropdown-item" href="javascript:;">
                        <img class="avatar avatar-xss avatar-4x3 me-2" src="./assets/svg/brands/pdf-icon.svg" alt="Image Description">
                        PDF
                      </a>
                    </div>
                  </div>
                  <!-- End Dropdown -->
                </div>
                <!-- End Header -->

                <!-- Body -->
                <div class="card-body">
                  <!-- Bar Chart -->
                  <canvas id="project" class="js-chart" style="width: 100%;height:300px;" data-hs-chartjs-options='{
                            "type": "line",
                            "data": {
                              "labels": ["Feb","Jan","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                              "datasets": [{
                                "data": [18,51,60,38,88,50,40,52,88,80,60,70],
                                "backgroundColor": ["rgba(55, 125, 255, 0)", "rgba(255, 255, 255, 0)"],
                                "borderColor": "#377dff",
                                "borderWidth": 2,
                                "pointRadius": 0,
                                "pointBorderColor": "#fff",
                                "pointBackgroundColor": "#377dff",
                                "pointHoverRadius": 0,
                                "hoverBorderColor": "#fff",
                                "hoverBackgroundColor": "#377dff",
                                "tension": 0.4
                              },
                              {
                                "data": [27,38,60,77,40,50,49,29,42,27,42,50],
                                "backgroundColor": ["rgba(0, 201, 219, 0)", "rgba(255, 255, 255, 0)"],
                                "borderColor": "#00c9db",
                                "borderWidth": 2,
                                "pointRadius": 0,
                                "pointBorderColor": "#fff",
                                "pointBackgroundColor": "#00c9db",
                                "pointHoverRadius": 0,
                                "hoverBorderColor": "#fff",
                                "hoverBackgroundColor": "#00c9db",
                                "tension": 0.4
                              }]
                            },
                            "options": {
                              "gradientPosition": {"y1": 200},
                              "scales": {
                                  "y": {
                                    "grid": {
                                      "color": "#e7eaf3",
                                      "drawBorder": false,
                                      "zeroLineColor": "#e7eaf3"
                                    },
                                    "ticks": {
                                      "min": 0,
                                      "max": 100,
                                      "stepSize": 20,
                                      "color": "#97a4af",                                
                                      "font": {
                                        "family": "Open Sans, sans-serif"
                                      },
                                      "padding": 10,
                                      "postfix": "k"
                                    }
                                  },
                                  "x": {
                                    "grid": {
                                      "display": false,
                                      "drawBorder": false
                                    },
                                    "ticks": {
                                    "color": "#97a4af",
                                      "font": {
                                        "family": "Open Sans, sans-serif"
                                      },
                                      "padding": 5
                                    }
                                  }
                              },
                              "plugins": {
                                "tooltip": {
                                  "prefix": "$",
                                  "postfix": "k",
                                  "hasIndicator": true,
                                  "mode": "index",
                                  "intersect": false,
                                  "lineMode": true,
                                  "lineWithLineColor": "rgba(19, 33, 68, 0.075)"
                                }
                              },
                              "hover": {
                                "mode": "nearest",
                                "intersect": true
                              }
                            }
                          }'>
                  </canvas>
                  <!-- End Bar Chart -->
                </div>
                <!-- End Body -->
              </div>
              <!-- End Card -->
              <div class="card mb-3 mb-lg-5">
                <!-- Header -->
                <div class="dropdown mb-3">
                    <button class="btn btn-outline-primary dropdown-toggle" type="button" id="downloadDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                      Download
                    </button>
                    <ul class="dropdown-menu" aria-labelledby="downloadDropdown">
                      <li><a class="dropdown-item" href="#" @click.prevent="downloadTable('csv')">Download CSV</a></li>
                      <li><a class="dropdown-item" href="#" @click.prevent="downloadTable('excel')">Download Excel</a></li>
                    </ul>
                  </div>
                <div class="card-header card-header-content-between">
                  <div v-if="scenarioResults.length" class="table-responsive mt-4">
                    <table class="table table-hover">
                      <thead class="thead-light">
                        <tr>
                          <th>Year</th>
                          <th>Primary Age</th>
                          <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
                          <th>Gross Income</th>
                          <th>Taxable Income</th>
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
                          <td>${{ row.gross_income }}</td>
                          <td>${{ row.taxable_income }}</td>
                          <td>12%</td>
                          <td>${{ row.federal_tax }}</td>
                          <td>${{ row.total_medicare }}</td>
                          <td>${{ (parseFloat(row.gross_income) - (parseFloat(row.federal_tax) + parseFloat(row.total_medicare))).toFixed(2) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              <!-- End Card -->
            </div>
            <div v-show="activeTab === 'socialSecurity'" class="tab-pane active">
              <!-- Social Security Chart Card -->
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <canvas id="socialSecurityChart" style="width: 100%; height: 300px;"></canvas>
                </div>
              </div>
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <h5 class="mb-4">IMPACT ON SOCIAL SECURITY CHECK (PRIMARY)</h5>
                  <div class="table-responsive">
                    <table class="table table-bordered">
                      <thead>
                        <tr>
                          <th>Year</th>
                          <th>Age</th>
                          <th>SSI Benefit</th>
                          <th>Total Medicare Expense</th>
                          <th>SSI Benefit Taxed</th>
                          <th>Remaining SSI Benefit</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, index) in scenarioResults" :key="index">
                          <td>{{ row.year }}</td>
                          <td>{{ row.primary_age }}</td>
                          <td>${{ parseFloat(row.social_security_benefit || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
                          <td>{{ (parseFloat(row.ssi_taxed || 0) * 100).toFixed(2) }}%</td>
                          <td class="bg-success text-white">${{ parseFloat(row.remaining_ssi || 0).toFixed(2) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div v-show="activeTab === 'medicare'" class="tab-pane active">
              <!-- Medicare Chart Card -->
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <canvas id="medicareChart" style="width: 100%; height: 300px;"></canvas>
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
                          <th>Age (mark)</th>
                          <th>Total Income</th>
                          <th>Income for Medicare</th>
                          <th>Part B (mark)</th>
                          <th>Part D (mark)</th>
                          <th>Total Cost</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, index) in scenarioResults" :key="index">
                          <td>{{ row.year }}</td>
                          <td>{{ row.primary_age }}</td>
                          <td>${{ parseFloat(row.gross_income || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.medicare_income || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.part_b || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.part_d || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
            <div v-show="activeTab === 'income'" class="tab-pane active">
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <p>This is the Income section.</p>
                </div>
              </div>
            </div>
            <div v-show="activeTab === 'rothConversion'" class="tab-pane active">
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <p>This is the Roth Conversion section.</p>
                </div>
              </div>
            </div>
            <div v-show="activeTab === 'worksheets'" class="tab-pane active">
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <p>This is the Social Security Worksheets section.</p>
                </div>
              </div>
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

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
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
        this.fetchScenarioData();
      })
      .catch(error => {
        console.error('Error loading client and scenario:', error);
      });
  },
  methods: {
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
        const ctx = document.getElementById('project');
        if (ctx && this.scenarioResults.length) {
          // Robust number parsing function
          const parseNumber = val => parseFloat(String(val).replace(/,/g, '')) || 0;
          const labels = this.scenarioResults.map(row => row.year.toString());
          // Calculate remainingIncome with explicit tax and medicare variables
          const remainingIncome1 = this.scenarioResults.map(row => {
            const gross = parseNumber(row.gross_income);
            const tax = parseNumber(row.federal_tax);
            const medicare = parseNumber(row.total_medicare);
            const remaining = gross - (tax + medicare);
            return parseFloat(remaining.toFixed(2));
          });
          const grossIncome = this.scenarioResults.map(row => parseNumber(row.gross_income));
          const federalTax = this.scenarioResults.map(row => parseNumber(row.federal_tax));
          const totalMedicare = this.scenarioResults.map(row => parseNumber(row.total_medicare));

          new Chart(ctx, {
            type: 'bar',
            data: {
              labels: labels,
              datasets: [
                {
                  type: 'line',
                  label: 'Gross Income',
                  data: grossIncome,
                  borderColor: "#377dff",
                  backgroundColor: "rgba(55, 125, 255, 0.1)",
                  borderWidth: 2,
                  tension: 0.3,
                  yAxisID: 'y'
                },
                {
                  type: 'line',
                  label: 'Remaining Income',
                  data: remainingIncome1,
                  borderColor: "#00c9db",
                  backgroundColor: "rgba(0, 201, 219, 0.1)",
                  borderWidth: 2,
                  tension: 0.3,
                  yAxisID: 'y'
                },
                {
                  label: 'Federal Tax',
                  data: federalTax,
                  backgroundColor: "#ff6b6b",
                  stack: 'Stack 0',
                  yAxisID: 'y'
                },
                {
                  label: 'Total Medicare',
                  data: totalMedicare,
                  backgroundColor: "#ffc107",
                  stack: 'Stack 0',
                  yAxisID: 'y'
                }
              ]
            },
            options: {
              responsive: true,
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
        }
        // Add Social Security Chart logic if on the appropriate tab
        if (this.activeTab === 'socialSecurity') {
          const ctxSS = document.getElementById('socialSecurityChart');
          if (ctxSS && this.scenarioResults.length) {
            const parseNumber = val => parseFloat(String(val).replace(/,/g, '')) || 0;
            const labels = this.scenarioResults.map(row => row.year.toString());
            const ssiBenefit = this.scenarioResults.map(row => parseNumber(row.social_security_benefit));
            const remainingSSI = this.scenarioResults.map(row => parseNumber(row.remaining_ssi));
            const medicareCost = this.scenarioResults.map(row => parseNumber(row.total_medicare));

            new Chart(ctxSS, {
              type: 'bar',
              data: {
                labels: labels,
                datasets: [
                  {
                    type: 'line',
                    label: 'SSI Benefit',
                    data: ssiBenefit,
                    borderColor: '#377dff',
                    backgroundColor: 'rgba(55, 125, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    yAxisID: 'y'
                  },
                  {
                    type: 'line',
                    label: 'Remaining SSI Benefit',
                    data: remainingSSI,
                    borderColor: '#00c9db',
                    backgroundColor: 'rgba(0, 201, 219, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    yAxisID: 'y'
                  },
                  {
                    label: 'Total Medicare Expense',
                    data: medicareCost,
                    backgroundColor: '#ffc107',
                    stack: 'Stack 0',
                    yAxisID: 'y'
                  }
                ]
              },
              options: {
                responsive: true,
                scales: {
                  x: {
                    stacked: true,
                    title: {
                      display: true,
                      text: 'Year'
                    }
                  },
                  y: {
                    stacked: false,
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
          }
        }
        // Add Medicare Chart logic if on the appropriate tab
        if (this.activeTab === 'medicare') {
          const ctxMedicare = document.getElementById('medicareChart');
          if (ctxMedicare && this.scenarioResults.length) {
            const parseNumber = val => parseFloat(String(val).replace(/,/g, '')) || 0;
            const labels = this.scenarioResults.map(row => row.year.toString());
            const totalIncome = this.scenarioResults.map(row => parseNumber(row.gross_income));
            const partB = this.scenarioResults.map(row => parseNumber(row.part_b));
            const partD = this.scenarioResults.map(row => parseNumber(row.part_d));

            new Chart(ctxMedicare, {
              type: 'bar',
              data: {
                labels: labels,
                datasets: [
                  {
                    type: 'line',
                    label: 'Total Income',
                    data: totalIncome,
                    borderColor: '#377dff',
                    backgroundColor: 'rgba(55, 125, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    yAxisID: 'y'
                  },
                  {
                    label: 'Part B',
                    data: partB,
                    backgroundColor: '#ff6b6b',
                    stack: 'Stack 0',
                    yAxisID: 'y'
                  },
                  {
                    label: 'Part D',
                    data: partD,
                    backgroundColor: '#00c9db',
                    stack: 'Stack 0',
                    yAxisID: 'y'
                  }
                ]
              },
              options: {
                responsive: true,
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
          }
        }
      });
    },
    initializeCircles() {
        this.$nextTick(() => {
            const maxRetries = 20;
            let retryCount = 0;

            const tryInit = () => {
                const CirclesGlobal = window.Circles;
                if (CirclesGlobal && typeof CirclesGlobal.create === 'function') {
                    document.querySelectorAll('.js-circle').forEach((el) => {
                        if (!el.dataset.initialized) {
                            const options = JSON.parse(el.getAttribute('data-hs-circles-options') || '{}');
                            console.log('Creating circle for element:', el.id, options);
                            CirclesGlobal.create({ id: el.id, ...options });
                            el.dataset.initialized = 'true';
                        }
                    });
                } else if (retryCount < maxRetries) {
                    retryCount++;
                    console.warn(`Circles.js not ready, retrying ${retryCount}/${maxRetries}...`);
                    setTimeout(tryInit, 200);
                } else {
                    console.error('❌ Circles.js never loaded.');
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
          this.scenarioResults = response.data;
          // Re-initialize chart with new data
          this.initializeChartJS();
        })
        .catch(error => {
          console.error("Error loading scenario data:", error);
        });
    },
  },
  watch: {
    activeTab(newVal) {
      console.log("Active tab changed to:", newVal);
      if (newVal === 'socialSecurity' || newVal === 'medicare') {
        console.log("🔍 Debug - scenarioResults:", this.scenarioResults);
        if (this.scenarioResults.length) {
          console.log("🔍 Debug - First row year:", this.scenarioResults[0].year);
          this.$nextTick(() => this.initializeChartJS());
        } else {
          console.warn(`⚠️ scenarioResults is empty when switching to ${newVal} tab`);
        }
      }
    },
    '$route.params.scenarioid': {
      immediate: true,
      handler(newVal) {
        const scenarioId = parseInt(newVal);
        this.scenario = this.scenarios.find(s => s.id === scenarioId);
        this.selectedScenarioId = scenarioId;
      }
    }
  }
};
</script>
