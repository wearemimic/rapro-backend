<template>
  <div class="retirement-paycheck-heatmap">
    <div class="heatmap-header mb-3">
      <h5 class="mb-2">Monthly Retirement Paycheck Heatmap</h5>
      <p class="text-muted small mb-0">
        Combined monthly Social Security benefits for different claiming age combinations
      </p>
    </div>
    
    <!-- Current Selection Display -->
    <div class="current-selection mb-3" v-if="currentSelection">
      <div class="alert alert-info">
        <strong>Current Selection:</strong>
        Primary claims at <strong>{{ Math.round(primaryClaimingAge) }}</strong>, 
        Spouse claims at <strong>{{ Math.round(spouseClaimingAge) }}</strong>
        = <strong>{{ formatCurrency(currentSelection.totalBenefit) }}/month</strong>
      </div>
    </div>

    <!-- Heatmap Grid -->
    <div class="heatmap-container">
      <!-- Age Labels (Top) -->
      <div class="age-labels-top">
        <div class="corner-label">Spouse ↓ / Primary →</div>
        <div 
          v-for="primaryAge in claimingAges" 
          :key="`primary-${primaryAge}`"
          class="age-label"
        >
          {{ primaryAge }}
        </div>
      </div>

      <!-- Heatmap Grid with Side Labels -->
      <div class="heatmap-grid">
        <div 
          v-for="spouseAge in claimingAges" 
          :key="`spouse-${spouseAge}`"
          class="heatmap-row"
        >
          <!-- Side Age Label -->
          <div class="age-label-side">{{ spouseAge }}</div>
          
          <!-- Heatmap Cells -->
          <div 
            v-for="primaryAge in claimingAges" 
            :key="`cell-${spouseAge}-${primaryAge}`"
            class="heatmap-cell"
            :class="{
              'current-selection': isCurrentSelection(primaryAge, spouseAge),
              'optimal-cell': isOptimalCell(primaryAge, spouseAge),
              'fra-cell': isFRACell(primaryAge, spouseAge)
            }"
            :style="getCellStyle(primaryAge, spouseAge)"
            @click="selectClaimingAges(primaryAge, spouseAge)"
            @mouseover="showTooltip($event, primaryAge, spouseAge)"
            @mouseout="hideTooltip"
          >
            <div class="cell-content">
              <div class="monthly-benefit">
                {{ formatCurrency(getCombinedBenefit(primaryAge, spouseAge)) }}
              </div>
              <div class="cell-ages">
                {{ primaryAge }}/{{ spouseAge }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="heatmap-legend mt-3">
      <div class="row">
        <div class="col-md-6">
          <div class="legend-item">
            <div class="legend-color current-selection-legend"></div>
            <span>Current Selection</span>
          </div>
          <div class="legend-item" v-if="showOptimal">
            <div class="legend-color optimal-legend"></div>
            <span>Optimal Strategy</span>
          </div>
          <div class="legend-item">
            <div class="legend-color fra-legend"></div>
            <span>Full Retirement Age</span>
          </div>
        </div>
        <div class="col-md-6">
          <div class="benefit-scale">
            <div class="scale-label">Monthly Benefits:</div>
            <div class="scale-gradient">
              <div class="scale-low">{{ formatCurrency(minBenefit) }}</div>
              <div class="scale-high">{{ formatCurrency(maxBenefit) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <div 
      v-if="tooltip.show" 
      class="heatmap-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <strong>Claiming Ages: {{ tooltip.primaryAge }}/{{ tooltip.spouseAge }}</strong><br>
        Primary: {{ formatCurrency(tooltip.primaryBenefit) }}/month<br>
        Spouse: {{ formatCurrency(tooltip.spouseBenefit) }}/month<br>
        <strong>Combined: {{ formatCurrency(tooltip.totalBenefit) }}/month</strong><br>
        <span class="text-muted">Lifetime: {{ formatCurrency(tooltip.lifetimeBenefit) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import socialSecurityService from '@/services/socialSecurityService.js';

export default {
  name: 'RetirementPaycheckHeatmap',
  props: {
    ssData: {
      type: Object,
      required: true
    },
    primaryClaimingAge: {
      type: Number,
      required: true
    },
    spouseClaimingAge: {
      type: Number,
      required: true
    },
    primaryLifeExpectancy: {
      type: Number,
      required: true
    },
    spouseLifeExpectancy: {
      type: Number,
      required: true
    },
    primaryFRA: {
      type: Number,
      default: 67
    },
    spouseFRA: {
      type: Number,
      default: 67
    },
    showOptimal: {
      type: Boolean,
      default: false
    },
    optimalStrategy: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      claimingAges: [62, 63, 64, 65, 66, 67, 68, 69, 70],
      benefitMatrix: {},
      minBenefit: 0,
      maxBenefit: 0,
      tooltip: {
        show: false,
        x: 0,
        y: 0,
        primaryAge: 0,
        spouseAge: 0,
        primaryBenefit: 0,
        spouseBenefit: 0,
        totalBenefit: 0,
        lifetimeBenefit: 0
      }
    };
  },
  computed: {
    currentSelection() {
      if (!this.ssData.primary || !this.ssData.spouse) return null;
      
      const roundedPrimary = Math.round(this.primaryClaimingAge);
      const roundedSpouse = Math.round(this.spouseClaimingAge);
      
      return {
        primaryAge: roundedPrimary,
        spouseAge: roundedSpouse,
        totalBenefit: this.getCombinedBenefit(roundedPrimary, roundedSpouse)
      };
    }
  },
  watch: {
    ssData: {
      handler() {
        this.calculateBenefitMatrix();
      },
      deep: true
    },
    primaryLifeExpectancy() {
      this.calculateBenefitMatrix();
    },
    spouseLifeExpectancy() {
      this.calculateBenefitMatrix();
    }
  },
  mounted() {
    this.calculateBenefitMatrix();
  },
  methods: {
    calculateBenefitMatrix() {
      if (!this.ssData.primary || !this.ssData.spouse) {
        return;
      }

      this.benefitMatrix = {};
      let minBenefit = Infinity;
      let maxBenefit = -Infinity;

      this.claimingAges.forEach(primaryAge => {
        this.benefitMatrix[primaryAge] = {};
        
        this.claimingAges.forEach(spouseAge => {
          const primaryBenefit = socialSecurityService.calculateBenefit(
            this.ssData.primary.amountAtFRA,
            primaryAge
          );
          
          const spouseBenefit = socialSecurityService.calculateBenefit(
            this.ssData.spouse.amountAtFRA,
            spouseAge
          );
          
          // Calculate spousal benefits
          const spousalAnalysis = socialSecurityService.calculateSpousalBenefits(
            this.ssData.primary,
            this.ssData.spouse,
            spouseAge
          );
          
          const actualSpouseBenefit = spousalAnalysis?.actualBenefit || spouseBenefit;
          const combinedBenefit = primaryBenefit + actualSpouseBenefit;
          
          // Calculate lifetime benefits
          const primaryLifetime = socialSecurityService.calculateLifetimeBenefits(
            this.ssData.primary.amountAtFRA,
            primaryAge,
            this.primaryLifeExpectancy
          );
          
          const spouseLifetime = socialSecurityService.calculateLifetimeBenefits(
            this.ssData.spouse.amountAtFRA,
            spouseAge,
            this.spouseLifeExpectancy
          );
          
          const totalLifetime = primaryLifetime.lifetimeTotal + spouseLifetime.lifetimeTotal;
          
          this.benefitMatrix[primaryAge][spouseAge] = {
            primaryBenefit,
            spouseBenefit: actualSpouseBenefit,
            combinedBenefit,
            lifetimeBenefit: totalLifetime
          };
          
          // Track min/max for color scaling
          minBenefit = Math.min(minBenefit, combinedBenefit);
          maxBenefit = Math.max(maxBenefit, combinedBenefit);
        });
      });
      
      this.minBenefit = minBenefit;
      this.maxBenefit = maxBenefit;
    },
    
    getCombinedBenefit(primaryAge, spouseAge) {
      if (!this.benefitMatrix[primaryAge]?.[spouseAge]) {
        return 0;
      }
      return this.benefitMatrix[primaryAge][spouseAge].combinedBenefit;
    },
    
    getCellStyle(primaryAge, spouseAge) {
      const benefit = this.getCombinedBenefit(primaryAge, spouseAge);
      if (benefit === 0 || this.maxBenefit === this.minBenefit) {
        return { backgroundColor: '#f8f9fa' };
      }
      
      // Normalize benefit to 0-1 scale
      const normalized = (benefit - this.minBenefit) / (this.maxBenefit - this.minBenefit);
      
      // Create color gradient from light blue to dark green
      const hue = 120 + (180 - 120) * (1 - normalized); // Green to blue
      const saturation = 40 + 40 * normalized; // 40% to 80%
      const lightness = 85 - 25 * normalized; // 85% to 60%
      
      return {
        backgroundColor: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
        borderColor: this.isCurrentSelection(primaryAge, spouseAge) ? '#007bff' : 'transparent'
      };
    },
    
    isCurrentSelection(primaryAge, spouseAge) {
      return Math.round(this.primaryClaimingAge) === primaryAge && 
             Math.round(this.spouseClaimingAge) === spouseAge;
    },
    
    isOptimalCell(primaryAge, spouseAge) {
      if (!this.showOptimal || !this.optimalStrategy) return false;
      return this.optimalStrategy.primaryAge === primaryAge && 
             this.optimalStrategy.spouseAge === spouseAge;
    },
    
    isFRACell(primaryAge, spouseAge) {
      return Math.round(this.primaryFRA) === primaryAge && 
             Math.round(this.spouseFRA) === spouseAge;
    },
    
    selectClaimingAges(primaryAge, spouseAge) {
      this.$emit('update:primaryClaimingAge', primaryAge);
      this.$emit('update:spouseClaimingAge', spouseAge);
    },
    
    showTooltip(event, primaryAge, spouseAge) {
      const benefit = this.benefitMatrix[primaryAge]?.[spouseAge];
      if (!benefit) return;
      
      this.tooltip = {
        show: true,
        x: event.clientX + 10,
        y: event.clientY - 10,
        primaryAge,
        spouseAge,
        primaryBenefit: benefit.primaryBenefit,
        spouseBenefit: benefit.spouseBenefit,
        totalBenefit: benefit.combinedBenefit,
        lifetimeBenefit: benefit.lifetimeBenefit
      };
    },
    
    hideTooltip() {
      this.tooltip.show = false;
    },
    
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    }
  }
};
</script>

<style scoped>
.retirement-paycheck-heatmap {
  width: 100%;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.heatmap-container {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.age-labels-top {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.corner-label {
  width: 60px;
  padding: 8px;
  font-size: 11px;
  font-weight: bold;
  text-align: center;
  background: #e9ecef;
  border-right: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.age-label {
  flex: 1;
  padding: 8px;
  text-align: center;
  font-weight: bold;
  font-size: 12px;
  border-right: 1px solid #dee2e6;
}

.age-label:last-child {
  border-right: none;
}

.heatmap-grid {
  display: flex;
  flex-direction: column;
}

.heatmap-row {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.heatmap-row:last-child {
  border-bottom: none;
}

.age-label-side {
  width: 60px;
  padding: 8px;
  text-align: center;
  font-weight: bold;
  font-size: 12px;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-cell {
  flex: 1;
  padding: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border-right: 1px solid #dee2e6;
  border-width: 2px;
  min-height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-cell:last-child {
  border-right: none;
}

.heatmap-cell:hover {
  border-color: #007bff !important;
  box-shadow: inset 0 0 0 1px #007bff;
  transform: scale(1.02);
  z-index: 10;
  position: relative;
}

.heatmap-cell.current-selection {
  border: 3px solid #007bff !important;
  font-weight: bold;
}

.heatmap-cell.optimal-cell {
  border: 3px solid #28a745 !important;
  position: relative;
}

.heatmap-cell.fra-cell {
  border: 2px dashed #6c757d !important;
}

.cell-content {
  text-align: center;
}

.monthly-benefit {
  font-size: 13px;
  font-weight: bold;
  color: #333;
}

.cell-ages {
  font-size: 10px;
  color: #6c757d;
  margin-top: 2px;
}

.heatmap-legend {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  border-radius: 3px;
}

.current-selection-legend {
  border: 3px solid #007bff;
  background: white;
}

.optimal-legend {
  border: 3px solid #28a745;
  background: white;
}

.fra-legend {
  border: 2px dashed #6c757d;
  background: white;
}

.benefit-scale {
  text-align: right;
}

.scale-label {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 5px;
}

.scale-gradient {
  display: flex;
  justify-content: space-between;
  background: linear-gradient(to right, #b3e0ff, #2d7d32);
  height: 20px;
  border-radius: 10px;
  padding: 0 10px;
  align-items: center;
  font-size: 11px;
  color: white;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
}

.heatmap-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 1000;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  max-width: 250px;
}

.tooltip-content {
  line-height: 1.4;
}

.current-selection {
  margin-bottom: 15px;
}

.current-selection .alert {
  margin-bottom: 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .corner-label {
    width: 45px;
    font-size: 9px;
    padding: 4px;
  }
  
  .age-label-side {
    width: 45px;
    font-size: 11px;
  }
  
  .heatmap-cell {
    min-height: 60px;
    padding: 4px;
  }
  
  .monthly-benefit {
    font-size: 11px;
  }
  
  .cell-ages {
    font-size: 9px;
  }
  
  .age-label {
    font-size: 11px;
    padding: 6px;
  }
}
</style>