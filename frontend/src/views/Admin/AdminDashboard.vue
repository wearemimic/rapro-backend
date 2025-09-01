<template>
  <div class="admin-dashboard">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
              <li class="breadcrumb-item active" aria-current="page">Admin Panel</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Admin Dashboard</h1>
        </div>
        <div class="col-auto">
          <span class="badge" :class="adminBadgeClass">{{ authStore.adminRoleDisplay }}</span>
        </div>
      </div>
    </div>

    <!-- Key Metrics Cards -->
    <div class="row">
      <!-- Total Users Card -->
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="card-subtitle mb-2">Total Users</h6>
            <div class="row align-items-center gx-2">
              <div class="col">
                <span class="js-counter display-4 text-dark" v-if="!loading">
                  {{ stats.totalUsers || 0 }}
                </span>
                <div v-else class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div class="col-auto">
                <i class="bi-people text-primary" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Subscriptions Card -->
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="card-subtitle mb-2">Active Subscriptions</h6>
            <div class="row align-items-center gx-2">
              <div class="col">
                <span class="js-counter display-4 text-dark" v-if="!loading">
                  {{ stats.activeSubscriptions || 0 }}
                </span>
                <div v-else class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div class="col-auto">
                <i class="bi-credit-card text-success" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Total Clients Card -->
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="card-subtitle mb-2">Total Clients</h6>
            <div class="row align-items-center gx-2">
              <div class="col">
                <span class="js-counter display-4 text-dark" v-if="!loading">
                  {{ stats.totalClients || 0 }}
                </span>
                <div v-else class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div class="col-auto">
                <i class="bi-person-badge text-info" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Total Scenarios Card -->
      <div class="col-sm-6 col-lg-3 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="card-subtitle mb-2">Total Scenarios</h6>
            <div class="row align-items-center gx-2">
              <div class="col">
                <span class="js-counter display-4 text-dark" v-if="!loading">
                  {{ stats.totalScenarios || 0 }}
                </span>
                <div v-else class="spinner-border spinner-border-sm" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
              <div class="col-auto">
                <i class="bi-graph-up text-warning" style="font-size: 2rem;"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions & System Status -->
    <div class="row">
      <!-- Quick Actions Card -->
      <div class="col-lg-6 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">Quick Actions</h4>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush list-group-no-gutters">
              <!-- User Management -->
              <div v-if="canAccessSection('user_management')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-people text-primary"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">User Management</h5>
                    <p class="text-body fs-6 mb-0">Manage user accounts and permissions</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/users" class="btn btn-outline-primary btn-sm">
                      Manage
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- Billing Management -->
              <div v-if="canAccessSection('billing')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-credit-card text-success"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">Billing Management</h5>
                    <p class="text-body fs-6 mb-0">Monitor subscriptions and payments</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/billing" class="btn btn-outline-success btn-sm">
                      View
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- Analytics -->
              <div v-if="canAccessSection('analytics')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-bar-chart text-info"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">Analytics</h5>
                    <p class="text-body fs-6 mb-0">View platform usage and performance</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/analytics" class="btn btn-outline-info btn-sm">
                      Analyze
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- System Monitoring -->
              <div v-if="canAccessSection('system_monitoring')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-cpu text-warning"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">System Monitoring</h5>
                    <p class="text-body fs-6 mb-0">Monitor system health and performance</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/monitoring" class="btn btn-outline-warning btn-sm">
                      Monitor
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- Support Tools -->
              <div v-if="canAccessSection('support_tools')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-life-preserver text-secondary"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">Support Tools</h5>
                    <p class="text-body fs-6 mb-0">Help users and manage support tickets</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/support" class="btn btn-outline-secondary btn-sm">
                      Support
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- Tax Data Management -->
              <div v-if="canAccessSection('system_configuration')" class="list-group-item">
                <div class="row align-items-center">
                  <div class="col-auto">
                    <i class="bi-file-earmark-spreadsheet text-danger"></i>
                  </div>
                  <div class="col ms-n2">
                    <h5 class="mb-1">Tax Data Management</h5>
                    <p class="text-body fs-6 mb-0">Upload and manage tax CSV files with backup controls</p>
                  </div>
                  <div class="col-auto">
                    <router-link to="/admin/tax-data" class="btn btn-outline-danger btn-sm">
                      Manage
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Status Card -->
      <div class="col-lg-6 mb-3 mb-lg-5">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">System Status</h4>
          </div>
          <div class="card-body">
            <!-- Platform Health -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h6 class="mb-1">Platform Health</h6>
                <span class="fs-6 text-body">Overall system status</span>
              </div>
              <div class="badge bg-success">Healthy</div>
            </div>

            <!-- Recent Activity -->
            <div class="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h6 class="mb-1">Active Users (24h)</h6>
                <span class="fs-6 text-body">Users active in last 24 hours</span>
              </div>
              <div class="fw-semi-bold">{{ stats.activeUsers24h || 0 }}</div>
            </div>

            <!-- Storage Usage -->
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="mb-1">Storage Usage</h6>
                <span class="fs-6 text-body">Document and media storage</span>
              </div>
              <div class="fw-semi-bold">{{ stats.storageUsage || '0 GB' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent User Activity -->
    <div class="card">
      <div class="card-header">
        <div class="row justify-content-between align-items-center flex-grow-1">
          <div class="col">
            <h4 class="card-header-title">Recent User Activity</h4>
          </div>
          <div class="col-auto">
            <button @click="refreshStats" :disabled="loading" class="btn btn-outline-primary btn-sm">
              <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
              Refresh
            </button>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else-if="recentActivity.length === 0" class="text-center py-4 text-muted">
          <i class="bi-inbox display-4 mb-3"></i>
          <p>No recent activity to display</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-borderless table-thead-bordered table-nowrap table-align-middle card-table">
            <thead class="thead-light">
              <tr>
                <th>User</th>
                <th>Action</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="activity in recentActivity" :key="activity.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar avatar-sm avatar-circle me-2">
                      <span class="avatar-initials">{{ getUserInitials(activity.user_email) }}</span>
                    </div>
                    <div class="ms-1">
                      <span class="d-block h5 text-inherit mb-0">{{ activity.user_name }}</span>
                      <span class="d-block fs-6 text-body">{{ activity.user_email }}</span>
                    </div>
                  </div>
                </td>
                <td>{{ activity.action }}</td>
                <td>{{ formatTime(activity.timestamp) }}</td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(activity.status)">
                    {{ activity.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { ref, onMounted, computed } from 'vue';

export default {
  name: 'AdminDashboard',
  setup() {
    const authStore = useAuthStore();
    const loading = ref(true);
    const error = ref(null);
    const stats = ref({
      totalUsers: 0,
      activeSubscriptions: 0,
      totalClients: 0,
      totalScenarios: 0,
      activeUsers24h: 0,
      storageUsage: '0 GB'
    });
    const recentActivity = ref([]);

    const adminBadgeClass = computed(() => {
      const role = authStore.adminRole;
      if (role === 'super_admin') return 'bg-danger';
      if (role === 'admin') return 'bg-primary';
      if (role === 'support') return 'bg-info';
      if (role === 'analyst') return 'bg-success';
      if (role === 'billing') return 'bg-warning';
      return 'bg-secondary';
    });

    const canAccessSection = (section) => {
      return authStore.canAccessAdminSection(section);
    };

    const getUserInitials = (email) => {
      return email.substring(0, 2).toUpperCase();
    };

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString();
    };

    const getStatusBadgeClass = (status) => {
      switch (status?.toLowerCase()) {
        case 'success': return 'bg-success';
        case 'failed': return 'bg-danger';
        case 'pending': return 'bg-warning';
        default: return 'bg-secondary';
      }
    };

    const fetchStats = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // Use the auth store method to fetch admin stats
        const data = await authStore.fetchAdminStats();
        stats.value = data;
        
        // Mock recent activity for now
        recentActivity.value = [
          {
            id: 1,
            user_name: 'John Advisor',
            user_email: 'john@advisor.com',
            action: 'Created new client',
            timestamp: new Date(Date.now() - 60000 * 30),
            status: 'success'
          },
          {
            id: 2,
            user_name: 'Sarah Planning',
            user_email: 'sarah@planning.com',
            action: 'Generated scenario report',
            timestamp: new Date(Date.now() - 60000 * 60),
            status: 'success'
          }
        ];
      } catch (err) {
        console.error('Error fetching admin stats:', err);
        error.value = err.message;
        
        // Mock data for demo purposes
        stats.value = {
          totalUsers: 165,
          activeSubscriptions: 142,
          totalClients: 2400,
          totalScenarios: 8100,
          activeUsers24h: 89,
          storageUsage: '2.4 GB'
        };
      } finally {
        loading.value = false;
      }
    };

    const refreshStats = () => {
      fetchStats();
    };

    onMounted(() => {
      fetchStats();
    });

    return {
      authStore,
      loading,
      error,
      stats,
      recentActivity,
      adminBadgeClass,
      canAccessSection,
      getUserInitials,
      formatTime,
      getStatusBadgeClass,
      refreshStats
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
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

.avatar {
  position: relative;
  display: inline-block;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
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

.list-group-item {
  padding: 1rem 0;
  border: none;
  border-bottom: 1px solid #e3e6f0;
}

.list-group-item:last-child {
  border-bottom: none;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>