<template>
    <div class="container-fluid" style="margin-top:80px;">
      <!-- PDF Generation Overlay -->
      <transition name="fade">
        <div v-if="isGeneratingPDF" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
             style="z-index: 9999; background-color: rgba(0, 0, 0, 0.6); backdrop-filter: blur(3px);">
          <div class="text-center bg-dark bg-opacity-75 p-5 rounded-3" style="min-width: 300px;">
            <div class="spinner-border text-primary mb-4" style="width: 4rem; height: 4rem;" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <h3 class="text-white mb-3">Generating Report</h3>
            <p class="text-white-50 mb-0">Please wait, this may take a moment...</p>
          </div>
        </div>
      </transition>
      
      <!-- Page Header -->
      <div class="page-header">
        <div class="d-flex mb-3">
          <div class="flex-grow-1">
            <div class="row">
              <div class="col-lg mb-3 mb-lg-0">
                
                <div class="d-flex align-items-center">
                  <span>Client:</span>
                  <router-link v-if="client" :to="{ name: 'ClientDetail', params: { id: client.id } }" class="ms-2">
                    {{ formatClientName(client) }}
                  </router-link>
                  <span v-else class="ms-2">Loading...</span>
                </div>

                <!-- End Row -->
              </div>
              <!-- End Col -->

              <div class="col-lg-auto d-flex align-items-center" v-if="!isPdfMode">
                <!-- Navigation Dropdowns (hidden in PDF mode) -->
                <div class="d-flex align-items-center me-3">
                  <span class="me-2 fw-semibold">Choose</span>
                  <!-- Scenario Switcher Dropdown -->
                  <div class="dropdown me-2">
                    <button class="btn btn-outline-primary dropdown-toggle" type="button" @click="toggleScenarioDropdown" :aria-expanded="scenarioDropdownOpen">
                      {{ scenario ? scenario.name : 'Select Scenario' }}
                    </button>
                    <ul class="dropdown-menu" :class="{ 'show': scenarioDropdownOpen }">
                      <li v-for="s in scenarios" :key="s.id">
                        <a class="dropdown-item" :class="{ active: selectedScenarioId === s.id }" href="#" @click.prevent="switchToScenario(s.id)">
                          <i class="bi-graph-up me-2"></i>{{ s.name }}
                        </a>
                      </li>
                    </ul>
                  </div>
                  <span class="me-2 text-muted">-</span>
                  <!-- Page Navigation Dropdown -->
                  <div class="dropdown">
                    <button class="btn btn-outline-primary dropdown-toggle" type="button" @click="toggleNavDropdown" :aria-expanded="navDropdownOpen">
                      <span v-if="activeTab === 'overview'">Scenario Overview</span>
                      <span v-else-if="activeTab === 'financial'">Financial Overview</span>
                      <span v-else-if="activeTab === 'socialSecurity'">Social Security Overview</span>
                      <span v-else-if="activeTab === 'socialSecurity2' && isAdminUser">Social Security 2</span>
                      <span v-else-if="activeTab === 'medicare'">Medicare Overview</span>
                      <span v-else-if="activeTab === 'income'">Income</span>
                      <span v-else-if="activeTab === 'rothConversion'">Roth Conversion</span>
                      <span v-else-if="activeTab === 'worksheets'">Social Security Worksheets</span>
                      <span v-else-if="activeTab === 'nextSteps'">Next Steps</span>
                      <span v-else>Select View</span>
                    </button>
                    <ul class="dropdown-menu" :class="{ 'show': navDropdownOpen }">
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'overview' }" href="#" @click.prevent="navigateToTab('overview')">
                        <i class="bi-graph-up me-2"></i>Scenario Overview
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'financial' }" href="#" @click.prevent="navigateToTab('financial')">
                        <i class="bi-bar-chart me-2"></i>Financial Overview
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'socialSecurity' }" href="#" @click.prevent="navigateToTab('socialSecurity')">
                        <i class="bi-shield-check me-2"></i>Social Security Overview
                      </a></li>
                      <li v-if="isAdminUser"><a class="dropdown-item" :class="{ active: activeTab === 'socialSecurity2' }" href="#" @click.prevent="navigateToTab('socialSecurity2')">
                        <i class="bi-shield me-2"></i>Social Security 2
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'medicare' }" href="#" @click.prevent="navigateToTab('medicare')">
                        <i class="bi-hospital me-2"></i>Medicare Overview
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'income' }" href="#" @click.prevent="navigateToTab('income')">
                        <i class="bi-currency-dollar me-2"></i>Income
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'rothConversion' }" href="#" @click.prevent="navigateToTab('rothConversion')">
                        <i class="bi-arrow-repeat me-2"></i>Roth Conversion
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'worksheets' }" href="#" @click.prevent="navigateToTab('worksheets')">
                        <i class="bi-table me-2"></i>Social Security Worksheets
                      </a></li>
                      <li><a class="dropdown-item" :class="{ active: activeTab === 'nextSteps' }" href="#" @click.prevent="navigateToTab('nextSteps')">
                        <i class="bi-list-check me-2"></i>Next Steps
                      </a></li>
                    </ul>
                  </div>
                </div>
                <!-- Actions Dropdown -->
                <div class="dropdown">
                  <button class="btn btn-primary dropdown-toggle" type="button" @click="toggleActionsDropdown" :aria-expanded="actionsDropdownOpen">
                    Actions
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end" :class="{ 'show': actionsDropdownOpen }">
                    <li><a class="dropdown-item" href="#" @click.prevent="createScenario('scratch')"><i class="bi-plus-circle me-2"></i>New Scenario</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="createScenario('duplicate')"><i class="bi-files me-2"></i>Duplicate Scenario</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="editScenario"><i class="bi-pencil me-2"></i>Edit Scenario</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="downloadScenarioPDF"><i class="bi-file-earmark-pdf me-2"></i>Download PDF Report</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                      <a class="dropdown-item d-flex justify-content-between align-items-center" href="#" @click.prevent="toggleScenarioSharing">
                        <span>
                          <i class="bi-share me-2"></i>
                          {{ scenario?.share_with_client ? 'Remove from Portal' : 'Share to Portal' }}
                        </span>
                        <span v-if="scenario?.share_with_client" class="badge bg-success">Shared</span>
                      </a>
                    </li>
                  </ul>
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

          <!-- Removed ScenarioMetrics from main layout - moved to overview tab -->
          <!-- Removed tab navigation - functionality moved to sidebar -->
          <div class="tab-content mt-4">
            <div v-show="activeTab === 'overview'" class="tab-pane active" style="margin-top:50px;">
              <div class="row">
                <!-- Left Card - 1/4 Width for Metrics -->
                <div class="col-lg-3 d-flex">
                  <div class="card flex-fill">
                    <div class="card-header">
                      <h4 class="card-header-title">Key Metrics</h4>
                    </div>
                    <div class="card-body d-flex flex-column">
                      <!-- Vertical Metrics Cards -->
                      <div class="row flex-fill">
                        <div class="col-12 mb-3">
                          <div class="card card-sm">
                            <div class="card-body">
                              <div class="d-flex align-items-center">
                                <div class="flex-shrink-0">
                                  <i class="bi-receipt nav-icon"></i>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                  <h6 class="mb-1">Federal and State Taxes</h6>
                                  <div v-if="isCalculating" class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                      <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <span class="text-muted">Calculating...</span>
                                  </div>
                                  <span v-else class="d-block fw-bold text-primary fs-2">{{ formatCurrency(totalFederalTaxes) }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div class="col-12 mb-3">
                          <div class="card card-sm">
                            <div class="card-body">
                              <div class="d-flex align-items-center">
                                <div class="flex-shrink-0">
                                  <i class="bi-bar-chart nav-icon"></i>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                  <h6 class="mb-1">Medicare Costs</h6>
                                  <div v-if="isCalculating" class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                      <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <span class="text-muted">Calculating...</span>
                                  </div>
                                  <span v-else class="d-block fw-bold text-primary fs-2">{{ formatCurrency(totalMedicareCosts) }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div class="col-12 mb-3">
                          <div class="card card-sm">
                            <div class="card-body">
                              <div class="d-flex align-items-center">
                                <div class="flex-shrink-0">
                                  <i class="bi-check2-circle nav-icon"></i>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                  <h6 class="mb-1">Medicare Out Of Pocket</h6>
                                  <div v-if="isCalculating" class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                      <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <span class="text-muted">Calculating...</span>
                                  </div>
                                  <span v-else class="d-block fw-bold text-primary fs-2">{{ formatCurrency(medicareOutOfPocket) }}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div class="col-12 mb-0">
                          <div class="card card-sm">
                            <div class="card-body">
                              <div class="d-flex align-items-center">
                                <div class="flex-shrink-0">
                                  <i class="bi-check2-circle nav-icon"></i>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                  <h6 class="mb-1">IRMAA Status</h6>
                                  <div v-if="isCalculating" class="d-flex align-items-center">
                                    <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                                      <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <span class="text-muted">Calculating...</span>
                                  </div>
                                  <div v-else :style="{width: '100%', height: '20px', backgroundColor: irmaaColor, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold', color: 'white', borderRadius: '3px'}">
                                    {{ irmaaPercentage }}%
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Right Card - 3/4 Width for Other Information -->
                <div class="col-lg-9">
                  <div class="card mb-4">
                    <div class="card-body">
                      <div class="row">
                        <div class="col-sm-6">
                          <h5 class="card-title mb-3">Client Information</h5>
                          <div class="client-info-item">
                            <span class="info-label">Name:</span>
                            <span class="info-value">{{ formatClientName(client) }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Tax Status:</span>
                            <span class="info-value">{{ client?.tax_status || 'Not specified' }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Current Age:</span>
                            <span class="info-value">{{ currentAge || 'Not specified' }}</span>
                          </div>
                          <div v-if="client?.tax_status?.toLowerCase() !== 'single'" class="client-info-item">
                            <span class="info-label">Spouse Age:</span>
                            <span class="info-value">{{ spouseAge || 'Not specified' }}</span>
                          </div>
                        </div>
                        <div class="col-sm-6">
                          <h5 class="card-title mb-3">Scenario Details</h5>
                          <div class="client-info-item">
                            <span class="info-label">Name:</span>
                            <span class="info-value">{{ scenario?.name || 'Not specified' }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Retirement Year:</span>
                            <span class="info-value">{{ scenario?.retirement_year || 'Not specified' }}</span>
                          </div>
                          <div class="client-info-item">
                            <span class="info-label">Mortality Age:</span>
                            <span class="info-value">{{ scenario?.mortality_age || 'Not specified' }}</span>
                          </div>
                          <div v-if="client?.tax_status?.toLowerCase() !== 'single'" class="client-info-item">
                            <span class="info-label">Spouse Mortality Age:</span>
                            <span class="info-value">{{ scenario?.spouse_mortality_age || 'Not specified' }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Financial Charts in Same Column -->
                  <!-- Row for Chart and Circle Card -->
                  <div class="row">
                    <!-- Financial Chart Card (2/3 width) -->
                    <div class="col-lg-8 col-md-7 mb-3 mb-lg-0">
                      <div class="card h-100">
                        <div class="card-body">
                          <div v-if="isCalculating" class="d-flex flex-column align-items-center justify-content-center" style="height: 300px;">
                            <div class="spinner-border text-primary mb-2" role="status">
                              <span class="visually-hidden">Loading...</span>
                            </div>
                            <span class="text-muted">Loading chart data...</span>
                          </div>
                          <div v-else class="financial-chart-container">
                            <Graph 
                              :data="overviewChartData" 
                              :options="overviewChartOptions"
                              :height="300"
                              type="line"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <!-- Circle Card (1/3 width) -->
                    <div class="col-lg-4 col-md-5 mb-3 mb-lg-0">
                      <div class="card h-100 d-flex flex-column justify-content-center align-items-center">
                        <div class="card-body w-100">
                          <h5 class="mb-4 text-center">Taxes & Medicare as % of Gross Income</h5>
                          <div v-if="isCalculating" class="d-flex flex-column align-items-center justify-content-center" style="min-height: 180px; padding-top: 20px;">
                            <div class="spinner-border text-primary mb-2" role="status">
                              <span class="visually-hidden">Loading...</span>
                            </div>
                            <span class="text-muted">Loading chart...</span>
                          </div>
                          <div v-else class="circles-chart d-flex justify-content-center" style="padding-top:20px; min-height: 180px;">
                            <div class="js-circle" id="circle-overview"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- End Charts Row -->
                </div>
                <!-- End Right Column -->
              </div>
              <!-- End Main Row -->
              
              <!-- Disclosures Card -->
              <DisclosuresCard />
            </div>
            <div v-show="activeTab === 'financial'" class="tab-pane active" style="margin-top:50px;">
              <FinancialOverviewTab :scenario="scenario" :scenario-results="scenarioResults" :filtered-results="filteredScenarioResults" :client="client" :mortality-age="scenario?.mortality_age" :spouse-mortality-age="scenario?.spouse_mortality_age" />
            </div>
            <div v-show="activeTab === 'socialSecurity'" class="tab-pane active" style="margin-top:50px;">
              <SocialSecurityOverviewTab :scenario="scenario" :scenario-results="scenarioResults" :client="client" :mortality-age="scenario?.mortality_age" :spouse-mortality-age="scenario?.spouse_mortality_age" :is-calculating="isCalculating" />
            </div>
            <div v-show="activeTab === 'socialSecurity2'" class="tab-pane active" style="margin-top:50px;">
              <SocialSecurity2Tab :key="`ss2-${scenario?.id}-${activeTab}`" :scenario="scenario" :scenario-results="scenarioResults" :client="client" @update-scenario="handleScenarioUpdate" />
            </div>
            <div v-show="activeTab === 'medicare'" class="tab-pane active" style="margin-top:50px;">
              <MedicareOverviewTab :scenario="scenario" :scenario-results="scenarioResults" :client="client" :partBInflationRate="partBInflationRate" :partDInflationRate="partDInflationRate" :totalIrmaaSurcharge="totalIrmaaSurcharge" :totalMedicareCost="totalMedicareCost" :mortality-age="scenario?.mortality_age" :spouse-mortality-age="scenario?.spouse_mortality_age" />
            </div>
            <div v-show="activeTab === 'income'" class="tab-pane active" style="margin-top:50px;">
              <div v-if="!assetDetails || assetDetails.length === 0" class="alert alert-warning">
                Loading asset data...
              </div>
              <IncomeTab v-else :scenario="scenario" :assetDetails="assetDetails" :scenarioResults="scenarioResults" :client="client" />
            </div>
            <div v-show="activeTab === 'rothConversion'" class="tab-pane active" style="margin-top:50px;">
              <RothConversionTab :scenario="scenario" :assetDetails="assetDetails" :scenarioResults="scenarioResults" :client="client" />
            </div>
            <div v-show="activeTab === 'worksheets'" class="tab-pane active" style="margin-top:50px;">
              <WorksheetsTab :scenarioResults="scenarioResults" :client="client" :benefitByAge="benefitByAge" :socialSecurityCola="socialSecurityCola" :medicareCosts="scenarioResults" />
            </div>
            <div v-show="activeTab === 'nextSteps'" class="tab-pane active" style="margin-top:50px;">
              <NextStepsTab />
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
        </div>
        <!-- End Col -->

        <div class="col-auto">
        </div>
        <!-- End Col -->
      </div>
      <!-- End Row -->

    <!-- End Footer -->
    </div>
</template>

<script>
import axios from 'axios'
import { API_CONFIG } from '@/config'
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { mapActions } from 'vuex';
import { useScenarioCalculationsStore } from '@/stores/scenarioCalculations';
import { useAuthStore } from '@/stores/auth';

import Chart from 'chart.js/auto';

import FinancialOverviewTab from './FinancialOverviewTab.vue';
import SocialSecurityOverviewTab from './SocialSecurityOverviewTab.vue';
import SocialSecurity2Tab from './SocialSecurity2Tab.vue';
import MedicareOverviewTab from './MedicareOverviewTab.vue';
import IncomeTab from './IncomeTab.vue';
import RothConversionTab from './RothConversionTab.vue';
import WorksheetsTab from './WorksheetsTab.vue';
import ScenarioMetrics from './ScenarioMetrics.vue';
import NextStepsTab from './NextStepsTab.vue';
import Graph from '../components/Graph.vue';
import DisclosuresCard from '../components/DisclosuresCard.vue';

// Chart.js registration moved to Graph.vue to avoid conflicts

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

const token = localStorage.getItem('token')
const headers = { Authorization: `Bearer ${token}` }

export default {
  components: {
    FinancialOverviewTab,
    SocialSecurityOverviewTab,
    SocialSecurity2Tab,
    MedicareOverviewTab,
    IncomeTab,
    RothConversionTab,
    WorksheetsTab,
    ScenarioMetrics,
    NextStepsTab,
    Graph,
    DisclosuresCard
  },
  data() {
    return {
      scenario: null,
      scenarios: [],
      selectedScenarioId: null,
      client: null,
      scenarioResults: [],
      activeTab: this.$route.query.tab || 'overview', // Use route query param or default to overview
      isPdfMode: this.$route.query.pdf === 'true', // Check if we're in PDF generation mode
      // PDF generation tracking
      isGeneratingPDF: false,
      pdfGenerationMessage: '',
      // Async calculation tracking
      isCalculating: false,
      calculationProgress: 0,
      calculationMessage: '',
      currentTaskId: null,
      calculationStartTime: null,
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
        worksheets: false,
        overviewFinancial: false,
        overviewFlow: false
      },
      // Dropdown states for navigation
      scenarioDropdownOpen: false,
      navDropdownOpen: false,
      actionsDropdownOpen: false,
      preRetirementIncome: 0,
      availableYears: [],
      conversionStartYear: null,
      yearsToConvert: 0,
      rothGrowthRate: 0,
      assetDetails: [],
    };
  },
  async mounted() {
    // Check if we should set a specific tab from route query params
    if (this.$route.query.tab) {
      this.activeTab = this.$route.query.tab;
    }
    
    // If in PDF mode, hide sidebar and header
    if (this.isPdfMode) {
      document.body.classList.add('pdf-mode');
      // Add CSS to hide navigation elements
      const style = document.createElement('style');
      style.innerHTML = `
        .pdf-mode .navbar-vertical,
        .pdf-mode .navbar-vertical-aside,
        .pdf-mode .header,
        .pdf-mode .navbar,
        .pdf-mode aside,
        .pdf-mode nav {
          display: none !important;
        }
        .pdf-mode .content,
        .pdf-mode .main,
        .pdf-mode .container-fluid {
          margin-left: 0 !important;
          margin-top: 0 !important;
          padding-top: 20px !important;
        }
      `;
      document.head.appendChild(style);
    }
    
    this.initPlugins();
    this.initializeCircles();
    
    // Add click handler to close dropdowns when clicking outside
    document.addEventListener('click', this.handleClickOutside);
    
    // Load all scenario data in one batch to prevent rate limiting
    await this.loadAllScenarioData();
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    document.removeEventListener('click', this.handleClickOutside);
    
    // Clean up chart instances
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
  },
  methods: {
    ...mapActions(['fetchScenarioData']),
    
    // Dropdown toggle methods
    toggleScenarioDropdown() {
      this.scenarioDropdownOpen = !this.scenarioDropdownOpen;
      // Close other dropdowns
      this.navDropdownOpen = false;
      this.actionsDropdownOpen = false;
    },
    
    toggleNavDropdown() {
      this.navDropdownOpen = !this.navDropdownOpen;
      // Close other dropdowns
      this.scenarioDropdownOpen = false;
      this.actionsDropdownOpen = false;
    },
    
    toggleActionsDropdown() {
      this.actionsDropdownOpen = !this.actionsDropdownOpen;
      // Close other dropdowns
      this.scenarioDropdownOpen = false;
      this.navDropdownOpen = false;
    },
    
    // Get auth token from localStorage or cookies
    getAuthToken() {
      // First check localStorage
      let token = localStorage.getItem('token');
      if (token) return token;
      
      // Fallback to cookies (for PDF generation)
      const name = 'token=';
      const decodedCookie = decodeURIComponent(document.cookie);
      const ca = decodedCookie.split(';');
      for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
          return c.substring(name.length, c.length);
        }
      }
      return null;
    },
    
    // Close dropdowns when clicking outside
    closeAllDropdowns() {
      this.scenarioDropdownOpen = false;
      this.navDropdownOpen = false;
      this.actionsDropdownOpen = false;
    },
    
    // Batch load all scenario data to prevent rate limiting
    async loadAllScenarioData() {
      const clientId = this.$route.params.id;
      const scenarioId = this.$route.params.scenarioid;
      
      try {
        console.log('Loading client and scenario data...');
        
        // Get token from localStorage or cookies (for PDF mode)
        const token = this.getAuthToken();
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        
        // First, load client data to get scenarios
        const clientResponse = await axios.get(`${API_CONFIG.API_URL}/clients/${clientId}/`, { headers });
        this.client = clientResponse.data;
        this.scenarios = clientResponse.data.scenarios || [];
        this.scenario = this.scenarios.find(s => s.id === parseInt(scenarioId));
        
        if (!this.scenario) {
          console.error('Scenario not found');
          return;
        }
        
        this.selectedScenarioId = this.scenario.id;
        
        // Set localStorage for sidebar access
        localStorage.setItem('currentClientId', clientId);
        localStorage.setItem('currentScenarioId', this.scenario.id);
        
        console.log('Client Tax Status:', this.client?.tax_status);
        console.log('Selected Scenario:', this.scenario);
        
        // Now batch load scenario-specific data with a small delay to prevent rate limiting
        await this.batchLoadScenarioDetails();
        
      } catch (error) {
        console.error('Error loading client and scenario:', error);
      }
    },
    
    async batchLoadScenarioDetails() {
      const scenarioId = this.scenario?.id;
      if (!scenarioId) return;
      
      try {
        console.log('Batch loading scenario details with delay...');
        
        // Load scenario calculation data first
        this.fetchScenarioData();
        
        // Add small delays between API calls to prevent rate limiting burst
        setTimeout(() => {
          this.fetchAssetDetails();
        }, 100);
        
        setTimeout(() => {
          if (this.scenario?.id) {
            this.fetchScenarioDetails();
          }
        }, 200);
        
      } catch (error) {
        console.error('Error batch loading scenario details:', error);
      }
    },
    scrollToTop() {
      console.log('Forcing scroll to top');
      // The main scrollable container in the layout is .main-content
      const mainContent = document.querySelector('.main-content');
      if (mainContent) {
        console.log('Scrolling .main-content container to top');
        mainContent.scrollTop = 0;
        mainContent.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      }
      // Also try other containers as fallback
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
      document.documentElement.scrollTop = 0;
      document.body.scrollTop = 0;
    },
    navigateToTab(tab) {
      // Close dropdown after selection
      this.navDropdownOpen = false;
      // Navigate to the selected tab by updating the URL
      this.$router.push({
        name: 'ScenarioDetail',
        params: { 
          id: this.$route.params.id, 
          scenarioid: this.$route.params.scenarioid 
        },
        query: { tab: tab }
      });
    },
    switchToScenario(scenarioId) {
      // Close dropdown after selection
      this.scenarioDropdownOpen = false;
      // Switch to a different scenario while maintaining current tab
      this.$router.push({
        name: 'ScenarioDetail',
        params: { 
          id: this.$route.params.id, 
          scenarioid: scenarioId 
        },
        query: { tab: this.activeTab }
      });
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    },
    async handleScenarioUpdate(updateData) {
      // Handle scenario updates from Social Security 2 tab
      console.log('Updating scenario with Social Security 2 data:', updateData);
      
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No auth token found');
          return;
        }
        
        const response = await fetch(`${API_CONFIG.API_URL}/scenarios/${this.scenario.id}/update/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(updateData)
        });
        
        if (response.ok) {
          const updatedScenario = await response.json();
          console.log('Scenario updated successfully:', updatedScenario);
          
          // Update local scenario data
          Object.assign(this.scenario, updatedScenario);
          
          // Refresh scenario results to reflect the changes
          this.loadScenarioData();
          
          // Show success message
          this.$toast?.success?.('Social Security claiming strategy saved successfully!') || 
          console.log('Social Security claiming strategy saved successfully!');
          
        } else {
          const error = await response.json();
          console.error('Error updating scenario:', error);
          this.$toast?.error?.('Failed to save Social Security claiming strategy') || 
          console.error('Failed to save Social Security claiming strategy');
        }
      } catch (error) {
        console.error('Network error updating scenario:', error);
        this.$toast?.error?.('Network error while saving changes') || 
        console.error('Network error while saving changes');
      }
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
      // Only worksheets tab needs chart initialization from ScenarioDetail
      // Other tabs now handle their own charts via Graph component
      if (this.activeTab !== 'worksheets') {
        return;
      }
      
      this.$nextTick(() => {
        const ctx = document.getElementById('breakevenChart');
        console.log('Canvas Context:', ctx); // Log the canvas context
        if (ctx && this.scenarioResults.length) {
          if (this.chartInstance) {
            this.chartInstance.destroy();
          }

          // Only handle worksheets tab - other tabs use Graph component
          const datasets = Object.entries(this.benefitByAge).map(([age, benefit], i) => {
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
          });

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
                  title: {
                    display: true,
                    text: 'Year'
                  }
                },
                y: {
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
        const maxRetries = 20;
        let retryCount = 0;
        const tryInit = () => {
          const CirclesGlobal = window.Circles;
          if (CirclesGlobal && typeof CirclesGlobal.create === 'function') {
            document.querySelectorAll('.js-circle').forEach((el) => {
              if (!el.dataset.initialized) {
                if (el.id === 'circle-overview') {
                  // Handle overview financial circle
                  const totalTaxAndMedicare = this.overviewTotalTax + this.overviewTotalMedicare;
                  const percentage = this.overviewTotalGrossIncome > 0 ? 
                    Math.round((totalTaxAndMedicare / this.overviewTotalGrossIncome) * 100) : 0;
                  
                  CirclesGlobal.create({
                    id: el.id,
                    value: percentage,
                    maxValue: 100,
                    width: 20,
                    radius: 70,
                    text: function(value) { return value + '%'; },
                    colors: ['#f0f0f0', '#377dff'],
                    duration: 400,
                    wrpClass: 'circles-wrp',
                    textClass: 'circles-text',
                    styleWrapper: true,
                    styleText: true
                  });
                } else if (el.id === 'circle-financial') {
                  // Skip financial circle - let FinancialOverviewTab handle it
                  return;
                } else {
                  // Handle IRMAA circles
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
                }
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
        axios.get(`${API_CONFIG.API_URL}/clients/${clientId}/`, { headers })
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
    fetchScenarioData(useSync = false) {
      // Use async calculation by default, sync as fallback
      if (!useSync) {
        console.log('🎯 SCENARIO_DEBUG: Starting async calculation...');
        this.startAsyncCalculation();
        return;
      }
      
      // Synchronous calculation (fallback)
      const scenarioId = this.$route.params.scenarioid;
      
      // Clean up existing charts when switching scenarios
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
      
      axios.get(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/calculate/`, { headers })
        .then(response => {
          console.log('🎯 SCENARIO_DEBUG [SCENARIO_DETAIL]: API response length:', response.data?.length);
          if (response.data && response.data.length) {
            this.scenarioResults = response.data;
            console.log('🎯 SCENARIO_DEBUG [SCENARIO_DETAIL]: scenarioResults set, length:', this.scenarioResults.length);
            console.log('🎯 SCENARIO_DEBUG [SCENARIO_DETAIL]: filteredScenarioResults length:', this.filteredScenarioResults.length);

            // Load asset details first, then initialize store
            console.log('📊 Loading assets for scenario:', this.$route.params.scenarioid);
            const scenarioId = this.$route.params.scenarioid;
            const token = localStorage.getItem('token');
            const assetHeaders = token ? { Authorization: `Bearer ${token}` } : {};

            axios.get(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/assets/`, { headers: assetHeaders })
              .then(response => {
                this.assetDetails = response.data;
                console.log('📊 Asset Details loaded:', this.assetDetails.length, 'assets');

                // NOW initialize the store with all data
                console.log('📊 Initializing calculations store');
                const calculationsStore = useScenarioCalculationsStore();
                calculationsStore.initialize(
                  this.scenarioResults,
                  this.assetDetails,
                  this.scenario,
                  this.client
                );
                console.log('📊 Store initialized');
              })
              .catch(error => {
                console.error('📊 Error fetching asset details:', error);
              });

            // Re-initialize chart with new data
            this.initializeChartJS();

            // Calculate and update the percentage metrics
            this.updateScenarioPercentages();
          } else {
            console.log('🎯 SCENARIO_DEBUG: No data received from API');
          }
        })
        .catch(error => {
          console.error("Error loading scenario data:", error);
        });
    },
    
    fetchScenarioDetails() {
      const scenarioId = this.$route.params.scenarioid;
      if (!scenarioId || !this.scenario) {
        return;
      }
      
      console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: fetchScenarioDetails called for scenario:', scenarioId);
      
      axios.get(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/detail/`, { headers })
        .then(response => {
          console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: Detailed scenario data received:', response.data);
          console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: Income sources in response:', response.data?.income_sources?.length || 0);
          
          // Merge all scenario data, not just income_sources
          if (response.data) {
            // Merge all fields from the detailed response
            Object.keys(response.data).forEach(key => {
              if (this.$set) {
                this.$set(this.scenario, key, response.data[key]);
              } else {
                this.scenario[key] = response.data[key];
              }
            });
            
            console.log('🔍 SS_REDUCTION_DEBUG: SS Reduction fields after merge:', {
              reduction_2030_ss: this.scenario.reduction_2030_ss,
              ss_adjustment_year: this.scenario.ss_adjustment_year,
              ss_adjustment_direction: this.scenario.ss_adjustment_direction,
              ss_adjustment_type: this.scenario.ss_adjustment_type,
              ss_adjustment_amount: this.scenario.ss_adjustment_amount,
              primary_ss_claiming_age: this.scenario.primary_ss_claiming_age,
              spouse_ss_claiming_age: this.scenario.spouse_ss_claiming_age
            });
            
            console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: Updated scenario with all fields');
            
            // Log social security specific data
            const socialSecurityIncomes = this.scenario.income_sources?.filter(income => income.income_type === 'social_security');
            console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: Social Security income sources:', socialSecurityIncomes?.length || 0);
            if (socialSecurityIncomes?.length) {
              socialSecurityIncomes.forEach(ss => {
                console.log('🔍 SS2_DEBUG [SCENARIO_DETAIL]: SS Income - Owner:', ss.owned_by, 'Amount at FRA:', ss.amount_at_fra, 'Monthly Amount:', ss.monthly_amount);
              });
            }
          }
        })
        .catch(error => {
          console.error("🔍 SS2_DEBUG [SCENARIO_DETAIL]: Error loading detailed scenario data:", error);
        });
    },
    
    updateScenarioPercentages() {
      // Only proceed if we have scenario results
      if (!this.scenarioResults || !this.scenarioResults.length) return;
      
      const scenarioId = this.$route.params.scenarioid;
      
      // Calculate income vs cost percentage (federal tax + medicare / gross income)
      let totalGross = 0;
      let totalTax = 0;
      let totalMedicare = 0;
      let totalIrmaa = 0;
      
      this.filteredScenarioResults.forEach(row => {
        totalGross += parseFloat(row.gross_income || 0);
        totalTax += parseFloat(row.federal_tax || 0);
        totalMedicare += parseFloat(row.total_medicare || 0);
        totalIrmaa += parseFloat(row.irmaa_surcharge || 0);
      });
      
      // Calculate percentages
      const incomeVsCostPercent = totalGross > 0 ? Math.round(((totalTax + totalMedicare) / totalGross) * 100) : 0;
      const medicareIrmaaPercent = totalMedicare > 0 ? Math.round((totalIrmaa / totalMedicare) * 100) : 0;
      
      console.log('Calculated percentages:', {
        incomeVsCostPercent,
        medicareIrmaaPercent,
        totalGross,
        totalTax,
        totalMedicare,
        totalIrmaa
      });
      
      // Send update to backend
      axios.put(
        `${API_CONFIG.API_URL}/scenarios/${scenarioId}/update-percentages/`,
        {
          income_vs_cost_percent: incomeVsCostPercent,
          medicare_irmaa_percent: medicareIrmaaPercent
        },
        { headers }
      )
      .then(response => {
        console.log('Updated scenario percentages:', response.data);
      })
      .catch(error => {
        console.error('Error updating scenario percentages:', error);
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
      // Handle navigation dropdowns
      const dropdownElement = event.target.closest('.dropdown');
      if (!dropdownElement) {
        this.closeAllDropdowns();
      }
      
      // Handle tab section dropdowns
      const dropdowns = {
        financial: this.$refs.financialDropdown,
        socialSecurity: this.$refs.socialSecurityDropdown,
        medicare: this.$refs.medicareDropdown,
        worksheets: this.$refs.worksheetsDropdown
      };

      for (const [tab, dropdown] of Object.entries(dropdowns)) {
        if (dropdown) {
          if (!dropdown.contains(event.target) && this.isDropdownOpen[tab]) {
            this.isDropdownOpen[tab] = false;
          }
        }
      }
    },
    exportGraphAndDataToPDF() {
      console.log('Exporting graph and data to PDF...');
      const doc = new jsPDF();
      let canvasId, tableData;

      // Only worksheets tab is handled by ScenarioDetail export
      // Other tabs handle their own exports via Graph component
      if (this.activeTab === 'worksheets') {
        canvasId = 'breakevenChart';
        tableData = this.benefitByAge;
      } else {
        console.warn('Export not supported from ScenarioDetail for tab:', this.activeTab);
        return;
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
    async fetchAssetDetails() {
      console.log('🔥 fetchAssetDetails: Loading assets for scenario:', this.scenario?.id);

      if (!this.scenario?.id) {
        console.error('🔥 fetchAssetDetails: No scenario ID available');
        return;
      }

      try {
        const token = this.getAuthToken();
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const response = await axios.get(
          `${API_CONFIG.API_URL}/scenarios/${this.scenario.id}/assets/`,
          { headers }
        );

        this.assetDetails = response.data;
        console.log('🔥 fetchAssetDetails: Loaded', this.assetDetails.length, 'assets');
        console.log('🔥 fetchAssetDetails: Assets:', this.assetDetails);

        // Initialize the store if we have all data
        if (this.scenarioResults && this.scenarioResults.length > 0) {
          const calculationsStore = useScenarioCalculationsStore();
          calculationsStore.initialize(
            this.scenarioResults,
            this.assetDetails,
            this.scenario,
            this.client
          );
          console.log('🔥 fetchAssetDetails: Store initialized with assets');
        }
      } catch (error) {
        console.error('🔥 fetchAssetDetails: Error loading assets:', error);
      }
    },
    createScenario(type) {
      // Close dropdown after selection
      this.actionsDropdownOpen = false;
      const clientId = this.$route.params.id;
      console.log('🔄 createScenario called with type:', type);
      console.log('📍 Client ID:', clientId);
      
      if (type === 'scratch') {
        console.log('➡️ Navigating to create new scenario from scratch');
        this.$router.push({ name: 'ScenarioCreate', params: { id: clientId } });
      } else if (type === 'duplicate') {
        const scenarioId = this.$route.params.scenarioid;
        console.log('📋 Duplicating scenario ID:', scenarioId);
        console.log('➡️ Navigating to duplicate scenario page');
        this.$router.push({ 
          name: 'ScenarioCreate', 
          params: { id: clientId },
          query: { duplicate: scenarioId }
        });
      }
    },
    editScenario() {
      // Close dropdown after selection
      this.actionsDropdownOpen = false;
      const clientId = this.$route.params.id;
      const scenarioId = this.$route.params.scenarioid;
      this.$router.push({ 
        name: 'ScenarioCreate', 
        params: { id: clientId },
        query: { edit: scenarioId }
      });
    },
    async toggleScenarioSharing() {
      // Close dropdown after selection
      this.actionsDropdownOpen = false;
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No auth token found');
          return;
        }

        const newSharingState = !this.scenario.share_with_client;
        
        const response = await fetch(`${API_CONFIG.API_URL}/scenarios/${this.scenario.id}/toggle-sharing/`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            share_with_client: newSharingState
          })
        });

        if (response.ok) {
          const updatedScenario = await response.json();
          // Update local scenario data
          this.scenario.share_with_client = updatedScenario.share_with_client;
          
          // Show success message
          const message = newSharingState 
            ? 'Scenario shared to client portal successfully!' 
            : 'Scenario removed from client portal successfully!';
          
          this.$toast?.success?.(message) || alert(message);
        } else {
          const error = await response.json();
          console.error('Failed to toggle scenario sharing:', error);
          alert('Failed to update scenario sharing. Please try again.');
        }
      } catch (error) {
        console.error('Error toggling scenario sharing:', error);
        alert('An error occurred. Please try again.');
      }
    },
    
    async downloadScenarioPDF() {
      // Close dropdown after selection
      this.actionsDropdownOpen = false;
      
      try {
        const clientId = this.$route.params.id;
        const scenarioId = this.$route.params.scenarioid;
        const token = localStorage.getItem('token');
        
        if (!token) {
          this.$toast?.error?.('Please log in to download the report') || console.error('Not logged in');
          return;
        }
        
        // Start loading state
        this.isGeneratingPDF = true;
        this.pdfGenerationMessage = 'Generating Report';
        
        // Call backend API to generate PDF
        const response = await fetch(`${import.meta.env.VITE_API_URL}/scenarios/${scenarioId}/generate-pdf/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            client_id: clientId,
            tabs: ['overview', 'financial', 'socialSecurity', 'medicare']
          })
        });
        
        if (response.ok) {
          const blob = await response.blob();
          
          // Create download link
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `scenario_${scenarioId}_report_${new Date().toISOString().split('T')[0]}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          
          this.$toast?.success?.('PDF report downloaded successfully!');
        } else {
          const error = await response.text();
          console.error('Failed to generate PDF:', error);
          this.$toast?.error?.('Failed to generate PDF report. Please try again.') || console.error('PDF generation failed');
        }
      } catch (error) {
        console.error('Error generating PDF:', error);
        this.$toast?.error?.('An error occurred while generating the PDF. Please try again.') || console.error('PDF generation error');
      } finally {
        // Always hide loading state
        this.isGeneratingPDF = false;
        this.pdfGenerationMessage = '';
      }
    },
    
    // New async calculation methods
    async startAsyncCalculation() {
      const scenarioId = this.$route.params.scenarioid;
      
      try {
        this.isCalculating = true;
        this.calculationProgress = 0;
        this.calculationMessage = 'Starting calculation...';
        this.calculationStartTime = Date.now();
        
        // Clean up existing charts when starting new calculation
        if (this.chartInstance) {
          this.chartInstance.destroy();
          this.chartInstance = null;
        }
        
        // Start async calculation
        const response = await axios.post(`${API_CONFIG.API_URL}/scenarios/${scenarioId}/calculate-async/`, {}, { 
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          }
        });
        
        this.currentTaskId = response.data.task_id;
        this.calculationMessage = response.data.message;
        
        // Start polling for progress
        this.pollTaskProgress();
        
      } catch (error) {
        console.error('Error starting async calculation:', error);
        this.isCalculating = false;
        this.calculationMessage = 'Failed to start calculation';
        
        // Fallback to synchronous calculation
        console.log('Falling back to synchronous calculation...');
        this.fetchScenarioData(true);
      }
    },
    
    async pollTaskProgress() {
      if (!this.currentTaskId) return;
      
      try {
        const response = await axios.get(`${API_CONFIG.API_URL}/tasks/${this.currentTaskId}/status/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          }
        });
        
        const taskData = response.data;
        this.calculationProgress = taskData.progress || 0;
        this.calculationMessage = taskData.message || 'Processing...';
        
        if (taskData.status === 'SUCCESS') {
          // Calculation completed successfully
          this.scenarioResults = taskData.results || [];
          this.isCalculating = false;
          this.calculationProgress = 100;
          this.calculationMessage = 'Calculation completed successfully!';
          
          // Re-initialize chart with new data
          this.initializeChartJS();
          
          // Calculate and update the percentage metrics
          this.updateScenarioPercentages();
          
          console.log('🎯 ASYNC_DEBUG: Calculation completed, results:', this.scenarioResults.length);
          
        } else if (taskData.status === 'FAILURE') {
          // Calculation failed
          this.isCalculating = false;
          this.calculationMessage = `Calculation failed: ${taskData.error || 'Unknown error'}`;
          console.error('Async calculation failed:', taskData.error);
          
          // Fallback to synchronous calculation
          console.log('Falling back to synchronous calculation...');
          this.fetchScenarioData(true);
          
        } else if (taskData.status === 'PROGRESS') {
          // Still in progress, continue polling
          setTimeout(() => {
            this.pollTaskProgress();
          }, 1000); // Poll every second
          
        } else {
          // PENDING or other states, continue polling
          setTimeout(() => {
            this.pollTaskProgress();
          }, 2000); // Poll every 2 seconds for pending tasks
        }
        
      } catch (error) {
        console.error('Error polling task progress:', error);
        this.isCalculating = false;
        this.calculationMessage = 'Error checking calculation progress';
        
        // Fallback to synchronous calculation
        this.fetchScenarioData(true);
      }
    },
    
    async cancelCalculation() {
      if (!this.currentTaskId) return;
      
      try {
        await axios.delete(`${API_CONFIG.API_URL}/tasks/${this.currentTaskId}/cancel/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json',
          }
        });
        
        this.isCalculating = false;
        this.calculationProgress = 0;
        this.calculationMessage = 'Calculation cancelled';
        this.currentTaskId = null;
        
      } catch (error) {
        console.error('Error cancelling task:', error);
        this.calculationMessage = 'Error cancelling calculation';
      }
    },
    
    getCalculationTimeElapsed() {
      if (!this.calculationStartTime) return '';
      
      const elapsed = Math.floor((Date.now() - this.calculationStartTime) / 1000);
      if (elapsed < 60) {
        return `${elapsed}s`;
      } else {
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        return `${minutes}m ${seconds}s`;
      }
    }
  },
  computed: {
    isAdminUser() {
      const authStore = useAuthStore();
      return authStore.isAdminUser;
    },
    filteredScenarioResults() {
      const mortalityAge = Number(this.scenario?.mortality_age) || 90;
      const spouseMortalityAge = Number(this.scenario?.spouse_mortality_age) || 90;
      const isSingle = this.client?.tax_status?.toLowerCase() === 'single';
      const maxAge = isSingle ? mortalityAge : Math.max(mortalityAge, spouseMortalityAge);
      return this.scenarioResults.filter(row => {
        if (isSingle) {
          return row.primary_age <= mortalityAge;
        } else {
          return (row.primary_age <= maxAge || (row.spouse_age && row.spouse_age <= maxAge));
        }
      });
    },
    totalFederalTaxes() {
      return this.filteredScenarioResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0).toFixed(2);
    },
    totalMedicareCosts() {
      return this.filteredScenarioResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0).toFixed(2);
    },
    totalIrmaaSurcharge() {
      return parseFloat(this.filteredScenarioResults.reduce((total, row) => total + (parseFloat(row.irmaa_surcharge || 0)), 0).toFixed(2));
    },
    totalMedicareCost() {
      return parseFloat(this.filteredScenarioResults.reduce((total, row) => total + (parseFloat(row.total_medicare || 0)), 0).toFixed(2));
    },
    currentAge() {
      if (!this.client?.birthdate) return null;
      const birthDate = new Date(this.client.birthdate);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      return age;
    },
    spouseAge() {
      if (!this.client?.spouse?.birthdate) return null;
      const birthDate = new Date(this.client.spouse.birthdate);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      return age;
    },
    irmaaPercentage() {
      if (!this.totalMedicareCost) return 0;
      return Math.round((this.totalIrmaaSurcharge / this.totalMedicareCost) * 100);
    },
    irmaaColor() {
      const pct = this.irmaaPercentage;
      if (pct > 50) {
        return '#ff0000'; // Red
      } else if (pct > 25) {
        return '#ffa500'; // Orange
      } else if (pct > 15) {
        return '#ffff00'; // Yellow
      } else {
        return '#00ff00'; // Green
      }
    },
    overviewChartData() {
      if (!this.filteredScenarioResults || !this.filteredScenarioResults.length) {
        return { labels: [], datasets: [] };
      }

      const labels = this.filteredScenarioResults.map(row => row.year.toString());
      const datasets = [
        {
          type: 'line',
          label: 'Gross Income',
          data: this.filteredScenarioResults.map(row => parseFloat(row.gross_income) || 0),
          borderColor: '#4285f4',
          backgroundColor: 'transparent',
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: '#4285f4',
          order: 1,
          fill: false
        },
        {
          type: 'line',
          label: 'Net Income',
          data: this.filteredScenarioResults.map(row => {
            const gross = parseFloat(row.gross_income) || 0;
            const tax = parseFloat(row.federal_tax) || 0;
            const medicare = parseFloat(row.total_medicare) || 0;
            return gross - tax - medicare;
          }),
          borderColor: '#34a853',
          backgroundColor: 'transparent',
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: '#34a853',
          order: 1,
          fill: false
        },
        {
          type: 'bar',
          label: 'Federal Tax',
          data: this.filteredScenarioResults.map(row => parseFloat(row.federal_tax) || 0),
          backgroundColor: '#ea4335',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        },
        {
          type: 'bar',
          label: 'Medicare',
          data: this.filteredScenarioResults.map(row => parseFloat(row.total_medicare) || 0),
          backgroundColor: '#fbbc05',
          stack: 'Stack 0',
          yAxisID: 'y',
          order: 2
        }
      ];

      return { labels, datasets };
    },
    overviewChartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Year'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Amount ($)'
            },
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return '$' + value.toLocaleString();
              }
            }
          }
        },
        plugins: {
          legend: {
            display: true,
            position: 'bottom'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        interaction: {
          mode: 'index',
          intersect: false
        }
      };
    },
    overviewTotalGrossIncome() {
      return this.filteredScenarioResults.reduce((total, row) => total + parseFloat(row.gross_income || 0), 0);
    },
    overviewTotalTax() {
      return this.filteredScenarioResults.reduce((total, row) => total + parseFloat(row.federal_tax || 0), 0);
    },
    overviewTotalMedicare() {
      return this.filteredScenarioResults.reduce((total, row) => total + parseFloat(row.total_medicare || 0), 0);
    },
    overviewNetIncome() {
      return this.filteredScenarioResults.reduce((total, row) => {
        const gross = parseFloat(row.gross_income || 0);
        const tax = parseFloat(row.federal_tax || 0);
        const medicare = parseFloat(row.total_medicare || 0);
        return total + (gross - tax - medicare);
      }, 0);
    },
    medicareOutOfPocket() {
      // Calculate Medicare out-of-pocket as the aggregate of negative "Remaining SSI" amounts
      return this.filteredScenarioResults.reduce((total, row) => {
        // Calculate remaining SSI using the same logic as SocialSecurityOverviewTab
        const primarySSI = parseFloat(row.ss_income_primary_gross || 0);
        const spouseSSI = parseFloat(row.ss_income_spouse_gross || 0);
        const totalSSI = primarySSI + spouseSSI;
        const ssDecrease = parseFloat(row.ss_decrease_amount || 0);
        const medicare = parseFloat(row.total_medicare || 0);
        
        const remainingSSI = totalSSI - ssDecrease - medicare;
        
        // Only add negative amounts (when Medicare exceeds SSI)
        if (remainingSSI < 0) {
          total += Math.abs(remainingSSI);
        }
        
        return total;
      }, 0);
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
    activeTab(newVal, oldVal) {
      console.log('Active tab changed from', oldVal, 'to:', newVal);
      // Scroll to top when changing tabs
      if (oldVal && newVal !== oldVal) {
        this.$nextTick(() => {
          this.scrollToTop();
        });
      }
      // Only worksheets tab needs chart initialization from ScenarioDetail
      if (newVal === 'worksheets') {
        if (this.scenarioResults.length) {
          this.initializeChartJS();
        } else {
          this.fetchScenarioData();
        }
      }
    },
    // Watch for route query parameter changes
    '$route.query.tab': {
      handler(newTab, oldTab) {
        console.log('Route tab changed from', oldTab, 'to', newTab);
        if (newTab) {
          this.activeTab = newTab;
          // Scroll to top when navigating directly via URL/sidebar links
          if (oldTab && newTab !== oldTab) {
            this.$nextTick(() => {
              this.scrollToTop();
            });
          }
        }
      },
      immediate: true
    },
    '$route.params.scenarioid': {
      immediate: true,
      handler(newVal) {
        const scenarioId = parseInt(newVal);
        this.scenario = this.scenarios.find(s => s.id === scenarioId);
        this.selectedScenarioId = scenarioId;
        
        // Use batched loading to prevent rate limiting when switching scenarios
        if (this.scenarios.length > 0 && this.scenario?.id) {
          this.batchLoadScenarioDetails();
        }
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

.client-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.client-info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 600;
  color: #495057;
  min-width: 120px;
  text-align: left;
}

.info-value {
  font-weight: 500;
  color: #212529;
  text-align: right;
  flex: 1;
  margin-left: 15px;
}

/* Scenario Navigation Dropdown Styles */
#scenarioNavDropdown, #scenarioSwitchDropdown {
  min-width: 160px;
}

.dropdown-menu {
  min-width: 220px;
}

.dropdown-item.active {
  background-color: #007bff;
  color: white;
}

.dropdown-item i {
  width: 16px;
  text-align: center;
}

/* Responsive adjustments for smaller screens */
@media (max-width: 991px) {
  .col-lg-auto {
    margin-top: 1rem;
  }
}

@media (max-width: 768px) {
  .d-flex.align-items-center {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .d-flex.align-items-center > span:first-child {
    margin-bottom: 0.5rem;
  }
  
  .dropdown {
    margin-top: 0.25rem;
    width: 100%;
    margin-right: 0;
  }
  
  .text-muted {
    display: none; /* Hide dash on mobile */
  }
  
  #scenarioNavDropdown, #scenarioSwitchDropdown {
    width: 100%;
  }
  
  .col-lg-auto .d-flex {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }
  
  .col-lg-auto .d-flex .dropdown {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}

/* Fade transition for PDF generation overlay */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
