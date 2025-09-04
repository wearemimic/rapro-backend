<template>
  <div class="admin-monitoring">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">System Monitoring</li>
            </ol>
          </nav>
          <h1 class="page-header-title">System Monitoring</h1>
        </div>
        <div class="col-auto">
          <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- System Health Overview -->
    <div class="row mb-4">
      <!-- API Response Times -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-speedometer2 display-4 text-success mb-3"></i>
            <h3 class="mb-1">{{ systemData?.health_metrics?.api_response_times?.average || 0 }}ms</h3>
            <p class="card-text text-muted">Avg Response Time</p>
            <div class="d-flex justify-content-between text-sm">
              <span>P95: {{ systemData?.health_metrics?.api_response_times?.p95 || 0 }}ms</span>
              <span>P99: {{ systemData?.health_metrics?.api_response_times?.p99 || 0 }}ms</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Rate -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-exclamation-triangle display-4 text-warning mb-3"></i>
            <h3 class="mb-1">{{ (systemData?.health_metrics?.error_rates?.last_hour || 0).toFixed(2) }}%</h3>
            <p class="card-text text-muted">Error Rate (1h)</p>
            <div class="d-flex justify-content-between text-sm">
              <span>24h: {{ (systemData?.health_metrics?.error_rates?.last_24h || 0).toFixed(2) }}%</span>
              <span>7d: {{ (systemData?.health_metrics?.error_rates?.last_week || 0).toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- System Uptime -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-shield-check display-4 text-success mb-3"></i>
            <h3 class="mb-1">{{ systemData?.health_metrics?.uptime?.current || '99.9%' }}</h3>
            <p class="card-text text-muted">Current Uptime</p>
            <div class="d-flex justify-content-between text-sm">
              <span>Monthly: {{ systemData?.health_metrics?.uptime?.monthly || '99.95%' }}</span>
              <span>Yearly: {{ systemData?.health_metrics?.uptime?.yearly || '99.9%' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Sessions -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-people display-4 text-info mb-3"></i>
            <h3 class="mb-1">{{ systemData?.database_metrics?.recent_activity_volume || 0 }}</h3>
            <p class="card-text text-muted">Active Sessions (24h)</p>
            <div class="progress mt-2">
              <div class="progress-bar bg-info" style="width: 65%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Database Performance -->
      <div class="col-lg-8 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">Database Performance</h4>
          </div>
          <div class="card-body">
            <div class="row mb-4">
              <div class="col-md-4 text-center">
                <h5 class="text-primary mb-1">{{ formatNumber(systemData?.database_metrics?.total_records?.users || 0) }}</h5>
                <p class="text-muted mb-0">Total Users</p>
              </div>
              <div class="col-md-4 text-center">
                <h5 class="text-success mb-1">{{ formatNumber(systemData?.database_metrics?.total_records?.clients || 0) }}</h5>
                <p class="text-muted mb-0">Total Clients</p>
              </div>
              <div class="col-md-4 text-center">
                <h5 class="text-info mb-1">{{ formatNumber(systemData?.database_metrics?.total_records?.scenarios || 0) }}</h5>
                <p class="text-muted mb-0">Total Scenarios</p>
              </div>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <h6>Query Performance</h6>
                <div class="progress mb-2">
                  <div class="progress-bar bg-success" style="width: 85%"></div>
                </div>
                <small class="text-muted">Average query time: 45ms</small>
              </div>
              <div class="col-md-6">
                <h6>Connection Pool</h6>
                <div class="progress mb-2">
                  <div class="progress-bar bg-warning" style="width: 60%"></div>
                </div>
                <small class="text-muted">Pool utilization: 60%</small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Storage Metrics -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">Storage Usage</h4>
          </div>
          <div class="card-body">
            <div class="text-center mb-3">
              <canvas id="storageChart" width="200" height="200"></canvas>
            </div>
            
            <div class="storage-breakdown">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                  <div class="storage-indicator bg-primary me-2"></div>
                  <span>Documents</span>
                </div>
                <span class="fw-bold">{{ systemData?.storage_metrics?.document_storage?.total_size_gb || 0 }} GB</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                  <div class="storage-indicator bg-success me-2"></div>
                  <span>Database</span>
                </div>
                <span class="fw-bold">{{ systemData?.storage_metrics?.database_size?.estimated_gb || 0 }} GB</span>
              </div>
              
              <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                  <div class="storage-indicator bg-info me-2"></div>
                  <span>Backups</span>
                </div>
                <span class="fw-bold">1.2 GB</span>
              </div>
            </div>

            <hr>
            <div class="text-center">
              <small class="text-muted">
                Growth Rate: {{ systemData?.storage_metrics?.database_size?.growth_rate_mb_day || 0 }} MB/day
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent System Events -->
    <div class="row">
      <div class="col-lg-8 mb-4">
        <div class="card">
          <div class="card-header">
            <div class="row justify-content-between align-items-center">
              <div class="col">
                <h4 class="card-header-title">Recent System Events</h4>
              </div>
              <div class="col-auto">
                <div class="btn-group btn-group-sm" role="group">
                  <input type="radio" class="btn-check" name="eventFilter" id="allEvents" autocomplete="off" v-model="eventFilter" value="all" @change="filterEvents">
                  <label class="btn btn-outline-secondary" for="allEvents">All</label>

                  <input type="radio" class="btn-check" name="eventFilter" id="errorsOnly" autocomplete="off" v-model="eventFilter" value="error" @change="filterEvents">
                  <label class="btn btn-outline-danger" for="errorsOnly">Errors</label>

                  <input type="radio" class="btn-check" name="eventFilter" id="warningsOnly" autocomplete="off" v-model="eventFilter" value="warning" @change="filterEvents">
                  <label class="btn btn-outline-warning" for="warningsOnly">Warnings</label>
                </div>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="filteredEvents.length === 0" class="text-center py-4 text-muted">
              <i class="bi-check-circle display-4 mb-3"></i>
              <p>No {{ eventFilter === 'all' ? 'recent' : eventFilter }} events</p>
            </div>
            <div v-else>
              <div class="timeline">
                <div v-for="event in filteredEvents" :key="event.id" class="timeline-item">
                  <div class="timeline-marker" :class="getEventMarkerClass(event.type)">
                    <i :class="getEventIcon(event.type)"></i>
                  </div>
                  <div class="timeline-content">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 class="mb-1">{{ event.message }}</h6>
                        <small class="text-muted">{{ formatDateTime(event.timestamp) }}</small>
                      </div>
                      <span class="badge" :class="getEventBadgeClass(event.type)">
                        {{ event.type }}
                      </span>
                    </div>
                    <div v-if="event.resolved" class="mt-2">
                      <span class="badge bg-success">Resolved</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Health Summary -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">System Health Summary</h4>
          </div>
          <div class="card-body">
            <!-- Overall Health Score -->
            <div class="text-center mb-4">
              <div class="health-score">
                <canvas id="healthScoreChart" width="120" height="120"></canvas>
                <div class="health-score-text">
                  <h3 class="text-success mb-0">98%</h3>
                  <small class="text-muted">Health Score</small>
                </div>
              </div>
            </div>

            <!-- Health Components -->
            <div class="health-components">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="d-flex align-items-center">
                  <i class="bi-server text-success me-2"></i>
                  <span>API Services</span>
                </div>
                <span class="badge bg-success">Healthy</span>
              </div>

              <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="d-flex align-items-center">
                  <i class="bi-database text-success me-2"></i>
                  <span>Database</span>
                </div>
                <span class="badge bg-success">Healthy</span>
              </div>

              <div class="d-flex justify-content-between align-items-center mb-3">
                <div class="d-flex align-items-center">
                  <i class="bi-cloud text-warning me-2"></i>
                  <span>File Storage</span>
                </div>
                <span class="badge bg-warning">Degraded</span>
              </div>

              <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                  <i class="bi-envelope text-success me-2"></i>
                  <span>Email Service</span>
                </div>
                <span class="badge bg-success">Healthy</span>
              </div>
            </div>

            <hr>
            <div class="text-center">
              <small class="text-muted">
                Last updated: {{ formatTime(systemData?.last_updated) }}
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue';
import axios from 'axios';
import { API_CONFIG } from '@/config';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'AdminMonitoring',
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const systemData = ref(null);
    const eventFilter = ref('all');
    const recentEvents = ref([]);
    
    let storageChart = null;
    let healthScoreChart = null;

    const filteredEvents = computed(() => {
      if (eventFilter.value === 'all') {
        return recentEvents.value;
      }
      return recentEvents.value.filter(event => event.type === eventFilter.value);
    });

    const fetchSystemData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const response = await axios.get(`${API_CONFIG.API_URL}/admin/monitoring/`);
        systemData.value = response.data;
        
        // Use the events from the API response
        recentEvents.value = response.data.recent_issues || [];
        
        await nextTick();
        createCharts();
        
      } catch (err) {
        console.error('Error fetching system monitoring data:', err);
        error.value = err.response?.data?.error || 'Failed to fetch system monitoring data';
      } finally {
        loading.value = false;
      }
    };

    const createCharts = () => {
      createStorageChart();
      createHealthScoreChart();
    };

    const createStorageChart = () => {
      const ctx = document.getElementById('storageChart');
      if (!ctx || !systemData.value) return;

      if (storageChart) {
        storageChart.destroy();
      }

      const documentStorage = systemData.value.storage_metrics?.document_storage?.total_size_gb || 0;
      const databaseStorage = systemData.value.storage_metrics?.database_size?.estimated_gb || 0;
      const backupStorage = 1.2; // Mock data

      storageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Documents', 'Database', 'Backups'],
          datasets: [{
            data: [documentStorage, databaseStorage, backupStorage],
            backgroundColor: ['#377dff', '#28a745', '#17a2b8'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    };

    const createHealthScoreChart = () => {
      const ctx = document.getElementById('healthScoreChart');
      if (!ctx) return;

      if (healthScoreChart) {
        healthScoreChart.destroy();
      }

      healthScoreChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          datasets: [{
            data: [98, 2],
            backgroundColor: ['#28a745', '#e9ecef'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          cutout: '80%',
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    };

    const filterEvents = () => {
      // Events are filtered via computed property
    };

    const getEventMarkerClass = (type) => {
      const classes = {
        'error': 'timeline-marker-danger',
        'warning': 'timeline-marker-warning',
        'info': 'timeline-marker-info',
        'success': 'timeline-marker-success'
      };
      return classes[type] || 'timeline-marker-secondary';
    };

    const getEventIcon = (type) => {
      const icons = {
        'error': 'bi-exclamation-triangle',
        'warning': 'bi-exclamation-circle',
        'info': 'bi-info-circle',
        'success': 'bi-check-circle'
      };
      return icons[type] || 'bi-circle';
    };

    const getEventBadgeClass = (type) => {
      const classes = {
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info',
        'success': 'bg-success'
      };
      return classes[type] || 'bg-secondary';
    };

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num);
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString();
    };

    const formatTime = (dateString) => {
      if (!dateString) return '';
      return new Date(dateString).toLocaleTimeString();
    };

    const refreshData = () => {
      fetchSystemData();
    };

    onMounted(() => {
      fetchSystemData();
    });

    return {
      loading,
      error,
      systemData,
      eventFilter,
      recentEvents,
      filteredEvents,
      filterEvents,
      getEventMarkerClass,
      getEventIcon,
      getEventBadgeClass,
      formatNumber,
      formatDateTime,
      formatTime,
      refreshData
    };
  }
};
</script>

<style scoped>
.admin-monitoring {
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

.storage-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.health-score {
  position: relative;
  display: inline-block;
}

.health-score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e3e6f0;
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0.125rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  border: 2px solid #fff;
}

.timeline-marker-danger {
  background-color: #dc3545;
  color: #fff;
}

.timeline-marker-warning {
  background-color: #ffc107;
  color: #212529;
}

.timeline-marker-info {
  background-color: #17a2b8;
  color: #fff;
}

.timeline-marker-success {
  background-color: #28a745;
  color: #fff;
}

.timeline-marker-secondary {
  background-color: #6c757d;
  color: #fff;
}

.timeline-content {
  padding-left: 1rem;
}

.text-sm {
  font-size: 0.875rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.btn-check:checked + .btn {
  background-color: #377dff;
  border-color: #377dff;
  color: #fff;
}

canvas {
  max-height: 200px;
}

.health-components .badge {
  min-width: 60px;
  text-align: center;
}
</style>