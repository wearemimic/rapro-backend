<template>
  <div class="section-preview" :class="{ 'compact': compact }">
    <div v-if="section.type === 'cover'" class="cover-preview">
      <div class="preview-header">
        <div class="logo-placeholder"></div>
        <h4 class="preview-title">{{ data.client?.first_name }} {{ data.client?.last_name }} Report</h4>
        <p class="preview-subtitle">{{ formatDate(new Date()) }}</p>
      </div>
    </div>

    <div v-else-if="section.type === 'summary'" class="summary-preview">
      <h5 class="preview-title">{{ section.title }}</h5>
      <div class="summary-content">
        <div class="key-metrics" v-if="!compact">
          <div class="metric-item">
            <span class="metric-value">${{ formatCurrency(totalAssets) }}</span>
            <span class="metric-label">Total Assets</span>
          </div>
          <div class="metric-item">
            <span class="metric-value">{{ retirementProbability }}%</span>
            <span class="metric-label">Success Rate</span>
          </div>
        </div>
        <div class="summary-text">
          <div class="placeholder-line"></div>
          <div class="placeholder-line short"></div>
          <div class="placeholder-line medium"></div>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'chart'" class="chart-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="chart-placeholder">
        <div v-if="section.config.chart_type === 'pie'" class="pie-chart-mock">
          <div class="pie-segment" style="--color: #0d6efd; --rotation: 0deg; --size: 45%;"></div>
          <div class="pie-segment" style="--color: #20c997; --rotation: 162deg; --size: 30%;"></div>
          <div class="pie-segment" style="--color: #fd7e14; --rotation: 270deg; --size: 25%;"></div>
        </div>
        <div v-else-if="section.config.chart_type === 'line'" class="line-chart-mock">
          <svg viewBox="0 0 200 100" class="chart-svg">
            <polyline 
              points="10,80 40,60 70,45 100,50 130,35 160,40 190,25"
              fill="none" 
              stroke="#0d6efd" 
              stroke-width="2"
            />
          </svg>
        </div>
        <div v-else-if="section.config.chart_type === 'bar'" class="bar-chart-mock">
          <div class="bar" style="height: 70%; background: #0d6efd;"></div>
          <div class="bar" style="height: 45%; background: #20c997;"></div>
          <div class="bar" style="height: 60%; background: #fd7e14;"></div>
          <div class="bar" style="height: 35%; background: #6f42c1;"></div>
        </div>
        <div v-else class="generic-chart">
          <i class="bi-bar-chart-line chart-icon"></i>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'data_table'" class="table-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="table-mock">
        <div class="table-header">
          <div class="table-cell">Asset</div>
          <div class="table-cell">Value</div>
          <div class="table-cell">%</div>
        </div>
        <div class="table-row">
          <div class="table-cell">401(k)</div>
          <div class="table-cell">$450,000</div>
          <div class="table-cell">68%</div>
        </div>
        <div class="table-row">
          <div class="table-cell">Roth IRA</div>
          <div class="table-cell">$85,000</div>
          <div class="table-cell">13%</div>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'monte_carlo'" class="monte-carlo-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="monte-carlo-content">
        <div class="probability-gauge">
          <div class="gauge-fill" style="width: 85%;"></div>
          <span class="gauge-text">85% Success</span>
        </div>
        <div class="confidence-levels" v-if="!compact">
          <div class="level-item">
            <span class="level-percent">90%</span>
            <div class="level-bar" style="width: 78%;"></div>
          </div>
          <div class="level-item">
            <span class="level-percent">75%</span>
            <div class="level-bar" style="width: 85%;"></div>
          </div>
          <div class="level-item">
            <span class="level-percent">50%</span>
            <div class="level-bar" style="width: 92%;"></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'irmaa'" class="irmaa-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="irmaa-content">
        <div class="bracket-indicator">
          <span class="bracket-label">Current Bracket</span>
          <span class="bracket-value">Bracket 2</span>
          <span class="bracket-impact">+$70.90/month</span>
        </div>
        <div class="threshold-chart" v-if="!compact">
          <div class="threshold-bar active"></div>
          <div class="threshold-bar active"></div>
          <div class="threshold-bar"></div>
          <div class="threshold-bar"></div>
          <div class="threshold-bar"></div>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'roth'" class="roth-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="roth-content">
        <div class="conversion-summary">
          <div class="conversion-item">
            <span class="item-label">Annual Conversion</span>
            <span class="item-value">$50,000</span>
          </div>
          <div class="conversion-item">
            <span class="item-label">Tax Cost</span>
            <span class="item-value">$12,000</span>
          </div>
          <div class="conversion-item">
            <span class="item-label">Break-even</span>
            <span class="item-value">7 years</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'recommendations'" class="recommendations-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="recommendations-list">
        <div class="recommendation-item">
          <i class="bi-1-circle priority-icon"></i>
          <span class="recommendation-text">Optimize tax bracket management</span>
        </div>
        <div class="recommendation-item">
          <i class="bi-2-circle priority-icon"></i>
          <span class="recommendation-text">Consider Roth conversions</span>
        </div>
        <div class="recommendation-item" v-if="!compact">
          <i class="bi-3-circle priority-icon"></i>
          <span class="recommendation-text">Review asset allocation</span>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'toc'" class="toc-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="toc-list">
        <div class="toc-item">
          <span class="toc-title">Executive Summary</span>
          <span class="toc-page">2</span>
        </div>
        <div class="toc-item">
          <span class="toc-title">Current Financial Position</span>
          <span class="toc-page">3</span>
        </div>
        <div class="toc-item" v-if="!compact">
          <span class="toc-title">Recommendations</span>
          <span class="toc-page">5</span>
        </div>
      </div>
    </div>

    <div v-else-if="section.type === 'page_break'" class="page-break-preview">
      <div class="page-break-indicator">
        <i class="bi-arrow-down-square"></i>
        <span>Page Break</span>
      </div>
    </div>

    <div v-else-if="section.type === 'spacer'" class="spacer-preview">
      <div class="spacer-indicator">
        <i class="bi-distribute-vertical"></i>
        <span>Spacer ({{ section.config.height }})</span>
      </div>
    </div>

    <div v-else class="generic-preview">
      <h5 class="preview-title" v-if="!compact">{{ section.title }}</h5>
      <div class="generic-content">
        <i :class="section.icon" class="generic-icon"></i>
        <div class="generic-text">
          <div class="placeholder-line"></div>
          <div class="placeholder-line short" v-if="!compact"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SectionPreview',
  props: {
    section: {
      type: Object,
      required: true
    },
    data: {
      type: Object,
      default: () => ({})
    },
    compact: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const totalAssets = computed(() => {
      if (!props.data.assets) return 0
      return props.data.assets.reduce((sum, asset) => sum + asset.value, 0)
    })

    const retirementProbability = computed(() => {
      return 85 // Mock probability
    })

    const formatCurrency = (amount) => {
      return (amount / 1000).toFixed(0) + 'K'
    }

    const formatDate = (date) => {
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    }

    return {
      totalAssets,
      retirementProbability,
      formatCurrency,
      formatDate
    }
  }
}
</script>

<style scoped>
.section-preview {
  min-height: 120px;
}

.section-preview.compact {
  min-height: 60px;
}

.preview-title {
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

/* Cover Preview */
.cover-preview {
  text-align: center;
  padding: 1rem;
}

.logo-placeholder {
  width: 60px;
  height: 40px;
  background: #e9ecef;
  margin: 0 auto 1rem;
  border-radius: 0.25rem;
}

/* Summary Preview */
.key-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-item {
  text-align: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
}

.metric-value {
  display: block;
  font-weight: bold;
  color: #0d6efd;
  font-size: 1.1rem;
}

.metric-label {
  display: block;
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Chart Previews */
.chart-placeholder {
  height: 120px;
  background: #f8f9fa;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pie-chart-mock {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: relative;
  background: conic-gradient(
    #0d6efd 0deg 162deg,
    #20c997 162deg 270deg,
    #fd7e14 270deg 360deg
  );
}

.line-chart-mock {
  width: 100%;
  height: 60px;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.bar-chart-mock {
  display: flex;
  align-items: end;
  gap: 8px;
  height: 60px;
  width: 120px;
}

.bar {
  flex: 1;
  border-radius: 2px 2px 0 0;
}

.generic-chart {
  font-size: 2rem;
  color: #6c757d;
}

/* Table Preview */
.table-mock {
  font-size: 0.875rem;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 0.375rem 0.375rem 0 0;
  font-weight: bold;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 0.5rem;
  padding: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.table-cell {
  padding: 0.25rem;
}

/* Monte Carlo Preview */
.probability-gauge {
  background: #e9ecef;
  height: 30px;
  border-radius: 15px;
  position: relative;
  margin-bottom: 1rem;
  overflow: hidden;
}

.gauge-fill {
  background: linear-gradient(90deg, #20c997, #0d6efd);
  height: 100%;
  border-radius: 15px;
  position: relative;
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-weight: bold;
  color: white;
  font-size: 0.875rem;
}

.confidence-levels {
  display: grid;
  gap: 0.5rem;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.level-percent {
  font-weight: bold;
  min-width: 35px;
}

.level-bar {
  height: 20px;
  background: #0d6efd;
  border-radius: 10px;
  flex-grow: 1;
  opacity: 0.7;
}

/* IRMAA Preview */
.bracket-indicator {
  text-align: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.bracket-label {
  display: block;
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.bracket-value {
  display: block;
  font-weight: bold;
  color: #0d6efd;
  font-size: 1.1rem;
}

.bracket-impact {
  display: block;
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.threshold-chart {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.threshold-bar {
  width: 20px;
  height: 30px;
  background: #e9ecef;
  border-radius: 2px;
}

.threshold-bar.active {
  background: #fd7e14;
}

/* Roth Preview */
.conversion-summary {
  display: grid;
  gap: 0.75rem;
}

.conversion-item {
  display: flex;
  justify-content: between;
  align-items: center;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 0.375rem;
}

.item-label {
  flex-grow: 1;
  font-size: 0.875rem;
  color: #6c757d;
}

.item-value {
  font-weight: bold;
  color: #0d6efd;
}

/* Recommendations Preview */
.recommendations-list {
  display: grid;
  gap: 0.5rem;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.priority-icon {
  color: #0d6efd;
  font-size: 1rem;
}

.recommendation-text {
  font-size: 0.875rem;
  color: #495057;
}

/* TOC Preview */
.toc-list {
  display: grid;
  gap: 0.5rem;
}

.toc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px dotted #dee2e6;
}

.toc-title {
  font-size: 0.875rem;
}

.toc-page {
  font-weight: bold;
  color: #6c757d;
}

/* Layout Previews */
.page-break-preview,
.spacer-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 0.375rem;
  color: #6c757d;
  font-size: 0.875rem;
}

/* Generic Preview */
.generic-preview {
  padding: 1rem;
}

.generic-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.generic-icon {
  font-size: 1.5rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.generic-text {
  flex-grow: 1;
}

/* Placeholder elements */
.placeholder-line {
  height: 12px;
  background: #e9ecef;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.placeholder-line.short {
  width: 60%;
}

.placeholder-line.medium {
  width: 80%;
}

/* Responsive adjustments */
.compact .key-metrics {
  grid-template-columns: 1fr;
  gap: 0.5rem;
}

.compact .chart-placeholder {
  height: 80px;
}

.compact .generic-content {
  align-items: center;
}

.compact .generic-icon {
  font-size: 1.2rem;
}
</style>