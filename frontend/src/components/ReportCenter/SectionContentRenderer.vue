<template>
  <div class="section-content-renderer">
    <!-- Executive Summary -->
    <div v-if="section.type === 'summary'" class="executive-summary">
      <div v-if="section.config.highlight_key_metrics" class="key-metrics-grid mb-4">
        <div class="metric-card">
          <div class="metric-value">${{ formatCurrency(totalAssets) }}</div>
          <div class="metric-label">Total Assets</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ successProbability }}%</div>
          <div class="metric-label">Success Probability</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">${{ formatCurrency(projectedIncome) }}</div>
          <div class="metric-label">Retirement Income</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{{ retirementAge }}</div>
          <div class="metric-label">Retirement Age</div>
        </div>
      </div>

      <div class="summary-content">
        <div v-if="section.config.bullet_points" class="summary-bullets">
          <h6>Key Findings:</h6>
          <ul class="findings-list">
            <li>Current retirement plan shows <strong>{{ successProbability }}% probability</strong> of meeting income goals</li>
            <li>Total portfolio value of <strong>${{ formatNumber(totalAssets) }}</strong> across all accounts</li>
            <li>Projected annual retirement income of <strong>${{ formatNumber(projectedIncome) }}</strong></li>
            <li v-if="hasIrmaaImpact">IRMAA surcharges may apply in <strong>{{ irmaaYears }}</strong> retirement years</li>
            <li v-if="hasRothOpportunity">Roth conversion opportunities identified for tax optimization</li>
          </ul>
        </div>
        <div v-else class="summary-paragraph">
          <p>
            Based on the comprehensive analysis of your current financial situation, this retirement plan 
            demonstrates a <strong>{{ successProbability }}% probability</strong> of successfully meeting your 
            retirement income goals. With total assets of <strong>${{ formatNumber(totalAssets) }}</strong>, 
            the projected annual retirement income is <strong>${{ formatNumber(projectedIncome) }}</strong>.
          </p>
        </div>
      </div>
    </div>

    <!-- Chart Rendering -->
    <div v-else-if="section.type === 'chart'" class="chart-section">
      <div class="chart-container">
        <canvas :ref="`chart-${section.uid}`" class="section-chart"></canvas>
      </div>
      <div v-if="section.config.show_legend" class="chart-legend mt-3">
        <div class="legend-items">
          <div v-for="item in chartLegend" :key="item.label" class="legend-item">
            <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
            <span class="legend-label">{{ item.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div v-else-if="section.type === 'data_table'" class="data-table-section">
      <div class="table-responsive">
        <table class="table table-striped" :class="{ 'table-striped': section.config.alternating_rows }">
          <thead class="table-dark">
            <tr>
              <th v-for="column in tableColumns" :key="column.key">{{ column.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableData" :key="row.id">
              <td v-for="column in tableColumns" :key="column.key">
                {{ formatTableValue(row[column.key], column.type) }}
              </td>
            </tr>
            <tr v-if="section.config.show_totals" class="table-warning fw-bold">
              <td>{{ tableTotalsLabel }}</td>
              <td v-for="column in tableColumns.slice(1)" :key="column.key">
                {{ formatTableValue(getTotalValue(column.key), column.type) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Monte Carlo Analysis -->
    <div v-else-if="section.type === 'monte_carlo'" class="monte-carlo-section">
      <div class="probability-summary mb-4">
        <div class="probability-gauge">
          <div class="gauge-container">
            <div class="gauge-fill" :style="{ width: `${successProbability}%` }"></div>
            <div class="gauge-text">
              <strong>{{ successProbability }}%</strong>
              <small class="d-block">Success Rate</small>
            </div>
          </div>
        </div>
      </div>

      <div class="confidence-analysis">
        <h6>Confidence Levels</h6>
        <div class="confidence-grid">
          <div 
            v-for="level in section.config.confidence_levels" 
            :key="level"
            class="confidence-item"
          >
            <div class="confidence-header">
              <span class="confidence-percent">{{ level }}%</span>
              <span class="confidence-label">Confidence</span>
            </div>
            <div class="confidence-bar">
              <div 
                class="bar-fill"
                :style="{ width: `${getConfidenceValue(level)}%` }"
              ></div>
            </div>
            <div class="confidence-value">
              ${{ formatNumber(getConfidenceAmount(level)) }} remaining
            </div>
          </div>
        </div>
      </div>

      <div v-if="section.config.show_histogram" class="histogram-section mt-4">
        <h6>Distribution of Outcomes</h6>
        <div class="histogram-chart">
          <canvas :ref="`histogram-${section.uid}`" class="histogram-canvas"></canvas>
        </div>
      </div>
    </div>

    <!-- IRMAA Analysis -->
    <div v-else-if="section.type === 'irmaa'" class="irmaa-section">
      <div class="current-status mb-4">
        <div class="status-card">
          <h6>Current IRMAA Status</h6>
          <div class="row">
            <div class="col-md-4 text-center">
              <div class="bracket-indicator">
                <span class="bracket-number">{{ currentBracket }}</span>
                <small class="d-block">Current Bracket</small>
              </div>
            </div>
            <div class="col-md-4 text-center">
              <div class="premium-impact">
                <span class="impact-amount">+${{ monthlyIrmaa }}</span>
                <small class="d-block">Monthly Surcharge</small>
              </div>
            </div>
            <div class="col-md-4 text-center">
              <div class="annual-impact">
                <span class="annual-amount">${{ formatNumber(monthlyIrmaa * 12) }}</span>
                <small class="d-block">Annual Impact</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="section.config.show_brackets" class="bracket-thresholds mb-4">
        <h6>IRMAA Bracket Thresholds {{ section.config.inflation_adjusted ? '(Inflation Adjusted)' : '' }}</h6>
        <div class="thresholds-table">
          <div class="threshold-row" v-for="(threshold, index) in irmaaThresholds" :key="index">
            <div class="bracket-level">Bracket {{ index + 1 }}</div>
            <div class="threshold-range">${{ formatNumber(threshold.min) }} - ${{ formatNumber(threshold.max) }}</div>
            <div class="surcharge-amount">+${{ threshold.surcharge }}/month</div>
          </div>
        </div>
      </div>

      <div v-if="section.config.yearly_projections" class="yearly-projections">
        <h6>{{ section.config.projection_years }}-Year IRMAA Projections</h6>
        <div class="projections-chart">
          <canvas :ref="`irmaa-${section.uid}`" class="projections-canvas"></canvas>
        </div>
      </div>
    </div>

    <!-- Roth Conversion Analysis -->
    <div v-else-if="section.type === 'roth'" class="roth-section">
      <div class="conversion-strategy mb-4">
        <div class="strategy-summary">
          <div class="row">
            <div class="col-md-3 text-center">
              <div class="strategy-metric">
                <span class="metric-value">${{ formatNumber(rothConversionAmount) }}</span>
                <small class="d-block">Annual Conversion</small>
              </div>
            </div>
            <div class="col-md-3 text-center">
              <div class="strategy-metric">
                <span class="metric-value">${{ formatNumber(taxCost) }}</span>
                <small class="d-block">Tax Cost</small>
              </div>
            </div>
            <div class="col-md-3 text-center">
              <div class="strategy-metric">
                <span class="metric-value">{{ breakevenYears }} years</span>
                <small class="d-block">Break-even</small>
              </div>
            </div>
            <div class="col-md-3 text-center">
              <div class="strategy-metric">
                <span class="metric-value">${{ formatNumber(lifetimeSavings) }}</span>
                <small class="d-block">Lifetime Savings</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="section.config.show_tax_impact" class="tax-impact-analysis mb-4">
        <h6>Tax Impact Analysis</h6>
        <div class="tax-comparison">
          <div class="comparison-chart">
            <canvas :ref="`roth-tax-${section.uid}`" class="tax-chart-canvas"></canvas>
          </div>
        </div>
      </div>

      <div v-if="section.config.breakeven_analysis" class="breakeven-analysis mb-4">
        <h6>Break-even Analysis</h6>
        <p class="analysis-text">
          Based on current tax rates and projected growth, the Roth conversion strategy will break even 
          in <strong>{{ breakevenYears }} years</strong>. After this point, the tax-free growth and 
          distributions from the Roth IRA will provide increasing value compared to keeping funds 
          in traditional tax-deferred accounts.
        </p>
      </div>

      <div v-if="section.config.optimal_timing" class="optimal-timing">
        <h6>Optimal Timing Strategy</h6>
        <div class="timing-recommendations">
          <div class="timing-item">
            <strong>Years 1-{{ Math.floor(section.config.conversion_years / 2) }}:</strong>
            Focus on lower tax bracket conversions (${{ formatNumber(rothConversionAmount) }}/year)
          </div>
          <div class="timing-item">
            <strong>Years {{ Math.floor(section.config.conversion_years / 2) + 1 }}-{{ section.config.conversion_years }}:</strong>
            Adjust conversion amounts based on income and tax situation
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-else-if="section.type === 'recommendations'" class="recommendations-section">
      <div class="recommendations-list">
        <div 
          v-for="(recommendation, index) in filteredRecommendations" 
          :key="index"
          class="recommendation-item"
          :class="{ 'high-priority': recommendation.priority === 'high' }"
        >
          <div class="recommendation-header">
            <div class="priority-indicator">
              <span class="priority-number">{{ index + 1 }}</span>
              <span v-if="section.config.priority_ranking" class="priority-level">
                {{ getPriorityLabel(recommendation.priority) }}
              </span>
            </div>
            <h6 class="recommendation-title">{{ recommendation.title }}</h6>
          </div>
          
          <div class="recommendation-content">
            <p>{{ recommendation.description }}</p>
            
            <div v-if="recommendation.impact" class="impact-summary">
              <strong>Expected Impact:</strong> {{ recommendation.impact }}
            </div>
            
            <div v-if="section.config.include_timeline && recommendation.timeline" class="timeline-info">
              <strong>Timeline:</strong> {{ recommendation.timeline }}
            </div>
            
            <div v-if="section.config.action_oriented && recommendation.action" class="action-items">
              <strong>Next Steps:</strong>
              <ul class="action-list">
                <li v-for="action in recommendation.actions" :key="action">{{ action }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tax Strategy -->
    <div v-else-if="section.type === 'tax_strategy'" class="tax-strategy-section">
      <div class="current-situation mb-4">
        <h6>Current Tax Situation</h6>
        <div class="tax-summary-grid">
          <div class="tax-metric">
            <span class="metric-label">Current Bracket</span>
            <span class="metric-value">{{ currentTaxBracket }}%</span>
          </div>
          <div class="tax-metric">
            <span class="metric-label">Effective Rate</span>
            <span class="metric-value">{{ effectiveTaxRate }}%</span>
          </div>
          <div class="tax-metric">
            <span class="metric-label">Annual Tax</span>
            <span class="metric-value">${{ formatNumber(annualTaxes) }}</span>
          </div>
        </div>
      </div>

      <div class="optimization-strategies">
        <h6>Tax Optimization Strategies</h6>
        <div class="strategy-list">
          <div class="strategy-item">
            <h7>Bracket Management</h7>
            <p>Manage income timing to stay within optimal tax brackets during retirement.</p>
          </div>
          <div class="strategy-item">
            <h7>Roth Conversions</h7>
            <p>Convert traditional IRA funds to Roth during lower income years.</p>
          </div>
          <div class="strategy-item">
            <h7>Asset Location</h7>
            <p>Optimize placement of assets between taxable and tax-advantaged accounts.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Generic Content -->
    <div v-else class="generic-section">
      <div class="content-placeholder">
        <div class="placeholder-content">
          <p>{{ section.description || 'This section will contain detailed analysis and recommendations specific to your financial situation.' }}</p>
          
          <div class="placeholder-metrics">
            <div class="row">
              <div class="col-6 col-md-3 mb-3">
                <div class="placeholder-metric">
                  <div class="metric-placeholder"></div>
                  <small class="text-muted">Key Metric 1</small>
                </div>
              </div>
              <div class="col-6 col-md-3 mb-3">
                <div class="placeholder-metric">
                  <div class="metric-placeholder"></div>
                  <small class="text-muted">Key Metric 2</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, nextTick } from 'vue'

export default {
  name: 'SectionContentRenderer',
  props: {
    section: {
      type: Object,
      required: true
    },
    data: {
      type: Object,
      default: () => ({})
    },
    settings: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    // Sample data computations
    const totalAssets = computed(() => {
      if (!props.data.assets) return 660000 // Mock total
      return props.data.assets.reduce((sum, asset) => sum + asset.value, 0)
    })

    const successProbability = computed(() => 85) // Mock value
    const projectedIncome = computed(() => 75000) // Mock value
    const retirementAge = computed(() => 65) // Mock value
    const hasIrmaaImpact = computed(() => true) // Mock
    const irmaaYears = computed(() => 15) // Mock
    const hasRothOpportunity = computed(() => true) // Mock

    // Chart data
    const chartLegend = computed(() => [
      { label: '401(k)', color: '#0d6efd' },
      { label: 'Roth IRA', color: '#20c997' },
      { label: 'Taxable', color: '#fd7e14' }
    ])

    // Table data
    const tableColumns = computed(() => {
      if (props.section.config.data_source === 'assets_detailed') {
        return [
          { key: 'name', label: 'Asset', type: 'text' },
          { key: 'value', label: 'Current Value', type: 'currency' },
          { key: 'allocation', label: 'Allocation %', type: 'percentage' },
          { key: 'growth_rate', label: 'Growth Rate', type: 'percentage' }
        ]
      }
      return [
        { key: 'name', label: 'Account', type: 'text' },
        { key: 'value', label: 'Value', type: 'currency' },
        { key: 'percentage', label: '%', type: 'percentage' }
      ]
    })

    const tableData = computed(() => {
      // Mock table data based on assets
      return [
        { id: 1, name: '401(k)', value: 450000, percentage: 68, allocation: 68, growth_rate: 7 },
        { id: 2, name: 'Roth IRA', value: 85000, percentage: 13, allocation: 13, growth_rate: 7 },
        { id: 3, name: 'Taxable', value: 125000, percentage: 19, allocation: 19, growth_rate: 6 }
      ]
    })

    const tableTotalsLabel = computed(() => 'Total')

    // IRMAA data
    const currentBracket = computed(() => 2)
    const monthlyIrmaa = computed(() => 70.90)
    const irmaaThresholds = computed(() => [
      { min: 0, max: 103000, surcharge: 0 },
      { min: 103000, max: 129000, surcharge: 70.90 },
      { min: 129000, max: 161000, surcharge: 177.10 },
      { min: 161000, max: 193000, surcharge: 283.50 },
      { min: 193000, max: 999999, surcharge: 389.90 }
    ])

    // Roth conversion data
    const rothConversionAmount = computed(() => 50000)
    const taxCost = computed(() => 12000)
    const breakevenYears = computed(() => 7)
    const lifetimeSavings = computed(() => 85000)

    // Tax data
    const currentTaxBracket = computed(() => 22)
    const effectiveTaxRate = computed(() => 18.5)
    const annualTaxes = computed(() => 15500)

    // Recommendations
    const recommendations = [
      {
        title: 'Optimize Tax Bracket Management',
        description: 'Consider timing income and deductions to stay within optimal tax brackets.',
        priority: 'high',
        impact: 'Potential savings of $3,000-5,000 annually',
        timeline: '3-6 months to implement',
        actions: ['Review current tax withholdings', 'Plan year-end tax strategies', 'Consider Roth conversions']
      },
      {
        title: 'Implement Roth Conversion Strategy',
        description: 'Convert traditional IRA funds to Roth IRA during lower income years.',
        priority: 'medium',
        impact: 'Long-term tax savings of $75,000+',
        timeline: '1-2 years to complete',
        actions: ['Calculate optimal conversion amounts', 'Set up systematic conversions', 'Monitor tax implications']
      },
      {
        title: 'Review Asset Allocation',
        description: 'Ensure investment allocation matches risk tolerance and time horizon.',
        priority: 'medium',
        impact: 'Improved risk-adjusted returns',
        timeline: 'Quarterly reviews',
        actions: ['Analyze current allocation', 'Rebalance as needed', 'Consider tax-efficient funds']
      }
    ]

    const filteredRecommendations = computed(() => {
      const maxRecs = props.section.config.max_recommendations || recommendations.length
      return recommendations.slice(0, maxRecs)
    })

    // Helper methods
    const formatCurrency = (amount) => {
      return (amount / 1000).toFixed(0) + 'K'
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat('en-US').format(num)
    }

    const formatTableValue = (value, type) => {
      switch (type) {
        case 'currency':
          return '$' + formatNumber(value)
        case 'percentage':
          return value + '%'
        default:
          return value
      }
    }

    const getTotalValue = (columnKey) => {
      return tableData.value.reduce((sum, row) => sum + (row[columnKey] || 0), 0)
    }

    const getConfidenceValue = (level) => {
      // Mock confidence values
      const values = { 50: 92, 75: 85, 90: 78 }
      return values[level] || 80
    }

    const getConfidenceAmount = (level) => {
      // Mock remaining amounts at different confidence levels
      const amounts = { 50: 250000, 75: 180000, 90: 120000 }
      return amounts[level] || 150000
    }

    const getPriorityLabel = (priority) => {
      const labels = { high: 'High Priority', medium: 'Medium', low: 'Low' }
      return labels[priority] || priority
    }

    // Chart rendering (placeholder - would use Chart.js in real implementation)
    onMounted(async () => {
      await nextTick()
      // Initialize charts based on section type
      // This would integrate with Chart.js or similar library
    })

    return {
      // Computed data
      totalAssets,
      successProbability,
      projectedIncome,
      retirementAge,
      hasIrmaaImpact,
      irmaaYears,
      hasRothOpportunity,
      chartLegend,
      tableColumns,
      tableData,
      tableTotalsLabel,
      currentBracket,
      monthlyIrmaa,
      irmaaThresholds,
      rothConversionAmount,
      taxCost,
      breakevenYears,
      lifetimeSavings,
      currentTaxBracket,
      effectiveTaxRate,
      annualTaxes,
      filteredRecommendations,

      // Methods
      formatCurrency,
      formatNumber,
      formatTableValue,
      getTotalValue,
      getConfidenceValue,
      getConfidenceAmount,
      getPriorityLabel
    }
  }
}
</script>

<style scoped>
.section-content-renderer {
  line-height: 1.6;
  color: #2c3e50;
}

/* Key Metrics Grid */
.key-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 1.5rem;
  border-radius: 0.5rem;
  text-align: center;
  border: 1px solid #dee2e6;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #0d6efd;
  display: block;
}

.metric-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-top: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Summary Content */
.findings-list {
  list-style-type: none;
  padding-left: 0;
}

.findings-list li {
  padding: 0.5rem 0;
  border-left: 4px solid #0d6efd;
  padding-left: 1rem;
  margin-bottom: 0.5rem;
}

/* Chart Styles */
.chart-container {
  height: 300px;
  margin-bottom: 1rem;
}

.section-chart {
  max-width: 100%;
  height: 100%;
}

.chart-legend {
  border-top: 1px solid #e9ecef;
  padding-top: 1rem;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}

/* Table Styles */
.data-table-section {
  overflow-x: auto;
}

/* Monte Carlo Styles */
.probability-gauge {
  margin-bottom: 2rem;
}

.gauge-container {
  background: #e9ecef;
  height: 80px;
  border-radius: 40px;
  position: relative;
  overflow: hidden;
}

.gauge-fill {
  background: linear-gradient(90deg, #28a745, #20c997, #17a2b8);
  height: 100%;
  border-radius: 40px;
  transition: width 0.8s ease;
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
  font-weight: bold;
}

.confidence-grid {
  display: grid;
  gap: 1rem;
}

.confidence-item {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.confidence-percent {
  font-weight: bold;
  color: #0d6efd;
}

.confidence-bar {
  background: #e9ecef;
  height: 20px;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.bar-fill {
  background: #0d6efd;
  height: 100%;
  transition: width 0.6s ease;
}

/* IRMAA Styles */
.status-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.bracket-indicator,
.premium-impact,
.annual-impact {
  text-align: center;
}

.bracket-number,
.impact-amount,
.annual-amount {
  font-size: 1.5rem;
  font-weight: bold;
  color: #dc3545;
  display: block;
}

.thresholds-table {
  background: white;
  border-radius: 0.375rem;
  overflow: hidden;
  border: 1px solid #dee2e6;
}

.threshold-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
}

.threshold-row:last-child {
  border-bottom: none;
}

.bracket-level {
  font-weight: bold;
  color: #495057;
}

.threshold-range {
  font-family: 'Courier New', monospace;
  color: #6c757d;
}

.surcharge-amount {
  font-weight: bold;
  color: #dc3545;
  text-align: right;
}

/* Roth Conversion Styles */
.strategy-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.strategy-metric {
  text-align: center;
}

.strategy-metric .metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #28a745;
  display: block;
}

.timing-recommendations {
  display: grid;
  gap: 1rem;
}

.timing-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
  border-left: 4px solid #28a745;
}

/* Recommendations Styles */
.recommendations-list {
  display: grid;
  gap: 1.5rem;
}

.recommendation-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1.5rem;
  transition: all 0.3s;
}

.recommendation-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.recommendation-item.high-priority {
  border-left: 5px solid #dc3545;
}

.recommendation-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.priority-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.priority-number {
  width: 40px;
  height: 40px;
  background: #0d6efd;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.priority-level {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  text-align: center;
  color: #6c757d;
}

.recommendation-title {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.impact-summary,
.timeline-info {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  color: #495057;
}

.action-list {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}

/* Tax Strategy Styles */
.tax-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.tax-metric {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 0.375rem;
  text-align: center;
  border: 1px solid #dee2e6;
}

.tax-metric .metric-label {
  display: block;
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.tax-metric .metric-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #0d6efd;
}

.strategy-list {
  display: grid;
  gap: 1rem;
}

.strategy-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
  border-left: 4px solid #0d6efd;
}

.strategy-item h7 {
  font-weight: bold;
  color: #2c3e50;
  display: block;
  margin-bottom: 0.5rem;
}

/* Generic/Placeholder Styles */
.content-placeholder {
  padding: 2rem;
  text-align: center;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border: 2px dashed #dee2e6;
}

.placeholder-metrics {
  margin-top: 2rem;
}

.placeholder-metric {
  text-align: center;
}

.metric-placeholder {
  height: 40px;
  background: #dee2e6;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .key-metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .threshold-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
    text-align: center;
  }
  
  .recommendation-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>