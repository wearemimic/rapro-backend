<template>
  <div class="admin-analytics">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Analytics</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Platform Analytics</h1>
        </div>
        <div class="col-auto">
          <!-- Analytics Controls -->
          <div class="btn-group me-2">
            <select v-model="selectedPeriod" @change="refreshData" class="form-select">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
          </div>
          <div class="btn-group me-2">
            <button @click="triggerCalculation('revenue')" :disabled="calculating" class="btn btn-outline-success btn-sm">
              <i class="bi-calculator" :class="{ 'spinner-border spinner-border-sm': calculating }"></i>
              Recalc Revenue
            </button>
            <button @click="triggerCalculation('daily')" :disabled="calculating" class="btn btn-outline-info btn-sm">
              <i class="bi-graph-up" :class="{ 'spinner-border spinner-border-sm': calculating }"></i>
              Run All Analytics
            </button>
          </div>
          <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Analytics Navigation Tabs -->
    <div class="row mb-4">
      <div class="col">
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'revenue' }" @click="activeTab = 'revenue'">
              <i class="bi-currency-dollar me-2"></i>Revenue Analytics
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'engagement' }" @click="activeTab = 'engagement'">
              <i class="bi-people me-2"></i>User Engagement
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'portfolio' }" @click="activeTab = 'portfolio'">
              <i class="bi-briefcase me-2"></i>Client Portfolio
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !hasAnyData" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading analytics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <!-- Revenue Analytics Tab -->
    <div v-show="activeTab === 'revenue'" class="tab-content">
      <!-- Revenue Metrics Cards -->
      <div class="row mb-4" v-if="revenueAnalytics?.current_metrics">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-primary">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Monthly Recurring Revenue</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    ${{ formatCurrency(revenueAnalytics.current_metrics.mrr?.value || 0) }}
                  </div>
                  <div class="text-xs" v-if="revenueAnalytics.growth_rates?.mrr">
                    <i class="bi-arrow-up text-success" v-if="revenueAnalytics.growth_rates.mrr > 0"></i>
                    <i class="bi-arrow-down text-danger" v-else-if="revenueAnalytics.growth_rates.mrr < 0"></i>
                    <span :class="getGrowthClass(revenueAnalytics.growth_rates.mrr)">
                      {{ Math.abs(revenueAnalytics.growth_rates.mrr) }}%
                    </span>
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-currency-dollar fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-success">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Annual Recurring Revenue</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    ${{ formatCurrency(revenueAnalytics.current_metrics.arr?.value || 0) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-graph-up fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-info">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Average Revenue Per User</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    ${{ formatCurrency(revenueAnalytics.current_metrics.arpu?.value || 0) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-person-check fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-warning">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Churn Rate</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ (revenueAnalytics.current_metrics.churn_rate?.value || 0).toFixed(2) }}%
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-person-dash fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Revenue Trends Chart -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <div class="row justify-content-between align-items-center">
                <div class="col">
                  <h4 class="card-header-title">Revenue Trends</h4>
                </div>
                <div class="col-auto">
                  <div class="btn-group btn-group-sm">
                    <input type="radio" class="btn-check" name="revenueMetric" id="mrrTrend" v-model="selectedRevenueMetric" value="mrr" @change="updateRevenueChart">
                    <label class="btn btn-outline-primary" for="mrrTrend">MRR</label>
                    <input type="radio" class="btn-check" name="revenueMetric" id="arrTrend" v-model="selectedRevenueMetric" value="arr" @change="updateRevenueChart">
                    <label class="btn btn-outline-primary" for="arrTrend">ARR</label>
                    <input type="radio" class="btn-check" name="revenueMetric" id="arpuTrend" v-model="selectedRevenueMetric" value="arpu" @change="updateRevenueChart">
                    <label class="btn btn-outline-primary" for="arpuTrend">ARPU</label>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-body">
              <canvas id="revenueTrendChart" width="400" height="150"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Subscription Breakdown -->
      <div class="row mb-4">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">Subscription Status</h4>
            </div>
            <div class="card-body">
              <canvas id="subscriptionChart" width="300" height="300"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">Plan Distribution</h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-6">
                  <div class="border-end">
                    <div class="display-6 text-primary">{{ revenueAnalytics?.plan_distribution?.monthly || 0 }}</div>
                    <div class="small text-muted">Monthly Plans</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="display-6 text-success">{{ revenueAnalytics?.plan_distribution?.annual || 0 }}</div>
                  <div class="small text-muted">Annual Plans</div>
                </div>
              </div>
              <hr>
              <canvas id="planRevenueChart" width="300" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Engagement Tab -->
    <div v-show="activeTab === 'engagement'" class="tab-content">
      <!-- Engagement Score Distribution -->
      <div class="row mb-4" v-if="engagementAnalytics?.score_distribution">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h4 class="card-header-title">User Engagement Distribution</h4>
            </div>
            <div class="card-body">
              <canvas id="engagementDistributionChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Engagement Trends -->
      <div class="row mb-4">
        <div class="col-lg-8">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">Engagement Trends</h4>
            </div>
            <div class="card-body">
              <canvas id="engagementTrendsChart" width="400" height="250"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">At-Risk Users</h4>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="display-4 text-danger">{{ engagementAnalytics?.at_risk_users_count || 0 }}</div>
                <div class="text-muted">Users needing attention</div>
              </div>
              <button @click="viewAtRiskUsers" class="btn btn-outline-danger w-100">
                View At-Risk Users
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Usage Metrics -->
      <div class="row mb-4" v-if="engagementAnalytics?.feature_usage">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h4 class="card-header-title">Feature Usage Averages</h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3">
                  <div class="metric-card">
                    <div class="metric-value">{{ (engagementAnalytics.feature_usage.avg_scenarios_created || 0).toFixed(1) }}</div>
                    <div class="metric-label">Avg Scenarios per User</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="metric-card">
                    <div class="metric-value">{{ (engagementAnalytics.feature_usage.avg_clients_added || 0).toFixed(1) }}</div>
                    <div class="metric-label">Avg Clients per User</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="metric-card">
                    <div class="metric-value">{{ (engagementAnalytics.feature_usage.avg_reports_generated || 0).toFixed(1) }}</div>
                    <div class="metric-label">Avg Reports per User</div>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="metric-card">
                    <div class="metric-value">{{ Math.round(engagementAnalytics.feature_usage.avg_session_duration || 0) }}m</div>
                    <div class="metric-label">Avg Session Duration</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Analytics Tab -->
    <div v-show="activeTab === 'portfolio'" class="tab-content">
      <!-- Portfolio Overview -->
      <div class="row mb-4" v-if="portfolioAnalytics?.current_stats">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-primary">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Total Clients</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ formatNumber(portfolioAnalytics.current_stats.total_clients) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-people fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-success">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Total Scenarios</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ formatNumber(portfolioAnalytics.current_stats.total_scenarios) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-graph-up fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-info">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Avg Clients per Advisor</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ (portfolioAnalytics.current_stats.avg_clients_per_advisor || 0).toFixed(1) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-person-badge fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-warning">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Avg Scenarios per Client</div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ (portfolioAnalytics.current_stats.avg_scenarios_per_client || 0).toFixed(1) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi-file-earmark-text fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Portfolio Trends -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h4 class="card-header-title">Portfolio Growth</h4>
            </div>
            <div class="card-body">
              <canvas id="portfolioTrendsChart" width="400" height="200"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Demographics and Features -->
      <div class="row mb-4">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">Client Age Demographics</h4>
            </div>
            <div class="card-body">
              <canvas id="ageDemographicsChart" width="300" height="300"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header">
              <h4 class="card-header-title">Feature Adoption</h4>
            </div>
            <div class="card-body">
              <div v-if="portfolioAnalytics?.feature_adoption" class="row">
                <div class="col-12 mb-3" v-for="(feature, key) in portfolioAnalytics.feature_adoption" :key="key">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <h6 class="mb-0">{{ getFeatureDisplayName(key) }}</h6>
                      <small class="text-muted">{{ feature.count }} scenarios</small>
                    </div>
                    <div class="fw-bold">{{ feature.percentage }}%</div>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div class="progress-bar" :style="{ width: feature.percentage + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Advisors -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h4 class="card-header-title">Top Performing Advisors</h4>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Advisor</th>
                      <th>Company</th>
                      <th>Clients</th>
                      <th>Scenarios</th>
                      <th>Scenarios per Client</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="advisor in portfolioAnalytics?.top_advisors" :key="advisor.advisor_id">
                      <td>
                        <div class="fw-bold">{{ advisor.advisor_name }}</div>
                        <div class="text-muted small">{{ advisor.advisor_email }}</div>
                      </td>
                      <td>{{ advisor.company_name || 'N/A' }}</td>
                      <td>
                        <span class="badge bg-primary rounded-pill">{{ advisor.client_count }}</span>
                      </td>
                      <td>
                        <span class="badge bg-success rounded-pill">{{ advisor.scenario_count }}</span>
                      </td>
                      <td>{{ advisor.avg_scenarios_per_client }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- At-Risk Users Modal -->
    <div class="modal fade" id="atRiskUsersModal" tabindex="-1" aria-labelledby="atRiskUsersModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="atRiskUsersModalLabel">At-Risk Users</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="table-responsive" v-if="atRiskUsers.length">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Engagement Score</th>
                    <th>Risk Factors</th>
                    <th>Subscription</th>
                    <th>Last Activity</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in atRiskUsers" :key="user.user_id">
                    <td>
                      <div class="fw-bold">{{ user.user_name }}</div>
                      <div class="text-muted small">{{ user.user_email }}</div>
                    </td>
                    <td>
                      <div class="progress" style="width: 80px; height: 20px;">
                        <div class="progress-bar bg-danger" :style="{ width: user.engagement_score + '%' }"></div>
                      </div>
                      <small class="text-muted">{{ user.engagement_score }}/100</small>
                    </td>
                    <td>
                      <span v-for="factor in user.risk_factors" :key="factor" class="badge bg-warning me-1">
                        {{ formatRiskFactor(factor) }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="getSubscriptionBadgeClass(user.subscription_status)">
                        {{ user.subscription_status }}
                      </span>
                    </td>
                    <td>{{ formatDate(user.date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-4">
              <div class="text-muted">Loading at-risk users...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminAnalytics',
  data() {
    return {
      loading: false,
      calculating: false,
      error: null,
      selectedPeriod: 30,
      activeTab: 'revenue',
      
      // Data
      revenueAnalytics: null,
      engagementAnalytics: null,
      portfolioAnalytics: null,
      atRiskUsers: [],
      
      // Chart instances
      charts: {},
      
      // UI state
      selectedRevenueMetric: 'mrr',
    }
  },
  computed: {
    hasAnyData() {
      return this.revenueAnalytics || this.engagementAnalytics || this.portfolioAnalytics
    }
  },
  async mounted() {
    await this.loadAnalyticsData()
  },
  beforeUnmount() {
    this.destroyCharts()
  },
  methods: {
    async loadAnalyticsData() {
      this.loading = true
      this.error = null

      try {
        const [revenueResp, engagementResp, portfolioResp] = await Promise.all([
          api.get(`/api/admin/analytics/revenue/?days=${this.selectedPeriod}`),
          api.get(`/api/admin/analytics/engagement/?days=${this.selectedPeriod}`),
          api.get(`/api/admin/analytics/portfolio/?days=${this.selectedPeriod}`)
        ])

        this.revenueAnalytics = revenueResp.data
        this.engagementAnalytics = engagementResp.data
        this.portfolioAnalytics = portfolioResp.data

        // Initialize charts after data load
        await this.$nextTick()
        this.initializeCharts()

      } catch (error) {
        console.error('Failed to load analytics:', error)
        this.error = error.response?.data?.error || 'Failed to load analytics data'
      } finally {
        this.loading = false
      }
    },

    async refreshData() {
      await this.loadAnalyticsData()
    },

    async triggerCalculation(type) {
      this.calculating = true
      
      try {
        await api.post('/api/admin/analytics/calculate/', { type })
        
        // Refresh data after calculation
        await this.loadAnalyticsData()
        
        // Show success toast
        this.$toast.success(`${type === 'revenue' ? 'Revenue' : 'All'} analytics recalculated successfully`)
        
      } catch (error) {
        console.error('Failed to trigger calculation:', error)
        this.$toast.error('Failed to trigger analytics calculation')
      } finally {
        this.calculating = false
      }
    },

    async viewAtRiskUsers() {
      try {
        const response = await api.get(`/api/admin/analytics/engagement/?days=${this.selectedPeriod}&at_risk_only=true`)
        this.atRiskUsers = response.data.at_risk_users
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('atRiskUsersModal'))
        modal.show()
        
      } catch (error) {
        console.error('Failed to load at-risk users:', error)
        this.$toast.error('Failed to load at-risk users')
      }
    },

    initializeCharts() {
      this.destroyCharts()
      
      if (this.activeTab === 'revenue' && this.revenueAnalytics) {
        this.createRevenueCharts()
      } else if (this.activeTab === 'engagement' && this.engagementAnalytics) {
        this.createEngagementCharts()  
      } else if (this.activeTab === 'portfolio' && this.portfolioAnalytics) {
        this.createPortfolioCharts()
      }
    },

    createRevenueCharts() {
      // Revenue Trend Chart
      const revenueTrendCtx = document.getElementById('revenueTrendChart')
      if (revenueTrendCtx && this.revenueAnalytics.revenue_trends?.[this.selectedRevenueMetric]) {
        const trendData = this.revenueAnalytics.revenue_trends[this.selectedRevenueMetric]
        
        this.charts.revenueTrend = new Chart(revenueTrendCtx, {
          type: 'line',
          data: {
            labels: trendData.map(d => this.formatDate(d.date, 'short')),
            datasets: [{
              label: this.selectedRevenueMetric.toUpperCase(),
              data: trendData.map(d => d.value),
              borderColor: '#4e73df',
              backgroundColor: 'rgba(78, 115, 223, 0.1)',
              fill: true,
              tension: 0.3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: (value) => this.selectedRevenueMetric.includes('rate') ? value + '%' : '$' + this.formatNumber(value)
                }
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const value = context.parsed.y
                    return this.selectedRevenueMetric.includes('rate') 
                      ? value.toFixed(2) + '%' 
                      : '$' + this.formatNumber(value)
                  }
                }
              }
            }
          }
        })
      }

      // Subscription Status Chart
      const subscriptionCtx = document.getElementById('subscriptionChart')
      if (subscriptionCtx && this.revenueAnalytics.subscription_breakdown) {
        const breakdown = this.revenueAnalytics.subscription_breakdown
        
        this.charts.subscription = new Chart(subscriptionCtx, {
          type: 'doughnut',
          data: {
            labels: ['Active', 'Trial', 'Past Due', 'Canceled'],
            datasets: [{
              data: [breakdown.active, breakdown.trialing, breakdown.past_due, breakdown.canceled],
              backgroundColor: ['#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
          }
        })
      }

      // Plan Revenue Chart
      const planRevenueCtx = document.getElementById('planRevenueChart')
      if (planRevenueCtx && this.revenueAnalytics.revenue_by_plan) {
        const monthlyData = this.revenueAnalytics.revenue_by_plan.monthly || []
        const annualData = this.revenueAnalytics.revenue_by_plan.annual || []
        
        const labels = monthlyData.map(d => this.formatDate(d.date, 'short'))
        
        this.charts.planRevenue = new Chart(planRevenueCtx, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Monthly Plans',
                data: monthlyData.map(d => d.value),
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
              },
              {
                label: 'Annual Plans',
                data: annualData.map(d => d.value),
                borderColor: '#1cc88a',
                backgroundColor: 'rgba(28, 200, 138, 0.1)',
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: (value) => '$' + this.formatNumber(value)
                }
              }
            }
          }
        })
      }
    },

    createEngagementCharts() {
      // Engagement Distribution Chart
      const distributionCtx = document.getElementById('engagementDistributionChart')
      if (distributionCtx && this.engagementAnalytics.score_distribution) {
        const distribution = this.engagementAnalytics.score_distribution
        
        this.charts.engagementDistribution = new Chart(distributionCtx, {
          type: 'bar',
          data: {
            labels: Object.keys(distribution),
            datasets: [{
              label: 'Users',
              data: Object.values(distribution),
              backgroundColor: ['#e74a3b', '#f6c23e', '#36b9cc', '#1cc88a', '#28a745']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        })
      }

      // Engagement Trends Chart
      const trendsCtx = document.getElementById('engagementTrendsChart')
      if (trendsCtx && this.engagementAnalytics.engagement_trends) {
        const trends = this.engagementAnalytics.engagement_trends
        
        this.charts.engagementTrends = new Chart(trendsCtx, {
          type: 'line',
          data: {
            labels: trends.map(d => this.formatDate(d.date, 'short')),
            datasets: [
              {
                label: 'Avg Engagement Score',
                data: trends.map(d => d.avg_engagement_score || 0),
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                yAxisID: 'y'
              },
              {
                label: 'At-Risk Users',
                data: trends.map(d => d.total_users_at_risk || 0),
                borderColor: '#e74a3b',
                backgroundColor: 'rgba(231, 74, 59, 0.1)',
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                grid: {
                  drawOnChartArea: false,
                }
              }
            }
          }
        })
      }
    },

    createPortfolioCharts() {
      // Portfolio Trends Chart
      const portfolioTrendsCtx = document.getElementById('portfolioTrendsChart')
      if (portfolioTrendsCtx && this.portfolioAnalytics.portfolio_trends) {
        const trends = this.portfolioAnalytics.portfolio_trends
        
        this.charts.portfolioTrends = new Chart(portfolioTrendsCtx, {
          type: 'line',
          data: {
            labels: trends.map(d => this.formatDate(d.date, 'short')),
            datasets: [
              {
                label: 'Total Clients',
                data: trends.map(d => d.total_clients),
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                yAxisID: 'y'
              },
              {
                label: 'Total Scenarios',
                data: trends.map(d => d.total_scenarios),
                borderColor: '#1cc88a',
                backgroundColor: 'rgba(28, 200, 138, 0.1)',
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                grid: {
                  drawOnChartArea: false,
                }
              }
            }
          }
        })
      }

      // Age Demographics Chart
      const ageDemographicsCtx = document.getElementById('ageDemographicsChart')
      if (ageDemographicsCtx && this.portfolioAnalytics.age_demographics) {
        const demographics = this.portfolioAnalytics.age_demographics
        
        this.charts.ageDemographics = new Chart(ageDemographicsCtx, {
          type: 'doughnut',
          data: {
            labels: demographics.map(d => d.age_group),
            datasets: [{
              data: demographics.map(d => d.count),
              backgroundColor: ['#36b9cc', '#1cc88a', '#f6c23e']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const demo = demographics[context.dataIndex]
                    return `${demo.age_group}: ${demo.count} (${demo.percentage}%)`
                  }
                }
              }
            }
          }
        })
      }
    },

    updateRevenueChart() {
      if (this.charts.revenueTrend) {
        this.charts.revenueTrend.destroy()
      }
      this.createRevenueCharts()
    },

    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy()
      })
      this.charts = {}
    },

    // Utility Methods
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value)
    },

    formatNumber(value) {
      return new Intl.NumberFormat('en-US').format(value)
    },

    formatDate(dateStr, format = 'long') {
      const date = new Date(dateStr)
      if (format === 'short') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    },

    getGrowthClass(rate) {
      return rate > 0 ? 'text-success' : 'text-danger'
    },

    getFeatureDisplayName(key) {
      const names = {
        roth_conversion: 'Roth Conversion',
        social_security_planning: 'Social Security Planning',
        monte_carlo: 'Monte Carlo Simulation'
      }
      return names[key] || key
    },

    formatRiskFactor(factor) {
      return factor.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    getSubscriptionBadgeClass(status) {
      const classes = {
        active: 'bg-success',
        trialing: 'bg-info',
        past_due: 'bg-warning',
        canceled: 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    }
  },

  watch: {
    activeTab() {
      this.$nextTick(() => {
        this.initializeCharts()
      })
    }
  }
}
</script>

<style scoped>
.admin-analytics {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}

.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}

.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}

.metric-card {
  text-align: center;
  padding: 1rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #5a5c69;
}

.metric-label {
  font-size: 0.875rem;
  color: #858796;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.nav-tabs .nav-link {
  border: none;
  color: #858796;
}

.nav-tabs .nav-link.active {
  background-color: transparent;
  border-bottom: 2px solid #4e73df;
  color: #4e73df;
  font-weight: bold;
}

.progress {
  background-color: #f8f9fc;
}

.card {
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
  border: 1px solid #e3e6f0;
}

.card-header {
  background-color: #f8f9fc;
  border-bottom: 1px solid #e3e6f0;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #5a5c69;
  font-size: 0.875rem;
}

.display-4 {
  font-size: 3rem;
  font-weight: 300;
}

.display-6 {
  font-size: 1.75rem;
  font-weight: 300;
}
</style>