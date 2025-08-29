<template>
  <div class="sentiment-dashboard">
    <!-- Overview Cards -->
    <div class="row mb-4">
      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-success text-white">
                  <i class="bi bi-emoji-smile"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ sentimentStats.positive || 0 }}</span>
                <span class="d-block fs-6 text-success">Positive Communications</span>
                <small class="text-muted">{{ getPercentage(sentimentStats.positive) }}% of total</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-danger text-white">
                  <i class="bi bi-emoji-frown"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ sentimentStats.negative || 0 }}</span>
                <span class="d-block fs-6 text-danger">Negative Communications</span>
                <small class="text-muted">{{ getPercentage(sentimentStats.negative) }}% of total</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-secondary text-white">
                  <i class="bi bi-emoji-neutral"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ sentimentStats.neutral || 0 }}</span>
                <span class="d-block fs-6 text-secondary">Neutral Communications</span>
                <small class="text-muted">{{ getPercentage(sentimentStats.neutral) }}% of total</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6 mb-3">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-shrink-0">
                <div class="avatar avatar-sm avatar-circle bg-info text-white">
                  <i class="bi bi-bar-chart"></i>
                </div>
              </div>
              <div class="flex-grow-1 ms-3">
                <span class="d-block h5 mb-0">{{ averageSentiment }}</span>
                <span class="d-block fs-6 text-info">Average Sentiment</span>
                <small class="text-muted">{{ getSentimentTrend() }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="row mb-4">
      <!-- Sentiment Distribution Chart -->
      <div class="col-lg-6 mb-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-transparent border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Sentiment Distribution</h6>
              <div class="dropdown">
                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                  {{ selectedPeriod }}
                </button>
                <ul class="dropdown-menu">
                  <li><button class="dropdown-item" @click="setPeriod('7 days')">Last 7 days</button></li>
                  <li><button class="dropdown-item" @click="setPeriod('30 days')">Last 30 days</button></li>
                  <li><button class="dropdown-item" @click="setPeriod('90 days')">Last 90 days</button></li>
                </ul>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div class="sentiment-donut-container">
              <canvas ref="sentimentDonutChart" width="300" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Sentiment Trend Chart -->
      <div class="col-lg-6 mb-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-transparent border-bottom">
            <h6 class="mb-0">Sentiment Trend</h6>
          </div>
          <div class="card-body">
            <div class="sentiment-line-container">
              <canvas ref="sentimentTrendChart" width="400" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Analysis -->
    <div class="row">
      <!-- High Priority Communications -->
      <div class="col-lg-4 mb-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-exclamation-triangle text-warning me-2"></i>
              High Priority
            </h6>
            <span class="badge bg-warning">{{ highPriorityItems.length }}</span>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                v-for="item in highPriorityItems.slice(0, 5)" 
                :key="item.id"
                class="list-group-item border-0 py-2 px-3"
              >
                <div class="d-flex align-items-center">
                  <div 
                    class="avatar avatar-xs avatar-circle me-2"
                    :class="getSentimentAvatarClass(item.sentiment)"
                  >
                    <i :class="getSentimentIcon(item.sentiment)"></i>
                  </div>
                  <div class="flex-grow-1 min-w-0">
                    <h6 class="text-truncate mb-0 fs-6">{{ item.subject }}</h6>
                    <small class="text-muted">{{ item.from }} • {{ formatDate(item.date) }}</small>
                  </div>
                  <div class="flex-shrink-0">
                    <span class="badge bg-danger badge-sm">{{ item.priority }}%</span>
                  </div>
                </div>
              </div>
              
              <div v-if="highPriorityItems.length === 0" class="text-center py-4">
                <i class="bi bi-check-circle text-success display-4 mb-2"></i>
                <p class="text-muted mb-0">No high priority communications</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sentiment Breakdown by Type -->
      <div class="col-lg-4 mb-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-transparent border-bottom">
            <h6 class="mb-0">
              <i class="bi bi-pie-chart text-primary me-2"></i>
              By Communication Type
            </h6>
          </div>
          <div class="card-body">
            <div 
              v-for="type in communicationTypes" 
              :key="type.name"
              class="d-flex justify-content-between align-items-center mb-3"
            >
              <div class="d-flex align-items-center">
                <i :class="type.icon" class="me-2 text-primary"></i>
                <span>{{ type.name }}</span>
              </div>
              <div class="d-flex align-items-center">
                <div class="sentiment-mini-bars me-2">
                  <div 
                    class="sentiment-bar bg-success" 
                    :style="{ width: (type.positive / type.total * 40) + 'px' }"
                    :title="`${type.positive} positive`"
                  ></div>
                  <div 
                    class="sentiment-bar bg-secondary" 
                    :style="{ width: (type.neutral / type.total * 40) + 'px' }"
                    :title="`${type.neutral} neutral`"
                  ></div>
                  <div 
                    class="sentiment-bar bg-danger" 
                    :style="{ width: (type.negative / type.total * 40) + 'px' }"
                    :title="`${type.negative} negative`"
                  ></div>
                </div>
                <small class="text-muted">{{ type.total }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent AI Analysis -->
      <div class="col-lg-4 mb-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-robot text-info me-2"></i>
              Recent AI Analysis
            </h6>
            <button class="btn btn-sm btn-outline-primary" @click="refreshAnalysis">
              <i class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                v-for="analysis in recentAnalysis.slice(0, 5)" 
                :key="analysis.id"
                class="list-group-item border-0 py-2 px-3"
              >
                <div class="d-flex align-items-start">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center mb-1">
                      <span 
                        class="badge badge-sm me-2"
                        :class="getSentimentBadgeClass(analysis.sentiment)"
                      >
                        {{ analysis.sentiment }}
                      </span>
                      <span class="badge badge-sm bg-info">{{ analysis.confidence }}%</span>
                    </div>
                    <h6 class="text-truncate mb-1 fs-6">{{ analysis.subject }}</h6>
                    <small class="text-muted">{{ formatDate(analysis.analyzedAt) }}</small>
                  </div>
                </div>
              </div>
              
              <div v-if="recentAnalysis.length === 0" class="text-center py-4">
                <i class="bi bi-robot text-muted display-4 mb-2"></i>
                <p class="text-muted mb-0">No recent AI analysis</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCommunicationStore } from '@/stores/communicationStore'

// Store
const communicationStore = useCommunicationStore()

// Component state
const selectedPeriod = ref('30 days')
const sentimentDonutChart = ref(null)
const sentimentTrendChart = ref(null)

// Charts instances
let donutChartInstance = null
let trendChartInstance = null

// Computed properties
const analytics = computed(() => communicationStore.analytics)

const sentimentStats = computed(() => {
  const stats = analytics.value.sentiment_stats || []
  return stats.reduce((acc, stat) => {
    acc[stat.ai_sentiment_label] = stat.count
    return acc
  }, {})
})

const totalCommunications = computed(() => {
  return Object.values(sentimentStats.value).reduce((sum, count) => sum + count, 0)
})

const averageSentiment = computed(() => {
  const avg = analytics.value.ai_averages?.avg_sentiment || 0
  if (avg > 0.3) return 'Positive'
  if (avg < -0.3) return 'Negative'
  return 'Neutral'
})

// Mock data for detailed components
const highPriorityItems = ref([
  {
    id: 1,
    subject: 'Urgent: Portfolio Review Needed',
    from: 'John Doe',
    date: new Date(Date.now() - 2 * 60 * 60 * 1000),
    sentiment: 'negative',
    priority: 85
  },
  {
    id: 2,
    subject: 'Retirement Planning Questions',
    from: 'Jane Smith',
    date: new Date(Date.now() - 4 * 60 * 60 * 1000),
    sentiment: 'neutral',
    priority: 78
  }
])

const communicationTypes = ref([
  {
    name: 'Email',
    icon: 'bi-envelope',
    positive: 45,
    neutral: 32,
    negative: 12,
    total: 89
  },
  {
    name: 'SMS',
    icon: 'bi-chat-dots',
    positive: 23,
    neutral: 15,
    negative: 8,
    total: 46
  },
  {
    name: 'Calls',
    icon: 'bi-telephone',
    positive: 18,
    neutral: 12,
    negative: 5,
    total: 35
  },
  {
    name: 'Meetings',
    icon: 'bi-calendar',
    positive: 12,
    neutral: 8,
    negative: 2,
    total: 22
  }
])

const recentAnalysis = ref([
  {
    id: 1,
    subject: 'Thank you for the portfolio update',
    sentiment: 'positive',
    confidence: 92,
    analyzedAt: new Date(Date.now() - 1 * 60 * 60 * 1000)
  },
  {
    id: 2,
    subject: 'Concerns about market volatility',
    sentiment: 'negative',
    confidence: 88,
    analyzedAt: new Date(Date.now() - 3 * 60 * 60 * 1000)
  }
])

// Methods
const getPercentage = (count) => {
  if (totalCommunications.value === 0) return 0
  return Math.round((count / totalCommunications.value) * 100)
}

const getSentimentTrend = () => {
  const positive = sentimentStats.value.positive || 0
  const negative = sentimentStats.value.negative || 0
  
  if (positive > negative * 1.5) return '📈 Trending positive'
  if (negative > positive * 1.5) return '📉 Needs attention'
  return '➡️ Stable'
}

const setPeriod = async (period) => {
  selectedPeriod.value = period
  const days = period.includes('7') ? 7 : period.includes('30') ? 30 : 90
  await communicationStore.fetchAnalytics({ days })
  updateCharts()
}

const getSentimentAvatarClass = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bg-success text-white'
    case 'negative': return 'bg-danger text-white'
    case 'neutral': return 'bg-secondary text-white'
    case 'mixed': return 'bg-warning text-white'
    default: return 'bg-light text-muted'
  }
}

const getSentimentIcon = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bi-emoji-smile'
    case 'negative': return 'bi-emoji-frown'
    case 'neutral': return 'bi-emoji-neutral'
    case 'mixed': return 'bi-emoji-expressionless'
    default: return 'bi-dash'
  }
}

const getSentimentBadgeClass = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bg-success'
    case 'negative': return 'bg-danger'
    case 'neutral': return 'bg-secondary'
    case 'mixed': return 'bg-warning'
    default: return 'bg-light text-dark'
  }
}

const formatDate = (date) => {
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const refreshAnalysis = async () => {
  await communicationStore.fetchAnalytics()
  updateCharts()
}

const initializeCharts = () => {
  if (!window.Chart) {
    console.warn('Chart.js not available, skipping chart initialization')
    return
  }

  // Initialize donut chart
  if (sentimentDonutChart.value) {
    const ctx = sentimentDonutChart.value.getContext('2d')
    donutChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Negative', 'Neutral', 'Mixed'],
        datasets: [{
          data: [
            sentimentStats.value.positive || 0,
            sentimentStats.value.negative || 0,
            sentimentStats.value.neutral || 0,
            sentimentStats.value.mixed || 0
          ],
          backgroundColor: [
            '#198754', // success
            '#dc3545', // danger
            '#6c757d', // secondary
            '#ffc107'  // warning
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
  }

  // Initialize trend chart
  if (sentimentTrendChart.value) {
    const ctx = sentimentTrendChart.value.getContext('2d')
    const dailyCounts = analytics.value.daily_counts || []
    
    trendChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: dailyCounts.map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        datasets: [{
          label: 'Communications',
          data: dailyCounts.map(d => d.count),
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    })
  }
}

const updateCharts = () => {
  if (donutChartInstance) {
    donutChartInstance.data.datasets[0].data = [
      sentimentStats.value.positive || 0,
      sentimentStats.value.negative || 0,
      sentimentStats.value.neutral || 0,
      sentimentStats.value.mixed || 0
    ]
    donutChartInstance.update()
  }

  if (trendChartInstance) {
    const dailyCounts = analytics.value.daily_counts || []
    trendChartInstance.data.labels = dailyCounts.map(d => 
      new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    )
    trendChartInstance.data.datasets[0].data = dailyCounts.map(d => d.count)
    trendChartInstance.update()
  }
}

// Lifecycle
onMounted(async () => {
  await communicationStore.fetchAnalytics()
  
  // Initialize charts after a short delay to ensure DOM is ready
  setTimeout(() => {
    initializeCharts()
  }, 100)
})

onUnmounted(() => {
  // Cleanup chart instances
  if (donutChartInstance) {
    donutChartInstance.destroy()
  }
  if (trendChartInstance) {
    trendChartInstance.destroy()
  }
})
</script>

<style scoped>
.sentiment-dashboard {
  padding: 1rem;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1rem;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
  font-size: 0.875rem;
}

.avatar-xs {
  width: 1.5rem;
  height: 1.5rem;
  font-size: 0.75rem;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.25em 0.5em;
}

.sentiment-donut-container,
.sentiment-line-container {
  position: relative;
  height: 300px;
}

.sentiment-mini-bars {
  display: flex;
  gap: 1px;
  height: 8px;
  align-items: end;
}

.sentiment-bar {
  height: 100%;
  min-width: 2px;
  border-radius: 1px;
}

.min-w-0 {
  min-width: 0;
}

.fs-6 {
  font-size: 0.875rem;
}

@media (max-width: 992px) {
  .col-lg-4,
  .col-lg-6 {
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 768px) {
  .sentiment-dashboard {
    padding: 0.5rem;
  }
  
  .col-xl-3,
  .col-md-6 {
    margin-bottom: 1rem;
  }
  
  .card-body {
    padding: 1rem;
  }
  
  .sentiment-donut-container,
  .sentiment-line-container {
    height: 250px;
  }
}

@media (max-width: 576px) {
  .d-flex.justify-content-between {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .dropdown {
    margin-top: 0.5rem;
  }
  
  .sentiment-mini-bars {
    margin-top: 0.25rem;
  }
}
</style>