<template>
  <div class="admin-performance">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Performance</li>
            </ol>
          </nav>
          <h1 class="page-header-title">System Performance</h1>
        </div>
        <div class="col-auto">
          <!-- Performance Controls -->
          <div class="btn-group me-2">
            <select v-model="selectedTimeframe" @change="refreshMetrics" class="form-select">
              <option value="1">Last hour</option>
              <option value="6">Last 6 hours</option>
              <option value="24">Last 24 hours</option>
              <option value="168">Last week</option>
            </select>
          </div>
          <button @click="refreshMetrics" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- System Health Overview -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">System Health Status</h5>
            <span class="badge" :class="overallHealthClass">{{ overallHealthStatus }}</span>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-2 col-sm-4 col-6 mb-3" v-for="(metric, key) in systemHealth.latest_metrics" :key="key">
                <div class="text-center">
                  <div class="h4 mb-1" :class="getMetricHealthClass(metric.status)">
                    {{ formatMetricValue(metric.value, metric.unit) }}
                  </div>
                  <div class="text-muted small">{{ formatMetricName(key) }}</div>
                  <div class="badge" :class="getStatusBadgeClass(metric.status)">{{ metric.status }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Metrics Navigation -->
    <div class="row mb-4">
      <div class="col">
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
              <i class="bi-speedometer2 me-2"></i>Overview
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'response_times' }" @click="activeTab = 'response_times'">
              <i class="bi-clock me-2"></i>Response Times
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'errors' }" @click="activeTab = 'errors'">
              <i class="bi-exclamation-triangle me-2"></i>Error Rates
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'resources' }" @click="activeTab = 'resources'">
              <i class="bi-cpu me-2"></i>System Resources
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'endpoints' }" @click="activeTab = 'endpoints'">
              <i class="bi-diagram-3 me-2"></i>API Endpoints
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
      <p class="mt-3">Loading performance data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <!-- Overview Tab -->
    <div v-show="activeTab === 'overview'" class="tab-content">
      <!-- Health Score Cards -->
      <div class="row mb-4" v-if="systemHealth?.health_scores">
        <div class="col-xl-3 col-md-6 mb-4" v-for="(score, key) in systemHealth.health_scores" :key="key">
          <div class="card border-left-primary">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">{{ formatScoreName(key) }}</div>
                  <div class="h5 mb-0 font-weight-bold" :class="getScoreClass(score)">{{ score }}%</div>
                </div>
                <div class="col-auto">
                  <div class="progress" style="width: 60px;">
                    <div class="progress-bar" :class="getProgressBarClass(score)" :style="{ width: score + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Issues -->
      <div class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Recent Issues</h5>
            </div>
            <div class="card-body">
              <div v-if="systemHealth?.recent_issues && systemHealth.recent_issues.length > 0">
                <div class="list-group list-group-flush">
                  <div 
                    v-for="issue in systemHealth.recent_issues" 
                    :key="issue.id"
                    class="list-group-item d-flex justify-content-between align-items-start"
                  >
                    <div class="ms-2 me-auto">
                      <div class="d-flex align-items-center mb-1">
                        <span class="badge me-2" :class="getSeverityBadgeClass(issue.severity)">
                          {{ issue.severity.toUpperCase() }}
                        </span>
                        <span class="badge bg-secondary">{{ issue.component }}</span>
                      </div>
                      <p class="mb-1">{{ issue.message }}</p>
                      <small class="text-muted">{{ formatTimestamp(issue.timestamp) }}</small>
                    </div>
                    <span class="badge" :class="issue.resolved ? 'bg-success' : 'bg-warning'">
                      {{ issue.resolved ? 'Resolved' : 'Active' }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-muted">
                <i class="bi-check-circle display-4"></i>
                <p class="mt-2">No recent issues detected</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">API Endpoint Status</h5>
            </div>
            <div class="card-body">
              <div v-if="systemHealth?.endpoint_status" class="text-center">
                <div class="mb-3">
                  <div class="display-6 text-success">{{ systemHealth.endpoint_status.healthy_endpoints }}</div>
                  <div class="text-muted">Healthy Endpoints</div>
                </div>
                <div class="row text-center">
                  <div class="col">
                    <div class="h6 text-warning">{{ systemHealth.endpoint_status.degraded_endpoints }}</div>
                    <div class="small text-muted">Degraded</div>
                  </div>
                  <div class="col">
                    <div class="h6 text-danger">{{ systemHealth.endpoint_status.failed_endpoints }}</div>
                    <div class="small text-muted">Failed</div>
                  </div>
                </div>
                <div class="progress mt-3">
                  <div 
                    class="progress-bar bg-success" 
                    :style="{ width: (systemHealth.endpoint_status.healthy_endpoints / systemHealth.endpoint_status.total_endpoints) * 100 + '%' }"
                  ></div>
                  <div 
                    class="progress-bar bg-warning" 
                    :style="{ width: (systemHealth.endpoint_status.degraded_endpoints / systemHealth.endpoint_status.total_endpoints) * 100 + '%' }"
                  ></div>
                  <div 
                    class="progress-bar bg-danger" 
                    :style="{ width: (systemHealth.endpoint_status.failed_endpoints / systemHealth.endpoint_status.total_endpoints) * 100 + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Response Times Tab -->
    <div v-show="activeTab === 'response_times'" class="tab-content">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">API Response Times</h5>
            </div>
            <div class="card-body">
              <div v-if="performanceMetrics?.averages?.response_time">
                <div class="row mb-4">
                  <div class="col-md-4 text-center">
                    <div class="h3 text-primary">{{ performanceMetrics.averages.response_time.average }}ms</div>
                    <div class="text-muted">Average Response Time</div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="h3 text-info">{{ performanceMetrics.averages.response_time.count }}</div>
                    <div class="text-muted">Total Requests</div>
                  </div>
                  <div class="col-md-4 text-center">
                    <div class="h3 text-success">{{ selectedTimeframe }}h</div>
                    <div class="text-muted">Time Period</div>
                  </div>
                </div>
                <!-- Response time chart would go here -->
                <div class="alert alert-info">
                  <i class="bi-info-circle me-2"></i>
                  Response time visualization chart will be implemented with Chart.js
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- API Endpoints Tab -->
    <div v-show="activeTab === 'endpoints'" class="tab-content">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Endpoint Performance</h5>
            </div>
            <div class="card-body">
              <div v-if="performanceMetrics?.endpoint_performance && performanceMetrics.endpoint_performance.length > 0">
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Endpoint</th>
                        <th>Avg Response Time</th>
                        <th>Request Count</th>
                        <th>Error Rate</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="endpoint in performanceMetrics.endpoint_performance.slice(0, 20)" :key="endpoint.endpoint">
                        <td>
                          <code class="small">{{ endpoint.endpoint }}</code>
                        </td>
                        <td>
                          <span class="badge" :class="getResponseTimeBadgeClass(endpoint.avg_response_time)">
                            {{ Math.round(endpoint.avg_response_time) }}ms
                          </span>
                        </td>
                        <td>{{ endpoint.request_count.toLocaleString() }}</td>
                        <td>
                          <span class="badge" :class="getErrorRateBadgeClass(endpoint.error_rate_percent)">
                            {{ endpoint.error_rate_percent }}%
                          </span>
                        </td>
                        <td>
                          <span class="badge" :class="getEndpointStatusClass(endpoint.error_rate_percent, endpoint.avg_response_time)">
                            {{ getEndpointStatus(endpoint.error_rate_percent, endpoint.avg_response_time) }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-else class="text-center py-4 text-muted">
                <i class="bi-graph-up display-4"></i>
                <p class="mt-2">No endpoint performance data available</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Resources Tab -->
    <div v-show="activeTab === 'resources'" class="tab-content">
      <div class="row">
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">CPU & Memory Usage</h5>
            </div>
            <div class="card-body">
              <div v-if="systemHealth?.latest_metrics">
                <div class="mb-3" v-if="systemHealth.latest_metrics.cpu_usage">
                  <div class="d-flex justify-content-between mb-1">
                    <span>CPU Usage</span>
                    <span class="fw-bold">{{ systemHealth.latest_metrics.cpu_usage.value }}%</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar" 
                      :class="getCpuProgressClass(systemHealth.latest_metrics.cpu_usage.value)"
                      :style="{ width: systemHealth.latest_metrics.cpu_usage.value + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="mb-3" v-if="systemHealth.latest_metrics.memory_usage">
                  <div class="d-flex justify-content-between mb-1">
                    <span>Memory Usage</span>
                    <span class="fw-bold">{{ systemHealth.latest_metrics.memory_usage.value }}%</span>
                  </div>
                  <div class="progress">
                    <div 
                      class="progress-bar" 
                      :class="getMemoryProgressClass(systemHealth.latest_metrics.memory_usage.value)"
                      :style="{ width: systemHealth.latest_metrics.memory_usage.value + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Database & Connections</h5>
            </div>
            <div class="card-body">
              <div v-if="systemHealth?.latest_metrics?.database_connections">
                <div class="text-center mb-3">
                  <div class="h4">{{ systemHealth.latest_metrics.database_connections.value }}</div>
                  <div class="text-muted">Active Connections</div>
                </div>
              </div>
              <div v-if="systemHealth?.latest_metrics?.active_users">
                <div class="text-center">
                  <div class="h4 text-success">{{ systemHealth.latest_metrics.active_users.value }}</div>
                  <div class="text-muted">Active Users (24h)</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Rates Tab -->
    <div v-show="activeTab === 'errors'" class="tab-content">
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Error Rate Analysis</h5>
            </div>
            <div class="card-body">
              <div class="alert alert-info">
                <i class="bi-info-circle me-2"></i>
                Detailed error rate analysis and charts will be implemented in the next iteration.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

export default {
  name: 'AdminPerformance',
  setup() {
    const authStore = useAuthStore()
    
    // Reactive state
    const loading = ref(false)
    const error = ref(null)
    const activeTab = ref('overview')
    const selectedTimeframe = ref('24')
    
    // Data
    const systemHealth = ref({})
    const performanceMetrics = ref({})
    
    // Computed properties
    const hasAnyData = computed(() => {
      return Object.keys(systemHealth.value).length > 0 || Object.keys(performanceMetrics.value).length > 0
    })
    
    const overallHealthStatus = computed(() => {
      if (!systemHealth.value?.health_scores) return 'Unknown'
      const overall = systemHealth.value.health_scores.overall
      if (overall >= 95) return 'Excellent'
      if (overall >= 90) return 'Good'
      if (overall >= 80) return 'Fair'
      return 'Poor'
    })
    
    const overallHealthClass = computed(() => {
      const overall = systemHealth.value?.health_scores?.overall || 0
      if (overall >= 95) return 'bg-success'
      if (overall >= 90) return 'bg-primary' 
      if (overall >= 80) return 'bg-warning'
      return 'bg-danger'
    })

    // Methods
    const refreshMetrics = async () => {
      loading.value = true
      error.value = null
      
      try {
        // Fetch system health dashboard
        const healthResponse = await axios.get('/api/admin/performance/health/')
        systemHealth.value = healthResponse.data
        
        // Fetch performance metrics
        const metricsResponse = await axios.get('/api/admin/performance/metrics/', {
          params: { hours: selectedTimeframe.value }
        })
        performanceMetrics.value = metricsResponse.data
        
      } catch (err) {
        console.error('Failed to fetch performance data:', err)
        error.value = err.response?.data?.error || 'Failed to load performance data'
      } finally {
        loading.value = false
      }
    }

    const formatMetricValue = (value, unit) => {
      if (unit === 'percent') return `${Math.round(value)}%`
      if (unit === 'ms') return `${Math.round(value)}ms`
      if (unit === 'count') return value.toLocaleString()
      return value
    }

    const formatMetricName = (key) => {
      const names = {
        response_time: 'Response Time',
        error_rate: 'Error Rate', 
        uptime: 'Uptime',
        cpu_usage: 'CPU Usage',
        memory_usage: 'Memory Usage',
        database_connections: 'DB Connections',
        active_users: 'Active Users'
      }
      return names[key] || key.replace('_', ' ').toUpperCase()
    }

    const formatScoreName = (key) => {
      const names = {
        overall: 'Overall Health',
        api_performance: 'API Performance',
        database_performance: 'Database Performance', 
        error_rate: 'Error Rate Score',
        uptime: 'Uptime Score'
      }
      return names[key] || key.replace('_', ' ')
    }

    const getMetricHealthClass = (status) => {
      return {
        'text-success': status === 'healthy',
        'text-warning': status === 'warning', 
        'text-danger': status === 'critical'
      }
    }

    const getStatusBadgeClass = (status) => {
      return {
        'bg-success': status === 'healthy',
        'bg-warning': status === 'warning',
        'bg-danger': status === 'critical'
      }
    }

    const getScoreClass = (score) => {
      if (score >= 95) return 'text-success'
      if (score >= 90) return 'text-primary'
      if (score >= 80) return 'text-warning'
      return 'text-danger'
    }

    const getProgressBarClass = (score) => {
      if (score >= 95) return 'bg-success'
      if (score >= 90) return 'bg-primary'
      if (score >= 80) return 'bg-warning' 
      return 'bg-danger'
    }

    const getSeverityBadgeClass = (severity) => {
      return {
        'bg-info': severity === 'info',
        'bg-warning': severity === 'warning',
        'bg-danger': severity === 'critical'
      }
    }

    const getResponseTimeBadgeClass = (responseTime) => {
      if (responseTime <= 200) return 'bg-success'
      if (responseTime <= 500) return 'bg-warning'
      return 'bg-danger'
    }

    const getErrorRateBadgeClass = (errorRate) => {
      if (errorRate <= 1) return 'bg-success'
      if (errorRate <= 5) return 'bg-warning'
      return 'bg-danger'
    }

    const getEndpointStatusClass = (errorRate, responseTime) => {
      if (errorRate <= 1 && responseTime <= 200) return 'bg-success'
      if (errorRate <= 5 && responseTime <= 500) return 'bg-warning'
      return 'bg-danger'
    }

    const getEndpointStatus = (errorRate, responseTime) => {
      if (errorRate <= 1 && responseTime <= 200) return 'Healthy'
      if (errorRate <= 5 && responseTime <= 500) return 'Degraded'
      return 'Critical'
    }

    const getCpuProgressClass = (usage) => {
      if (usage <= 70) return 'bg-success'
      if (usage <= 85) return 'bg-warning'
      return 'bg-danger'
    }

    const getMemoryProgressClass = (usage) => {
      if (usage <= 80) return 'bg-success'
      if (usage <= 90) return 'bg-warning' 
      return 'bg-danger'
    }

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    // Watch for timeframe changes
    watch(selectedTimeframe, () => {
      refreshMetrics()
    })

    // Initialize
    onMounted(() => {
      refreshMetrics()
      
      // Set up auto-refresh every 30 seconds
      const interval = setInterval(refreshMetrics, 30000)
      
      // Clean up on unmount
      return () => clearInterval(interval)
    })

    return {
      // State
      loading,
      error,
      activeTab,
      selectedTimeframe,
      systemHealth,
      performanceMetrics,
      
      // Computed
      hasAnyData,
      overallHealthStatus,
      overallHealthClass,
      
      // Methods
      refreshMetrics,
      formatMetricValue,
      formatMetricName,
      formatScoreName,
      getMetricHealthClass,
      getStatusBadgeClass,
      getScoreClass,
      getProgressBarClass,
      getSeverityBadgeClass,
      getResponseTimeBadgeClass,
      getErrorRateBadgeClass,
      getEndpointStatusClass,
      getEndpointStatus,
      getCpuProgressClass,
      getMemoryProgressClass,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.admin-performance {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0;
}

.card {
  border: 1px solid #e3e6f0;
  border-radius: 0.35rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(33, 40, 50, 0.15);
}

.card-header {
  background-color: #f8f9fc;
  border-bottom: 1px solid #e3e6f0;
}

.card-header-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0;
}

.display-4 {
  font-size: 2.5rem;
  font-weight: 300;
  line-height: 1.2;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.border-left-primary {
  border-left: 4px solid #007bff !important;
}
</style>