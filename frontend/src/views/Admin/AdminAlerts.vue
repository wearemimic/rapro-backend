<template>
  <div class="admin-alerts">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Alert Management</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Alert & Notification Management</h1>
        </div>
        <div class="col-auto">
          <!-- Alert Controls -->
          <div class="btn-group me-2">
            <button @click="showCreateRuleModal = true" class="btn btn-primary">
              <i class="bi-plus-circle me-1"></i>Create Rule
            </button>
            <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
              <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Management Tabs -->
    <div class="row mb-4">
      <div class="col">
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
              <i class="bi-gear me-2"></i>Alert Rules
              <span class="badge bg-primary ms-1">{{ alertRules.length }}</span>
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'notifications' }" @click="activeTab = 'notifications'">
              <i class="bi-bell me-2"></i>Recent Notifications
              <span class="badge bg-info ms-1">{{ notifications.length }}</span>
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
              <i class="bi-sliders me-2"></i>Settings
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
      <p class="mt-3">Loading alert data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <!-- Alert Rules Tab -->
    <div v-show="activeTab === 'rules'" class="tab-content">
      <!-- Rules Filters -->
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="input-group">
            <span class="input-group-text"><i class="bi-funnel"></i></span>
            <select class="form-select" v-model="rulesFilter.alert_type" @change="refreshAlertRules">
              <option value="">All Alert Types</option>
              <option value="metric_threshold">Metric Threshold</option>
              <option value="error_rate">Error Rate</option>
              <option value="user_activity">User Activity</option>
              <option value="revenue_change">Revenue Change</option>
              <option value="system_health">System Health</option>
              <option value="sla_breach">SLA Breach</option>
            </select>
          </div>
        </div>
        <div class="col-md-3">
          <div class="input-group">
            <span class="input-group-text"><i class="bi-toggle-on"></i></span>
            <select class="form-select" v-model="rulesFilter.is_active" @change="refreshAlertRules">
              <option value="">All Rules</option>
              <option value="true">Active Only</option>
              <option value="false">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Alert Rules List -->
      <div class="card">
        <div class="card-body">
          <div v-if="alertRules.length > 0">
            <div class="row">
              <div v-for="rule in alertRules" :key="rule.id" class="col-lg-6 col-xl-4 mb-4">
                <div class="card h-100" :class="{ 'border-success': rule.is_active, 'border-secondary': !rule.is_active }">
                  <div class="card-header d-flex justify-content-between align-items-center">
                    <div class="d-flex align-items-center">
                      <span class="badge me-2" :class="getAlertTypeBadgeClass(rule.alert_type)">
                        {{ rule.alert_type_display }}
                      </span>
                      <span class="badge" :class="rule.is_active ? 'bg-success' : 'bg-secondary'">
                        {{ rule.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                    <div class="btn-group btn-group-sm">
                      <button @click="testAlertRule(rule)" class="btn btn-outline-primary" title="Test">
                        <i class="bi-play-circle"></i>
                      </button>
                      <button @click="editAlertRule(rule)" class="btn btn-outline-secondary" title="Edit">
                        <i class="bi-pencil"></i>
                      </button>
                      <button @click="deleteAlertRule(rule)" class="btn btn-outline-danger" title="Delete">
                        <i class="bi-trash"></i>
                      </button>
                    </div>
                  </div>
                  
                  <div class="card-body">
                    <h6 class="card-title">{{ rule.name }}</h6>
                    <p class="card-text text-muted small" v-if="rule.description">{{ rule.description }}</p>
                    
                    <div class="mb-2" v-if="rule.threshold_value">
                      <strong>Threshold:</strong> {{ rule.comparison_operator }} {{ rule.threshold_value }}
                    </div>
                    
                    <div class="mb-2">
                      <strong>Check Interval:</strong> Every {{ rule.check_interval_minutes }} min
                    </div>
                    
                    <div class="mb-2">
                      <strong>Cooldown:</strong> {{ rule.cooldown_minutes }} min
                    </div>

                    <div class="mb-3">
                      <strong>Channels:</strong>
                      <div class="mt-1">
                        <span v-for="channel in rule.notification_channels" :key="channel" 
                              class="badge bg-info me-1">{{ channel }}</span>
                      </div>
                    </div>

                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <small class="text-muted">
                          Triggered: {{ rule.trigger_count }} times
                        </small>
                      </div>
                      <div>
                        <small class="text-muted" v-if="rule.last_triggered">
                          Last: {{ formatDate(rule.last_triggered) }}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- No Rules State -->
          <div v-else class="text-center py-5">
            <i class="bi-bell-slash display-4 text-muted"></i>
            <p class="mt-3">No alert rules configured</p>
            <button @click="showCreateRuleModal = true" class="btn btn-primary">
              Create First Alert Rule
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications Tab -->
    <div v-show="activeTab === 'notifications'" class="tab-content">
      <!-- Notifications Filters -->
      <div class="row mb-3">
        <div class="col-md-3">
          <select class="form-select" v-model="notificationsFilter.status" @change="refreshNotifications">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="sent">Sent</option>
            <option value="failed">Failed</option>
            <option value="delivered">Delivered</option>
          </select>
        </div>
        <div class="col-md-3">
          <select class="form-select" v-model="notificationsFilter.days" @change="refreshNotifications">
            <option value="1">Last 24 hours</option>
            <option value="7" selected>Last 7 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="card">
        <div class="card-body">
          <div v-if="notifications.length > 0">
            <div class="list-group list-group-flush">
              <div v-for="notification in notifications" :key="notification.id" 
                   class="list-group-item d-flex justify-content-between align-items-start">
                <div class="ms-2 me-auto">
                  <div class="d-flex align-items-center mb-2">
                    <span class="badge me-2" :class="getSeverityBadgeClass(notification.severity)">
                      {{ notification.severity.toUpperCase() }}
                    </span>
                    <span class="badge bg-secondary me-2">{{ notification.notification_channel }}</span>
                    <span class="badge me-2" :class="getStatusBadgeClass(notification.status)">
                      {{ notification.status_display }}
                    </span>
                    <small class="text-muted">{{ notification.alert_rule.name }}</small>
                  </div>
                  
                  <p class="mb-1">{{ notification.alert_message }}</p>
                  
                  <div class="small text-muted">
                    <div>To: {{ notification.recipient }}</div>
                    <div>Created: {{ formatDateTime(notification.created_at) }}</div>
                    <div v-if="notification.sent_at">Sent: {{ formatDateTime(notification.sent_at) }}</div>
                    <div v-if="notification.error_message" class="text-danger">
                      Error: {{ notification.error_message }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="notificationsPagination.totalPages > 1" class="mt-3">
              <nav aria-label="Notifications pagination">
                <ul class="pagination pagination-sm justify-content-center">
                  <li class="page-item" :class="{ disabled: notificationsPagination.page <= 1 }">
                    <button class="page-link" @click="changeNotificationsPage(notificationsPagination.page - 1)" 
                            :disabled="notificationsPagination.page <= 1">Previous</button>
                  </li>
                  <li v-for="page in getVisiblePages(notificationsPagination)" :key="page"
                      class="page-item" :class="{ active: page === notificationsPagination.page }">
                    <button class="page-link" @click="changeNotificationsPage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ disabled: notificationsPagination.page >= notificationsPagination.totalPages }">
                    <button class="page-link" @click="changeNotificationsPage(notificationsPagination.page + 1)"
                            :disabled="notificationsPagination.page >= notificationsPagination.totalPages">Next</button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
          
          <!-- No Notifications State -->
          <div v-else class="text-center py-5">
            <i class="bi-bell display-4 text-muted"></i>
            <p class="mt-3">No notifications found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Tab -->
    <div v-show="activeTab === 'settings'" class="tab-content">
      <div class="row">
        <div class="col-lg-8">
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Global Alert Settings</h5>
            </div>
            <div class="card-body">
              <div class="alert alert-info">
                <i class="bi-info-circle me-2"></i>
                Global alert settings and notification channel configuration will be implemented here.
              </div>
              
              <!-- Default notification channels -->
              <div class="mb-3">
                <label class="form-label">Default Notification Channels</label>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="emailDefault" checked disabled>
                  <label class="form-check-label" for="emailDefault">Email (Required)</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="slackDefault">
                  <label class="form-check-label" for="slackDefault">Slack (Coming Soon)</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="smsDefault">
                  <label class="form-check-label" for="smsDefault">SMS (Coming Soon)</label>
                </div>
              </div>

              <!-- Default recipients -->
              <div class="mb-3">
                <label class="form-label">Default Recipients</label>
                <textarea class="form-control" rows="3" placeholder="admin@example.com&#10;alerts@example.com"></textarea>
                <div class="form-text">One email address per line</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Rule Modal -->
    <div class="modal fade" :class="{ show: showCreateRuleModal || showEditRuleModal }" 
         style="display: block;" v-if="showCreateRuleModal || showEditRuleModal">
      <div class="modal-backdrop" @click="closeRuleModal"></div>
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingRule ? 'Edit' : 'Create' }} Alert Rule</h5>
            <button type="button" class="btn-close" @click="closeRuleModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveAlertRule">
              <div class="row">
                <div class="col-md-8">
                  <div class="mb-3">
                    <label class="form-label">Rule Name *</label>
                    <input type="text" class="form-control" v-model="ruleForm.name" required>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Status</label>
                    <select class="form-select" v-model="ruleForm.is_active">
                      <option :value="true">Active</option>
                      <option :value="false">Inactive</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea class="form-control" v-model="ruleForm.description" rows="2"></textarea>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Alert Type *</label>
                    <select class="form-select" v-model="ruleForm.alert_type" required>
                      <option value="">Select Type</option>
                      <option value="metric_threshold">Metric Threshold</option>
                      <option value="error_rate">Error Rate</option>
                      <option value="user_activity">User Activity</option>
                      <option value="revenue_change">Revenue Change</option>
                      <option value="system_health">System Health</option>
                      <option value="sla_breach">SLA Breach</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label class="form-label">Comparison</label>
                    <select class="form-select" v-model="ruleForm.comparison_operator">
                      <option value=">">Greater than (>)</option>
                      <option value=">=">Greater or equal (>=)</option>
                      <option value="<">Less than (<)</option>
                      <option value="<=">Less or equal (<=)</option>
                      <option value="==">Equal to (==)</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-3">
                  <div class="mb-3">
                    <label class="form-label">Threshold Value</label>
                    <input type="number" class="form-control" v-model="ruleForm.threshold_value" step="0.01">
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Check Interval (minutes)</label>
                    <input type="number" class="form-control" v-model="ruleForm.check_interval_minutes" min="1" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Cooldown Period (minutes)</label>
                    <input type="number" class="form-control" v-model="ruleForm.cooldown_minutes" min="0" required>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Notification Channels</label>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" value="email" v-model="ruleForm.notification_channels" id="channelEmail">
                  <label class="form-check-label" for="channelEmail">Email</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" value="slack" v-model="ruleForm.notification_channels" id="channelSlack" disabled>
                  <label class="form-check-label" for="channelSlack">Slack (Coming Soon)</label>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Recipients</label>
                <textarea 
                  class="form-control" 
                  v-model="recipientsText" 
                  rows="3" 
                  placeholder="admin@example.com&#10;alerts@example.com"
                ></textarea>
                <div class="form-text">One email address per line</div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeRuleModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveAlertRule" :disabled="savingRule">
              <span v-if="savingRule" class="spinner-border spinner-border-sm me-1"></span>
              {{ editingRule ? 'Update' : 'Create' }} Rule
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'AdminAlerts',
  setup() {
    // Reactive state
    const loading = ref(false)
    const error = ref(null)
    const activeTab = ref('rules')
    
    // Alert rules
    const alertRules = ref([])
    const rulesFilter = ref({
      alert_type: '',
      is_active: ''
    })
    
    // Notifications
    const notifications = ref([])
    const notificationsFilter = ref({
      status: '',
      days: 7
    })
    const notificationsPagination = ref({
      page: 1,
      limit: 20,
      totalCount: 0,
      totalPages: 0
    })
    
    // Modals
    const showCreateRuleModal = ref(false)
    const showEditRuleModal = ref(false)
    const editingRule = ref(null)
    const savingRule = ref(false)
    
    // Rule form
    const ruleForm = ref({
      name: '',
      description: '',
      alert_type: '',
      is_active: true,
      threshold_value: null,
      comparison_operator: '>',
      notification_channels: ['email'],
      recipients: [],
      check_interval_minutes: 5,
      cooldown_minutes: 60
    })

    // Computed properties
    const hasAnyData = computed(() => {
      return alertRules.value.length > 0 || notifications.value.length > 0
    })

    const recipientsText = computed({
      get() {
        return ruleForm.value.recipients.join('\n')
      },
      set(value) {
        ruleForm.value.recipients = value.split('\n').map(r => r.trim()).filter(r => r)
      }
    })

    // Methods
    const refreshData = () => {
      if (activeTab.value === 'rules') {
        refreshAlertRules()
      } else if (activeTab.value === 'notifications') {
        refreshNotifications()
      }
    }

    const refreshAlertRules = async () => {
      loading.value = true
      error.value = null
      
      try {
        const params = { ...rulesFilter.value }
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        
        const response = await axios.get('/api/admin/alerts/rules/', { params })
        alertRules.value = response.data.alert_rules
        
      } catch (err) {
        console.error('Failed to fetch alert rules:', err)
        error.value = err.response?.data?.error || 'Failed to load alert rules'
      } finally {
        loading.value = false
      }
    }

    const refreshNotifications = async () => {
      loading.value = true
      error.value = null
      
      try {
        const params = {
          page: notificationsPagination.value.page,
          limit: notificationsPagination.value.limit,
          ...notificationsFilter.value
        }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        
        const response = await axios.get('/api/admin/alerts/notifications/', { params })
        notifications.value = response.data.notifications
        notificationsPagination.value = {
          page: response.data.page,
          limit: response.data.limit,
          totalCount: response.data.totalCount,
          totalPages: response.data.totalPages
        }
        
      } catch (err) {
        console.error('Failed to fetch notifications:', err)
        error.value = err.response?.data?.error || 'Failed to load notifications'
      } finally {
        loading.value = false
      }
    }

    const editAlertRule = (rule) => {
      editingRule.value = rule
      ruleForm.value = {
        name: rule.name,
        description: rule.description || '',
        alert_type: rule.alert_type,
        is_active: rule.is_active,
        threshold_value: rule.threshold_value,
        comparison_operator: rule.comparison_operator,
        notification_channels: [...rule.notification_channels],
        recipients: [...rule.recipients],
        check_interval_minutes: rule.check_interval_minutes,
        cooldown_minutes: rule.cooldown_minutes
      }
      showEditRuleModal.value = true
    }

    const closeRuleModal = () => {
      showCreateRuleModal.value = false
      showEditRuleModal.value = false
      editingRule.value = null
      resetRuleForm()
    }

    const resetRuleForm = () => {
      ruleForm.value = {
        name: '',
        description: '',
        alert_type: '',
        is_active: true,
        threshold_value: null,
        comparison_operator: '>',
        notification_channels: ['email'],
        recipients: [],
        check_interval_minutes: 5,
        cooldown_minutes: 60
      }
    }

    const saveAlertRule = async () => {
      savingRule.value = true
      
      try {
        if (editingRule.value) {
          // Update existing rule
          await axios.put(`/api/admin/alerts/rules/${editingRule.value.id}/`, ruleForm.value)
        } else {
          // Create new rule
          await axios.post('/api/admin/alerts/rules/create/', ruleForm.value)
        }
        
        closeRuleModal()
        refreshAlertRules()
        
      } catch (err) {
        console.error('Failed to save alert rule:', err)
        error.value = err.response?.data?.error || 'Failed to save alert rule'
      } finally {
        savingRule.value = false
      }
    }

    const deleteAlertRule = async (rule) => {
      if (!confirm(`Are you sure you want to delete the alert rule "${rule.name}"?`)) {
        return
      }
      
      try {
        await axios.delete(`/api/admin/alerts/rules/${rule.id}/delete/`)
        refreshAlertRules()
        
      } catch (err) {
        console.error('Failed to delete alert rule:', err)
        error.value = err.response?.data?.error || 'Failed to delete alert rule'
      }
    }

    const testAlertRule = async (rule) => {
      try {
        await axios.post(`/api/admin/alerts/rules/${rule.id}/test/`)
        alert(`Test notification sent for rule "${rule.name}"`)
        
      } catch (err) {
        console.error('Failed to test alert rule:', err)
        error.value = err.response?.data?.error || 'Failed to test alert rule'
      }
    }

    const changeNotificationsPage = (page) => {
      if (page >= 1 && page <= notificationsPagination.value.totalPages) {
        notificationsPagination.value.page = page
        refreshNotifications()
      }
    }

    const getVisiblePages = (pagination) => {
      const pages = []
      const totalPages = pagination.totalPages
      const currentPage = pagination.page
      
      const start = Math.max(1, currentPage - 2)
      const end = Math.min(totalPages, currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    }

    // Helper methods
    const getAlertTypeBadgeClass = (alertType) => {
      const classes = {
        metric_threshold: 'bg-primary',
        error_rate: 'bg-danger',
        user_activity: 'bg-info',
        revenue_change: 'bg-success',
        system_health: 'bg-warning',
        sla_breach: 'bg-dark'
      }
      return classes[alertType] || 'bg-secondary'
    }

    const getSeverityBadgeClass = (severity) => {
      const classes = {
        info: 'bg-info',
        low: 'bg-success',
        medium: 'bg-warning',
        high: 'bg-danger',
        critical: 'bg-danger'
      }
      return classes[severity] || 'bg-secondary'
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        pending: 'bg-warning',
        sent: 'bg-primary',
        failed: 'bg-danger',
        delivered: 'bg-success'
      }
      return classes[status] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Watch for tab changes
    watch(activeTab, (newTab) => {
      if (newTab === 'rules') {
        refreshAlertRules()
      } else if (newTab === 'notifications') {
        refreshNotifications()
      }
    })

    // Initialize
    onMounted(() => {
      refreshAlertRules()
    })

    return {
      // State
      loading,
      error,
      activeTab,
      alertRules,
      notifications,
      rulesFilter,
      notificationsFilter,
      notificationsPagination,
      showCreateRuleModal,
      showEditRuleModal,
      editingRule,
      savingRule,
      ruleForm,
      
      // Computed
      hasAnyData,
      recipientsText,
      
      // Methods
      refreshData,
      refreshAlertRules,
      refreshNotifications,
      editAlertRule,
      closeRuleModal,
      resetRuleForm,
      saveAlertRule,
      deleteAlertRule,
      testAlertRule,
      changeNotificationsPage,
      getVisiblePages,
      getAlertTypeBadgeClass,
      getSeverityBadgeClass,
      getStatusBadgeClass,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.admin-alerts {
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

.modal {
  background: rgba(0, 0, 0, 0.5);
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  z-index: -1;
}
</style>