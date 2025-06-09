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
                    <a href="/clients/{clientId}">{{ formatClientName(client) }}</a>
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
                <!-- Header -->
                
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
              <div class="card mb-3 mb-lg-5">
                <!-- Header -->
                <div class="card-header card-header-content-between">
                  <h5 class="mb-4">401k Year-by-Year Details</h5>
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead class="thead-light">
                        <tr>
                          <th>Year</th>
                          <th>401k Balance</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in scenarioResults" :key="row.year">
                          <td>{{ row.year }}</td>
                          <td>${{ row["401k_balance"] }}</td>
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
                <div class="card-header card-header-content-between">
                  <div class="dropdown">
                    <button type="button" class="btn btn-white btn-sm dropdown-toggle" @click="toggleDropdown('socialSecurity')" :aria-expanded="isDropdownOpen.socialSecurity">
                      <i class="bi-download me-2"></i> Export
                    </button>
                    <div class="dropdown-menu dropdown-menu-sm-end" :class="{ show: isDropdownOpen.socialSecurity }" aria-labelledby="usersExportDropdown">
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
                <div class="card-body">
                  <canvas id="socialSecurityChart" style="width: 100%; height: 300px !important;"></canvas>
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
                          <td>${{ parseFloat(row.ss_income || 0).toFixed(2) }}</td>
                          <td>${{ parseFloat(row.total_medicare || 0).toFixed(2) }}</td>
                          <td></td>
                          <td class="bg-success text-white">${{ (parseFloat(row.ss_income || 0) - parseFloat(row.total_medicare || 0)).toFixed(2) }}</td>
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
            </div>
            <div v-show="activeTab === 'income'" class="tab-pane active">
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <h5 class="mb-4">Types of Income in Scenario</h5>
                  <ul>
                    <li v-for="incomeType in incomeFields" :key="incomeType">
                      {{ incomeType }}
                    </li>
                  </ul>
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
              <div class="mb-3">
                <label for="colaInput" class="form-label">Social Security COLA (%)</label>
                <input type="number" class="form-control" id="colaInput" v-model.number="socialSecurityCola" @change="initializeChartJS" min="0" step="0.1">
              </div>
              <div class="card mb-3 mb-lg-5">
                <div class="card-body">
                  <canvas id="breakevenChart" style="width: 100%; height: 300px !important;"></canvas>
                </div>
              </div>
              <!-- Social Security Claim Comparison Table -->
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
              <!-- End Social Security Claim Comparison Table -->
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

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

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
      }
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
        console.log('Client Tax Status:', this.client?.tax_status);
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
        if (ctx && this.scenarioResults.length) {
          if (this.chartInstance) {
            this.chartInstance.destroy();
          }

          console.log('Scenario Results:', this.scenarioResults);
          console.log('Remaining SSI Benefit Data:', this.scenarioResults.map(row => parseFloat(row.remaining_ssi || 0)));

          const datasets = this.activeTab === 'worksheets' ? [
            ...Object.entries(this.benefitByAge).map(([age, benefit], i) => {
              const label = `Total Lifetime Value (Age ${age})`;
              const data = [];
              console.log(`Processing Age: ${age}, Benefit: ${benefit}`);
              let cumulativeIncome = 0;
              const startYear = 62 + (age - 62); // Adjust the start year based on age
              for (let year = 62; year <= 90; year++) {
                if (year >= startYear) {
                  cumulativeIncome += benefit;
                  data.push(cumulativeIncome);
                } else {
                  data.push(null); // Fill with null or zero until the start year
                }
                console.log(`Year: ${year}, Cumulative Income: ${cumulativeIncome}`);
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
                console.log(`Year: ${row.year}, SSI Benefit: ${ssiBenefit}, Medicare Expense: ${medicareExpense}, Remaining SSI: ${remainingSSI}`);
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
            type: 'line',
            label: 'Total Income',
            data: this.scenarioResults.map(row => parseFloat(row.gross_income || 0)),
            borderColor: "#377dff",
            backgroundColor: "rgba(55, 125, 255, 0.1)",
            borderWidth: 2,
            tension: 0.3,
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

          console.log('Datasets:', datasets);
          console.log('Chart Context:', ctx);

          this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
              labels: this.scenarioResults.map(row => row.year.toString()), // Use actual years from data
              datasets: datasets
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                x: {
                  stacked: false,
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
                            const defaultOptions = {
                                radius: 25,
                                width: 7,
                                fgStrokeLinecap: 'round',
                                textFontSize: 14,
                                additionalText: '%',
                                textClass: 'circles-chart-content',
                                textColor: '#377dff'
                            };
                            CirclesGlobal.create({ id: el.id, ...defaultOptions, ...options });
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
          console.log('API Response:', response.data);
          // Re-initialize chart with new data
          this.initializeChartJS();
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
    }
  },
  watch: {
    activeTab(newVal) {
      console.log("Active tab changed to:", newVal);
      if (['socialSecurity', 'medicare', 'worksheets'].includes(newVal)) {
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
