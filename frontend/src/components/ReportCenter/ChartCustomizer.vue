<template>
  <div class="chart-customizer">
    <div class="customizer-header mb-3">
      <h6 class="mb-0">
        <i class="bi-bar-chart me-2"></i>Chart Customization
      </h6>
    </div>

    <!-- Chart Type Selection -->
    <div class="config-group mb-4">
      <label class="form-label">Chart Type</label>
      <div class="chart-type-grid">
        <div 
          v-for="chartType in availableChartTypes" 
          :key="chartType.id"
          class="chart-type-option"
          :class="{ 'selected': localConfig.chart_type === chartType.id }"
          @click="updateChartType(chartType.id)"
        >
          <div class="chart-type-icon">
            <i :class="chartType.icon"></i>
          </div>
          <div class="chart-type-label">{{ chartType.label }}</div>
        </div>
      </div>
    </div>

    <!-- Data Source Configuration -->
    <div class="config-group mb-4">
      <label class="form-label">Data Source</label>
      <select class="form-select form-select-sm" v-model="localConfig.data_source" @change="onConfigChange">
        <option v-for="source in availableDataSources" :key="source.id" :value="source.id">
          {{ source.label }}
        </option>
      </select>
      <small class="form-text text-muted">{{ getDataSourceDescription(localConfig.data_source) }}</small>
    </div>

    <!-- Chart Appearance -->
    <div class="config-group mb-4">
      <h6 class="config-subtitle">Appearance</h6>
      
      <!-- Color Scheme -->
      <div class="mb-3">
        <label class="form-label">Color Scheme</label>
        <div class="color-scheme-options">
          <div 
            v-for="scheme in colorSchemes" 
            :key="scheme.id"
            class="color-scheme-option"
            :class="{ 'selected': localConfig.color_scheme === scheme.id }"
            @click="updateColorScheme(scheme.id)"
          >
            <div class="color-preview">
              <div 
                v-for="(color, index) in scheme.colors.slice(0, 4)" 
                :key="index"
                class="color-swatch"
                :style="{ backgroundColor: color }"
              ></div>
            </div>
            <small>{{ scheme.label }}</small>
          </div>
        </div>
      </div>

      <!-- Chart Size -->
      <div class="row">
        <div class="col-6">
          <label class="form-label">Width</label>
          <div class="input-group input-group-sm">
            <input 
              type="number" 
              class="form-control" 
              v-model.number="localConfig.width"
              min="200" 
              max="800"
              @input="onConfigChange"
            >
            <span class="input-group-text">px</span>
          </div>
        </div>
        <div class="col-6">
          <label class="form-label">Height</label>
          <div class="input-group input-group-sm">
            <input 
              type="number" 
              class="form-control" 
              v-model.number="localConfig.height"
              min="150" 
              max="600"
              @input="onConfigChange"
            >
            <span class="input-group-text">px</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart-Specific Options -->
    <!-- Line/Area Chart Options -->
    <div v-if="isTimelineChart" class="config-group mb-4">
      <h6 class="config-subtitle">Timeline Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Time Range</label>
        <div class="row">
          <div class="col-6">
            <div class="input-group input-group-sm">
              <input 
                type="number" 
                class="form-control" 
                v-model.number="localConfig.start_year"
                :min="currentYear" 
                :max="currentYear + 50"
                @input="onConfigChange"
              >
              <span class="input-group-text">Start</span>
            </div>
          </div>
          <div class="col-6">
            <div class="input-group input-group-sm">
              <input 
                type="number" 
                class="form-control" 
                v-model.number="localConfig.projection_years"
                min="5" 
                max="50"
                @input="onConfigChange"
              >
              <span class="input-group-text">Years</span>
            </div>
          </div>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-projections"
          v-model="localConfig.show_projections"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-projections">
          Show Projected Values
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="smooth-lines"
          v-model="localConfig.smooth_lines"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="smooth-lines">
          Smooth Line Curves
        </label>
      </div>
    </div>

    <!-- Pie Chart Options -->
    <div v-if="localConfig.chart_type === 'pie'" class="config-group mb-4">
      <h6 class="config-subtitle">Pie Chart Settings</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-percentages"
          v-model="localConfig.show_percentages"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-percentages">
          Show Percentages
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-values"
          v-model="localConfig.show_values"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-values">
          Show Values
        </label>
      </div>

      <div class="mb-3">
        <label class="form-label">Donut Hole Size</label>
        <input 
          type="range" 
          class="form-range" 
          v-model.number="localConfig.donut_size"
          min="0" 
          max="80"
          @input="onConfigChange"
        >
        <div class="range-labels">
          <small>Pie</small>
          <small>Donut</small>
        </div>
      </div>
    </div>

    <!-- Bar Chart Options -->
    <div v-if="isBarChart" class="config-group mb-4">
      <h6 class="config-subtitle">Bar Chart Settings</h6>
      
      <div class="mb-3">
        <label class="form-label">Orientation</label>
        <div class="btn-group w-100" role="group">
          <input 
            type="radio" 
            class="btn-check" 
            id="vertical-bars" 
            value="vertical"
            v-model="localConfig.orientation"
            @change="onConfigChange"
          >
          <label class="btn btn-outline-secondary btn-sm" for="vertical-bars">Vertical</label>
          
          <input 
            type="radio" 
            class="btn-check" 
            id="horizontal-bars" 
            value="horizontal"
            v-model="localConfig.orientation"
            @change="onConfigChange"
          >
          <label class="btn btn-outline-secondary btn-sm" for="horizontal-bars">Horizontal</label>
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="stacked-bars"
          v-model="localConfig.stacked"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="stacked-bars">
          Stacked Bars
        </label>
      </div>
    </div>

    <!-- Legend and Labels -->
    <div class="config-group mb-4">
      <h6 class="config-subtitle">Legend & Labels</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-legend"
          v-model="localConfig.show_legend"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-legend">
          Show Legend
        </label>
      </div>

      <div v-if="localConfig.show_legend" class="mb-3">
        <label class="form-label">Legend Position</label>
        <select class="form-select form-select-sm" v-model="localConfig.legend_position" @change="onConfigChange">
          <option value="top">Top</option>
          <option value="bottom">Bottom</option>
          <option value="left">Left</option>
          <option value="right">Right</option>
        </select>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-title"
          v-model="localConfig.show_title"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-title">
          Show Chart Title
        </label>
      </div>

      <div v-if="localConfig.show_title" class="mb-3">
        <input 
          type="text" 
          class="form-control form-control-sm" 
          placeholder="Enter chart title"
          v-model="localConfig.title"
          @input="onConfigChange"
        >
      </div>
    </div>

    <!-- Axes Configuration (for bar/line charts) -->
    <div v-if="hasAxes" class="config-group mb-4">
      <h6 class="config-subtitle">Axes</h6>
      
      <div class="row">
        <div class="col-12 mb-3">
          <label class="form-label">X-Axis Label</label>
          <input 
            type="text" 
            class="form-control form-control-sm" 
            placeholder="X-axis label"
            v-model="localConfig.x_axis_label"
            @input="onConfigChange"
          >
        </div>
        <div class="col-12 mb-3">
          <label class="form-label">Y-Axis Label</label>
          <input 
            type="text" 
            class="form-control form-control-sm" 
            placeholder="Y-axis label"
            v-model="localConfig.y_axis_label"
            @input="onConfigChange"
          >
        </div>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="start-at-zero"
          v-model="localConfig.start_at_zero"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="start-at-zero">
          Start Y-axis at Zero
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="show-grid"
          v-model="localConfig.show_grid"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="show-grid">
          Show Grid Lines
        </label>
      </div>
    </div>

    <!-- Animation Settings -->
    <div class="config-group mb-4">
      <h6 class="config-subtitle">Animation</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="enable-animation"
          v-model="localConfig.enable_animation"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="enable-animation">
          Enable Animation
        </label>
      </div>

      <div v-if="localConfig.enable_animation" class="mb-3">
        <label class="form-label">Animation Duration</label>
        <div class="input-group input-group-sm">
          <input 
            type="number" 
            class="form-control" 
            v-model.number="localConfig.animation_duration"
            min="200" 
            max="3000"
            step="100"
            @input="onConfigChange"
          >
          <span class="input-group-text">ms</span>
        </div>
      </div>
    </div>

    <!-- Data Formatting -->
    <div class="config-group mb-4">
      <h6 class="config-subtitle">Data Formatting</h6>
      
      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="format-currency"
          v-model="localConfig.format_currency"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="format-currency">
          Format as Currency
        </label>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="abbreviate-numbers"
          v-model="localConfig.abbreviate_numbers"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="abbreviate-numbers">
          Abbreviate Large Numbers (1K, 1M)
        </label>
      </div>

      <div v-if="localConfig.format_currency" class="mb-3">
        <label class="form-label">Decimal Places</label>
        <select class="form-select form-select-sm" v-model.number="localConfig.decimal_places" @change="onConfigChange">
          <option :value="0">0 (Whole numbers)</option>
          <option :value="1">1 decimal place</option>
          <option :value="2">2 decimal places</option>
        </select>
      </div>
    </div>

    <!-- Export Settings -->
    <div class="config-group mb-4">
      <h6 class="config-subtitle">Export Options</h6>
      
      <div class="mb-3">
        <label class="form-label">Export Quality</label>
        <select class="form-select form-select-sm" v-model="localConfig.export_quality" @change="onConfigChange">
          <option value="standard">Standard (72 DPI)</option>
          <option value="high">High (150 DPI)</option>
          <option value="print">Print Quality (300 DPI)</option>
        </select>
      </div>

      <div class="form-check mb-2">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="transparent-background"
          v-model="localConfig.transparent_background"
          @change="onConfigChange"
        >
        <label class="form-check-label" for="transparent-background">
          Transparent Background
        </label>
      </div>
    </div>

    <!-- Live Preview -->
    <div class="config-group">
      <h6 class="config-subtitle">Preview</h6>
      <div class="chart-preview-container">
        <div class="preview-loading" v-if="isGeneratingPreview">
          <div class="spinner-border spinner-border-sm me-2"></div>
          Updating preview...
        </div>
        <canvas 
          ref="previewCanvas" 
          class="chart-preview-canvas"
          :width="localConfig.width"
          :height="localConfig.height"
        ></canvas>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="customizer-actions mt-4">
      <div class="d-grid gap-2">
        <button class="btn btn-primary btn-sm" @click="applyChanges">
          <i class="bi-check-circle me-1"></i>Apply Changes
        </button>
        <button class="btn btn-outline-secondary btn-sm" @click="resetToDefaults">
          <i class="bi-arrow-counterclockwise me-1"></i>Reset to Defaults
        </button>
        <button class="btn btn-outline-info btn-sm" @click="saveAsTemplate">
          <i class="bi-bookmark-plus me-1"></i>Save as Template
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'ChartCustomizer',
  props: {
    chartConfig: {
      type: Object,
      required: true
    },
    sampleData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['config-updated', 'apply-changes'],
  setup(props, { emit }) {
    const previewCanvas = ref(null)
    const isGeneratingPreview = ref(false)
    const previewChart = ref(null)

    // Local configuration state
    const localConfig = ref({
      // Chart basics
      chart_type: 'bar',
      data_source: 'assets',
      
      // Appearance
      color_scheme: 'professional',
      width: 400,
      height: 300,
      
      // Timeline specific
      start_year: new Date().getFullYear(),
      projection_years: 30,
      show_projections: true,
      smooth_lines: false,
      
      // Pie chart specific
      show_percentages: true,
      show_values: false,
      donut_size: 0,
      
      // Bar chart specific
      orientation: 'vertical',
      stacked: false,
      
      // Legend and labels
      show_legend: true,
      legend_position: 'bottom',
      show_title: true,
      title: '',
      
      // Axes
      x_axis_label: '',
      y_axis_label: '',
      start_at_zero: true,
      show_grid: true,
      
      // Animation
      enable_animation: true,
      animation_duration: 1000,
      
      // Formatting
      format_currency: true,
      abbreviate_numbers: true,
      decimal_places: 0,
      
      // Export
      export_quality: 'high',
      transparent_background: false,
      
      ...props.chartConfig
    })

    // Available chart types
    const availableChartTypes = [
      { id: 'bar', label: 'Bar Chart', icon: 'bi-bar-chart' },
      { id: 'line', label: 'Line Chart', icon: 'bi-graph-up' },
      { id: 'area', label: 'Area Chart', icon: 'bi-area-chart' },
      { id: 'pie', label: 'Pie Chart', icon: 'bi-pie-chart' },
      { id: 'doughnut', label: 'Doughnut', icon: 'bi-circle' },
      { id: 'timeline', label: 'Timeline', icon: 'bi-graph-up-arrow' },
      { id: 'scatter', label: 'Scatter Plot', icon: 'bi-scatter-chart' },
      { id: 'radar', label: 'Radar Chart', icon: 'bi-radar' }
    ]

    // Available data sources
    const availableDataSources = [
      { id: 'assets', label: 'Current Assets', description: 'Portfolio asset allocation and values' },
      { id: 'income_projections', label: 'Income Projections', description: 'Projected retirement income over time' },
      { id: 'asset_timeline', label: 'Asset Timeline', description: 'Asset growth and depletion timeline' },
      { id: 'expenses', label: 'Expenses', description: 'Current and projected expenses' },
      { id: 'tax_analysis', label: 'Tax Analysis', description: 'Tax implications and bracket analysis' },
      { id: 'monte_carlo', label: 'Monte Carlo Results', description: 'Probability distribution of outcomes' },
      { id: 'social_security', label: 'Social Security', description: 'Social Security claiming strategies' },
      { id: 'irmaa_analysis', label: 'IRMAA Analysis', description: 'Medicare premium impact analysis' },
      { id: 'roth_conversion', label: 'Roth Conversion', description: 'Roth conversion strategy analysis' }
    ]

    // Color schemes
    const colorSchemes = [
      {
        id: 'professional',
        label: 'Professional',
        colors: ['#0d6efd', '#198754', '#dc3545', '#fd7e14', '#6f42c1', '#20c997']
      },
      {
        id: 'vibrant',
        label: 'Vibrant',
        colors: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
      },
      {
        id: 'muted',
        label: 'Muted',
        colors: ['#8da0cb', '#fc8d62', '#66c2a5', '#e78ac3', '#a6d854', '#ffd92f']
      },
      {
        id: 'monochrome',
        label: 'Monochrome',
        colors: ['#333333', '#666666', '#999999', '#cccccc', '#555555', '#aaaaaa']
      },
      {
        id: 'financial',
        label: 'Financial',
        colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
      }
    ]

    // Computed properties
    const currentYear = computed(() => new Date().getFullYear())
    
    const isTimelineChart = computed(() => {
      return ['line', 'area', 'timeline'].includes(localConfig.value.chart_type)
    })

    const isBarChart = computed(() => {
      return ['bar', 'column'].includes(localConfig.value.chart_type)
    })

    const hasAxes = computed(() => {
      return !['pie', 'doughnut', 'radar'].includes(localConfig.value.chart_type)
    })

    // Methods
    const getDataSourceDescription = (sourceId) => {
      const source = availableDataSources.find(s => s.id === sourceId)
      return source?.description || ''
    }

    const updateChartType = (chartType) => {
      localConfig.value.chart_type = chartType
      
      // Set appropriate defaults for chart type
      if (chartType === 'pie' || chartType === 'doughnut') {
        localConfig.value.show_legend = true
        localConfig.value.legend_position = 'right'
      } else if (isTimelineChart.value) {
        localConfig.value.show_projections = true
      }
      
      onConfigChange()
    }

    const updateColorScheme = (schemeId) => {
      localConfig.value.color_scheme = schemeId
      onConfigChange()
    }

    const onConfigChange = () => {
      emit('config-updated', localConfig.value)
      updatePreview()
    }

    const updatePreview = async () => {
      isGeneratingPreview.value = true
      
      await nextTick()
      
      try {
        if (previewChart.value) {
          previewChart.value.destroy()
        }
        
        const chartData = generateSampleChartData()
        const chartOptions = generateChartOptions()
        
        previewChart.value = new Chart(previewCanvas.value, {
          type: getChartJsType(localConfig.value.chart_type),
          data: chartData,
          options: chartOptions
        })
      } catch (error) {
        console.error('Error updating chart preview:', error)
      } finally {
        isGeneratingPreview.value = false
      }
    }

    const generateSampleChartData = () => {
      const scheme = colorSchemes.find(s => s.id === localConfig.value.color_scheme)
      const colors = scheme?.colors || colorSchemes[0].colors

      switch (localConfig.value.data_source) {
        case 'assets':
          return {
            labels: ['401(k)', 'Roth IRA', 'Taxable Investments', 'Real Estate'],
            datasets: [{
              label: 'Asset Values',
              data: [450000, 85000, 125000, 200000],
              backgroundColor: colors.slice(0, 4),
              borderWidth: 1
            }]
          }
        
        case 'income_projections':
          const years = Array.from({ length: localConfig.value.projection_years }, 
            (_, i) => localConfig.value.start_year + i)
          const incomeData = years.map((_, i) => 75000 + (i * 2000))
          
          return {
            labels: years.filter((_, i) => i % 5 === 0), // Every 5 years
            datasets: [{
              label: 'Projected Income',
              data: incomeData.filter((_, i) => i % 5 === 0),
              backgroundColor: colors[0],
              borderColor: colors[0],
              fill: localConfig.value.chart_type === 'area'
            }]
          }
        
        default:
          return {
            labels: ['Category A', 'Category B', 'Category C', 'Category D'],
            datasets: [{
              label: 'Sample Data',
              data: [300, 150, 100, 200],
              backgroundColor: colors.slice(0, 4)
            }]
          }
      }
    }

    const generateChartOptions = () => {
      const options = {
        responsive: false,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: localConfig.value.show_legend,
            position: localConfig.value.legend_position
          },
          title: {
            display: localConfig.value.show_title && localConfig.value.title,
            text: localConfig.value.title
          }
        },
        animation: {
          duration: localConfig.value.enable_animation ? localConfig.value.animation_duration : 0
        }
      }

      // Add axes configuration for applicable chart types
      if (hasAxes.value) {
        options.scales = {
          x: {
            title: {
              display: !!localConfig.value.x_axis_label,
              text: localConfig.value.x_axis_label
            },
            grid: {
              display: localConfig.value.show_grid
            }
          },
          y: {
            beginAtZero: localConfig.value.start_at_zero,
            title: {
              display: !!localConfig.value.y_axis_label,
              text: localConfig.value.y_axis_label
            },
            grid: {
              display: localConfig.value.show_grid
            },
            ticks: {
              callback: function(value) {
                if (localConfig.value.format_currency) {
                  return formatCurrency(value)
                }
                return value
              }
            }
          }
        }
      }

      // Pie/doughnut specific options
      if (localConfig.value.chart_type === 'doughnut') {
        options.cutout = localConfig.value.donut_size + '%'
      }

      return options
    }

    const getChartJsType = (chartType) => {
      const typeMap = {
        'timeline': 'line',
        'area': 'line'
      }
      return typeMap[chartType] || chartType
    }

    const formatCurrency = (value) => {
      if (localConfig.value.abbreviate_numbers) {
        if (value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M'
        if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'K'
      }
      return '$' + value.toLocaleString()
    }

    const applyChanges = () => {
      emit('apply-changes', localConfig.value)
    }

    const resetToDefaults = () => {
      localConfig.value = {
        chart_type: 'bar',
        data_source: 'assets',
        color_scheme: 'professional',
        width: 400,
        height: 300,
        start_year: currentYear.value,
        projection_years: 30,
        show_projections: true,
        smooth_lines: false,
        show_percentages: true,
        show_values: false,
        donut_size: 0,
        orientation: 'vertical',
        stacked: false,
        show_legend: true,
        legend_position: 'bottom',
        show_title: true,
        title: '',
        x_axis_label: '',
        y_axis_label: '',
        start_at_zero: true,
        show_grid: true,
        enable_animation: true,
        animation_duration: 1000,
        format_currency: true,
        abbreviate_numbers: true,
        decimal_places: 0,
        export_quality: 'high',
        transparent_background: false
      }
      onConfigChange()
    }

    const saveAsTemplate = () => {
      // Implement template saving logic
      console.log('Saving chart template:', localConfig.value)
    }

    // Initialize
    onMounted(async () => {
      await nextTick()
      updatePreview()
    })

    // Watch for prop changes
    watch(() => props.chartConfig, (newConfig) => {
      localConfig.value = { ...localConfig.value, ...newConfig }
      updatePreview()
    }, { deep: true })

    return {
      // Refs
      previewCanvas,
      isGeneratingPreview,
      
      // Data
      localConfig,
      availableChartTypes,
      availableDataSources,
      colorSchemes,
      
      // Computed
      currentYear,
      isTimelineChart,
      isBarChart,
      hasAxes,
      
      // Methods
      getDataSourceDescription,
      updateChartType,
      updateColorScheme,
      onConfigChange,
      applyChanges,
      resetToDefaults,
      saveAsTemplate
    }
  }
}
</script>

<style scoped>
.chart-customizer {
  max-height: 800px;
  overflow-y: auto;
}

.config-group {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.config-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.config-subtitle {
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Chart Type Selection */
.chart-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 0.5rem;
}

.chart-type-option {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 0.75rem 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-type-option:hover {
  border-color: #0d6efd;
  background-color: #f8f9ff;
}

.chart-type-option.selected {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

.chart-type-icon {
  font-size: 1.5rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.chart-type-option.selected .chart-type-icon {
  color: #0d6efd;
}

.chart-type-label {
  font-size: 0.75rem;
  color: #495057;
}

/* Color Scheme Selection */
.color-scheme-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.color-scheme-option {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 0.75rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.color-scheme-option:hover {
  border-color: #0d6efd;
}

.color-scheme-option.selected {
  border-color: #0d6efd;
  background-color: #f8f9ff;
}

.color-preview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  margin-bottom: 0.5rem;
  height: 20px;
  border-radius: 0.25rem;
  overflow: hidden;
}

.color-swatch {
  height: 100%;
}

.color-scheme-option small {
  color: #6c757d;
  font-size: 0.75rem;
}

/* Range Input Styling */
.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Chart Preview */
.chart-preview-container {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 1rem;
  text-align: center;
  min-height: 200px;
  position: relative;
}

.preview-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.chart-preview-canvas {
  max-width: 100%;
  height: auto;
  border-radius: 0.25rem;
}

/* Form Elements */
.form-label {
  font-size: 0.875rem;
  color: #495057;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-control-sm,
.form-select-sm {
  font-size: 0.875rem;
}

.form-check-label {
  font-size: 0.875rem;
  color: #495057;
}

.form-text {
  font-size: 0.75rem;
  color: #6c757d;
}

.input-group-text {
  font-size: 0.875rem;
  background: #f8f9fa;
}

/* Responsive Design */
@media (max-width: 576px) {
  .chart-type-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .color-scheme-options {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .row .col-6 {
    margin-bottom: 1rem;
  }
}
</style>