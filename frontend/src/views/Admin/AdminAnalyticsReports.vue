<template>
  <div class="admin-analytics-reports">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-0">Analytics & Reports</h2>
        <p class="text-muted mb-0">Advanced reporting and analytics dashboard</p>
      </div>
      <div>
        <button class="btn btn-primary me-2" @click="showCreateReportModal = true">
          <i class="fas fa-plus me-1"></i>Create Report
        </button>
        <button class="btn btn-outline-primary" @click="showCreateDashboardModal = true">
          <i class="fas fa-tachometer-alt me-1"></i>Create Dashboard
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4" v-if="summary">
      <div class="col-md-3">
        <div class="card border-0 bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Total Users</h6>
                <h3 class="mb-0">{{ summary.total_users }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-users fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.active_users_30d }} active last 30 days</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Revenue</h6>
                <h3 class="mb-0">${{ formatCurrency(summary.total_revenue) }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-dollar-sign fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">${{ formatCurrency(summary.revenue_30d) }} last 30 days</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Reports Executed</h6>
                <h3 class="mb-0">{{ summary.reports_executed }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-chart-bar fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.scheduled_reports_active }} scheduled</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-warning text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">High Risk Users</h6>
                <h3 class="mb-0">{{ summary.high_risk_users }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-exclamation-triangle fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.high_value_users }} high value</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'reports' }" @click="activeTab = 'reports'">
          <i class="fas fa-chart-line me-1"></i>Custom Reports
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'schedules' }" @click="activeTab = 'schedules'">
          <i class="fas fa-calendar-alt me-1"></i>Schedules
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'executions' }" @click="activeTab = 'executions'">
          <i class="fas fa-history me-1"></i>Execution History
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'dashboards' }" @click="activeTab = 'dashboards'">
          <i class="fas fa-tachometer-alt me-1"></i>Dashboards
        </a>
      </li>
    </ul>

    <!-- Reports Tab -->
    <div v-if="activeTab === 'reports'">
      <div class="card">
        <div class="card-header">
          <div class="row align-items-center">
            <div class="col">
              <h5 class="mb-0">Custom Reports</h5>
            </div>
            <div class="col-auto">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search reports..." 
                  v-model="reportSearchQuery"
                >
                <button class="btn btn-outline-secondary" type="button">
                  <i class="fas fa-search"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Created By</th>
                  <th>Views</th>
                  <th>Last Viewed</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="report in filteredReports" :key="report.id">
                  <td>
                    <div>
                      <strong>{{ report.report_name }}</strong>
                      <div v-if="report.description" class="text-muted small">{{ report.description }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="badge bg-secondary">{{ formatReportType(report.report_type) }}</span>
                  </td>
                  <td>{{ report.created_by_name }}</td>
                  <td>{{ report.view_count }}</td>
                  <td>{{ formatDate(report.last_viewed) }}</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="executeReport(report)">
                        <i class="fas fa-play"></i>
                      </button>
                      <button class="btn btn-outline-secondary" @click="editReport(report)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-outline-info" @click="duplicateReport(report)">
                        <i class="fas fa-copy"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="deleteReport(report)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedules Tab -->
    <div v-if="activeTab === 'schedules'">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Report Schedules</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Schedule Name</th>
                  <th>Report</th>
                  <th>Frequency</th>
                  <th>Next Run</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="schedule in schedules" :key="schedule.id">
                  <td>{{ schedule.schedule_name }}</td>
                  <td>{{ schedule.report_name }}</td>
                  <td>{{ formatFrequency(schedule.frequency) }}</td>
                  <td>{{ formatDate(schedule.next_run) }}</td>
                  <td>
                    <span class="badge" :class="getStatusClass(schedule.status)">
                      {{ schedule.status }}
                    </span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-primary" 
                        @click="toggleSchedule(schedule)"
                        :title="schedule.status === 'active' ? 'Pause' : 'Resume'"
                      >
                        <i :class="schedule.status === 'active' ? 'fas fa-pause' : 'fas fa-play'"></i>
                      </button>
                      <button class="btn btn-outline-secondary" @click="editSchedule(schedule)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="deleteSchedule(schedule)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution History Tab -->
    <div v-if="activeTab === 'executions'">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Execution History</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Report</th>
                  <th>Started At</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Results</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="execution in executions" :key="execution.id">
                  <td>{{ execution.report_name }}</td>
                  <td>{{ formatDate(execution.started_at) }}</td>
                  <td>{{ execution.duration_formatted }}</td>
                  <td>
                    <span class="badge" :class="getStatusClass(execution.status)">
                      {{ execution.status }}
                    </span>
                  </td>
                  <td>{{ execution.result_count || 0 }} rows</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-primary" 
                        @click="viewExecution(execution)"
                        v-if="execution.status === 'completed'"
                      >
                        <i class="fas fa-eye"></i>
                      </button>
                      <button 
                        class="btn btn-outline-info" 
                        @click="downloadExecution(execution)"
                        v-if="execution.export_file_path"
                      >
                        <i class="fas fa-download"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboards Tab -->
    <div v-if="activeTab === 'dashboards'">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Executive Dashboards</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Name</th>
                  <th>Widgets</th>
                  <th>Views</th>
                  <th>Default</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="dashboard in dashboards" :key="dashboard.id">
                  <td>
                    <div>
                      <strong>{{ dashboard.dashboard_name }}</strong>
                      <div v-if="dashboard.description" class="text-muted small">{{ dashboard.description }}</div>
                    </div>
                  </td>
                  <td>{{ dashboard.widgets.length }} widgets</td>
                  <td>{{ dashboard.view_count }}</td>
                  <td>
                    <span v-if="dashboard.is_default" class="badge bg-primary">Default</span>
                  </td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="viewDashboard(dashboard)">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="btn btn-outline-secondary" @click="editDashboard(dashboard)">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button 
                        class="btn btn-outline-info" 
                        @click="setDefaultDashboard(dashboard)"
                        v-if="!dashboard.is_default"
                      >
                        <i class="fas fa-star"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="deleteDashboard(dashboard)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Report Modal -->
    <div class="modal fade" tabindex="-1" v-if="showCreateReportModal" style="display: block;" @click.self="showCreateReportModal = false">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Custom Report</h5>
            <button type="button" class="btn-close" @click="showCreateReportModal = false"></button>
          </div>
          <div class="modal-body">
            <ReportBuilder @save="saveReport" @cancel="showCreateReportModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Dashboard Modal -->
    <div class="modal fade" tabindex="-1" v-if="showCreateDashboardModal" style="display: block;" @click.self="showCreateDashboardModal = false">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Executive Dashboard</h5>
            <button type="button" class="btn-close" @click="showCreateDashboardModal = false"></button>
          </div>
          <div class="modal-body">
            <DashboardBuilder @save="saveDashboard" @cancel="showCreateDashboardModal = false" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import ReportBuilder from '@/components/Analytics/ReportBuilder.vue'
import DashboardBuilder from '@/components/Analytics/DashboardBuilder.vue'

export default {
  name: 'AdminAnalyticsReports',
  components: {
    ReportBuilder,
    DashboardBuilder
  },
  setup() {
    const activeTab = ref('reports')
    const summary = ref(null)
    const reports = ref([])
    const schedules = ref([])
    const executions = ref([])
    const dashboards = ref([])
    const reportSearchQuery = ref('')
    const showCreateReportModal = ref(false)
    const showCreateDashboardModal = ref(false)
    const loading = ref(false)

    const filteredReports = computed(() => {
      if (!reportSearchQuery.value) return reports.value
      const query = reportSearchQuery.value.toLowerCase()
      return reports.value.filter(report => 
        report.report_name.toLowerCase().includes(query) ||
        (report.description && report.description.toLowerCase().includes(query))
      )
    })

    const loadSummary = async () => {
      try {
        const response = await api.get('/api/admin/analytics-summary/')
        summary.value = response.data
      } catch (error) {
        console.error('Error loading analytics summary:', error)
      }
    }

    const loadReports = async () => {
      try {
        const response = await api.get('/api/admin/reports/')
        reports.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading reports:', error)
      }
    }

    const loadSchedules = async () => {
      try {
        const response = await api.get('/api/admin/report-schedules/')
        schedules.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading schedules:', error)
      }
    }

    const loadExecutions = async () => {
      try {
        const response = await api.get('/api/admin/report-executions/')
        executions.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading executions:', error)
      }
    }

    const loadDashboards = async () => {
      try {
        const response = await api.get('/api/admin/dashboards/')
        dashboards.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading dashboards:', error)
      }
    }

    const executeReport = async (report) => {
      try {
        loading.value = true
        const response = await api.post(`/api/admin/reports/${report.id}/execute/`)
        // Handle execution results - could show in modal or navigate to results page
        console.log('Report executed:', response.data)
        loadExecutions() // Refresh execution history
      } catch (error) {
        console.error('Error executing report:', error)
        alert('Failed to execute report')
      } finally {
        loading.value = false
      }
    }

    const duplicateReport = async (report) => {
      try {
        const response = await api.post(`/api/admin/reports/${report.id}/duplicate/`)
        reports.value.push(response.data)
        alert('Report duplicated successfully')
      } catch (error) {
        console.error('Error duplicating report:', error)
        alert('Failed to duplicate report')
      }
    }

    const deleteReport = async (report) => {
      if (!confirm(`Are you sure you want to delete "${report.report_name}"?`)) return
      
      try {
        await api.delete(`/api/admin/reports/${report.id}/`)
        reports.value = reports.value.filter(r => r.id !== report.id)
      } catch (error) {
        console.error('Error deleting report:', error)
        alert('Failed to delete report')
      }
    }

    const toggleSchedule = async (schedule) => {
      try {
        const action = schedule.status === 'active' ? 'pause' : 'resume'
        const response = await api.post(`/api/admin/report-schedules/${schedule.id}/${action}/`)
        
        // Update local data
        const index = schedules.value.findIndex(s => s.id === schedule.id)
        if (index !== -1) {
          schedules.value[index] = response.data
        }
      } catch (error) {
        console.error('Error toggling schedule:', error)
        alert('Failed to update schedule')
      }
    }

    const setDefaultDashboard = async (dashboard) => {
      try {
        const response = await api.post(`/api/admin/dashboards/${dashboard.id}/set_default/`)
        
        // Update local data
        dashboards.value.forEach(d => {
          d.is_default = d.id === dashboard.id
        })
        
        const index = dashboards.value.findIndex(d => d.id === dashboard.id)
        if (index !== -1) {
          dashboards.value[index] = response.data
        }
      } catch (error) {
        console.error('Error setting default dashboard:', error)
        alert('Failed to set default dashboard')
      }
    }

    const saveReport = async (reportData) => {
      try {
        const response = await api.post('/api/admin/reports/', reportData)
        reports.value.push(response.data)
        showCreateReportModal.value = false
        alert('Report created successfully')
      } catch (error) {
        console.error('Error creating report:', error)
        alert('Failed to create report')
      }
    }

    const saveDashboard = async (dashboardData) => {
      try {
        const response = await api.post('/api/admin/dashboards/', dashboardData)
        dashboards.value.push(response.data)
        showCreateDashboardModal.value = false
        alert('Dashboard created successfully')
      } catch (error) {
        console.error('Error creating dashboard:', error)
        alert('Failed to create dashboard')
      }
    }

    // Utility functions
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', { 
        minimumFractionDigits: 0, 
        maximumFractionDigits: 0 
      }).format(value)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString()
    }

    const formatReportType = (type) => {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatFrequency = (frequency) => {
      return frequency.charAt(0).toUpperCase() + frequency.slice(1)
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        active: 'bg-success',
        completed: 'bg-success',
        running: 'bg-primary',
        paused: 'bg-warning',
        failed: 'bg-danger',
        disabled: 'bg-secondary'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    // Placeholder functions for actions that need implementation
    const editReport = (report) => {
      console.log('Edit report:', report)
      // TODO: Implement edit modal
    }

    const editSchedule = (schedule) => {
      console.log('Edit schedule:', schedule)
      // TODO: Implement edit modal
    }

    const deleteSchedule = async (schedule) => {
      if (!confirm(`Are you sure you want to delete "${schedule.schedule_name}"?`)) return
      
      try {
        await api.delete(`/api/admin/report-schedules/${schedule.id}/`)
        schedules.value = schedules.value.filter(s => s.id !== schedule.id)
      } catch (error) {
        console.error('Error deleting schedule:', error)
        alert('Failed to delete schedule')
      }
    }

    const viewExecution = (execution) => {
      console.log('View execution:', execution)
      // TODO: Show execution results
    }

    const downloadExecution = (execution) => {
      window.open(`/api${execution.export_file_path}`, '_blank')
    }

    const viewDashboard = (dashboard) => {
      console.log('View dashboard:', dashboard)
      // TODO: Navigate to dashboard view
    }

    const editDashboard = (dashboard) => {
      console.log('Edit dashboard:', dashboard)
      // TODO: Implement edit modal
    }

    const deleteDashboard = async (dashboard) => {
      if (!confirm(`Are you sure you want to delete "${dashboard.dashboard_name}"?`)) return
      
      try {
        await api.delete(`/api/admin/dashboards/${dashboard.id}/`)
        dashboards.value = dashboards.value.filter(d => d.id !== dashboard.id)
      } catch (error) {
        console.error('Error deleting dashboard:', error)
        alert('Failed to delete dashboard')
      }
    }

    onMounted(() => {
      loadSummary()
      loadReports()
      loadSchedules()
      loadExecutions()
      loadDashboards()
    })

    return {
      activeTab,
      summary,
      reports,
      schedules,
      executions,
      dashboards,
      reportSearchQuery,
      showCreateReportModal,
      showCreateDashboardModal,
      loading,
      filteredReports,
      executeReport,
      duplicateReport,
      deleteReport,
      editReport,
      toggleSchedule,
      editSchedule,
      deleteSchedule,
      viewExecution,
      downloadExecution,
      viewDashboard,
      editDashboard,
      deleteDashboard,
      setDefaultDashboard,
      saveReport,
      saveDashboard,
      formatCurrency,
      formatDate,
      formatReportType,
      formatFrequency,
      getStatusClass
    }
  }
}
</script>

<style scoped>
.admin-analytics-reports {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.nav-link {
  cursor: pointer;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.bg-primary .opacity-75 {
  opacity: 0.75 !important;
}

.bg-success .opacity-75 {
  opacity: 0.75 !important;
}

.bg-info .opacity-75 {
  opacity: 0.75 !important;
}

.bg-warning .opacity-75 {
  opacity: 0.75 !important;
}
</style>