<template>
  <div>
    <!-- Row for Graph and Insights -->
    <div class="row mb-3 mb-lg-5">
      <!-- Graph Card (2/3 width) -->
      <div class="col-lg-8">
        <div class="card h-100">
          <div class="card-body">
            <div style="height: 300px">
              <Graph 
                :data="chartData" 
                :options="chartOptions"
                :height="300"
                type="line"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- Insights Card (1/3 width) -->
      <div class="col-lg-4">
        <div class="card h-100">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">Social Security Insights</h5>
            <div class="insights-content flex-grow-1" style="overflow-y: auto; max-height: 250px;">
              
              <!-- Primary Claiming Strategy -->
              <div class="insight-item mb-3">
                <div class="d-flex align-items-center mb-2">
                  <i class="bi bi-person-fill text-primary me-2"></i>
                  <strong>{{ client?.first_name || 'Primary' }} Benefits</strong>
                </div>
                <div class="insight-details">
                  <p class="mb-1 small">
                    <strong>Claiming Age:</strong> {{ primaryClaimingAge }}
                    <span v-if="primaryClaimingAge < primaryFRA" class="text-warning ms-1">(Early)</span>
                    <span v-else-if="primaryClaimingAge > primaryFRA" class="text-success ms-1">(Delayed)</span>
                    <span v-else class="text-info ms-1">(At FRA)</span>
                  </p>
                  <p class="mb-1 small">
                    <strong>Full Retirement Age:</strong> {{ primaryFRA }}
                  </p>
                  <p class="mb-1 small">
                    <strong>Monthly Benefit:</strong> {{ formatCurrency(primaryMonthlyBenefit) }}
                  </p>
                </div>
              </div>

              <!-- Spouse Claiming Strategy (if applicable) -->
              <div v-if="hasSpouse" class="insight-item mb-3">
                <div class="d-flex align-items-center mb-2">
                  <i class="bi bi-person-fill text-info me-2"></i>
                  <strong>{{ client?.spouse?.first_name || 'Spouse' }} Benefits</strong>
                </div>
                <div class="insight-details">
                  <p class="mb-1 small">
                    <strong>Claiming Age:</strong> {{ spouseClaimingAge }}
                    <span v-if="spouseClaimingAge < spouseFRA" class="text-warning ms-1">(Early)</span>
                    <span v-else-if="spouseClaimingAge > spouseFRA" class="text-success ms-1">(Delayed)</span>
                    <span v-else class="text-info ms-1">(At FRA)</span>
                  </p>
                  <p class="mb-1 small">
                    <strong>Full Retirement Age:</strong> {{ spouseFRA }}
                  </p>
                  <p class="mb-1 small">
                    <strong>Monthly Benefit:</strong> {{ formatCurrency(spouseMonthlyBenefit) }}
                  </p>
                </div>
              </div>

              <!-- SS Reduction Information (if applicable) -->
              <div v-if="hasSocialSecurityReduction" class="insight-item mb-3">
                <div class="d-flex align-items-center mb-2">
                  <i class="bi bi-exclamation-triangle text-warning me-2"></i>
                  <strong class="text-warning">SS Benefit Reduction</strong>
                </div>
                <div class="insight-details">
                  <p class="mb-1 small">
                    <strong>Year:</strong> {{ reductionYear }}
                  </p>
                  <p class="mb-1 small">
                    <strong>Reduction:</strong> 
                    <span v-if="reductionType === 'percentage'">
                      {{ reductionPercentage }}%
                    </span>
                    <span v-else>
                      {{ formatCurrency(reductionPercentage) }}
                    </span>
                  </p>
                  <p class="mb-0 small text-muted">
                    Applied as {{ reductionType === 'percentage' ? 'percentage reduction' : 'fixed dollar reduction' }}
                  </p>
                </div>
              </div>

              <!-- Strategy Summary -->
              <div class="insight-item">
                <div class="d-flex align-items-center mb-2">
                  <i class="bi bi-lightbulb text-success me-2"></i>
                  <strong>Strategy Impact</strong>
                </div>
                <div class="insight-details">
                  <p class="mb-1 small" v-if="isOptimalStrategy">
                    <span class="text-success">✓ Optimized claiming strategy</span>
                  </p>
                  <p class="mb-1 small" v-else>
                    <span class="text-warning">⚠ Consider reviewing claiming strategy</span>
                  </p>
                  <p class="mb-0 small text-muted">
                    Combined monthly: {{ formatCurrency(totalMonthlyBenefit) }}
                  </p>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Row for Graph and Insights -->
    <!-- Card for Table -->
    <div class="card mb-3 mb-lg-5">
      <div class="card-header">
        <h4 class="card-header-title">Social Security Overview Table</h4>
      </div>
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="thead-light">
              <tr>
                <th>Year</th>
                <th>Primary Age</th>
                <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse Age</th>
                <th>Primary SSI Benefit</th>
                <th v-if="client?.tax_status?.toLowerCase() !== 'single'">Spouse SSI Benefit</th>
                <th v-if="hasSsDecrease">SS Decrease</th>
                <th>Total Medicare</th>
                <th>SSI Taxed</th>
                <th>Remaining SSI</th>
                <th>Indicators</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in filteredResults" :key="row.year" :class="{ 'irmaa-bracket-row': isIrmaaBracketHit(row, idx) }">
                <td>{{ row.year }}</td>
                <td v-if="row.primary_age <= (Number(mortalityAge) || 90)">{{ row.primary_age }}</td>
                <td v-else></td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single' && row.spouse_age <= (Number(spouseMortalityAge) || 90)">{{ row.spouse_age }}</td>
                <td v-else-if="client?.tax_status?.toLowerCase() !== 'single'"></td>
                <td>
                  ${{ parseFloat(row.ss_income_primary_gross || 0).toFixed(2) }}
                </td>
                <td v-if="client?.tax_status?.toLowerCase() !== 'single'">
                  ${{ parseFloat(row.ss_income_spouse_gross || 0).toFixed(2) }}
                </td>
                <td v-if="hasSsDecrease" class="text-danger">
                  ${{ getSsDecreaseAmount(row).toFixed(2) }}
                </td>
                <td style="position: relative;">
                  ${{ parseFloat(row.total_medicare || 0).toFixed(2) }}
                  <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon" @click.stop="toggleIrmaaTooltip(idx)">
                    ℹ️
                  </span>
                  <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                    IRMAA Bracket: {{ getIrmaaBracketLabel(row) }}
                  </div>
                </td>
                <td>${{ parseFloat(row.ssi_taxed || 0).toFixed(2) }}</td>
                <td :class="{ 'cell-negative': getRemainingSSI(row) < 0 }">
                  ${{ getRemainingSSI(row).toFixed(2) }}
                </td>
                <td style="position: relative; text-align: center;">
                  <span v-if="row.ss_decrease_applied" class="ss-decrease-icon" @click.stop="toggleSsDecreaseTooltip(idx)" title="Social Security Decrease">
                    📉
                  </span>
                  <span v-if="isIrmaaBracketHit(row, idx)" class="irmaa-info-icon-table" @click.stop="toggleIrmaaTooltip(idx)" title="IRMAA Information" :style="{ marginLeft: row.ss_decrease_applied ? '5px' : '0' }">
                    ℹ️
                  </span>
                  <div v-if="openIrmaaTooltipIdx === idx" class="irmaa-popover">
                    {{ getIrmaaBracketLabel(row) }}
                  </div>
                  <div v-if="openSsDecreaseTooltipIdx === idx" class="ss-decrease-popover">
                    Social Security {{ reductionPercentage }}% reduction applied starting {{ row.year }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <!-- End Card for Table -->
    
    <!-- Disclosures Card -->
    <DisclosuresCard />
  </div>
</template>

<script>
import { jsPDF } from 'jspdf';
import { applyPlugin } from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import Graph from '../components/Graph.vue';
import DisclosuresCard from '../components/DisclosuresCard.vue';

// Apply the plugin to jsPDF
applyPlugin(jsPDF);

const IRMAA_THRESHOLDS = {
  'single': [
    106000, 133000, 167000, 200000, 500000
  ],
  'married filing jointly': [
    212000, 266000, 334000, 400000, 750000
  ],
  'married filing separately': [
    106000, 394000
  ]
};
const IRMAA_LABELS = {
  'single': [
    '≤ $106,000',
    '$106,001 – $133,000',
    '$133,001 – $167,000',
    '$167,001 – $200,000',
    '$200,001 – $500,000',
    '>$500,000'
  ],
  'married filing jointly': [
    '≤ $212,000',
    '$212,001 – $266,000',
    '$266,001 – $334,000',
    '$334,001 – $400,000',
    '$400,001 – $750,000',
    '>$750,000'
  ],
  'married filing separately': [
    '≤ $106,000',
    '$106,001 – $394,000',
    '>$394,000'
  ]
};

export default {
  components: {
    Graph,
    DisclosuresCard
  },
  props: {
    scenario: {
      type: Object,
      required: true
    },
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
      },
      openIrmaaTooltipIdx: null,
      openSsDecreaseTooltipIdx: null
    };
  },
  watch: {
    scenario: {
      handler(newScenario) {
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Scenario prop changed:', newScenario);
        if (newScenario) {
          this.logBenefitData();
        }
      },
      immediate: true
    },
    scenarioResults: {
      handler(newResults) {
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Scenario Results prop changed:', newResults?.length, 'items');
        if (newResults && newResults.length > 0) {
          this.logBenefitData();
        }
      },
      immediate: true
    }
  },
  computed: {
    filteredResults() {
      if (!this.scenarioResults || !Array.isArray(this.scenarioResults)) {
        return [];
      }
      
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
    },
    irmaaThresholds() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_THRESHOLDS) {
        return IRMAA_THRESHOLDS[status];
      }
      return IRMAA_THRESHOLDS['single'];
    },
    irmaaLabels() {
      const status = (this.client?.tax_status || '').toLowerCase();
      if (status in IRMAA_LABELS) {
        return IRMAA_LABELS[status];
      }
      return IRMAA_LABELS['single'];
    },
    chartData() {
      console.log('🔍 SocialSecurity chartData computed with filteredResults:', this.filteredResults);
      if (!this.filteredResults || !this.filteredResults.length) {
        console.warn('⚠️ SocialSecurity: No filtered results, returning empty chart data');
        return { labels: [], datasets: [] };
      }

      const labels = this.filteredResults.map(row => row.year.toString());
      const datasets = [
        {
          type: 'line',
          label: 'Primary SSI Benefit',
          data: this.filteredResults.map(row => parseFloat(row.ss_income_primary_gross || 0)),
          borderColor: "#377dff",
          backgroundColor: "transparent",
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: "#377dff",
          fill: false
        },
        {
          type: 'line',
          label: 'Remaining SSI Benefit',
          data: this.filteredResults.map(row => {
            return this.getRemainingSSI(row);
          }),
          borderColor: "#00c9db",
          backgroundColor: "transparent",
          borderWidth: 3,
          tension: 0.3,
          yAxisID: 'y',
          pointRadius: 3,
          pointBackgroundColor: "#00c9db",
          fill: false
        },
        {
          type: 'bar',
          label: 'Medicare Expense',
          data: this.filteredResults.map(row => parseFloat(row.total_medicare || 0)),
          backgroundColor: "#ffc107",
          stack: 'Stack 0',
          yAxisID: 'y'
        }
      ];
      
      // Add spouse SSI if married and has spouse benefits
      if (this.client?.tax_status?.toLowerCase() !== 'single') {
        // Check if there are any spouse benefits in the data
        const hasSpouseBenefits = this.filteredResults.some(row => parseFloat(row.ss_income_spouse || 0) > 0);
        
        if (hasSpouseBenefits) {
          datasets.splice(1, 0, {
            type: 'line',
            label: 'Spouse SSI Benefit',
            data: this.filteredResults.map(row => parseFloat(row.ss_income_spouse_gross || 0)),
            borderColor: "#9b59b6",
            backgroundColor: "transparent",
            borderWidth: 3,
            tension: 0.3,
            yAxisID: 'y',
            pointRadius: 3,
            pointBackgroundColor: "#9b59b6",
            fill: false
          });
        }
      }

      // Add vertical line dataset for SS reduction if enabled
      console.log('🟢 SS_CHART_DEBUG: hasSocialSecurityReduction:', this.hasSocialSecurityReduction);
      console.log('🟢 SS_CHART_DEBUG: reductionYear:', this.reductionYear);
      console.log('🟢 SS_CHART_DEBUG: labels:', labels);
      
      if (this.hasSocialSecurityReduction && this.reductionYear) {
        const reductionYear = this.reductionYear;
        const firstYear = parseInt(labels[0]);
        const reductionIndex = labels.findIndex(label => parseInt(label) === reductionYear);
        console.log('🟢 SS_CHART_DEBUG: reductionIndex:', reductionIndex, 'for year:', reductionYear);
        console.log('🟢 SS_CHART_DEBUG: firstYear:', firstYear, 'reductionYear:', reductionYear);
        
        if (reductionIndex !== -1) {
          // Reduction year is within the chart timeline
          const maxValue = Math.max(...datasets.flatMap(dataset => dataset.data.filter(val => val !== null && val !== undefined)));
          console.log('🟢 SS_CHART_DEBUG: maxValue:', maxValue);
          
          const reductionLineData = new Array(labels.length).fill(null);
          const markerValue = Math.max(maxValue * 1.1, 1000);
          reductionLineData[reductionIndex] = markerValue;
          
          datasets.push({
            type: 'scatter',
            label: `SS Reduction Begins (${reductionYear})`,
            data: reductionLineData,
            borderColor: 'rgba(255, 99, 71, 1)',
            backgroundColor: 'rgba(255, 99, 71, 0.8)',
            borderWidth: 3,
            pointRadius: 10,
            pointStyle: 'triangle',
            pointBackgroundColor: 'rgba(255, 99, 71, 0.9)',
            pointBorderColor: 'rgba(255, 99, 71, 1)',
            pointBorderWidth: 3,
            yAxisID: 'y'
          });
          console.log('🟢 SS_CHART_DEBUG: Added reduction marker in timeline');
        } else if (reductionYear < firstYear) {
          // Reduction already happened before chart timeline starts
          const maxValue = Math.max(...datasets.flatMap(dataset => dataset.data.filter(val => val !== null && val !== undefined)));
          const markerValue = Math.max(maxValue * 1.1, 1000);
          
          // Add indicator at the beginning of the chart
          const reductionLineData = new Array(labels.length).fill(null);
          reductionLineData[0] = markerValue; // Show at first year
          
          datasets.push({
            type: 'scatter',
            label: `SS Reduction Applied (Since ${reductionYear})`,
            data: reductionLineData,
            borderColor: 'rgba(255, 165, 0, 1)', // Orange color for "already applied"
            backgroundColor: 'rgba(255, 165, 0, 0.8)',
            borderWidth: 3,
            pointRadius: 12,
            pointStyle: 'rect', // Rectangle for "already applied"
            pointBackgroundColor: 'rgba(255, 165, 0, 0.9)',
            pointBorderColor: 'rgba(255, 165, 0, 1)',
            pointBorderWidth: 3,
            yAxisID: 'y'
          });
          console.log('🟢 SS_CHART_DEBUG: Added "already applied" marker for year', reductionYear);
        } else {
          console.log('🟢 SS_CHART_DEBUG: Reduction year not found in labels');
        }
      } else {
        console.log('🟢 SS_CHART_DEBUG: No SS reduction or no reduction year');
      }

      console.log('✅ SocialSecurity chartData computed successfully:', { labels, datasets });
      return { labels, datasets };
    },
    chartOptions() {
      const options = {
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
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            position: 'bottom'
          }
        }
      };


      return options;
    },
    hasSsDecrease() {
      // Check if any row has SS decrease applied
      return this.filteredResults && this.filteredResults.some(row => row.ss_decrease_applied);
    },
    
    // Social Security Insights computed properties
    hasSpouse() {
      return this.client?.tax_status?.toLowerCase() !== 'single';
    },
    
    primaryClaimingAge() {
      // The field is primary_ss_claiming_age in the model
      return this.scenario?.primary_ss_claiming_age || 67;
    },
    
    spouseClaimingAge() {
      if (!this.hasSpouse) return null;
      // The field is spouse_ss_claiming_age in the model
      return this.scenario?.spouse_ss_claiming_age || 67;
    },
    
    primaryFRA() {
      // Calculate Full Retirement Age based on birth year
      const birthYear = this.client?.birth_year || 1960;
      if (birthYear <= 1937) return 65;
      if (birthYear <= 1942) return 65 + (birthYear - 1937) * 2/12;
      if (birthYear <= 1954) return 66;
      if (birthYear <= 1959) return 66 + (birthYear - 1954) * 2/12;
      return 67;
    },
    
    spouseFRA() {
      if (!this.hasSpouse) return null;
      const spouseBirthYear = this.client?.spouse?.birth_year || 1960;
      if (spouseBirthYear <= 1937) return 65;
      if (spouseBirthYear <= 1942) return 65 + (spouseBirthYear - 1937) * 2/12;
      if (spouseBirthYear <= 1954) return 66;
      if (spouseBirthYear <= 1959) return 66 + (spouseBirthYear - 1954) * 2/12;
      return 67;
    },
    
    primaryMonthlyBenefit() {
      // First try to get from Social Security income objects using correct field names
      const ssIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'primary' || income.owned_by === 'Primary')
      );
      
      if (ssIncomes && ssIncomes.length > 0) {
        // Use amount_per_month if available (this is the monthly amount)
        const monthlyAmount = ssIncomes[0].amount_per_month;
        const fraAmount = ssIncomes[0].amount_at_fra;
        
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary - amount_per_month:', monthlyAmount, 'amount_at_fra:', fraAmount);
        
        if (monthlyAmount && monthlyAmount > 0) {
          return parseFloat(monthlyAmount);
        } else if (fraAmount && fraAmount > 0) {
          // amount_at_fra might be monthly FRA amount
          return parseFloat(fraAmount);
        }
      }
      
      // Fallback to scenario results - but convert if it looks like annual amount
      if (this.filteredResults && this.filteredResults.length > 0) {
        const resultAmount = parseFloat(this.filteredResults[0].ss_income_primary || 0);
        // If the amount is very large (>5000), it might be annual, so convert to monthly
        if (resultAmount > 5000) {
          return resultAmount / 12;
        }
        return resultAmount;
      }
      
      // Last fallback to scenario field
      return this.scenario?.ss_benefit_primary || 0;
    },
    
    spouseMonthlyBenefit() {
      if (!this.hasSpouse) return 0;
      
      // First try to get from Social Security income objects using correct field names
      const ssIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'spouse' || income.owned_by === 'Spouse')
      );
      
      if (ssIncomes && ssIncomes.length > 0) {
        // Use amount_per_month if available (this is the monthly amount)
        const monthlyAmount = ssIncomes[0].amount_per_month;
        const fraAmount = ssIncomes[0].amount_at_fra;
        
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse - amount_per_month:', monthlyAmount, 'amount_at_fra:', fraAmount);
        
        if (monthlyAmount && monthlyAmount > 0) {
          return parseFloat(monthlyAmount);
        } else if (fraAmount && fraAmount > 0) {
          // amount_at_fra might be monthly FRA amount
          return parseFloat(fraAmount);
        }
      }
      
      // Fallback to scenario results - but convert if it looks like annual amount
      if (this.filteredResults && this.filteredResults.length > 0) {
        const resultAmount = parseFloat(this.filteredResults[0].ss_income_spouse || 0);
        // If the amount is very large (>5000), it might be annual, so convert to monthly
        if (resultAmount > 5000) {
          console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Converting spouse annual to monthly:', resultAmount, '->', resultAmount / 12);
          return resultAmount / 12;
        }
        return resultAmount;
      }
      
      // Last fallback to scenario field
      return this.scenario?.ss_benefit_spouse || 0;
    },
    
    totalMonthlyBenefit() {
      return this.primaryMonthlyBenefit + this.spouseMonthlyBenefit;
    },
    
    hasSocialSecurityReduction() {
      // Check if reduction is enabled and it's a decrease (not increase)
      return this.scenario?.reduction_2030_ss === true && 
             this.scenario?.ss_adjustment_direction === 'decrease';
    },
    
    reductionYear() {
      return this.scenario?.ss_adjustment_year || 2030;
    },
    
    reductionPercentage() {
      return this.scenario?.ss_adjustment_amount || 23;
    },
    
    reductionType() {
      return this.scenario?.ss_adjustment_type || 'percentage';
    },
    
    reductionDirection() {
      return this.scenario?.ss_adjustment_direction || 'decrease';
    },
    
    isOptimalStrategy() {
      // Simple optimization logic - claiming at or after FRA is generally better
      const primaryOptimal = this.primaryClaimingAge >= this.primaryFRA;
      const spouseOptimal = !this.hasSpouse || (this.spouseClaimingAge >= this.spouseFRA);
      return primaryOptimal && spouseOptimal;
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
    isIrmaaBracketHit(row, idx) {
      // Returns true if this row's MAGI crosses into a new IRMAA bracket
      const currentBracket = row.irmaa_bracket_number || 0;
      
      if (currentBracket > 0) {
        // We're in an IRMAA bracket
        if (idx === 0) {
          // First row - show if in any bracket
          return true;
        }
        
        // Check if bracket changed from previous row
        const prevRow = this.filteredResults[idx - 1];
        const prevBracket = prevRow?.irmaa_bracket_number || 0;
        
        // Show indicator if bracket number changed
        return currentBracket !== prevBracket;
      }
      
      return false;
    },
    getIrmaaBracketLabel(row) {
      const magi = Number(row.magi);
      const bracketNum = row.irmaa_bracket_number || 0;
      const bracketThreshold = Number(row.irmaa_bracket_threshold);
      const year = row.year;
      
      const bracketLabels = {
        0: 'No IRMAA',
        1: 'IRMAA Bracket 1',
        2: 'IRMAA Bracket 2', 
        3: 'IRMAA Bracket 3',
        4: 'IRMAA Bracket 4',
        5: 'IRMAA Bracket 5 (Highest)'
      };
      
      if (bracketNum > 0) {
        return `${bracketLabels[bracketNum] || `IRMAA Bracket ${bracketNum}`}: MAGI (${this.formatCurrency(magi)}) exceeds ${this.formatCurrency(bracketThreshold)} in ${year}`;
      } else {
        const firstThreshold = Number(row.irmaa_threshold);
        const difference = firstThreshold - magi;
        return `No IRMAA: ${this.formatCurrency(difference)} below first threshold of ${this.formatCurrency(firstThreshold)} in ${year}`;
      }
    },
    toggleIrmaaTooltip(idx) {
      this.openIrmaaTooltipIdx = this.openIrmaaTooltipIdx === idx ? null : idx;
      // Close SS decrease tooltip when opening IRMAA tooltip
      this.openSsDecreaseTooltipIdx = null;
    },
    toggleSsDecreaseTooltip(idx) {
      this.openSsDecreaseTooltipIdx = this.openSsDecreaseTooltipIdx === idx ? null : idx;
      // Close IRMAA tooltip when opening SS decrease tooltip
      this.openIrmaaTooltipIdx = null;
    },
    closeIrmaaTooltip() {
      this.openIrmaaTooltipIdx = null;
    },
    closeSsDecreaseTooltip() {
      this.openSsDecreaseTooltipIdx = null;
    },
    handleClickOutside(event) {
      if (!event.target.closest('.irmaa-info-icon') && !event.target.closest('.irmaa-info-icon-table') && !event.target.closest('.irmaa-popover')) {
        this.closeIrmaaTooltip();
      }
      if (!event.target.closest('.ss-decrease-icon') && !event.target.closest('.ss-decrease-popover')) {
        this.closeSsDecreaseTooltip();
      }
    },
    getSsDecreaseAmount(row) {
      if (!row.ss_decrease_applied) {
        return 0;
      }
      
      // Return the actual SS decrease amount from the backend
      return parseFloat(row.ss_decrease_amount || 0);
    },
    getRemainingSSI(row) {
      const primarySSI = parseFloat(row.ss_income_primary_gross || 0);
      const spouseSSI = parseFloat(row.ss_income_spouse_gross || 0);
      const totalSSI = primarySSI + spouseSSI;
      const ssDecrease = this.getSsDecreaseAmount(row);
      const medicare = parseFloat(row.total_medicare || 0);
      
      return totalSSI - ssDecrease - medicare;
    },
    
    logBenefitData() {
      if (!this.scenario) return;
      
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: === LOGGING BENEFIT DATA ===');
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Scenario Income Array:', this.scenario?.income);
      
      const primarySSIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'primary' || income.owned_by === 'Primary')
      );
      const spouseSSIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'spouse' || income.owned_by === 'Spouse')
      );
      
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary SS Income Objects:', primarySSIncomes);
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse SS Income Objects:', spouseSSIncomes);
      
      if (primarySSIncomes?.[0]) {
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary income fields:', Object.keys(primarySSIncomes[0]));
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary monthly_amount:', primarySSIncomes[0].monthly_amount);
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary annual_amount:', primarySSIncomes[0].annual_amount);
      }
      
      if (spouseSSIncomes?.[0]) {
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse income fields:', Object.keys(spouseSSIncomes[0]));
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse monthly_amount:', spouseSSIncomes[0].monthly_amount);
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse annual_amount:', spouseSSIncomes[0].annual_amount);
      }
      
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Computed Primary Monthly Benefit:', this.primaryMonthlyBenefit);
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Computed Spouse Monthly Benefit:', this.spouseMonthlyBenefit);
      
      if (this.scenarioResults?.[0]) {
        console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: First scenario result SS fields:', {
          ss_income_primary: this.scenarioResults[0].ss_income_primary,
          ss_income_spouse: this.scenarioResults[0].ss_income_spouse
        });
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
    
    console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: SOCIAL SECURITY OVERVIEW TAB MOUNTED');
    
    // Add a short delay to ensure data is loaded
    this.$nextTick(() => {
      // Debug: Log scenario data to see what fields are available
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Scenario data:', this.scenario);
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Scenario Results first row:', this.scenarioResults?.[0]);
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Income array:', this.scenario?.income);
      
      const primarySSIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'primary' || income.owned_by === 'Primary')
      );
      const spouseSSIncomes = this.scenario?.income?.filter(income => 
        income.income_type === 'social_security' && 
        (income.owned_by === 'spouse' || income.owned_by === 'Spouse')
      );
      
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Primary SS Incomes:', primarySSIncomes);
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Spouse SS Incomes:', spouseSSIncomes);
      
      console.log('🟢 SS_INSIGHTS_DEBUG_UNIQUE_2025: Benefit fields debug:', {
        scenario_primary_benefit: this.scenario?.ss_benefit_primary,
        scenario_spouse_benefit: this.scenario?.ss_benefit_spouse,
        results_primary_ss: this.scenarioResults?.[0]?.ss_income_primary,
        results_spouse_ss: this.scenarioResults?.[0]?.ss_income_spouse,
        computed_primary: this.primaryMonthlyBenefit,
        computed_spouse: this.spouseMonthlyBenefit,
        primary_ss_income_monthly: primarySSIncomes?.[0]?.monthly_amount,
        primary_ss_income_annual: primarySSIncomes?.[0]?.annual_amount,
        spouse_ss_income_monthly: spouseSSIncomes?.[0]?.monthly_amount,
        spouse_ss_income_annual: spouseSSIncomes?.[0]?.annual_amount
      });
    });
    console.log('Social Security Tab - Reduction fields:', {
      reduction_2030_ss: this.scenario?.reduction_2030_ss,
      ss_adjustment_year: this.scenario?.ss_adjustment_year,
      ss_adjustment_direction: this.scenario?.ss_adjustment_direction,
      ss_adjustment_type: this.scenario?.ss_adjustment_type,
      ss_adjustment_amount: this.scenario?.ss_adjustment_amount,
      primary_ss_claiming_age: this.scenario?.primary_ss_claiming_age,
      spouse_ss_claiming_age: this.scenario?.spouse_ss_claiming_age
    });
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
.irmaa-bracket-row {
  border-top: 2px solid #ff8000 !important;
}
.irmaa-info-icon,
.irmaa-info-icon-table {
  margin-left: 6px;
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}
.ss-decrease-icon {
  cursor: pointer;
  font-size: 1em;
  vertical-align: middle;
}
.irmaa-popover,
.ss-decrease-popover {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  border: 1px solid #aaa;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  padding: 6px 12px;
  z-index: 10;
  font-size: 0.95em;
  white-space: nowrap;
}
.ss-decrease-popover {
  background: #fff9e6;
  border-color: #ffc107;
}
.text-danger {
  color: #c0392b !important;
}
.cell-negative {
  background: #ec4836 !important;
  color: #fff !important;
}

/* Insights Card Styling */
.insights-content {
  padding: 0.5rem 0;
  padding-right: 0.5rem; /* Add padding for scrollbar */
}

/* Custom scrollbar styling */
.insights-content::-webkit-scrollbar {
  width: 6px;
}

.insights-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.insights-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.insights-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.insight-item {
  border-left: 3px solid #e9ecef;
  padding-left: 0.75rem;
  margin-bottom: 1rem;
}

.insight-item:last-child {
  margin-bottom: 0;
}

.insight-details {
  margin-left: 1.5rem;
}

.insight-details p {
  line-height: 1.4;
}

.insight-item .bi {
  font-size: 1.1em;
}
</style> 