<template>
  <div class="report-builder">
    <form @submit.prevent="handleSave">
      <div class="row">
        <!-- Basic Information -->
        <div class="col-md-6">
          <div class="mb-3">
            <label for="reportName" class="form-label">Report Name *</label>
            <input 
              type="text" 
              class="form-control" 
              id="reportName"
              v-model="report.report_name" 
              required
            >
          </div>
          
          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea 
              class="form-control" 
              id="description"
              v-model="report.description" 
              rows="3"
            ></textarea>
          </div>

          <div class="mb-3">
            <label for="reportType" class="form-label">Report Type *</label>
            <select class="form-select" id="reportType" v-model="report.report_type" required>
              <option value="">Select Type</option>
              <option value="user_analytics">User Analytics</option>
              <option value="revenue_analytics">Revenue Analytics</option>
              <option value="engagement_analytics">Engagement Analytics</option>
              <option value="performance_analytics">Performance Analytics</option>
              <option value="churn_analytics">Churn Analytics</option>
              <option value="custom">Custom Query</option>
            </select>
          </div>
        </div>

        <!-- Visualization Settings -->
        <div class="col-md-6">
          <div class="mb-3">
            <label for="chartType" class="form-label">Chart Type</label>
            <select class="form-select" id="chartType" v-model="report.chart_type">
              <option value="">Table Only</option>
              <option value="line">Line Chart</option>
              <option value="bar">Bar Chart</option>
              <option value="pie">Pie Chart</option>
              <option value="area">Area Chart</option>
              <option value="scatter">Scatter Plot</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">Access Control</label>
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isPublic"
                v-model="report.is_public"
              >
              <label class="form-check-label" for="isPublic">
                Make this report public (visible to all users)
              </label>
            </div>
          </div>

          <div class="mb-3" v-if="!report.is_public">
            <label for="allowedRoles" class="form-label">Allowed Roles</label>
            <select 
              class="form-select" 
              id="allowedRoles" 
              v-model="report.allowed_roles" 
              multiple
            >
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
            </select>
            <div class="form-text">Hold Ctrl/Cmd to select multiple roles</div>
          </div>
        </div>
      </div>

      <!-- Data Source Configuration -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Data Sources</h6>
        <div class="mb-3">
          <label class="form-label">Select Data Sources</label>
          <div class="row">
            <div class="col-md-4" v-for="source in availableDataSources" :key="source.value">
              <div class="form-check">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="source.value"
                  :value="source.value"
                  v-model="report.data_sources"
                >
                <label class="form-check-label" :for="source.value">
                  {{ source.label }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters Configuration -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Filters</h6>
        <div class="row">
          <div class="col-md-6">
            <div class="mb-3">
              <label for="dateRange" class="form-label">Date Range</label>
              <select class="form-select" id="dateRange" v-model="dateRangeFilter">
                <option value="">All Time</option>
                <option value="last_7_days">Last 7 Days</option>
                <option value="last_30_days">Last 30 Days</option>
                <option value="last_90_days">Last 90 Days</option>
                <option value="last_year">Last Year</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>

            <div v-if="dateRangeFilter === 'custom'" class="mb-3">
              <div class="row">
                <div class="col-6">
                  <label for="startDate" class="form-label">Start Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="startDate"
                    v-model="customDateRange.start"
                  >
                </div>
                <div class="col-6">
                  <label for="endDate" class="form-label">End Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="endDate"
                    v-model="customDateRange.end"
                  >
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="mb-3">
              <label for="userSegment" class="form-label">User Segment</label>
              <select class="form-select" id="userSegment" v-model="userSegmentFilter">
                <option value="">All Users</option>
                <option value="new_users">New Users (Last 30 Days)</option>
                <option value="active_users">Active Users</option>
                <option value="inactive_users">Inactive Users</option>
                <option value="high_value">High Value Users</option>
                <option value="at_risk">At Risk Users</option>
              </select>
            </div>

            <div class="mb-3">
              <label for="statusFilter" class="form-label">Status Filter</label>
              <select class="form-select" id="statusFilter" v-model="statusFilter">
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="pending">Pending</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Grouping and Aggregation -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Grouping & Aggregation</h6>
        <div class="row">
          <div class="col-md-6">
            <div class="mb-3">
              <label for="groupBy" class="form-label">Group By</label>
              <select 
                class="form-select" 
                id="groupBy" 
                v-model="report.grouping" 
                multiple
              >
                <option value="date">Date</option>
                <option value="user_type">User Type</option>
                <option value="region">Region</option>
                <option value="subscription_tier">Subscription Tier</option>
                <option value="acquisition_channel">Acquisition Channel</option>
              </select>
              <div class="form-text">Hold Ctrl/Cmd to select multiple</div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label">Aggregations</label>
              <div class="row">
                <div class="col-6" v-for="agg in availableAggregations" :key="agg.value">
                  <div class="form-check">
                    <input 
                      class="form-check-input" 
                      type="checkbox" 
                      :id="agg.value"
                      :value="agg.value"
                      v-model="report.aggregations"
                    >
                    <label class="form-check-label" :for="agg.value">
                      {{ agg.label }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sorting -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Sorting</h6>
        <div class="row">
          <div class="col-md-6">
            <div class="mb-3">
              <label for="sortField" class="form-label">Sort By</label>
              <select class="form-select" id="sortField" v-model="sortField">
                <option value="">No Sorting</option>
                <option value="created_at">Created Date</option>
                <option value="updated_at">Updated Date</option>
                <option value="name">Name</option>
                <option value="value">Value</option>
                <option value="count">Count</option>
              </select>
            </div>
          </div>

          <div class="col-md-6">
            <div class="mb-3">
              <label for="sortDirection" class="form-label">Sort Direction</label>
              <select class="form-select" id="sortDirection" v-model="sortDirection">
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Section -->
      <div class="mb-4" v-if="showPreview">
        <h6 class="border-bottom pb-2">Report Preview</h6>
        <div class="alert alert-info">
          <i class="fas fa-info-circle me-2"></i>
          Report preview would show sample data based on your configuration
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="d-flex justify-content-between">
        <div>
          <button type="button" class="btn btn-outline-secondary me-2" @click="resetForm">
            <i class="fas fa-undo me-1"></i>Reset
          </button>
          <button type="button" class="btn btn-outline-info" @click="togglePreview">
            <i class="fas fa-eye me-1"></i>{{ showPreview ? 'Hide' : 'Show' }} Preview
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-secondary me-2" @click="$emit('cancel')">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isValid">
            <i class="fas fa-save me-1"></i>Create Report
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'ReportBuilder',
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const report = ref({
      report_name: '',
      description: '',
      report_type: '',
      data_sources: [],
      filters: {},
      grouping: [],
      aggregations: [],
      sorting: [],
      chart_type: '',
      chart_config: {},
      is_public: false,
      allowed_roles: []
    })

    const dateRangeFilter = ref('')
    const customDateRange = ref({ start: '', end: '' })
    const userSegmentFilter = ref('')
    const statusFilter = ref('')
    const sortField = ref('')
    const sortDirection = ref('desc')
    const showPreview = ref(false)

    const availableDataSources = [
      { value: 'users', label: 'Users' },
      { value: 'scenarios', label: 'Scenarios' },
      { value: 'clients', label: 'Clients' },
      { value: 'communications', label: 'Communications' },
      { value: 'tasks', label: 'Tasks' },
      { value: 'documents', label: 'Documents' },
      { value: 'analytics', label: 'Analytics Events' },
      { value: 'revenue', label: 'Revenue Data' }
    ]

    const availableAggregations = [
      { value: 'count', label: 'Count' },
      { value: 'sum', label: 'Sum' },
      { value: 'avg', label: 'Average' },
      { value: 'min', label: 'Minimum' },
      { value: 'max', label: 'Maximum' }
    ]

    const isValid = computed(() => {
      return report.value.report_name && 
             report.value.report_type && 
             report.value.data_sources.length > 0
    })

    // Watch for filter changes and update report filters
    watch([dateRangeFilter, customDateRange, userSegmentFilter, statusFilter], () => {
      updateFilters()
    }, { deep: true })

    // Watch for sort changes and update report sorting
    watch([sortField, sortDirection], () => {
      updateSorting()
    })

    const updateFilters = () => {
      const filters = {}

      if (dateRangeFilter.value) {
        if (dateRangeFilter.value === 'custom') {
          if (customDateRange.value.start && customDateRange.value.end) {
            filters.date_range = {
              start: customDateRange.value.start,
              end: customDateRange.value.end
            }
          }
        } else {
          filters.date_range = dateRangeFilter.value
        }
      }

      if (userSegmentFilter.value) {
        filters.user_segment = userSegmentFilter.value
      }

      if (statusFilter.value) {
        filters.status = statusFilter.value
      }

      report.value.filters = filters
    }

    const updateSorting = () => {
      if (sortField.value) {
        report.value.sorting = [{
          field: sortField.value,
          direction: sortDirection.value
        }]
      } else {
        report.value.sorting = []
      }
    }

    const handleSave = () => {
      if (!isValid.value) return

      // Create a clean copy of the report data
      const reportData = {
        ...report.value,
        chart_config: report.value.chart_type ? { 
          type: report.value.chart_type,
          // Add default chart configuration based on type
          title: report.value.report_name,
          responsive: true
        } : {}
      }

      emit('save', reportData)
    }

    const resetForm = () => {
      report.value = {
        report_name: '',
        description: '',
        report_type: '',
        data_sources: [],
        filters: {},
        grouping: [],
        aggregations: [],
        sorting: [],
        chart_type: '',
        chart_config: {},
        is_public: false,
        allowed_roles: []
      }
      dateRangeFilter.value = ''
      customDateRange.value = { start: '', end: '' }
      userSegmentFilter.value = ''
      statusFilter.value = ''
      sortField.value = ''
      sortDirection.value = 'desc'
    }

    const togglePreview = () => {
      showPreview.value = !showPreview.value
    }

    return {
      report,
      dateRangeFilter,
      customDateRange,
      userSegmentFilter,
      statusFilter,
      sortField,
      sortDirection,
      showPreview,
      availableDataSources,
      availableAggregations,
      isValid,
      handleSave,
      resetForm,
      togglePreview
    }
  }
}
</script>

<style scoped>
.border-bottom {
  border-bottom: 1px solid #dee2e6 !important;
}

.form-check-label {
  font-size: 0.9rem;
}

.form-text {
  font-size: 0.8rem;
}

.alert {
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
}

.alert-info {
  color: #055160;
  background-color: #cff4fc;
  border-color: #b8daff;
}

h6 {
  font-weight: 600;
  color: #495057;
  margin-bottom: 1rem;
}

.form-select[multiple] {
  height: auto;
  min-height: 100px;
}

.btn-group {
  gap: 0.25rem;
}
</style>