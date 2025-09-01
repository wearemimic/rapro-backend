<template>
  <div class="admin-configuration">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 admin-page-header">
      <div>
        <h3 class="mb-1">System Configuration</h3>
        <p class="text-muted mb-0">Manage feature flags, system settings, integrations, and email templates</p>
      </div>
      <div>
        <button 
          class="btn btn-primary me-2" 
          @click="showCreateModal = true"
          :disabled="loading"
        >
          <i class="bi bi-plus-circle me-2"></i>
          Add Configuration
        </button>
        <button 
          class="btn btn-outline-secondary" 
          @click="loadConfigurationSummary"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Feature Flags</h6>
                <h4 class="text-primary mb-0">{{ configSummary.feature_flags_total || 0 }}</h4>
                <small class="text-muted">{{ configSummary.feature_flags_enabled || 0 }} enabled</small>
              </div>
              <div class="text-primary">
                <i class="bi bi-toggles2 fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">System Configs</h6>
                <h4 class="text-info mb-0">{{ configSummary.system_configs_total || 0 }}</h4>
                <small class="text-muted">{{ Object.keys(configSummary.system_configs_by_category || {}).length }} categories</small>
              </div>
              <div class="text-info">
                <i class="bi bi-gear-fill fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Integrations</h6>
                <h4 class="text-success mb-0">{{ configSummary.integrations_total || 0 }}</h4>
                <small class="text-muted">{{ configSummary.integrations_active || 0 }} active</small>
              </div>
              <div class="text-success">
                <i class="bi bi-plugin fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">Pending Approvals</h6>
                <h4 class="text-warning mb-0">{{ configSummary.pending_approvals_total || 0 }}</h4>
                <small class="text-muted">{{ configSummary.recent_changes_count || 0 }} recent changes</small>
              </div>
              <div class="text-warning">
                <i class="bi bi-clock-history fs-1"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4" id="configTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'feature-flags' }"
          @click="activeTab = 'feature-flags'"
          type="button"
        >
          <i class="bi bi-toggles2 me-2"></i>
          Feature Flags
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'system-configs' }"
          @click="activeTab = 'system-configs'"
          type="button"
        >
          <i class="bi bi-gear me-2"></i>
          System Configs
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'integrations' }"
          @click="activeTab = 'integrations'"
          type="button"
        >
          <i class="bi bi-plugin me-2"></i>
          Integrations
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'email-templates' }"
          @click="activeTab = 'email-templates'"
          type="button"
        >
          <i class="bi bi-envelope-fill me-2"></i>
          Email Templates
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link"
          :class="{ active: activeTab === 'audit-log' }"
          @click="activeTab = 'audit-log'"
          type="button"
        >
          <i class="bi bi-journal-text me-2"></i>
          Audit Log
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      
      <!-- Feature Flags Tab -->
      <div v-if="activeTab === 'feature-flags'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Feature Flags</h6>
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="showFeatureFlagModal = true"
              >
                <i class="bi bi-plus me-1"></i>
                Add Feature Flag
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loadingFlags" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="featureFlags.length === 0" class="text-center py-4">
              <i class="bi bi-toggles2 text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No feature flags found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Rollout</th>
                    <th>Environments</th>
                    <th>Approval</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="flag in featureFlags" :key="flag.id">
                    <td>
                      <div class="fw-medium">{{ flag.name }}</div>
                    </td>
                    <td>
                      <span class="text-muted small">{{ flag.description || '-' }}</span>
                    </td>
                    <td>
                      <span class="badge" :class="flag.is_enabled ? 'bg-success' : 'bg-secondary'">
                        {{ flag.is_enabled ? 'Enabled' : 'Disabled' }}
                      </span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ flag.rollout_percentage }}%</span>
                    </td>
                    <td>
                      <div class="d-flex flex-wrap gap-1">
                        <span v-if="flag.enabled_in_dev" class="badge bg-success">Dev</span>
                        <span v-if="flag.enabled_in_staging" class="badge bg-warning">Staging</span>
                        <span v-if="flag.enabled_in_prod" class="badge bg-danger">Prod</span>
                      </div>
                    </td>
                    <td>
                      <span class="badge" :class="getApprovalStatusClass(flag.approval_status)">
                        {{ formatApprovalStatus(flag.approval_status) }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editFeatureFlag(flag)"
                          title="Edit"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          v-if="flag.approval_status === 'pending'"
                          class="btn btn-outline-success"
                          @click="approveFeatureFlag(flag)"
                          title="Approve"
                        >
                          <i class="bi bi-check-lg"></i>
                        </button>
                        <button 
                          v-if="flag.approval_status === 'pending'"
                          class="btn btn-outline-danger"
                          @click="rejectFeatureFlag(flag)"
                          title="Reject"
                        >
                          <i class="bi bi-x-lg"></i>
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

      <!-- System Configs Tab -->
      <div v-if="activeTab === 'system-configs'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">System Configurations</h6>
              <div class="d-flex gap-2">
                <select v-model="configFilters.category" class="form-select form-select-sm" style="width: auto;">
                  <option value="">All Categories</option>
                  <option v-for="category in configCategories" :key="category" :value="category">
                    {{ category }}
                  </option>
                </select>
                <select v-model="configFilters.environment" class="form-select form-select-sm" style="width: auto;">
                  <option value="">All Environments</option>
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
                <button 
                  class="btn btn-sm btn-outline-primary"
                  @click="showSystemConfigModal = true"
                >
                  <i class="bi bi-plus me-1"></i>
                  Add Config
                </button>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loadingConfigs" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="filteredSystemConfigs.length === 0" class="text-center py-4">
              <i class="bi bi-gear text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No system configurations found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Key</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Environment</th>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Approval</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="config in filteredSystemConfigs" :key="config.id">
                    <td>
                      <code class="small">{{ config.config_key }}</code>
                    </td>
                    <td>
                      <div class="fw-medium">{{ config.config_name }}</div>
                      <small class="text-muted">{{ config.description }}</small>
                    </td>
                    <td>
                      <span class="badge bg-primary">{{ config.category }}</span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ config.environment }}</span>
                    </td>
                    <td>{{ config.config_type }}</td>
                    <td>
                      <span v-if="config.is_sensitive" class="text-muted">***SENSITIVE***</span>
                      <span v-else class="font-monospace small">
                        {{ truncateValue(config.config_value) }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="getApprovalStatusClass(config.approval_status)">
                        {{ formatApprovalStatus(config.approval_status) }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editSystemConfig(config)"
                          title="Edit"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          v-if="config.approval_status === 'pending'"
                          class="btn btn-outline-success"
                          @click="approveSystemConfig(config)"
                          title="Approve"
                        >
                          <i class="bi bi-check-lg"></i>
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

      <!-- Integrations Tab -->
      <div v-if="activeTab === 'integrations'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Integration Settings</h6>
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="showIntegrationModal = true"
              >
                <i class="bi bi-plus me-1"></i>
                Add Integration
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loadingIntegrations" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="integrations.length === 0" class="text-center py-4">
              <i class="bi bi-plugin text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No integrations configured</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Integration</th>
                    <th>Environment</th>
                    <th>Status</th>
                    <th>Last Tested</th>
                    <th>Test Status</th>
                    <th>Approval</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="integration in integrations" :key="integration.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <i class="bi bi-plugin me-2"></i>
                        <span class="fw-medium">{{ integration.integration_name }}</span>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ integration.environment }}</span>
                    </td>
                    <td>
                      <span class="badge" :class="integration.is_active ? 'bg-success' : 'bg-secondary'">
                        {{ integration.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <span class="text-muted small">
                        {{ formatDate(integration.last_tested) || 'Never' }}
                      </span>
                    </td>
                    <td>
                      <span v-if="integration.test_status" class="badge" :class="getTestStatusClass(integration.test_status)">
                        {{ integration.test_status }}
                      </span>
                    </td>
                    <td>
                      <span class="badge" :class="getApprovalStatusClass(integration.approval_status)">
                        {{ formatApprovalStatus(integration.approval_status) }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editIntegration(integration)"
                          title="Edit"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-info"
                          @click="testIntegration(integration)"
                          title="Test Connection"
                        >
                          <i class="bi bi-lightning"></i>
                        </button>
                        <button 
                          v-if="integration.approval_status === 'pending'"
                          class="btn btn-outline-success"
                          @click="approveIntegration(integration)"
                          title="Approve"
                        >
                          <i class="bi bi-check-lg"></i>
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

      <!-- Email Templates Tab -->
      <div v-if="activeTab === 'email-templates'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Email Templates</h6>
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="showEmailTemplateModal = true"
              >
                <i class="bi bi-plus me-1"></i>
                Add Template
              </button>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loadingTemplates" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="emailTemplates.length === 0" class="text-center py-4">
              <i class="bi bi-envelope text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No email templates found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Usage</th>
                    <th>Approval</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="template in emailTemplates" :key="template.id">
                    <td>
                      <div class="fw-medium">{{ template.template_name }}</div>
                      <small class="text-muted">{{ template.description }}</small>
                    </td>
                    <td>
                      <span class="badge bg-primary">{{ template.template_type }}</span>
                    </td>
                    <td>
                      <span class="text-muted small">{{ template.subject }}</span>
                    </td>
                    <td>
                      <span class="badge" :class="template.is_active ? 'bg-success' : 'bg-secondary'">
                        {{ template.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <span class="text-muted small">{{ template.usage_count || 0 }} times</span>
                    </td>
                    <td>
                      <span class="badge" :class="getApprovalStatusClass(template.approval_status)">
                        {{ formatApprovalStatus(template.approval_status) }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button 
                          class="btn btn-outline-primary"
                          @click="editEmailTemplate(template)"
                          title="Edit"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-info"
                          @click="previewEmailTemplate(template)"
                          title="Preview"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button 
                          v-if="template.approval_status === 'pending'"
                          class="btn btn-outline-success"
                          @click="approveEmailTemplate(template)"
                          title="Approve"
                        >
                          <i class="bi bi-check-lg"></i>
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

      <!-- Audit Log Tab -->
      <div v-if="activeTab === 'audit-log'" class="tab-pane active">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <div class="d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Configuration Audit Log</h6>
              <div class="d-flex gap-2">
                <select v-model="auditFilters.object_type" class="form-select form-select-sm" style="width: auto;">
                  <option value="">All Types</option>
                  <option value="feature_flag">Feature Flags</option>
                  <option value="system_config">System Configs</option>
                  <option value="integration">Integrations</option>
                  <option value="email_template">Email Templates</option>
                </select>
                <select v-model="auditFilters.action" class="form-select form-select-sm" style="width: auto;">
                  <option value="">All Actions</option>
                  <option value="create">Create</option>
                  <option value="update">Update</option>
                  <option value="delete">Delete</option>
                  <option value="approve">Approve</option>
                  <option value="reject">Reject</option>
                </select>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="loadingAuditLog" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="auditLogs.length === 0" class="text-center py-4">
              <i class="bi bi-journal-text text-muted fs-1 mb-3"></i>
              <p class="text-muted mb-0">No audit log entries found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>User</th>
                    <th>Object Type</th>
                    <th>Object Name</th>
                    <th>Action</th>
                    <th>Approval Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in auditLogs" :key="log.id">
                    <td>
                      <span class="text-muted small">{{ formatDate(log.created_at) }}</span>
                    </td>
                    <td>
                      <span class="fw-medium">{{ log.user_name || 'System' }}</span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ formatObjectType(log.object_type) }}</span>
                    </td>
                    <td>{{ log.object_name }}</td>
                    <td>
                      <span class="badge" :class="getActionClass(log.action)">
                        {{ log.action }}
                      </span>
                    </td>
                    <td>
                      <span v-if="log.approval_status" class="badge" :class="getApprovalStatusClass(log.approval_status)">
                        {{ formatApprovalStatus(log.approval_status) }}
                      </span>
                      <span v-else class="text-muted">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import api from '@/services/api.js';

export default {
  name: 'AdminConfiguration',
  setup() {
    // Reactive data
    const loading = ref(false);
    const loadingFlags = ref(false);
    const loadingConfigs = ref(false);
    const loadingIntegrations = ref(false);
    const loadingTemplates = ref(false);
    const loadingAuditLog = ref(false);
    
    const activeTab = ref('feature-flags');
    
    const configSummary = ref({});
    const featureFlags = ref([]);
    const systemConfigs = ref([]);
    const integrations = ref([]);
    const emailTemplates = ref([]);
    const auditLogs = ref([]);
    
    const configCategories = ref([]);
    
    const showCreateModal = ref(false);
    const showFeatureFlagModal = ref(false);
    const showSystemConfigModal = ref(false);
    const showIntegrationModal = ref(false);
    const showEmailTemplateModal = ref(false);
    
    const configFilters = reactive({
      category: '',
      environment: ''
    });
    
    const auditFilters = reactive({
      object_type: '',
      action: ''
    });

    // Computed properties
    const filteredSystemConfigs = computed(() => {
      let filtered = systemConfigs.value;
      
      if (configFilters.category) {
        filtered = filtered.filter(config => config.category === configFilters.category);
      }
      
      if (configFilters.environment) {
        filtered = filtered.filter(config => config.environment === configFilters.environment);
      }
      
      return filtered;
    });

    // Methods
    const loadConfigurationSummary = async () => {
      try {
        loading.value = true;
        const response = await api.get('/admin/config-summary/');
        configSummary.value = response.data;
      } catch (error) {
        console.error('Error loading configuration summary:', error);
      } finally {
        loading.value = false;
      }
    };

    const loadFeatureFlags = async () => {
      try {
        loadingFlags.value = true;
        const response = await api.get('/admin/feature-flags/');
        featureFlags.value = response.data.results || response.data;
      } catch (error) {
        console.error('Error loading feature flags:', error);
      } finally {
        loadingFlags.value = false;
      }
    };

    const loadSystemConfigs = async () => {
      try {
        loadingConfigs.value = true;
        const response = await api.get('/admin/system-configs/');
        systemConfigs.value = response.data.results || response.data;
        
        // Load categories
        const categoriesResponse = await api.get('/admin/system-configs/categories/');
        configCategories.value = categoriesResponse.data;
      } catch (error) {
        console.error('Error loading system configs:', error);
      } finally {
        loadingConfigs.value = false;
      }
    };

    const loadIntegrations = async () => {
      try {
        loadingIntegrations.value = true;
        const response = await api.get('/admin/integrations/');
        integrations.value = response.data.results || response.data;
      } catch (error) {
        console.error('Error loading integrations:', error);
      } finally {
        loadingIntegrations.value = false;
      }
    };

    const loadEmailTemplates = async () => {
      try {
        loadingTemplates.value = true;
        const response = await api.get('/admin/email-templates/');
        emailTemplates.value = response.data.results || response.data;
      } catch (error) {
        console.error('Error loading email templates:', error);
      } finally {
        loadingTemplates.value = false;
      }
    };

    const loadAuditLog = async () => {
      try {
        loadingAuditLog.value = true;
        const params = new URLSearchParams();
        if (auditFilters.object_type) params.append('object_type', auditFilters.object_type);
        if (auditFilters.action) params.append('action', auditFilters.action);
        
        const response = await api.get(`/admin/config-audit/?${params}`);
        auditLogs.value = response.data.results || response.data;
      } catch (error) {
        console.error('Error loading audit log:', error);
      } finally {
        loadingAuditLog.value = false;
      }
    };

    // Approval actions
    const approveFeatureFlag = async (flag) => {
      try {
        await api.post(`/admin/feature-flags/${flag.id}/approve/`);
        await loadFeatureFlags();
        await loadConfigurationSummary();
      } catch (error) {
        console.error('Error approving feature flag:', error);
      }
    };

    const rejectFeatureFlag = async (flag) => {
      try {
        await api.post(`/admin/feature-flags/${flag.id}/reject/`);
        await loadFeatureFlags();
        await loadConfigurationSummary();
      } catch (error) {
        console.error('Error rejecting feature flag:', error);
      }
    };

    const approveSystemConfig = async (config) => {
      try {
        await api.post(`/admin/system-configs/${config.id}/approve/`);
        await loadSystemConfigs();
        await loadConfigurationSummary();
      } catch (error) {
        console.error('Error approving system config:', error);
      }
    };

    const approveIntegration = async (integration) => {
      try {
        await api.post(`/admin/integrations/${integration.id}/approve/`);
        await loadIntegrations();
        await loadConfigurationSummary();
      } catch (error) {
        console.error('Error approving integration:', error);
      }
    };

    const approveEmailTemplate = async (template) => {
      try {
        await api.post(`/admin/email-templates/${template.id}/approve/`);
        await loadEmailTemplates();
        await loadConfigurationSummary();
      } catch (error) {
        console.error('Error approving email template:', error);
      }
    };

    const testIntegration = async (integration) => {
      try {
        const response = await api.post(`/admin/integrations/${integration.id}/test_connection/`);
        console.log('Integration test result:', response.data);
        await loadIntegrations();
      } catch (error) {
        console.error('Error testing integration:', error);
      }
    };

    const previewEmailTemplate = async (template) => {
      try {
        const sampleData = {
          user_name: 'John Doe',
          company_name: 'Example Corp',
          email: 'john@example.com'
        };
        
        const response = await api.post(`/admin/email-templates/${template.id}/preview/`, {
          sample_data: sampleData
        });
        
        console.log('Email preview:', response.data);
        // Could show a modal with preview here
      } catch (error) {
        console.error('Error previewing email template:', error);
      }
    };

    // Edit actions (placeholders for now)
    const editFeatureFlag = (flag) => {
      console.log('Edit feature flag:', flag);
      showFeatureFlagModal.value = true;
    };

    const editSystemConfig = (config) => {
      console.log('Edit system config:', config);
      showSystemConfigModal.value = true;
    };

    const editIntegration = (integration) => {
      console.log('Edit integration:', integration);
      showIntegrationModal.value = true;
    };

    const editEmailTemplate = (template) => {
      console.log('Edit email template:', template);
      showEmailTemplateModal.value = true;
    };

    // Utility functions
    const formatDate = (dateString) => {
      if (!dateString) return null;
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    const formatApprovalStatus = (status) => {
      const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected'
      };
      return statusMap[status] || status;
    };

    const getApprovalStatusClass = (status) => {
      const classMap = {
        'pending': 'bg-warning',
        'approved': 'bg-success',
        'rejected': 'bg-danger'
      };
      return classMap[status] || 'bg-secondary';
    };

    const getTestStatusClass = (status) => {
      const classMap = {
        'success': 'bg-success',
        'failed': 'bg-danger',
        'pending': 'bg-warning'
      };
      return classMap[status] || 'bg-secondary';
    };

    const getActionClass = (action) => {
      const classMap = {
        'create': 'bg-success',
        'update': 'bg-info',
        'delete': 'bg-danger',
        'approve': 'bg-success',
        'reject': 'bg-danger'
      };
      return classMap[action] || 'bg-secondary';
    };

    const formatObjectType = (type) => {
      const typeMap = {
        'feature_flag': 'Feature Flag',
        'system_config': 'System Config',
        'integration': 'Integration',
        'email_template': 'Email Template'
      };
      return typeMap[type] || type;
    };

    const truncateValue = (value, maxLength = 50) => {
      if (!value) return '-';
      return value.length > maxLength ? value.substring(0, maxLength) + '...' : value;
    };

    // Watch for tab changes to load data
    watch(activeTab, (newTab) => {
      switch (newTab) {
        case 'feature-flags':
          if (featureFlags.value.length === 0) loadFeatureFlags();
          break;
        case 'system-configs':
          if (systemConfigs.value.length === 0) loadSystemConfigs();
          break;
        case 'integrations':
          if (integrations.value.length === 0) loadIntegrations();
          break;
        case 'email-templates':
          if (emailTemplates.value.length === 0) loadEmailTemplates();
          break;
        case 'audit-log':
          if (auditLogs.value.length === 0) loadAuditLog();
          break;
      }
    });

    // Watch for filter changes
    watch([auditFilters], () => {
      if (activeTab.value === 'audit-log') {
        loadAuditLog();
      }
    }, { deep: true });

    // Load initial data
    onMounted(() => {
      loadConfigurationSummary();
      loadFeatureFlags(); // Load first tab by default
    });

    return {
      // Reactive data
      loading,
      loadingFlags,
      loadingConfigs,
      loadingIntegrations,
      loadingTemplates,
      loadingAuditLog,
      activeTab,
      configSummary,
      featureFlags,
      systemConfigs,
      integrations,
      emailTemplates,
      auditLogs,
      configCategories,
      showCreateModal,
      showFeatureFlagModal,
      showSystemConfigModal,
      showIntegrationModal,
      showEmailTemplateModal,
      configFilters,
      auditFilters,

      // Computed
      filteredSystemConfigs,

      // Methods
      loadConfigurationSummary,
      loadFeatureFlags,
      loadSystemConfigs,
      loadIntegrations,
      loadEmailTemplates,
      loadAuditLog,
      approveFeatureFlag,
      rejectFeatureFlag,
      approveSystemConfig,
      approveIntegration,
      approveEmailTemplate,
      testIntegration,
      previewEmailTemplate,
      editFeatureFlag,
      editSystemConfig,
      editIntegration,
      editEmailTemplate,
      formatDate,
      formatApprovalStatus,
      getApprovalStatusClass,
      getTestStatusClass,
      getActionClass,
      formatObjectType,
      truncateValue
    };
  }
};
</script>

<style scoped>
.admin-configuration {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.admin-configuration-content {
  padding: 0;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  padding: 12px 20px;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-bottom: 2px solid #0d6efd;
  background-color: transparent;
}

.table th {
  border-top: none;
  padding: 12px;
  font-weight: 600;
  color: #495057;
}

.table td {
  padding: 12px;
  vertical-align: middle;
}

.btn-group .btn {
  padding: 6px 10px;
}

.card-header {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem 1.5rem;
}

.table-responsive {
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
}

.badge {
  font-size: 0.75em;
}

.font-monospace {
  font-family: 'Courier New', Courier, monospace;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>