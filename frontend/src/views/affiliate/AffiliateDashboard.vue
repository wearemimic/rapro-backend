<template>
  <div class="affiliate-dashboard">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Affiliate Analytics Dashboard</h1>
        <p class="text-muted">Monitor affiliate program performance and metrics</p>
      </div>
      <div>
        <select v-model="dateRange" class="form-select" @change="refreshData">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="365">Last Year</option>
        </select>
      </div>
    </div>

    <!-- Key Metrics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Total Affiliates</h6>
                <h3 class="mb-0">{{ metrics.totalAffiliates }}</h3>
                <small :class="metrics.affiliateGrowth >= 0 ? 'text-success' : 'text-danger'">
                  <i :class="metrics.affiliateGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                  {{ Math.abs(metrics.affiliateGrowth) }}% vs last period
                </small>
              </div>
              <div class="text-primary">
                <i class="fas fa-users fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Total Clicks</h6>
                <h3 class="mb-0">{{ metrics.totalClicks.toLocaleString() }}</h3>
                <small :class="metrics.clickGrowth >= 0 ? 'text-success' : 'text-danger'">
                  <i :class="metrics.clickGrowth >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
                  {{ Math.abs(metrics.clickGrowth) }}% vs last period
                </small>
              </div>
              <div class="text-info">
                <i class="fas fa-mouse-pointer fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Conversions</h6>
                <h3 class="mb-0">{{ metrics.totalConversions }}</h3>
                <small class="text-muted">
                  {{ metrics.conversionRate.toFixed(2) }}% conversion rate
                </small>
              </div>
              <div class="text-success">
                <i class="fas fa-chart-line fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-2">Revenue Generated</h6>
                <h3 class="mb-0">${{ metrics.totalRevenue.toLocaleString() }}</h3>
                <small class="text-muted">
                  ${{ metrics.avgOrderValue.toFixed(2) }} avg order
                </small>
              </div>
              <div class="text-warning">
                <i class="fas fa-dollar-sign fa-2x"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Performance Trends</h5>
          </div>
          <div class="card-body">
            <div class="btn-group btn-group-sm mb-3" role="group">
              <button
                type="button"
                class="btn"
                :class="trendMetric === 'clicks' ? 'btn-primary' : 'btn-outline-primary'"
                @click="trendMetric = 'clicks'"
              >
                Clicks
              </button>
              <button
                type="button"
                class="btn"
                :class="trendMetric === 'conversions' ? 'btn-primary' : 'btn-outline-primary'"
                @click="trendMetric = 'conversions'"
              >
                Conversions
              </button>
              <button
                type="button"
                class="btn"
                :class="trendMetric === 'revenue' ? 'btn-primary' : 'btn-outline-primary'"
                @click="trendMetric = 'revenue'"
              >
                Revenue
              </button>
            </div>
            <Graph
              v-if="performanceChartData"
              :data="performanceChartData"
              :options="performanceChartOptions"
              :height="300"
              type="line"
            />
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Traffic Sources</h5>
          </div>
          <div class="card-body">
            <Graph
              v-if="trafficSourcesData"
              :data="trafficSourcesData"
              :options="pieChartOptions"
              :height="300"
              type="doughnut"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Top Performers Table -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Top Performing Affiliates</h5>
            <button class="btn btn-sm btn-outline-primary" @click="viewAllAffiliates">
              View All
            </button>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Affiliate</th>
                    <th>Clicks</th>
                    <th>Conversions</th>
                    <th>Revenue</th>
                    <th>Rate</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="affiliate in topAffiliates" :key="affiliate.id">
                    <td>
                      <div>
                        <strong>{{ affiliate.business_name }}</strong>
                        <br>
                        <small class="text-muted">{{ affiliate.affiliate_code }}</small>
                      </div>
                    </td>
                    <td>{{ affiliate.clicks.toLocaleString() }}</td>
                    <td>
                      {{ affiliate.conversions }}
                      <br>
                      <small class="text-muted">{{ affiliate.conversionRate.toFixed(1) }}%</small>
                    </td>
                    <td>${{ affiliate.revenue.toLocaleString() }}</td>
                    <td>
                      <span class="badge bg-success">
                        {{ affiliate.commission_rate }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Conversions</h5>
            <span class="badge bg-primary">Live</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Affiliate</th>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Commission</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="conversion in recentConversions" :key="conversion.id">
                    <td>
                      <small>{{ formatTimeAgo(conversion.created_at) }}</small>
                    </td>
                    <td>
                      <small>{{ conversion.affiliate_name }}</small>
                    </td>
                    <td>
                      <small>{{ conversion.customer_email }}</small>
                    </td>
                    <td>${{ conversion.amount.toFixed(2) }}</td>
                    <td>
                      <span class="badge bg-success">
                        ${{ conversion.commission.toFixed(2) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Charts -->
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Conversion Funnel</h5>
          </div>
          <div class="card-body">
            <Graph
              v-if="funnelChartData"
              :data="funnelChartData"
              :options="funnelChartOptions"
              :height="250"
              type="bar"
            />
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Commission Distribution</h5>
          </div>
          <div class="card-body">
            <Graph
              v-if="commissionChartData"
              :data="commissionChartData"
              :options="commissionChartOptions"
              :height="250"
              type="bar"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAffiliateStore } from '@/stores/affiliateStore'
import Graph from '@/components/Graph.vue'

export default {
  name: 'AffiliateDashboard',
  components: {
    Graph
  },
  setup() {
    const router = useRouter()
    const affiliateStore = useAffiliateStore()
    
    // Data
    const dateRange = ref(30)
    const trendMetric = ref('clicks')
    const metrics = ref({
      totalAffiliates: 0,
      affiliateGrowth: 0,
      totalClicks: 0,
      clickGrowth: 0,
      totalConversions: 0,
      conversionRate: 0,
      totalRevenue: 0,
      avgOrderValue: 0
    })
    
    const topAffiliates = ref([])
    const recentConversions = ref([])
    
    // Chart Data
    const performanceChartData = ref(null)
    const trafficSourcesData = ref(null)
    const funnelChartData = ref(null)
    const commissionChartData = ref(null)
    
    // Chart Options
    const performanceChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          grid: {
            display: false
          }
        },
        y: {
          display: true,
          beginAtZero: true
        }
      }
    }
    
    const pieChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
    
    const funnelChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          display: true
        },
        y: {
          display: true,
          beginAtZero: true
        }
      }
    }
    
    const commissionChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          beginAtZero: true
        }
      }
    }
    
    // Methods
    const loadDashboardData = async () => {
      // Generate sample data for demonstration
      // In production, this would fetch from the API
      
      // Metrics
      metrics.value = {
        totalAffiliates: 87,
        affiliateGrowth: 12.5,
        totalClicks: 45678,
        clickGrowth: 23.4,
        totalConversions: 234,
        conversionRate: 0.51,
        totalRevenue: 125450,
        avgOrderValue: 535.68
      }
      
      // Top Affiliates
      topAffiliates.value = [
        {
          id: 1,
          business_name: 'Digital Marketing Pro',
          affiliate_code: 'DMP2025',
          clicks: 5432,
          conversions: 45,
          conversionRate: 0.83,
          revenue: 24500,
          commission_rate: 25
        },
        {
          id: 2,
          business_name: 'Finance Advisory Group',
          affiliate_code: 'FAG001',
          clicks: 3211,
          conversions: 38,
          conversionRate: 1.18,
          revenue: 20300,
          commission_rate: 20
        },
        {
          id: 3,
          business_name: 'Retirement Experts',
          affiliate_code: 'RET789',
          clicks: 2890,
          conversions: 28,
          conversionRate: 0.97,
          revenue: 15400,
          commission_rate: 20
        },
        {
          id: 4,
          business_name: 'Wealth Advisors LLC',
          affiliate_code: 'WAL456',
          clicks: 2156,
          conversions: 22,
          conversionRate: 1.02,
          revenue: 11800,
          commission_rate: 15
        }
      ]
      
      // Recent Conversions
      recentConversions.value = [
        {
          id: 1,
          created_at: new Date(Date.now() - 1000 * 60 * 15),
          affiliate_name: 'Digital Marketing Pro',
          customer_email: 'john***@gmail.com',
          amount: 599,
          commission: 149.75
        },
        {
          id: 2,
          created_at: new Date(Date.now() - 1000 * 60 * 45),
          affiliate_name: 'Finance Advisory',
          customer_email: 'sarah***@yahoo.com',
          amount: 399,
          commission: 79.80
        },
        {
          id: 3,
          created_at: new Date(Date.now() - 1000 * 60 * 120),
          affiliate_name: 'Retirement Experts',
          customer_email: 'mike***@outlook.com',
          amount: 599,
          commission: 119.80
        },
        {
          id: 4,
          created_at: new Date(Date.now() - 1000 * 60 * 180),
          affiliate_name: 'Wealth Advisors',
          customer_email: 'lisa***@gmail.com',
          amount: 399,
          commission: 59.85
        }
      ]
      
      updateChartData()
    }
    
    const updateChartData = () => {
      // Performance Trends
      const labels = generateDateLabels(dateRange.value)
      const data = generateTrendData(labels.length, trendMetric.value)
      
      performanceChartData.value = {
        labels,
        datasets: [{
          label: trendMetric.value.charAt(0).toUpperCase() + trendMetric.value.slice(1),
          data,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.4
        }]
      }
      
      // Traffic Sources
      trafficSourcesData.value = {
        labels: ['Social Media', 'Email', 'Blog', 'Direct', 'Other'],
        datasets: [{
          data: [35, 25, 20, 15, 5],
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)'
          ]
        }]
      }
      
      // Conversion Funnel
      funnelChartData.value = {
        labels: ['Clicks', 'Visits', 'Signups', 'Trials', 'Conversions'],
        datasets: [{
          data: [45678, 12340, 3456, 892, 234],
          backgroundColor: 'rgba(54, 162, 235, 0.8)'
        }]
      }
      
      // Commission Distribution
      commissionChartData.value = {
        labels: ['Pending', 'Approved', 'Processing', 'Paid'],
        datasets: [{
          data: [8500, 5200, 2100, 45600],
          backgroundColor: [
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(40, 167, 69, 0.8)'
          ]
        }]
      }
    }
    
    const generateDateLabels = (days) => {
      const labels = []
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))
      }
      return labels
    }
    
    const generateTrendData = (points, metric) => {
      const data = []
      let base = metric === 'clicks' ? 1000 : metric === 'conversions' ? 5 : 2000
      
      for (let i = 0; i < points; i++) {
        base += Math.random() * 200 - 100
        data.push(Math.max(0, Math.round(base)))
      }
      return data
    }
    
    const formatTimeAgo = (date) => {
      const seconds = Math.floor((new Date() - date) / 1000)
      
      if (seconds < 60) return `${seconds}s ago`
      const minutes = Math.floor(seconds / 60)
      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.floor(hours / 24)
      return `${days}d ago`
    }
    
    const refreshData = () => {
      loadDashboardData()
    }
    
    const viewAllAffiliates = () => {
      router.push('/affiliates')
    }
    
    // Watchers
    watch(trendMetric, () => {
      updateChartData()
    })
    
    // Lifecycle
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      dateRange,
      trendMetric,
      metrics,
      topAffiliates,
      recentConversions,
      performanceChartData,
      trafficSourcesData,
      funnelChartData,
      commissionChartData,
      performanceChartOptions,
      pieChartOptions,
      funnelChartOptions,
      commissionChartOptions,
      formatTimeAgo,
      refreshData,
      viewAllAffiliates
    }
  }
}
</script>

<style scoped>
.affiliate-dashboard {
  padding: 20px;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  margin-bottom: 1.5rem;
}

.card-header {
  background-color: #fff;
  border-bottom: 1px solid #e3e6f0;
  font-weight: 600;
}

.table td {
  vertical-align: middle;
}

.btn-group .btn {
  font-size: 0.875rem;
}
</style>