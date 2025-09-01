<template>
  <div class="dashboard-builder">
    <form @submit.prevent="handleSave">
      <div class="row">
        <!-- Basic Information -->
        <div class="col-md-6">
          <div class="mb-3">
            <label for="dashboardName" class="form-label">Dashboard Name *</label>
            <input 
              type="text" 
              class="form-control" 
              id="dashboardName"
              v-model="dashboard.dashboard_name" 
              required
            >
          </div>
          
          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea 
              class="form-control" 
              id="description"
              v-model="dashboard.description" 
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- Dashboard Settings -->
        <div class="col-md-6">
          <div class="mb-3">
            <label for="refreshInterval" class="form-label">Refresh Interval (seconds)</label>
            <select class="form-select" id="refreshInterval" v-model="dashboard.refresh_interval">
              <option :value="60">1 minute</option>
              <option :value="300">5 minutes</option>
              <option :value="600">10 minutes</option>
              <option :value="1800">30 minutes</option>
              <option :value="3600">1 hour</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">Access Control</label>
            <div class="form-check">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isDefault"
                v-model="dashboard.is_default"
              >
              <label class="form-check-label" for="isDefault">
                Set as default dashboard
              </label>
            </div>
          </div>

          <div class="mb-3">
            <label for="visibleRoles" class="form-label">Visible to Roles</label>
            <select 
              class="form-select" 
              id="visibleRoles" 
              v-model="dashboard.visible_to_roles" 
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

      <!-- Widget Configuration -->
      <div class="mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h6 class="mb-0">Dashboard Widgets</h6>
          <button type="button" class="btn btn-sm btn-outline-primary" @click="showAddWidgetModal = true">
            <i class="fas fa-plus me-1"></i>Add Widget
          </button>
        </div>

        <!-- Widgets Grid Preview -->
        <div class="widgets-preview border rounded p-3" style="min-height: 300px; background-color: #f8f9fa;">
          <div v-if="dashboard.widgets.length === 0" class="text-center text-muted py-5">
            <i class="fas fa-plus-circle fa-3x mb-3"></i>
            <p>No widgets added yet. Click "Add Widget" to get started.</p>
          </div>

          <div v-else class="widgets-grid">
            <div 
              v-for="(widget, index) in dashboard.widgets" 
              :key="widget.id"
              class="widget-item card mb-3"
              :style="getWidgetStyle(widget)"
            >
              <div class="card-header d-flex justify-content-between align-items-center py-2">
                <small class="fw-bold">{{ widget.title }}</small>
                <div class="btn-group btn-group-sm">
                  <button type="button" class="btn btn-outline-secondary btn-sm" @click="editWidget(index)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button type="button" class="btn btn-outline-danger btn-sm" @click="removeWidget(index)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
              <div class="card-body py-2">
                <div class="widget-preview">
                  <div v-if="widget.type === 'metric'" class="text-center">
                    <h4 class="mb-0">{{ widget.config.sample_value || '1,234' }}</h4>
                    <small class="text-muted">{{ widget.config.metric_name || 'Sample Metric' }}</small>
                  </div>
                  <div v-else-if="widget.type === 'chart'" class="text-center">
                    <i :class="getChartIcon(widget.config.chart_type)" class="fa-2x text-muted"></i>
                    <div><small>{{ widget.config.chart_type }} Chart</small></div>
                  </div>
                  <div v-else-if="widget.type === 'table'" class="text-center">
                    <i class="fas fa-table fa-2x text-muted"></i>
                    <div><small>Data Table</small></div>
                  </div>
                  <div v-else class="text-center">
                    <i class="fas fa-widget fa-2x text-muted"></i>
                    <div><small>{{ widget.type }}</small></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Layout Configuration -->
      <div class="mb-4">
        <h6 class="border-bottom pb-2">Layout Settings</h6>
        <div class="row">
          <div class="col-md-6">
            <div class="mb-3">
              <label for="gridColumns" class="form-label">Grid Columns</label>
              <select class="form-select" id="gridColumns" v-model="layoutConfig.columns">
                <option :value="2">2 Columns</option>
                <option :value="3">3 Columns</option>
                <option :value="4">4 Columns</option>
                <option :value="6">6 Columns</option>
              </select>
            </div>
          </div>

          <div class="col-md-6">
            <div class="mb-3">
              <label for="gridGap" class="form-label">Grid Gap</label>
              <select class="form-select" id="gridGap" v-model="layoutConfig.gap">
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="d-flex justify-content-between">
        <div>
          <button type="button" class="btn btn-outline-secondary me-2" @click="resetForm">
            <i class="fas fa-undo me-1"></i>Reset
          </button>
          <button type="button" class="btn btn-outline-info" @click="previewDashboard">
            <i class="fas fa-eye me-1"></i>Preview
          </button>
        </div>
        <div>
          <button type="button" class="btn btn-secondary me-2" @click="$emit('cancel')">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isValid">
            <i class="fas fa-save me-1"></i>Create Dashboard
          </button>
        </div>
      </div>
    </form>

    <!-- Add Widget Modal -->
    <div class="modal fade" tabindex="-1" v-if="showAddWidgetModal" style="display: block;" @click.self="showAddWidgetModal = false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingWidget !== null ? 'Edit' : 'Add' }} Widget</h5>
            <button type="button" class="btn-close" @click="closeWidgetModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveWidget">
              <div class="mb-3">
                <label for="widgetTitle" class="form-label">Widget Title *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="widgetTitle"
                  v-model="currentWidget.title" 
                  required
                >
              </div>

              <div class="mb-3">
                <label for="widgetType" class="form-label">Widget Type *</label>
                <select class="form-select" id="widgetType" v-model="currentWidget.type" required>
                  <option value="">Select Type</option>
                  <option value="metric">Single Metric</option>
                  <option value="chart">Chart</option>
                  <option value="table">Data Table</option>
                  <option value="progress">Progress Bar</option>
                  <option value="gauge">Gauge</option>
                </select>
              </div>

              <!-- Metric Configuration -->
              <div v-if="currentWidget.type === 'metric'" class="mb-3">
                <label for="metricName" class="form-label">Metric Name</label>
                <select class="form-select" id="metricName" v-model="currentWidget.config.metric_name">
                  <option value="total_users">Total Users</option>
                  <option value="active_users">Active Users</option>
                  <option value="total_revenue">Total Revenue</option>
                  <option value="new_signups">New Signups</option>
                  <option value="churn_rate">Churn Rate</option>
                </select>
              </div>

              <!-- Chart Configuration -->
              <div v-if="currentWidget.type === 'chart'" class="mb-3">
                <label for="chartType" class="form-label">Chart Type</label>
                <select class="form-select" id="chartType" v-model="currentWidget.config.chart_type">
                  <option value="line">Line Chart</option>
                  <option value="bar">Bar Chart</option>
                  <option value="pie">Pie Chart</option>
                  <option value="area">Area Chart</option>
                </select>
              </div>

              <!-- Size Configuration -->
              <div class="row">
                <div class="col-6">
                  <div class="mb-3">
                    <label for="widgetWidth" class="form-label">Width</label>
                    <select class="form-select" id="widgetWidth" v-model="currentWidget.config.width">
                      <option :value="1">1 Column</option>
                      <option :value="2">2 Columns</option>
                      <option :value="3">3 Columns</option>
                      <option :value="4">4 Columns</option>
                    </select>
                  </div>
                </div>
                <div class="col-6">
                  <div class="mb-3">
                    <label for="widgetHeight" class="form-label">Height</label>
                    <select class="form-select" id="widgetHeight" v-model="currentWidget.config.height">
                      <option value="small">Small</option>
                      <option value="medium">Medium</option>
                      <option value="large">Large</option>
                    </select>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeWidgetModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveWidget">
              {{ editingWidget !== null ? 'Update' : 'Add' }} Widget
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive } from 'vue'

export default {
  name: 'DashboardBuilder',
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const dashboard = ref({
      dashboard_name: '',
      description: '',
      refresh_interval: 300,
      widgets: [],
      visible_to_roles: ['admin'],
      is_default: false
    })

    const layoutConfig = reactive({
      columns: 3,
      gap: 'medium'
    })

    const showAddWidgetModal = ref(false)
    const editingWidget = ref(null)
    const currentWidget = ref({
      id: '',
      title: '',
      type: '',
      config: {
        width: 1,
        height: 'medium',
        metric_name: '',
        chart_type: 'line'
      }
    })

    const isValid = computed(() => {
      return dashboard.value.dashboard_name && dashboard.value.widgets.length > 0
    })

    const getWidgetStyle = (widget) => {
      const width = widget.config.width || 1
      const height = widget.config.height || 'medium'
      
      const heightMap = {
        small: '150px',
        medium: '200px',
        large: '300px'
      }

      return {
        width: `${(width / layoutConfig.columns) * 100}%`,
        height: heightMap[height],
        display: 'inline-block',
        verticalAlign: 'top'
      }
    }

    const getChartIcon = (chartType) => {
      const iconMap = {
        line: 'fas fa-chart-line',
        bar: 'fas fa-chart-bar',
        pie: 'fas fa-chart-pie',
        area: 'fas fa-chart-area'
      }
      return iconMap[chartType] || 'fas fa-chart-bar'
    }

    const generateWidgetId = () => {
      return 'widget_' + Math.random().toString(36).substr(2, 9)
    }

    const resetWidgetForm = () => {
      currentWidget.value = {
        id: generateWidgetId(),
        title: '',
        type: '',
        config: {
          width: 1,
          height: 'medium',
          metric_name: '',
          chart_type: 'line'
        }
      }
    }

    const saveWidget = () => {
      if (!currentWidget.value.title || !currentWidget.value.type) return

      const widget = {
        ...currentWidget.value,
        id: currentWidget.value.id || generateWidgetId()
      }

      if (editingWidget.value !== null) {
        // Edit existing widget
        dashboard.value.widgets[editingWidget.value] = widget
      } else {
        // Add new widget
        dashboard.value.widgets.push(widget)
      }

      closeWidgetModal()
    }

    const editWidget = (index) => {
      editingWidget.value = index
      currentWidget.value = { ...dashboard.value.widgets[index] }
      showAddWidgetModal.value = true
    }

    const removeWidget = (index) => {
      if (confirm('Are you sure you want to remove this widget?')) {
        dashboard.value.widgets.splice(index, 1)
      }
    }

    const closeWidgetModal = () => {
      showAddWidgetModal.value = false
      editingWidget.value = null
      resetWidgetForm()
    }

    const handleSave = () => {
      if (!isValid.value) return

      const dashboardData = {
        ...dashboard.value,
        layout_config: {
          ...layoutConfig,
          widget_positions: dashboard.value.widgets.map((widget, index) => ({
            id: widget.id,
            position: index,
            width: widget.config.width,
            height: widget.config.height
          }))
        }
      }

      emit('save', dashboardData)
    }

    const resetForm = () => {
      dashboard.value = {
        dashboard_name: '',
        description: '',
        refresh_interval: 300,
        widgets: [],
        visible_to_roles: ['admin'],
        is_default: false
      }
      layoutConfig.columns = 3
      layoutConfig.gap = 'medium'
    }

    const previewDashboard = () => {
      // TODO: Implement dashboard preview
      alert('Dashboard preview functionality coming soon!')
    }

    // Initialize widget form
    resetWidgetForm()

    return {
      dashboard,
      layoutConfig,
      showAddWidgetModal,
      editingWidget,
      currentWidget,
      isValid,
      getWidgetStyle,
      getChartIcon,
      saveWidget,
      editWidget,
      removeWidget,
      closeWidgetModal,
      handleSave,
      resetForm,
      previewDashboard
    }
  }
}
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.border-bottom {
  border-bottom: 1px solid #dee2e6 !important;
}

.widgets-preview {
  border: 2px dashed #dee2e6;
}

.widgets-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.widget-item {
  border: 1px solid #dee2e6;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.widget-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 60px;
}

.form-select[multiple] {
  height: auto;
  min-height: 100px;
}

h6 {
  font-weight: 600;
  color: #495057;
}

.card-header {
  background-color: rgba(0, 0, 0, 0.03);
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
}

.btn-group-sm .btn {
  padding: 0.125rem 0.25rem;
  font-size: 0.75rem;
}
</style>