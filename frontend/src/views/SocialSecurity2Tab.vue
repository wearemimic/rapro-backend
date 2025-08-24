<template>
  <div class="social-security-2-container">
    <!-- Header Section -->
    <div class="ss-header mb-4">
      <div class="header-content">
        <div class="header-icon">
          <i class="bi bi-shield-check text-primary"></i>
        </div>
        <div class="header-text">
          <h4 class="mb-1">Social Security | When will I claim benefits and how does this affect my plan?</h4>
          <p class="mb-0 text-muted">
            If claiming age for 
            <span class="text-primary fw-bold">
              <i class="bi bi-person-fill"></i> {{ client?.first_name }} is {{ Math.round(primaryClaimingAge) }} ({{ primaryClaimingDate }})
            </span>
            <span v-if="hasSpouse">
              and for 
              <span class="text-info fw-bold">
                <i class="bi bi-person-fill"></i> {{ client?.spouse?.first_name || 'Spouse' }} is {{ Math.round(spouseClaimingAge) }} ({{ spouseClaimingDate }})
              </span>
            </span>
            lifetime benefits will be <span class="text-success fw-bold">{{ formatCurrency(totalLifetimeBenefits) }}</span>
            (<span class="text-muted">{{ benefitPercentage }}% of the maximum</span>)
          </p>
        </div>
      </div>
    </div>

    <!-- Main Layout: 3-column design -->
    <div class="row g-4">
      <!-- Left Sidebar: Smart Tools -->
      <div class="col-xl-3 col-lg-4">
        <div class="smart-tools-panel">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <!-- Life Expectancy Section -->
              <div class="tool-section mb-4">
                <h6 class="section-title">Life Expectancy</h6>
                <div class="life-expectancy-inputs">
                  <div class="expectancy-row mb-3">
                    <label class="form-label small">{{ client?.first_name || 'Primary' }}'s Life Expectancy</label>
                    <div class="input-group input-group-sm">
                      <span class="input-group-text"><i class="bi bi-person-fill text-primary"></i></span>
                      <input type="number" v-model="primaryLifeExpectancy" class="form-control" min="60" max="100" @input="updateCalculations">
                      <span class="input-group-text">{{ getPrimaryLifeExpectancyYear }}</span>
                    </div>
                  </div>
                  
                  <div class="expectancy-row mb-3" v-if="hasSpouse">
                    <label class="form-label small">{{ client?.spouse?.first_name || 'Spouse' }}'s Life Expectancy</label>
                    <div class="input-group input-group-sm">
                      <span class="input-group-text"><i class="bi bi-person-fill text-info"></i></span>
                      <input type="number" v-model="spouseLifeExpectancy" class="form-control" min="60" max="100" @input="updateCalculations">
                      <span class="input-group-text">{{ getSpouseLifeExpectancyYear }}</span>
                    </div>
                  </div>
                </div>
                <p class="small text-muted mb-0">No Stress Test or Interest Rate</p>
              </div>

              <!-- Individual Benefit Controls -->
              <div class="tool-section mb-4">
                <h6 class="section-title">{{ client?.first_name }}'s Monthly Benefit</h6>
                <div class="benefit-control">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="bi bi-gear"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="bi bi-printer"></i>
                    </button>
                  </div>
                  
                  <div class="age-slider-container mb-3">
                    <div class="slider-labels">
                      <span class="small">62</span>
                      <span class="small text-success">{{ Math.round(primaryClaimingAge) }}</span>
                      <span class="small">70</span>
                    </div>
                    <input 
                      type="range" 
                      v-model="primaryClaimingAge" 
                      class="form-range primary-slider" 
                      min="62" 
                      max="70" 
                      step="0.25"
                      @input="updateCalculations"
                    >
                    <div class="fra-marker" :style="`left: ${primaryFRAPosition}%`">
                      <small class="text-success">○</small>
                    </div>
                  </div>
                  
                  <div class="claiming-info">
                    <p class="small mb-1">Claiming at {{ Math.round(primaryClaimingAge) }} ({{ primaryClaimingDate }})</p>
                    <div class="benefit-amount">
                      <span class="small text-muted">Social Security Benefit:</span>
                      <span class="fw-bold text-primary">{{ formatCurrency(primaryMonthlyBenefit) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Spouse Benefit Controls -->
              <div class="tool-section mb-4" v-if="hasSpouse">
                <h6 class="section-title">{{ client?.spouse?.first_name || 'Spouse' }}'s Monthly Benefit</h6>
                <div class="benefit-control">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="bi bi-gear"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary">
                      <i class="bi bi-printer"></i>
                    </button>
                  </div>
                  
                  <div class="age-slider-container mb-3">
                    <div class="slider-labels">
                      <span class="small">62</span>
                      <span class="small text-success">{{ Math.round(spouseClaimingAge) }}</span>
                      <span class="small">70</span>
                    </div>
                    <input 
                      type="range" 
                      v-model="spouseClaimingAge" 
                      class="form-range spouse-slider" 
                      min="62" 
                      max="70" 
                      step="0.25"
                      @input="updateCalculations"
                    >
                    <div class="fra-marker" :style="`left: ${spouseFRAPosition}%`">
                      <small class="text-success">○</small>
                    </div>
                  </div>
                  
                  <div class="claiming-info">
                    <p class="small mb-1">Claiming at {{ Math.round(spouseClaimingAge) }} ({{ spouseClaimingDate }})</p>
                    <div class="benefit-amount mb-2">
                      <span class="small text-muted">Social Security Benefit:</span>
                      <span class="fw-bold text-info">{{ formatCurrency(spouseMonthlyBenefit) }}</span>
                    </div>
                    <div class="benefit-amount" v-if="spousalBenefitAnalysis">
                      <span class="small text-muted">Survival Benefit:</span>
                      <span class="fw-bold text-success">+{{ formatCurrency(spousalBenefitAnalysis.additionalAmount) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- IRMAA Stress Test -->
              <div class="tool-section mb-4">
                <div class="form-check form-switch">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="includeStressTest" 
                    id="stressTestSwitch"
                  >
                  <label class="form-check-label fw-bold" for="stressTestSwitch">
                    IRMAA Stress Test
                  </label>
                </div>
                <p class="small text-muted mb-3">Show Reduction in benefit due to IRMAA</p>
                
              </div>

            </div>

            <!-- Action Buttons -->
            <div class="card-footer bg-light border-0">
              <div class="d-flex gap-2">
                <button class="btn btn-outline-secondary btn-sm" @click="resetToDefaults">
                  <i class="bi bi-arrow-clockwise me-1"></i>Reset
                </button>
                <button class="btn btn-primary btn-sm flex-fill" @click="applyChanges">
                  Apply Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Chart Area -->
      <div class="col-xl-6 col-lg-8">
        <div class="chart-container">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-0">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">{{ activeChartTab === 'lifetime' ? 'Total Lifetime Benefits' : 'Monthly Retirement Paycheck' }}</h5>
                <div class="chart-tabs">
                  <div class="btn-group btn-group-sm" role="group">
                    <button 
                      type="button" 
                      class="btn" 
                      :class="activeChartTab === 'lifetime' ? 'btn-primary' : 'btn-outline-primary'"
                      @click="activeChartTab = 'lifetime'"
                    >
                      Lifetime Benefits
                    </button>
                    <button 
                      type="button" 
                      class="btn" 
                      :class="activeChartTab === 'paycheck' ? 'btn-primary' : 'btn-outline-primary'"
                      @click="activeChartTab = 'paycheck'"
                    >
                      Retirement Paycheck
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="card-body p-0 position-relative">
              <!-- Lifetime Benefits Chart -->
              <div v-show="activeChartTab === 'lifetime'" class="chart-wrapper">
                <canvas ref="lifetimeChart" class="chart-canvas"></canvas>
                <div class="chart-tooltip" v-if="chartTooltip" :style="tooltipStyle">
                  <div class="tooltip-content">
                    <div class="tooltip-title">{{ chartTooltip.title }}</div>
                    <div class="tooltip-values">
                      <div class="tooltip-value primary">
                        <i class="bi bi-person-fill text-primary"></i>
                        {{ chartTooltip.primary }}
                      </div>
                      <div class="tooltip-value spouse" v-if="chartTooltip.spouse">
                        <i class="bi bi-person-fill text-info"></i>
                        {{ chartTooltip.spouse }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Retirement Paycheck Heatmap -->
              <div v-show="activeChartTab === 'paycheck'" class="heatmap-wrapper">
                <div class="heatmap-container">
                  <div class="heatmap-grid">
                    <div 
                      v-for="cell in heatmapData" 
                      :key="`${cell.x}-${cell.y}`"
                      class="heatmap-cell" 
                      :class="getHeatmapCellClass(cell)"
                      :style="getHeatmapCellStyle(cell)"
                      @click="selectHeatmapCell(cell)"
                      @mouseover="showHeatmapTooltip(cell, $event)"
                      @mouseout="hideHeatmapTooltip"
                    >
                      <span v-if="isCurrentSelection(cell)" class="cell-value">
                        {{ formatCurrency(cell.v) }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Heatmap Axes -->
                  <div class="heatmap-axes">
                    <div class="x-axis">
                      <div class="axis-label">{{ client?.first_name }}'s Claiming Age</div>
                      <div class="axis-ticks">
                        <span v-for="age in [62, 63, 64, 65, 66, 67, 68, 69, 70]" :key="age">{{ age }}</span>
                      </div>
                    </div>
                    <div class="y-axis">
                      <div class="axis-label">{{ client?.spouse?.first_name || 'Spouse' }}'s Claiming Age</div>
                      <div class="axis-ticks">
                        <span v-for="age in [70, 69, 68, 67, 66, 65, 64, 63, 62]" :key="age">{{ age }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Chart Controls -->
              <div class="chart-controls">
                <div class="bottom-controls">
                  <div class="range-labels">
                    <span class="range-label">${{ formatNumber(chartRangeMin) }}</span>
                    <span class="range-label">${{ formatNumber(chartRangeMax) }}</span>
                  </div>
                  <button class="btn btn-primary btn-sm snap-button" @click="snapToOptimal">
                    <i class="bi bi-bullseye me-1"></i>Snap to Optimal
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Sidebar: Analysis -->
      <div class="col-xl-3 col-lg-4">
        <div class="analysis-panel">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <!-- Lifetime Benefits Summary -->
              <div class="analysis-section mb-4">
                <h6 class="section-title">Lifetime Benefits</h6>
                <div class="benefit-percentage text-muted small mb-1">
                  {{ benefitPercentage }}% of max (~{{ formatCurrency(maxLifetimeBenefits) }})
                </div>
                <div class="benefit-total display-6 text-primary fw-bold">
                  {{ formatCurrency(totalLifetimeBenefits) }}
                </div>
              </div>

              <!-- Break-Even Point -->
              <div class="analysis-section mb-4" v-if="breakEvenAnalysis">
                <h6 class="section-title">Break-Even Point</h6>
                <div class="break-even-info">
                  <div class="break-even-time">
                    <i class="bi bi-clock text-muted me-2"></i>
                    <span class="fw-bold">{{ breakEvenAnalysis.yearsToBreakEven }} years from now</span>
                  </div>
                  <div class="break-even-ages mt-2">
                    <div class="age-indicator">
                      <i class="bi bi-person-fill text-primary me-1"></i>
                      <span>{{ Math.round(breakEvenAnalysis.primaryAge) }}</span>
                      <i class="bi bi-info-circle text-muted ms-1"></i>
                    </div>
                    <div class="age-indicator" v-if="hasSpouse">
                      <i class="bi bi-person-fill text-info me-1"></i>
                      <span>{{ Math.round(breakEvenAnalysis.spouseAge) }}</span>
                      <i class="bi bi-info-circle text-muted ms-1"></i>
                    </div>
                  </div>
                  <div class="break-even-date text-muted small mt-1">
                    {{ breakEvenAnalysis.date }}
                  </div>
                </div>
              </div>

              <!-- Time before Claiming -->
              <div class="analysis-section mb-4">
                <h6 class="section-title">Time before Claiming</h6>
                
                <div class="claiming-timeline">
                  <div class="timeline-item">
                    <div class="timeline-header">
                      <span class="timeline-title">Partial Benefits</span>
                    </div>
                    <div class="timeline-content">
                      <div class="timeline-time">
                        <i class="bi bi-clock text-muted me-2"></i>
                        <span>{{ partialBenefitsTime }}</span>
                      </div>
                      <div class="timeline-amount">
                        <i class="bi bi-person-fill text-primary me-1"></i>
                        <span class="fw-bold">{{ formatCurrency(partialBenefitsAmount) }}/mo</span>
                      </div>
                    </div>
                  </div>

                  <div class="timeline-item">
                    <div class="timeline-header">
                      <span class="timeline-title">Full Benefits</span>
                    </div>
                    <div class="timeline-content">
                      <div class="timeline-time">
                        <i class="bi bi-clock text-muted me-2"></i>
                        <span>{{ fullBenefitsTime }}</span>
                      </div>
                      <div class="timeline-amount">
                        <i class="bi bi-people-fill text-primary me-1"></i>
                        <span class="fw-bold">{{ formatCurrency(fullBenefitsAmount) }}/mo</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Hide Tradeoffs Link -->
              <div class="text-center">
                <button class="btn btn-link text-primary text-decoration-none" @click="toggleTradeoffs">
                  <span v-if="!showTradeoffs">Show</span>
                  <span v-else>Hide</span>
                  Tradeoffs
                </button>
              </div>

              <!-- Tradeoffs Section -->
              <div v-if="showTradeoffs" class="analysis-section mt-4">
                <h6 class="section-title">Tradeoffs Analysis</h6>
                <div class="tradeoffs-content">
                  <div class="tradeoff-item mb-2">
                    <span class="tradeoff-label">Early Claiming:</span>
                    <span class="tradeoff-value text-danger">-{{ earlyClaimingPenalty }}%</span>
                  </div>
                  <div class="tradeoff-item mb-2">
                    <span class="tradeoff-label">Delayed Claiming:</span>
                    <span class="tradeoff-value text-success">+{{ delayedClaimingBonus }}%</span>
                  </div>
                  <div class="tradeoff-item">
                    <span class="tradeoff-label">Optimal Strategy:</span>
                    <span class="tradeoff-value text-primary">{{ optimalStrategy }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Disclosures Card -->
    <DisclosuresCard />
  </div>
</template>

<script>
import { socialSecurityService } from '@/services/socialSecurityService';
import Chart from 'chart.js/auto';
import DisclosuresCard from '@/components/DisclosuresCard.vue';

export default {
  name: 'SocialSecurity2Tab',
  components: {
    DisclosuresCard
  },
  props: {
    client: {
      type: Object,
      required: true
    },
    scenario: {
      type: Object,
      required: true
    },
    scenarioResults: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      // UI State
      activeChartTab: 'lifetime',
      showTradeoffs: false,
      
      // Claiming ages (in years)
      primaryClaimingAge: 67,
      spouseClaimingAge: 67,
      
      // Life expectancy
      primaryLifeExpectancy: null,
      spouseLifeExpectancy: null,
      
      // Advanced options
      includeStressTest: false,
      
      // Social Security data
      ssData: {
        primary: null,
        spouse: null
      },
      
      // Calculated values
      primaryMonthlyBenefit: 0,
      spouseMonthlyBenefit: 0,
      totalLifetimeBenefits: 0,
      maxLifetimeBenefits: 0,
      benefitPercentage: 0,
      spousalBenefitAnalysis: null,
      breakEvenAnalysis: null,
      
      // Chart data
      lifetimeChart: null,
      heatmapData: [],
      chartTooltip: null,
      tooltipStyle: {},
      chartRangeMin: 500000,
      chartRangeMax: 1000000,
      
      // Constants
      primaryFRA: 67,
      spouseFRA: 67,
      currentYear: new Date().getFullYear(),
      currentAge: 65,
      spouseCurrentAge: 63
    };
  },
  computed: {
    hasSpouse() {
      return this.client?.spouse || this.client?.tax_status?.toLowerCase() === 'married filing jointly';
    },
    primaryClaimingDate() {
      if (!this.client?.birthdate) return 'N/A';
      const birthDate = new Date(this.client.birthdate);
      const claimDate = new Date(birthDate);
      claimDate.setFullYear(claimDate.getFullYear() + Math.floor(this.primaryClaimingAge));
      return claimDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    },
    spouseClaimingDate() {
      if (!this.client?.spouse?.birthdate) return 'N/A';
      const birthDate = new Date(this.client.spouse.birthdate);
      const claimDate = new Date(birthDate);
      claimDate.setFullYear(claimDate.getFullYear() + Math.floor(this.spouseClaimingAge));
      return claimDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    },
    primaryFRAPosition() {
      return ((this.primaryFRA - 62) / 8) * 100;
    },
    spouseFRAPosition() {
      return ((this.spouseFRA - 62) / 8) * 100;
    },
    partialBenefitsTime() {
      // Calculate time until partial benefits begin
      return '1 year from now';
    },
    partialBenefitsAmount() {
      return this.primaryMonthlyBenefit * 0.8; // Example calculation
    },
    fullBenefitsTime() {
      return '4 years from now';
    },
    fullBenefitsAmount() {
      return this.primaryMonthlyBenefit + this.spouseMonthlyBenefit;
    },
    earlyClaimingPenalty() {
      return Math.round((1 - (this.primaryClaimingAge < this.primaryFRA ? 0.75 : 1)) * 100);
    },
    delayedClaimingBonus() {
      return Math.round((this.primaryClaimingAge > this.primaryFRA ? 0.32 : 0) * 100);
    },
    optimalStrategy() {
      return `Claim at ${this.primaryFRA}`;
    },
    getPrimaryLifeExpectancyYear() {
      if (!this.client?.birthdate || !this.primaryLifeExpectancy) return '';
      const birthDate = new Date(this.client.birthdate);
      const lifeExpectancyYear = birthDate.getFullYear() + this.primaryLifeExpectancy;
      return lifeExpectancyYear.toString();
    },
    getSpouseLifeExpectancyYear() {
      if (!this.client?.spouse?.birthdate || !this.spouseLifeExpectancy) return '';
      const birthDate = new Date(this.client.spouse.birthdate);
      const lifeExpectancyYear = birthDate.getFullYear() + this.spouseLifeExpectancy;
      return lifeExpectancyYear.toString();
    }
  },
  mounted() {
    console.log('🔄 SocialSecurity2Tab mounted - initializing...');
    this.initializeData();
    this.$nextTick(() => {
      this.initializeCharts();
    });
  },
  watch: {
    scenario: {
      handler() {
        if (this.$el) { // Only reinitialize if component is already mounted
          this.initializeData();
        }
      },
      deep: true
    }
  },
  beforeUnmount() {
    if (this.lifetimeChart) {
      this.lifetimeChart.destroy();
    }
  },
  methods: {
    toggleTradeoffs() {
      this.showTradeoffs = !this.showTradeoffs;
    },
    initializeData() {
      console.log('🔍 SS2_DEBUG: initializeData called');
      console.log('🔍 SS2_DEBUG: scenario in initializeData:', this.scenario?.id);
      console.log('🔍 SS2_DEBUG: scenario.income_sources in initializeData:', this.scenario?.income_sources);
      
      // Set life expectancy from scenario
      if (this.scenario?.mortality_age) {
        this.primaryLifeExpectancy = Number(this.scenario.mortality_age);
      } else {
        // Default to 85 if not set
        this.primaryLifeExpectancy = 85;
      }
      
      if (this.hasSpouse && this.scenario?.spouse_mortality_age) {
        this.spouseLifeExpectancy = Number(this.scenario.spouse_mortality_age);
      } else if (this.hasSpouse) {
        // Default to 85 if not set
        this.spouseLifeExpectancy = 85;
      }
      
      // Extract Social Security data first
      this.extractSocialSecurityData();
      
      // Set FRA and default claiming ages from Social Security data
      if (this.ssData.primary) {
        // Set FRA from Social Security data if available
        if (this.ssData.primary.startAge) {
          this.primaryFRA = this.ssData.primary.startAge;
          // Default claiming age to FRA unless already saved
          if (!this.scenario?.primary_ss_claiming_age) {
            this.primaryClaimingAge = this.primaryFRA;
          }
        }
      }
      
      if (this.hasSpouse && this.ssData.spouse) {
        if (this.ssData.spouse.startAge) {
          this.spouseFRA = this.ssData.spouse.startAge;
          // Default claiming age to FRA unless already saved
          if (!this.scenario?.spouse_ss_claiming_age) {
            this.spouseClaimingAge = this.spouseFRA;
          }
        }
      }
      
      // Load saved settings (override defaults if they exist)
      if (this.scenario?.primary_ss_claiming_age) {
        this.primaryClaimingAge = this.scenario.primary_ss_claiming_age;
      }
      
      if (this.scenario?.spouse_ss_claiming_age) {
        this.spouseClaimingAge = this.scenario.spouse_ss_claiming_age;
      }
      
      // Calculate initial benefits
      this.updateCalculations();
    },
    extractSocialSecurityData() {
      console.log('🔍 SS2_DEBUG: extractSocialSecurityData called');
      console.log('🔍 SS2_DEBUG: scenario.income_sources:', this.scenario?.income_sources);
      
      if (!this.scenario?.income_sources) {
        console.log('🔍 SS2_DEBUG: No income_sources, using fallback data');
        // Use fallback data for demonstration purposes
        this.ssData.primary = {
          amountAtFRA: 2800, // Sample benefit amount at FRA
          startAge: 67,      // Full Retirement Age
          endAge: 100,
          ownedBy: 'primary',
          cola: 0.02
        };
        
        if (this.hasSpouse) {
          this.ssData.spouse = {
            amountAtFRA: 2200, // Sample spouse benefit amount at FRA
            startAge: 67,      // Full Retirement Age
            endAge: 100,
            ownedBy: 'spouse',
            cola: 0.02
          };
        }
        return;
      }
      
      const ssIncomeSources = this.scenario.income_sources.filter(income => 
        income.income_type === 'Social Security' || income.income_type === 'social_security'
      );
      
      console.log('🔍 SS2_DEBUG: Found SS income sources:', ssIncomeSources);
      
      ssIncomeSources.forEach(income => {
        console.log('🔍 SS2_DEBUG: Processing SS income:', income);
        console.log('🔍 SS2_DEBUG: amount_at_fra:', income.amount_at_fra);
        console.log('🔍 SS2_DEBUG: monthly_amount:', income.monthly_amount);
        
        const data = {
          amountAtFRA: parseFloat(income.amount_at_fra || income.monthly_amount || 2800),
          startAge: parseInt(income.age_to_begin_withdrawal) || 67,
          endAge: parseInt(income.age_to_end_withdrawal) || 100,
          ownedBy: income.owned_by,
          cola: parseFloat(income.cola) || 0.02
        };
        
        console.log('🔍 SS2_DEBUG: Extracted SS data:', data);
        
        if (income.owned_by === 'primary') {
          this.ssData.primary = data;
        } else if (income.owned_by === 'spouse') {
          this.ssData.spouse = data;
        }
      });
      
      // Ensure we have at least primary data
      if (!this.ssData.primary) {
        this.ssData.primary = {
          amountAtFRA: 2800,
          startAge: 67,
          endAge: 100,
          ownedBy: 'primary',
          cola: 0.02
        };
      }
    },
    updateCalculations() {
      this.calculateMonthlyBenefits();
      this.calculateLifetimeBenefits();
      this.calculateBreakEvenAnalysis();
      this.generateHeatmapData();
      this.updateCharts();
    },
    calculateMonthlyBenefits() {
      if (this.ssData.primary) {
        this.primaryMonthlyBenefit = socialSecurityService.calculateBenefit(
          this.ssData.primary.amountAtFRA,
          this.primaryClaimingAge,
          this.primaryFRA
        );
      }
      
      if (this.hasSpouse && this.ssData.spouse) {
        this.spouseMonthlyBenefit = socialSecurityService.calculateBenefit(
          this.ssData.spouse.amountAtFRA,
          this.spouseClaimingAge,
          this.spouseFRA
        );
        
        this.spousalBenefitAnalysis = socialSecurityService.calculateSpousalBenefits(
          this.ssData.primary, 
          this.ssData.spouse, 
          this.spouseClaimingAge
        );
      }
    },
    calculateLifetimeBenefits() {
      const primaryLifetime = this.calculateLifetimeBenefitsForPerson(
        this.primaryMonthlyBenefit, 
        this.primaryClaimingAge, 
        this.primaryLifeExpectancy
      );
      
      const spouseLifetime = this.hasSpouse ? this.calculateLifetimeBenefitsForPerson(
        this.spouseMonthlyBenefit, 
        this.spouseClaimingAge, 
        this.spouseLifeExpectancy
      ) : 0;
      
      this.totalLifetimeBenefits = primaryLifetime + spouseLifetime;
      
      // Calculate optimal for percentage
      if (this.ssData.primary) {
        const optimalAnalysis = socialSecurityService.calculateOptimalStrategy(
          this.ssData,
          {
            primary: this.primaryLifeExpectancy,
            spouse: this.spouseLifeExpectancy
          }
        );
        
        if (optimalAnalysis?.optimal) {
          this.maxLifetimeBenefits = optimalAnalysis.optimal.totalLifetimeBenefits;
          this.benefitPercentage = Math.round((this.totalLifetimeBenefits / this.maxLifetimeBenefits) * 100);
        }
      }
    },
    calculateLifetimeBenefitsForPerson(monthlyBenefit, claimingAge, lifeExpectancy) {
      const yearsOfBenefits = Math.max(0, lifeExpectancy - claimingAge);
      return monthlyBenefit * 12 * yearsOfBenefits;
    },
    calculateBreakEvenAnalysis() {
      if (!this.ssData.primary) return;
      
      this.breakEvenAnalysis = socialSecurityService.calculateBreakEvenAge(
        this.ssData.primary.amountAtFRA,
        Math.min(this.primaryClaimingAge, this.primaryFRA),
        Math.max(this.primaryClaimingAge, this.primaryFRA)
      );
      
      if (this.breakEvenAnalysis) {
        this.breakEvenAnalysis.primaryAge = this.currentAge + this.breakEvenAnalysis.yearsToBreakEven;
        this.breakEvenAnalysis.spouseAge = this.spouseCurrentAge + this.breakEvenAnalysis.yearsToBreakEven;
        this.breakEvenAnalysis.date = new Date(this.currentYear + this.breakEvenAnalysis.yearsToBreakEven, 2).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      }
    },
    generateHeatmapData() {
      if (!this.hasSpouse || !this.ssData.primary || !this.ssData.spouse) return;
      
      this.heatmapData = socialSecurityService.generateCouplesHeatmapData(this.ssData) || [];
    },
    initializeCharts() {
      this.initializeLifetimeChart();
    },
    initializeLifetimeChart() {
      const canvas = this.$refs.lifetimeChart;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      
      // Generate chart data
      const chartData = this.generateLifetimeChartData();
      
      this.lifetimeChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              enabled: false,
              external: this.handleChartTooltip
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: `${this.client?.first_name}'s Claiming Age`
              },
              min: 62,
              max: 70
            },
            y: {
              title: {
                display: true,
                text: 'Total Lifetime Benefits ($)'
              },
              ticks: {
                callback: function(value) {
                  return '$' + (value / 1000) + 'K';
                }
              }
            }
          },
          elements: {
            point: {
              radius: 6,
              hoverRadius: 8
            }
          }
        }
      });
    },
    generateLifetimeChartData() {
      // Generate data points for the lifetime benefits chart
      const ages = [];
      const benefits = [];
      
      for (let age = 62; age <= 70; age += 0.5) {
        ages.push(age);
        
        const monthlyBenefit = socialSecurityService.calculateBenefit(
          this.ssData.primary?.amountAtFRA || 2000,
          age,
          this.primaryFRA
        );
        
        const lifetimeBenefit = this.calculateLifetimeBenefitsForPerson(
          monthlyBenefit,
          age,
          this.primaryLifeExpectancy
        );
        
        benefits.push(lifetimeBenefit);
      }
      
      return {
        labels: ages,
        datasets: [{
          label: 'Lifetime Benefits',
          data: benefits,
          borderColor: '#007bff',
          backgroundColor: 'rgba(0, 123, 255, 0.1)',
          fill: true,
          tension: 0.4
        }]
      };
    },
    updateCharts() {
      if (this.lifetimeChart) {
        const chartData = this.generateLifetimeChartData();
        this.lifetimeChart.data = chartData;
        this.lifetimeChart.update();
      }
    },
    handleChartTooltip(context) {
      // Custom tooltip handling for charts
      const tooltip = context.tooltip;
      
      if (tooltip.opacity === 0) {
        this.chartTooltip = null;
        return;
      }
      
      this.chartTooltip = {
        title: `Age ${tooltip.dataPoints[0].label}`,
        primary: this.formatCurrency(tooltip.dataPoints[0].raw),
        spouse: this.hasSpouse ? this.formatCurrency(tooltip.dataPoints[0].raw * 0.6) : null
      };
      
      this.tooltipStyle = {
        left: tooltip.caretX + 'px',
        top: tooltip.caretY + 'px',
        opacity: 1
      };
    },
    getHeatmapCellClass(cell) {
      const intensity = (cell.v - this.chartRangeMin) / (this.chartRangeMax - this.chartRangeMin);
      if (intensity > 0.8) return 'intensity-5';
      if (intensity > 0.6) return 'intensity-4';
      if (intensity > 0.4) return 'intensity-3';
      if (intensity > 0.2) return 'intensity-2';
      return 'intensity-1';
    },
    getHeatmapCellStyle(cell) {
      const intensity = (cell.v - this.chartRangeMin) / (this.chartRangeMax - this.chartRangeMin);
      const opacity = Math.max(0.1, Math.min(1, intensity));
      return {
        backgroundColor: `rgba(0, 123, 255, ${opacity})`
      };
    },
    isCurrentSelection(cell) {
      return Math.round(cell.x) === Math.round(this.primaryClaimingAge) && 
             Math.round(cell.y) === Math.round(this.spouseClaimingAge);
    },
    selectHeatmapCell(cell) {
      this.primaryClaimingAge = cell.x;
      this.spouseClaimingAge = cell.y;
      this.updateCalculations();
    },
    showHeatmapTooltip(cell, event) {
      // Show tooltip for heatmap cells
    },
    hideHeatmapTooltip() {
      // Hide heatmap tooltip
    },
    snapToOptimal() {
      if (!this.ssData.primary) return;
      
      const optimalAnalysis = socialSecurityService.calculateOptimalStrategy(
        this.ssData,
        {
          primary: this.primaryLifeExpectancy,
          spouse: this.spouseLifeExpectancy
        }
      );
      
      if (optimalAnalysis?.optimal) {
        this.primaryClaimingAge = optimalAnalysis.optimal.primaryAge;
        if (this.hasSpouse) {
          this.spouseClaimingAge = optimalAnalysis.optimal.spouseAge;
        }
        this.updateCalculations();
      }
    },
    resetToDefaults() {
      this.primaryClaimingAge = this.primaryFRA;
      this.spouseClaimingAge = this.spouseFRA;
      
      if (this.scenario?.mortality_age) {
        this.primaryLifeExpectancy = Number(this.scenario.mortality_age);
      }
      
      if (this.scenario?.spouse_mortality_age) {
        this.spouseLifeExpectancy = Number(this.scenario.spouse_mortality_age);
      }
      
      this.includeStressTest = false;
      this.updateCalculations();
    },
    applyChanges() {
      this.$emit('update-scenario', {
        primary_ss_claiming_age: this.primaryClaimingAge,
        spouse_ss_claiming_age: this.spouseClaimingAge,
        ss_include_irmaa: this.includeStressTest
      });
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    },
    formatNumber(value) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    }
  }
};
</script>

<style scoped>
.social-security-2-container {
  padding: 0;
  background: #f8f9fa;
  min-height: 100vh;
}

/* Header Styles */
.ss-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  padding: 1.5rem;
  margin: 0;
}

.header-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.header-icon {
  font-size: 2rem;
  color: #007bff;
}

.header-text h4 {
  color: #495057;
  font-weight: 600;
}

/* Smart Tools Panel */
.smart-tools-panel .card {
  background: white;
}

.tool-section {
  border-bottom: 1px solid #f1f3f4;
  padding-bottom: 1rem;
}

.tool-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-title {
  color: #495057;
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

/* Life Expectancy Controls */
.life-expectancy-inputs .input-group-text {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  font-size: 0.8rem;
}

/* Benefit Controls */
.benefit-control {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
}

.age-slider-container {
  position: relative;
  margin: 1rem 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.form-range {
  width: 100%;
  margin: 0.5rem 0;
}

.primary-slider::-webkit-slider-thumb {
  background: #007bff;
}

.spouse-slider::-webkit-slider-thumb {
  background: #17a2b8;
}

.fra-marker {
  position: absolute;
  bottom: -5px;
  transform: translateX(-50%);
  font-size: 1.2rem;
  color: #28a745;
}

.claiming-info {
  background: white;
  border-radius: 6px;
  padding: 0.75rem;
}

.benefit-amount {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Chart Container */
.chart-container {
  height: 600px;
}

.chart-wrapper, .heatmap-wrapper {
  height: 500px;
  position: relative;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Chart Tooltip */
.chart-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  pointer-events: none;
  z-index: 1000;
}

.tooltip-content {
  min-width: 120px;
}

.tooltip-title {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.tooltip-value {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.125rem;
}

/* Heatmap Styles */
.heatmap-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(9, 1fr);
  grid-template-rows: repeat(9, 1fr);
  gap: 2px;
  flex: 1;
  padding: 2rem 2rem 4rem 4rem;
}

.heatmap-cell {
  background: #e3f2fd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
}

.heatmap-cell:hover {
  transform: scale(1.05);
  z-index: 10;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.heatmap-cell.intensity-1 { background: rgba(0, 123, 255, 0.2); }
.heatmap-cell.intensity-2 { background: rgba(0, 123, 255, 0.4); }
.heatmap-cell.intensity-3 { background: rgba(0, 123, 255, 0.6); }
.heatmap-cell.intensity-4 { background: rgba(0, 123, 255, 0.8); }
.heatmap-cell.intensity-5 { background: rgba(0, 123, 255, 1.0); }

.heatmap-axes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.x-axis {
  position: absolute;
  bottom: 0;
  left: 4rem;
  right: 2rem;
  height: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.y-axis {
  position: absolute;
  left: 0;
  top: 2rem;
  bottom: 4rem;
  width: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transform: rotate(-90deg);
}

.axis-label {
  font-weight: bold;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.axis-ticks {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 0.7rem;
  color: #6c757d;
}

/* Chart Controls */
.chart-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem;
  border-top: 1px solid #e9ecef;
}

.bottom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.range-labels {
  display: flex;
  gap: 2rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.snap-button {
  border-radius: 20px;
  padding: 0.5rem 1.5rem;
  font-weight: 600;
}

/* Analysis Panel */
.analysis-panel .card {
  background: white;
}

.analysis-section {
  border-bottom: 1px solid #f1f3f4;
  padding-bottom: 1rem;
}

.analysis-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.benefit-percentage {
  font-size: 0.8rem;
}

.benefit-total {
  font-size: 2.5rem !important;
  line-height: 1;
}

/* Break-Even Analysis */
.break-even-info {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 0.75rem;
}

.break-even-time {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.break-even-ages {
  display: flex;
  gap: 1rem;
}

.age-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9rem;
}

/* Timeline */
.claiming-timeline {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 0.75rem;
}

.timeline-item {
  margin-bottom: 1rem;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-header {
  margin-bottom: 0.25rem;
}

.timeline-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: #495057;
}

.timeline-content {
  padding-left: 1rem;
}

.timeline-time, .timeline-amount {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
}

/* Tradeoffs */
.tradeoffs-content {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 0.75rem;
}

.tradeoff-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.tradeoff-label {
  color: #6c757d;
}

.tradeoff-value {
  font-weight: bold;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .heatmap-grid {
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(7, 1fr);
  }
  
  .chart-container {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .social-security-2-container {
    padding: 0.5rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .benefit-total {
    font-size: 2rem !important;
  }
}
</style>