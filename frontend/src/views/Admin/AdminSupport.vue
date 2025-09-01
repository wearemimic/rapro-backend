<template>
  <div class="admin-support">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Support Tools</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Support Tools</h1>
        </div>
        <div class="col-auto">
          <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Support Metrics Overview -->
    <div class="row mb-4">
      <!-- Users Needing Help -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-person-exclamation display-4 text-warning mb-3"></i>
            <h3 class="mb-1">{{ supportData?.support_metrics?.total_users_needing_help || 0 }}</h3>
            <p class="card-text text-muted">Users Needing Help</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-warning" style="width: 35%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Billing Issues -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-credit-card-2-back display-4 text-danger mb-3"></i>
            <h3 class="mb-1">{{ supportData?.support_metrics?.billing_issues || 0 }}</h3>
            <p class="card-text text-muted">Billing Issues</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-danger" style="width: 25%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Authentication Issues -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-shield-exclamation display-4 text-info mb-3"></i>
            <h3 class="mb-1">{{ supportData?.support_metrics?.auth_issues || 0 }}</h3>
            <p class="card-text text-muted">Auth Issues</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-info" style="width: 15%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Sessions -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-people display-4 text-success mb-3"></i>
            <h3 class="mb-1">{{ supportData?.support_metrics?.active_sessions || 0 }}</h3>
            <p class="card-text text-muted">Active Sessions</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-success" style="width: 70%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Recent Support Issues -->
      <div class="col-lg-8 mb-4">
        <div class="card">
          <div class="card-header">
            <div class="row justify-content-between align-items-center">
              <div class="col">
                <h4 class="card-header-title">Recent Support Issues</h4>
              </div>
              <div class="col-auto">
                <div class="btn-group btn-group-sm" role="group">
                  <input type="radio" class="btn-check" name="issueFilter" id="allIssues" autocomplete="off" v-model="issueFilter" value="all" @change="filterIssues">
                  <label class="btn btn-outline-secondary" for="allIssues">All</label>

                  <input type="radio" class="btn-check" name="issueFilter" id="billingOnly" autocomplete="off" v-model="issueFilter" value="billing" @change="filterIssues">
                  <label class="btn btn-outline-warning" for="billingOnly">Billing</label>

                  <input type="radio" class="btn-check" name="issueFilter" id="authOnly" autocomplete="off" v-model="issueFilter" value="authentication" @change="filterIssues">
                  <label class="btn btn-outline-info" for="authOnly">Auth</label>
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
            <div v-else-if="filteredIssues.length === 0" class="text-center py-4 text-muted">
              <i class="bi-check-circle display-4 mb-3 text-success"></i>
              <p>No {{ issueFilter === 'all' ? 'recent' : issueFilter }} issues</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-borderless table-thead-bordered table-nowrap table-align-middle">
                <thead class="thead-light">
                  <tr>
                    <th>User</th>
                    <th>Issue Type</th>
                    <th>Description</th>
                    <th>Status</th>
                    <th>Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="issue in filteredIssues" :key="issue.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar avatar-sm avatar-circle me-2">
                          <span class="avatar-initials">{{ getUserInitials(issue.user_email) }}</span>
                        </div>
                        <div>
                          <h6 class="mb-0">{{ issue.user_email }}</h6>
                          <small class="text-muted">ID: {{ issue.id }}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="badge" :class="getIssueTypeBadgeClass(issue.type)">
                        {{ formatIssueType(issue.type) }}
                      </span>
                    </td>
                    <td>
                      <div>
                        {{ issue.description }}
                      </div>
                    </td>
                    <td>
                      <span class="badge" :class="getIssueStatusBadgeClass(issue.status)">
                        {{ issue.status }}
                      </span>
                    </td>
                    <td>{{ formatDateTime(issue.timestamp) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button @click="viewIssueDetails(issue)" class="btn btn-outline-primary" title="View Details">
                          <i class="bi-eye"></i>
                        </button>
                        <button @click="resolveIssue(issue)" class="btn btn-outline-success" title="Resolve">
                          <i class="bi-check"></i>
                        </button>
                        <button @click="contactUser(issue)" class="btn btn-outline-info" title="Contact User">
                          <i class="bi-envelope"></i>
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

      <!-- User Activity Panel -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">User Activity Insights</h4>
          </div>
          <div class="card-body">
            <!-- Most Active Users -->
            <div class="mb-4">
              <h6 class="mb-3">Most Active Users (This Week)</h6>
              <div v-for="user in supportData?.user_activity?.most_active_users?.slice(0, 5)" :key="user.user__email" class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                  <div class="avatar avatar-xs avatar-circle me-2">
                    <span class="avatar-initials small">{{ getUserInitials(user.user__email) }}</span>
                  </div>
                  <small>{{ user.user__email }}</small>
                </div>
                <span class="badge bg-success">{{ user.activity_count }}</span>
              </div>
            </div>

            <!-- Least Active Users -->
            <div>
              <h6 class="mb-3">Inactive Users (14+ Days)</h6>
              <div v-for="user in supportData?.user_activity?.least_active_users?.slice(0, 5)" :key="user.email" class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                  <div class="avatar avatar-xs avatar-circle me-2">
                    <span class="avatar-initials small">{{ getUserInitials(user.email) }}</span>
                  </div>
                  <div>
                    <small class="d-block">{{ user.email }}</small>
                    <small class="text-muted">{{ user.company_name }}</small>
                  </div>
                </div>
                <button @click="contactInactiveUser(user)" class="btn btn-outline-warning btn-sm">
                  <i class="bi-envelope"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Support Actions -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h4 class="card-header-title">Support Actions</h4>
          </div>
          <div class="card-body">
            <div class="row">
              <!-- Bulk Actions -->
              <div class="col-md-4 mb-3">
                <div class="support-action-card">
                  <i class="bi-people-fill display-6 text-primary mb-3"></i>
                  <h5>Bulk User Actions</h5>
                  <p class="text-muted mb-3">Perform actions on multiple users at once</p>
                  <div class="d-grid gap-2">
                    <button @click="showBulkPasswordReset" class="btn btn-outline-primary btn-sm">
                      <i class="bi-key me-1"></i>Bulk Password Reset
                    </button>
                    <button @click="showBulkEmail" class="btn btn-outline-info btn-sm">
                      <i class="bi-envelope me-1"></i>Send Bulk Email
                    </button>
                  </div>
                </div>
              </div>

              <!-- User Impersonation -->
              <div class="col-md-4 mb-3">
                <div class="support-action-card">
                  <i class="bi-person-check-fill display-6 text-warning mb-3"></i>
                  <h5>User Impersonation</h5>
                  <p class="text-muted mb-3">Login as a user to troubleshoot issues</p>
                  <div class="input-group mb-2">
                    <input v-model="impersonateEmail" type="email" class="form-control form-control-sm" placeholder="User email">
                    <button @click="impersonateUser" :disabled="!impersonateEmail" class="btn btn-outline-warning btn-sm">
                      <i class="bi-box-arrow-in-right me-1"></i>Impersonate
                    </button>
                  </div>
                  <small class="text-muted">All impersonation sessions are logged</small>
                </div>
              </div>

              <!-- System Announcements -->
              <div class="col-md-4 mb-3">
                <div class="support-action-card">
                  <i class="bi-megaphone-fill display-6 text-success mb-3"></i>
                  <h5>System Announcements</h5>
                  <p class="text-muted mb-3">Send platform-wide notifications</p>
                  <div class="d-grid gap-2">
                    <button @click="createAnnouncement" class="btn btn-outline-success btn-sm">
                      <i class="bi-plus-circle me-1"></i>Create Announcement
                    </button>
                    <button @click="scheduleMaintenanceNotice" class="btn btn-outline-secondary btn-sm">
                      <i class="bi-calendar-event me-1"></i>Maintenance Notice
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Support Statistics -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h4 class="card-header-title">Support Statistics</h4>
          </div>
          <div class="card-body">
            <div class="row text-center">
              <div class="col-md-3">
                <div class="stat-card">
                  <h3 class="text-success mb-1">94.2%</h3>
                  <p class="text-muted mb-0">Issue Resolution Rate</p>
                </div>
              </div>
              <div class="col-md-3">
                <div class="stat-card">
                  <h3 class="text-info mb-1">2.1 hrs</h3>
                  <p class="text-muted mb-0">Average Response Time</p>
                </div>
              </div>
              <div class="col-md-3">
                <div class="stat-card">
                  <h3 class="text-warning mb-1">4.8/5</h3>
                  <p class="text-muted mb-0">User Satisfaction</p>
                </div>
              </div>
              <div class="col-md-3">
                <div class="stat-card">
                  <h3 class="text-primary mb-1">156</h3>
                  <p class="text-muted mb-0">Issues Resolved This Week</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

export default {
  name: 'AdminSupport',
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const supportData = ref(null);
    const issueFilter = ref('all');
    const impersonateEmail = ref('');
    const recentIssues = ref([]);

    const filteredIssues = computed(() => {
      if (issueFilter.value === 'all') {
        return recentIssues.value;
      }
      return recentIssues.value.filter(issue => issue.type === issueFilter.value);
    });

    const fetchSupportData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const response = await axios.get('http://localhost:8000/api/admin/support/');
        supportData.value = response.data;
        
        // Set recent issues from the API response
        recentIssues.value = response.data.recent_issues || [];
        
      } catch (err) {
        console.error('Error fetching support data:', err);
        error.value = err.response?.data?.error || 'Failed to fetch support data';
      } finally {
        loading.value = false;
      }
    };

    const filterIssues = () => {
      // Issues are filtered via computed property
    };

    const getUserInitials = (email) => {
      return email ? email.substring(0, 2).toUpperCase() : '??';
    };

    const formatIssueType = (type) => {
      const typeMap = {
        'billing': 'Billing',
        'authentication': 'Authentication',
        'technical': 'Technical',
        'general': 'General'
      };
      return typeMap[type] || type;
    };

    const getIssueTypeBadgeClass = (type) => {
      const classes = {
        'billing': 'bg-warning',
        'authentication': 'bg-info',
        'technical': 'bg-danger',
        'general': 'bg-secondary'
      };
      return classes[type] || 'bg-secondary';
    };

    const getIssueStatusBadgeClass = (status) => {
      const classes = {
        'resolved': 'bg-success',
        'unresolved': 'bg-danger',
        'in_progress': 'bg-info',
        'needs_attention': 'bg-warning'
      };
      return classes[status] || 'bg-secondary';
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return '';
      return new Date(dateString).toLocaleString();
    };

    const viewIssueDetails = (issue) => {
      console.log('View issue details:', issue);
      // TODO: Implement issue detail modal
    };

    const resolveIssue = async (issue) => {
      try {
        // In a real implementation, this would call an API to resolve the issue
        console.log('Resolving issue:', issue);
        
        // Update the issue status locally
        const issueIndex = recentIssues.value.findIndex(i => i.id === issue.id);
        if (issueIndex !== -1) {
          recentIssues.value[issueIndex].status = 'resolved';
        }
      } catch (err) {
        console.error('Error resolving issue:', err);
      }
    };

    const contactUser = (issue) => {
      console.log('Contact user:', issue);
      // TODO: Implement user contact functionality (email/SMS)
    };

    const contactInactiveUser = (user) => {
      console.log('Contact inactive user:', user);
      // TODO: Implement contact functionality for inactive users
    };

    const impersonateUser = async () => {
      if (!impersonateEmail.value) return;
      
      try {
        console.log('Impersonating user:', impersonateEmail.value);
        // TODO: Implement user impersonation functionality
        alert('User impersonation would be implemented here');
        impersonateEmail.value = '';
      } catch (err) {
        console.error('Error impersonating user:', err);
      }
    };

    const showBulkPasswordReset = () => {
      console.log('Show bulk password reset modal');
      // TODO: Implement bulk password reset modal
    };

    const showBulkEmail = () => {
      console.log('Show bulk email modal');
      // TODO: Implement bulk email modal
    };

    const createAnnouncement = () => {
      console.log('Create announcement');
      // TODO: Implement announcement creation
    };

    const scheduleMaintenanceNotice = () => {
      console.log('Schedule maintenance notice');
      // TODO: Implement maintenance notice scheduling
    };

    const refreshData = () => {
      fetchSupportData();
    };

    onMounted(() => {
      fetchSupportData();
    });

    return {
      loading,
      error,
      supportData,
      issueFilter,
      impersonateEmail,
      recentIssues,
      filteredIssues,
      filterIssues,
      getUserInitials,
      formatIssueType,
      getIssueTypeBadgeClass,
      getIssueStatusBadgeClass,
      formatDateTime,
      viewIssueDetails,
      resolveIssue,
      contactUser,
      contactInactiveUser,
      impersonateUser,
      showBulkPasswordReset,
      showBulkEmail,
      createAnnouncement,
      scheduleMaintenanceNotice,
      refreshData
    };
  }
};
</script>

<style scoped>
.admin-support {
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

.avatar {
  position: relative;
  display: inline-block;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
}

.avatar-xs {
  width: 1.5rem;
  height: 1.5rem;
}

.avatar-initials {
  width: 100%;
  height: 100%;
  background-color: #377dff;
  color: #fff;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.875rem;
}

.avatar-initials.small {
  font-size: 0.65rem;
}

.progress-sm {
  height: 0.375rem;
}

.support-action-card {
  text-align: center;
  padding: 1.5rem;
  border: 1px solid #e3e6f0;
  border-radius: 0.375rem;
  background-color: #f8f9fc;
  height: 100%;
}

.stat-card {
  padding: 1rem 0;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.btn-group .btn {
  margin-right: 0.25rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.btn-check:checked + .btn {
  background-color: #377dff;
  border-color: #377dff;
  color: #fff;
}

.display-6 {
  font-size: 2rem;
  font-weight: 600;
  line-height: 1.2;
}
</style>