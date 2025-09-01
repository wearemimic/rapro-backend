<template>
  <div class="section-configuration">
    <!-- Cover Page Configuration -->
    <div v-if="section.type === 'cover'" class="config-group">
      <h6 class="config-title">Cover Page Settings</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`include-logo-${section.uid}`"
          v-model="localConfig.include_logo"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`include-logo-${section.uid}`">
          Include Company Logo
        </label>
      </div>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`include-date-${section.uid}`"
          v-model="localConfig.include_date"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`include-date-${section.uid}`">
          Include Report Date
        </label>
      </div>
      
      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`include-client-${section.uid}`"
          v-model="localConfig.include_client_name"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`include-client-${section.uid}`">
          Include Client Name
        </label>
      </div>

      <div class="mb-3">
        <label class="form-label">Template Style</label>
        <select class="form-select form-select-sm" v-model="localConfig.template_style" @change="emitUpdate">
          <option value="professional">Professional</option>
          <option value="executive">Executive</option>
          <option value="modern">Modern</option>
          <option value="classic">Classic</option>
        </select>
      </div>
    </div>

    <!-- Chart Configuration -->
    <div v-else-if="section.type === 'chart'" class="config-group">
      <h6 class="config-title">Chart Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Chart Type</label>
        <select class="form-select form-select-sm" v-model="localConfig.chart_type" @change="emitUpdate">
          <option value="pie">Pie Chart</option>
          <option value="line">Line Chart</option>
          <option value="bar">Bar Chart</option>
          <option value="area">Area Chart</option>
          <option value="timeline">Timeline Chart</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Data Source</label>
        <select class="form-select form-select-sm" v-model="localConfig.data_source" @change="emitUpdate">
          <option value="assets">Current Assets</option>
          <option value="income_projections">Income Projections</option>
          <option value="asset_timeline">Asset Timeline</option>
          <option value="expenses">Expenses</option>
          <option value="tax_analysis">Tax Analysis</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Color Scheme</label>
        <select class="form-select form-select-sm" v-model="localConfig.colors" @change="emitUpdate">
          <option value="professional">Professional Blue</option>
          <option value="vibrant">Vibrant</option>
          <option value="muted">Muted</option>
          <option value="monochrome">Monochrome</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <div v-if="['line', 'area', 'timeline'].includes(localConfig.chart_type)" class="mb-3">
        <label class="form-label">Projection Years</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.years"
            min="5" 
            max="50"
            @input="emitUpdate"
          >
          <span class="input-group-text">years</span>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-legend-${section.uid}`"
          v-model="localConfig.show_legend"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-legend-${section.uid}`">
          Show Legend
        </label>
      </div>
    </div>

    <!-- Data Table Configuration -->
    <div v-else-if="section.type === 'data_table'" class="config-group">
      <h6 class="config-title">Table Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Data Source</label>
        <select class="form-select form-select-sm" v-model="localConfig.data_source" @change="emitUpdate">
          <option value="financial_summary">Financial Summary</option>
          <option value="assets_detailed">Assets Detailed</option>
          <option value="income_sources">Income Sources</option>
          <option value="tax_breakdown">Tax Breakdown</option>
          <option value="scenario_comparison">Scenario Comparison</option>
        </select>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`format-currency-${section.uid}`"
          v-model="localConfig.format_currency"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`format-currency-${section.uid}`">
          Format as Currency
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-totals-${section.uid}`"
          v-model="localConfig.show_totals"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-totals-${section.uid}`">
          Show Totals Row
        </label>
      </div>

      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`alternating-rows-${section.uid}`"
          v-model="localConfig.alternating_rows"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`alternating-rows-${section.uid}`">
          Alternating Row Colors
        </label>
      </div>
    </div>

    <!-- Monte Carlo Configuration -->
    <div v-else-if="section.type === 'monte_carlo'" class="config-group">
      <h6 class="config-title">Monte Carlo Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Number of Simulations</label>
        <select class="form-select form-select-sm" v-model.number="localConfig.simulations" @change="emitUpdate">
          <option :value="1000">1,000 Simulations</option>
          <option :value="5000">5,000 Simulations</option>
          <option :value="10000">10,000 Simulations</option>
          <option :value="25000">25,000 Simulations</option>
        </select>
      </div>

      <div class="mb-3">
        <label class="form-label">Confidence Levels</label>
        <div class="confidence-checkboxes">
          <div class="form-check form-check-inline">
            <input 
              class="form-check-input" 
              type="checkbox" 
              :id="`conf-50-${section.uid}`"
              :checked="localConfig.confidence_levels.includes(50)"
              @change="toggleConfidenceLevel(50)"
            >
            <label class="form-check-label" :for="`conf-50-${section.uid}`">50%</label>
          </div>
          <div class="form-check form-check-inline">
            <input 
              class="form-check-input" 
              type="checkbox" 
              :id="`conf-75-${section.uid}`"
              :checked="localConfig.confidence_levels.includes(75)"
              @change="toggleConfidenceLevel(75)"
            >
            <label class="form-check-label" :for="`conf-75-${section.uid}`">75%</label>
          </div>
          <div class="form-check form-check-inline">
            <input 
              class="form-check-input" 
              type="checkbox" 
              :id="`conf-90-${section.uid}`"
              :checked="localConfig.confidence_levels.includes(90)"
              @change="toggleConfidenceLevel(90)"
            >
            <label class="form-check-label" :for="`conf-90-${section.uid}`">90%</label>
          </div>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-histogram-${section.uid}`"
          v-model="localConfig.show_histogram"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-histogram-${section.uid}`">
          Include Histogram
        </label>
      </div>
    </div>

    <!-- IRMAA Configuration -->
    <div v-else-if="section.type === 'irmaa'" class="config-group">
      <h6 class="config-title">IRMAA Analysis Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Projection Years</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.projection_years"
            min="5" 
            max="30"
            @input="emitUpdate"
          >
          <span class="input-group-text">years</span>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-brackets-${section.uid}`"
          v-model="localConfig.show_brackets"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-brackets-${section.uid}`">
          Show Bracket Thresholds
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`inflation-adjusted-${section.uid}`"
          v-model="localConfig.inflation_adjusted"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`inflation-adjusted-${section.uid}`">
          Inflation Adjusted
        </label>
      </div>

      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`yearly-projections-${section.uid}`"
          v-model="localConfig.yearly_projections"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`yearly-projections-${section.uid}`">
          Yearly Projections
        </label>
      </div>
    </div>

    <!-- Roth Conversion Configuration -->
    <div v-else-if="section.type === 'roth'" class="config-group">
      <h6 class="config-title">Roth Conversion Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Conversion Period</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.conversion_years"
            min="1" 
            max="20"
            @input="emitUpdate"
          >
          <span class="input-group-text">years</span>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-tax-impact-${section.uid}`"
          v-model="localConfig.show_tax_impact"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-tax-impact-${section.uid}`">
          Show Tax Impact
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`breakeven-analysis-${section.uid}`"
          v-model="localConfig.breakeven_analysis"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`breakeven-analysis-${section.uid}`">
          Break-even Analysis
        </label>
      </div>

      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`optimal-timing-${section.uid}`"
          v-model="localConfig.optimal_timing"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`optimal-timing-${section.uid}`">
          Optimal Timing
        </label>
      </div>
    </div>

    <!-- Summary Configuration -->
    <div v-else-if="section.type === 'summary'" class="config-group">
      <h6 class="config-title">Summary Settings</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`bullet-points-${section.uid}`"
          v-model="localConfig.bullet_points"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`bullet-points-${section.uid}`">
          Use Bullet Points
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`key-metrics-${section.uid}`"
          v-model="localConfig.highlight_key_metrics"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`key-metrics-${section.uid}`">
          Highlight Key Metrics
        </label>
      </div>

      <div v-if="localConfig.bullet_points" class="mb-3">
        <label class="form-label">Max Points</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.max_points"
            min="3" 
            max="10"
            @input="emitUpdate"
          >
          <span class="input-group-text">points</span>
        </div>
      </div>
    </div>

    <!-- Recommendations Configuration -->
    <div v-else-if="section.type === 'recommendations'" class="config-group">
      <h6 class="config-title">Recommendations Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Max Recommendations</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.max_recommendations"
            min="3" 
            max="10"
            @input="emitUpdate"
          >
          <span class="input-group-text">items</span>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`priority-ranking-${section.uid}`"
          v-model="localConfig.priority_ranking"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`priority-ranking-${section.uid}`">
          Priority Ranking
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`include-timeline-${section.uid}`"
          v-model="localConfig.include_timeline"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`include-timeline-${section.uid}`">
          Include Timeline
        </label>
      </div>

      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`action-oriented-${section.uid}`"
          v-model="localConfig.action_oriented"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`action-oriented-${section.uid}`">
          Action-Oriented Language
        </label>
      </div>
    </div>

    <!-- Spacer Configuration -->
    <div v-else-if="section.type === 'spacer'" class="config-group">
      <h6 class="config-title">Spacer Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Height</label>
        <select class="form-select form-select-sm" v-model="localConfig.height" @change="emitUpdate">
          <option value="small">Small (0.5 inch)</option>
          <option value="medium">Medium (1 inch)</option>
          <option value="large">Large (1.5 inch)</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <div v-if="localConfig.height === 'custom'" class="mb-3">
        <label class="form-label">Custom Height</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.custom_height"
            min="0.1" 
            max="3"
            step="0.1"
            @input="emitUpdate"
          >
          <span class="input-group-text">inches</span>
        </div>
      </div>
    </div>

    <!-- Generic Configuration -->
    <div v-else class="config-group">
      <h6 class="config-title">Section Settings</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`show-header-${section.uid}`"
          v-model="localConfig.show_header"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`show-header-${section.uid}`">
          Show Section Header
        </label>
      </div>

      <div class="form-check mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          :id="`page-break-before-${section.uid}`"
          v-model="localConfig.page_break_before"
          @change="emitUpdate"
        >
        <label class="form-check-label" :for="`page-break-before-${section.uid}`">
          Page Break Before
        </label>
      </div>
    </div>

    <!-- Advanced Settings -->
    <div class="config-group">
      <button 
        class="btn btn-sm btn-outline-secondary w-100"
        type="button"
        @click="showAdvanced = !showAdvanced"
      >
        <i class="bi-gear me-1"></i>
        {{ showAdvanced ? 'Hide' : 'Show' }} Advanced Settings
        <i :class="showAdvanced ? 'bi-chevron-up' : 'bi-chevron-down'" class="ms-1"></i>
      </button>

      <div v-if="showAdvanced" class="mt-3">
        <div class="mb-3">
          <label class="form-label">CSS Classes</label>
          <input 
            type="text" 
            class="form-control form-control-sm" 
            v-model="localConfig.css_classes"
            placeholder="custom-class another-class"
            @input="emitUpdate"
          >
          <small class="form-text text-muted">Space-separated CSS classes</small>
        </div>

        <div class="mb-3">
          <label class="form-label">Custom Styles</label>
          <textarea 
            class="form-control form-control-sm" 
            rows="3"
            v-model="localConfig.custom_styles"
            placeholder="margin-top: 20px; font-size: 14px;"
            @input="emitUpdate"
          ></textarea>
          <small class="form-text text-muted">Custom CSS styles</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'SectionConfiguration',
  props: {
    section: {
      type: Object,
      required: true
    }
  },
  emits: ['update'],
  setup(props, { emit }) {
    const showAdvanced = ref(false)
    
    // Create a local copy of the config to avoid direct mutation
    const localConfig = ref({ ...props.section.config })

    // Watch for changes in section prop and update local config
    watch(() => props.section.config, (newConfig) => {
      localConfig.value = { ...newConfig }
    }, { deep: true })

    // Emit updates to parent
    const emitUpdate = () => {
      emit('update', localConfig.value)
    }

    // Helper for confidence levels toggle
    const toggleConfidenceLevel = (level) => {
      const levels = localConfig.value.confidence_levels || []
      const index = levels.indexOf(level)
      
      if (index > -1) {
        levels.splice(index, 1)
      } else {
        levels.push(level)
        levels.sort((a, b) => a - b)
      }
      
      localConfig.value.confidence_levels = [...levels]
      emitUpdate()
    }

    return {
      showAdvanced,
      localConfig,
      emitUpdate,
      toggleConfidenceLevel
    }
  }
}
</script>

<style scoped>
.section-configuration {
  padding: 0;
}

.config-group {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.config-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.config-title {
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-label {
  font-size: 0.875rem;
  color: #495057;
  margin-bottom: 0.25rem;
}

.form-control-sm,
.form-select-sm {
  font-size: 0.875rem;
}

.form-check {
  margin-bottom: 0.5rem;
}

.form-check-label {
  font-size: 0.875rem;
  color: #495057;
}

.confidence-checkboxes {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.input-group-text {
  font-size: 0.875rem;
  background: #f8f9fa;
  border-color: #ced4da;
}

.form-text {
  font-size: 0.75rem;
}

/* Advanced settings button */
.config-group:last-child .btn {
  border-style: dashed;
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .confidence-checkboxes {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>