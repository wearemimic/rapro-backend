<template>
  <div class="admin-users">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">User Management</li>
            </ol>
          </nav>
          <h1 class="page-header-title">User Management</h1>
        </div>
        <div class="col-auto">
          <button @click="refreshUsers" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Search -->
          <div class="col-md-4">
            <div class="input-group">
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                type="text"
                class="form-control"
                placeholder="Search users..."
              >
              <span class="input-group-text">
                <i class="bi-search"></i>
              </span>
            </div>
          </div>
          
          <!-- Role Filter -->
          <div class="col-md-3">
            <select v-model="filters.role" @change="fetchUsers" class="form-select">
              <option value="">All Roles</option>
              <option value="super_admin">Super Admin</option>
              <option value="admin">Administrator</option>
              <option value="support">Support Staff</option>
              <option value="analyst">Business Analyst</option>
              <option value="billing">Billing Admin</option>
            </select>
          </div>
          
          <!-- Status Filter -->
          <div class="col-md-3">
            <select v-model="filters.status" @change="fetchUsers" class="form-select">
              <option value="">All Statuses</option>
              <option value="active">Active Subscriptions</option>
              <option value="trial">Trial Users</option>
              <option value="admin">Admin Users</option>
            </select>
          </div>
          
          <!-- Results per page -->
          <div class="col-md-2">
            <select v-model="pagination.limit" @change="fetchUsers" class="form-select">
              <option value="10">10 per page</option>
              <option value="20">20 per page</option>
              <option value="50">50 per page</option>
              <option value="100">100 per page</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card">
      <div class="card-header">
        <div class="row justify-content-between align-items-center flex-grow-1">
          <div class="col">
            <h4 class="card-header-title">
              Users 
              <span v-if="!loading" class="badge bg-secondary ms-2">{{ pagination.totalCount }}</span>
            </h4>
          </div>
        </div>
      </div>
      
      <div class="card-body">
        <!-- Loading State -->
        <div v-if="loading && users.length === 0" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="bi-exclamation-triangle me-2"></i>{{ error }}
        </div>

        <!-- Empty State -->
        <div v-else-if="users.length === 0 && !loading" class="text-center py-4 text-muted">
          <i class="bi-people display-4 mb-3"></i>
          <p>No users found</p>
        </div>

        <!-- Users Table -->
        <div v-else class="table-responsive">
          <table class="table table-borderless table-thead-bordered table-nowrap table-align-middle">
            <thead class="thead-light">
              <tr>
                <th>User</th>
                <th>Company</th>
                <th>Subscription</th>
                <th>Admin Role</th>
                <th>Activity</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <!-- User Info -->
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar avatar-sm avatar-circle me-3">
                      <span class="avatar-initials">{{ getUserInitials(user.email) }}</span>
                    </div>
                    <div class="ms-1">
                      <h5 class="text-inherit mb-0">
                        {{ user.first_name }} {{ user.last_name }}
                      </h5>
                      <span class="d-block fs-6 text-body">{{ user.email }}</span>
                      <span v-if="user.phone_number" class="d-block fs-6 text-muted">
                        {{ user.phone_number }}
                      </span>
                    </div>
                  </div>
                </td>

                <!-- Company -->
                <td>
                  <div v-if="user.company_name">
                    <span class="d-block">{{ user.company_name }}</span>
                    <span v-if="user.city || user.state" class="d-block fs-6 text-muted">
                      {{ user.city }}<span v-if="user.city && user.state">, </span>{{ user.state }}
                    </span>
                  </div>
                  <span v-else class="text-muted">—</span>
                </td>

                <!-- Subscription -->
                <td>
                  <div class="d-flex flex-column">
                    <span class="badge mb-1" :class="getSubscriptionBadgeClass(user.subscription_status)">
                      {{ formatSubscriptionStatus(user.subscription_status) }}
                    </span>
                    <span v-if="user.subscription_plan" class="fs-6 text-muted">
                      {{ user.subscription_plan }} plan
                    </span>
                    <span v-if="user.subscription_end_date" class="fs-6 text-muted">
                      Until {{ formatDate(user.subscription_end_date) }}
                    </span>
                  </div>
                </td>

                <!-- Admin Role -->
                <td>
                  <div v-if="user.is_platform_admin">
                    <span class="badge mb-1" :class="getAdminRoleBadgeClass(user.admin_role)">
                      {{ user.admin_role_display }}
                    </span>
                    <div class="btn-group btn-group-sm">
                      <button 
                        @click="editUserRole(user)"
                        class="btn btn-outline-secondary btn-sm"
                        title="Edit Role"
                      >
                        <i class="bi-pencil"></i>
                      </button>
                    </div>
                  </div>
                  <div v-else class="d-flex align-items-center">
                    <span class="text-muted me-2">—</span>
                    <button 
                      @click="editUserRole(user)"
                      class="btn btn-outline-primary btn-sm"
                      title="Grant Admin Access"
                    >
                      <i class="bi-person-plus"></i>
                    </button>
                  </div>
                </td>

                <!-- Activity -->
                <td>
                  <div class="d-flex flex-column">
                    <small class="text-muted mb-1">
                      {{ user.client_count }} clients, {{ user.scenario_count }} scenarios
                    </small>
                    <small class="text-muted">
                      Joined {{ formatDate(user.date_joined) }}
                    </small>
                    <small v-if="user.last_login" class="text-muted">
                      Last login {{ formatDate(user.last_login) }}
                    </small>
                  </div>
                </td>

                <!-- Actions -->
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      @click="viewUser(user)"
                      class="btn btn-outline-primary"
                      title="View Details"
                    >
                      <i class="bi-eye"></i>
                    </button>
                    <button 
                      v-if="canImpersonateUser(user)"
                      @click="impersonateUser(user)"
                      class="btn btn-outline-warning"
                      title="Impersonate User"
                    >
                      <i class="bi-person-check"></i>
                    </button>
                    <div class="dropdown">
                      <button 
                        class="btn btn-outline-secondary dropdown-toggle"
                        data-bs-toggle="dropdown"
                      >
                        <i class="bi-three-dots"></i>
                      </button>
                      <div class="dropdown-menu">
                        <button @click="resetPassword(user)" class="dropdown-item">
                          <i class="bi-key me-2"></i>Reset Password
                        </button>
                        <button 
                          @click="toggleUserStatus(user)"
                          class="dropdown-item"
                          :class="{ 'text-danger': user.is_active, 'text-success': !user.is_active }"
                        >
                          <i class="bi-power me-2"></i>
                          {{ user.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="d-flex justify-content-between align-items-center mt-4">
          <div>
            Showing {{ ((pagination.page - 1) * pagination.limit) + 1 }} to 
            {{ Math.min(pagination.page * pagination.limit, pagination.totalCount) }} 
            of {{ pagination.totalCount }} users
          </div>
          <nav>
            <ul class="pagination pagination-sm mb-0">
              <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
                <button @click="goToPage(pagination.page - 1)" class="page-link">Previous</button>
              </li>
              <li 
                v-for="pageNum in getVisiblePages()" 
                :key="pageNum" 
                class="page-item"
                :class="{ active: pageNum === pagination.page }"
              >
                <button @click="goToPage(pageNum)" class="page-link">{{ pageNum }}</button>
              </li>
              <li class="page-item" :class="{ disabled: pagination.page >= pagination.totalPages }">
                <button @click="goToPage(pagination.page + 1)" class="page-link">Next</button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>

    <!-- Edit Role Modal -->
    <div class="modal fade" id="editRoleModal" tabindex="-1" ref="editRoleModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Admin Role</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedUser">
              <p><strong>User:</strong> {{ selectedUser.email }}</p>
              
              <!-- Admin Access Toggle -->
              <div class="form-check mb-3">
                <input 
                  v-model="roleForm.is_platform_admin"
                  class="form-check-input" 
                  type="checkbox" 
                  id="adminAccess"
                >
                <label class="form-check-label" for="adminAccess">
                  Grant Admin Access
                </label>
              </div>

              <!-- Role Selection -->
              <div v-if="roleForm.is_platform_admin" class="mb-3">
                <label class="form-label">Admin Role</label>
                <select v-model="roleForm.admin_role" class="form-select">
                  <option value="">Select Role</option>
                  <option value="super_admin">Super Administrator</option>
                  <option value="admin">Administrator</option>
                  <option value="support">Support Staff</option>
                  <option value="analyst">Business Analyst</option>
                  <option value="billing">Billing Administrator</option>
                </select>
              </div>

              <!-- Role Description -->
              <div v-if="roleForm.admin_role" class="alert alert-info">
                <strong>{{ getRoleDisplayName(roleForm.admin_role) }}:</strong>
                {{ getRoleDescription(roleForm.admin_role) }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              @click="saveUserRole" 
              :disabled="roleFormLoading"
              type="button" 
              class="btn btn-primary"
            >
              <span v-if="roleFormLoading" class="spinner-border spinner-border-sm me-2"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

export default {
  name: 'AdminUsers',
  setup() {
    const authStore = useAuthStore();
    const loading = ref(false);
    const error = ref(null);
    const users = ref([]);
    const searchQuery = ref('');
    const selectedUser = ref(null);
    const roleFormLoading = ref(false);
    
    const filters = ref({
      role: '',
      status: ''
    });
    
    const pagination = ref({
      page: 1,
      limit: 20,
      totalCount: 0,
      totalPages: 0
    });
    
    const roleForm = ref({
      is_platform_admin: false,
      admin_role: '',
      admin_permissions: {}
    });

    // Debounced search
    let searchTimeout;
    const debouncedSearch = () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        pagination.value.page = 1;
        fetchUsers();
      }, 500);
    };

    const fetchUsers = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        const params = {
          page: pagination.value.page,
          limit: pagination.value.limit,
          search: searchQuery.value,
          role: filters.value.role,
          status: filters.value.status
        };
        
        const response = await axios.get('http://localhost:8000/api/admin/users/', { params });
        
        users.value = response.data.users;
        pagination.value = {
          ...pagination.value,
          totalCount: response.data.totalCount,
          totalPages: response.data.totalPages
        };
        
      } catch (err) {
        console.error('Error fetching users:', err);
        error.value = err.response?.data?.error || 'Failed to fetch users';
      } finally {
        loading.value = false;
      }
    };

    const refreshUsers = () => {
      fetchUsers();
    };

    const goToPage = (page) => {
      if (page >= 1 && page <= pagination.value.totalPages) {
        pagination.value.page = page;
        fetchUsers();
      }
    };

    const getVisiblePages = () => {
      const current = pagination.value.page;
      const total = pagination.value.totalPages;
      const delta = 2;
      const range = [];
      
      const start = Math.max(1, current - delta);
      const end = Math.min(total, current + delta);
      
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    };

    const getUserInitials = (email) => {
      return email.substring(0, 2).toUpperCase();
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString();
    };

    const formatSubscriptionStatus = (status) => {
      const statusMap = {
        'active': 'Active',
        'trialing': 'Trial',
        'past_due': 'Past Due',
        'canceled': 'Canceled',
        'incomplete': 'Incomplete',
        'incomplete_expired': 'Expired',
        'unpaid': 'Unpaid'
      };
      return statusMap[status] || status || 'Unknown';
    };

    const getSubscriptionBadgeClass = (status) => {
      const classMap = {
        'active': 'bg-success',
        'trialing': 'bg-info',
        'past_due': 'bg-warning',
        'canceled': 'bg-danger',
        'incomplete': 'bg-secondary',
        'incomplete_expired': 'bg-secondary',
        'unpaid': 'bg-warning'
      };
      return classMap[status] || 'bg-secondary';
    };

    const getAdminRoleBadgeClass = (role) => {
      const classMap = {
        'super_admin': 'bg-danger',
        'admin': 'bg-primary',
        'support': 'bg-info',
        'analyst': 'bg-success',
        'billing': 'bg-warning'
      };
      return classMap[role] || 'bg-secondary';
    };

    const getRoleDisplayName = (role) => {
      const roleMap = {
        'super_admin': 'Super Administrator',
        'admin': 'Administrator',
        'support': 'Support Staff',
        'analyst': 'Business Analyst',
        'billing': 'Billing Administrator'
      };
      return roleMap[role] || role;
    };

    const getRoleDescription = (role) => {
      const descriptions = {
        'super_admin': 'Full access to all admin features and settings',
        'admin': 'Access to user management, analytics, billing, and system monitoring',
        'support': 'Access to user management and support tools',
        'analyst': 'Access to analytics and reporting features',
        'billing': 'Access to billing and payment management'
      };
      return descriptions[role] || '';
    };

    const canImpersonateUser = (user) => {
      // Super admins can impersonate anyone except other super admins
      if (authStore.adminRole === 'super_admin') {
        return user.admin_role !== 'super_admin';
      }
      // Regular admins can impersonate non-admin users
      return authStore.adminRole === 'admin' && !user.is_platform_admin;
    };

    const editUserRole = (user) => {
      selectedUser.value = user;
      roleForm.value = {
        is_platform_admin: user.is_platform_admin || false,
        admin_role: user.admin_role || '',
        admin_permissions: user.admin_permissions || {}
      };
      
      // Show modal using Bootstrap
      const modal = new bootstrap.Modal(document.getElementById('editRoleModal'));
      modal.show();
    };

    const saveUserRole = async () => {
      if (!selectedUser.value) return;
      
      try {
        roleFormLoading.value = true;
        
        await axios.put(`http://localhost:8000/api/admin/users/${selectedUser.value.id}/admin-role/`, {
          admin_role: roleForm.value.is_platform_admin ? roleForm.value.admin_role : '',
          admin_permissions: roleForm.value.admin_permissions,
          is_platform_admin: roleForm.value.is_platform_admin
        });
        
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editRoleModal'));
        modal.hide();
        
        // Refresh users list
        await fetchUsers();
        
        // Show success message (you could add a toast here)
        console.log('User role updated successfully');
        
      } catch (err) {
        console.error('Error updating user role:', err);
        error.value = err.response?.data?.error || 'Failed to update user role';
      } finally {
        roleFormLoading.value = false;
      }
    };

    const viewUser = (user) => {
      // Navigate to user detail page or show user detail modal
      console.log('View user:', user);
      // TODO: Implement user detail view
    };

    const impersonateUser = async (user) => {
      // Show confirmation dialog with reason input
      const reason = prompt(
        `Enter the reason for impersonating ${user.email}:\n\n` +
        'Note: All actions will be logged for audit purposes.',
        'User support and troubleshooting'
      );
      
      if (!reason || reason.trim() === '') {
        alert('Reason is required for user impersonation.');
        return;
      }
      
      try {
        // Start impersonation session
        const response = await axios.post(`http://localhost:8000/api/admin/users/${user.id}/impersonate/`, {
          reason: reason.trim()
        });
        
        const impersonationData = response.data;
        
        // Show success message and session info
        const proceedImpersonation = confirm(
          `Impersonation session started for ${user.email}\n\n` +
          `Session will expire in ${impersonationData.expires_in_minutes} minutes.\n` +
          `${impersonationData.warning}\n\n` +
          'Click OK to proceed with impersonation.'
        );
        
        if (proceedImpersonation) {
          // Store impersonation data in session storage
          sessionStorage.setItem('impersonation_session', JSON.stringify({
            session_id: impersonationData.session_data.session_id,
            session_key: impersonationData.session_data.session_key,
            target_user: impersonationData.target_user,
            started_at: impersonationData.session_data.started_at,
            admin_user_id: impersonationData.session_data.admin_user_id
          }));
          
          // Navigate to main dashboard as impersonated user
          // In a full implementation, you would switch the user context
          alert(
            `You are now impersonating ${user.email}.\n\n` +
            'Session ID: ' + impersonationData.session_data.session_id + '\n' +
            'Remember to end the session when finished.'
          );
          
          // For now, just show the session info
          console.log('Impersonation started:', impersonationData);
          
          // TODO: Implement actual user context switching
          // This would typically involve:
          // 1. Updating the auth store with impersonated user data
          // 2. Adding impersonation indicators to the UI
          // 3. Redirecting to the main application as the impersonated user
        }
        
      } catch (err) {
        console.error('Error starting impersonation:', err);
        const errorMessage = err.response?.data?.error || 'Failed to start impersonation session';
        alert(`Impersonation failed: ${errorMessage}`);
      }
    };

    const resetPassword = (user) => {
      // Implement password reset
      console.log('Reset password for:', user);
      // TODO: Implement password reset functionality
    };

    const toggleUserStatus = (user) => {
      // Implement user activation/deactivation
      console.log('Toggle status for:', user);
      // TODO: Implement user status toggle
    };

    onMounted(() => {
      fetchUsers();
    });

    return {
      authStore,
      loading,
      error,
      users,
      searchQuery,
      filters,
      pagination,
      selectedUser,
      roleForm,
      roleFormLoading,
      debouncedSearch,
      fetchUsers,
      refreshUsers,
      goToPage,
      getVisiblePages,
      getUserInitials,
      formatDate,
      formatSubscriptionStatus,
      getSubscriptionBadgeClass,
      getAdminRoleBadgeClass,
      getRoleDisplayName,
      getRoleDescription,
      canImpersonateUser,
      editUserRole,
      saveUserRole,
      viewUser,
      impersonateUser,
      resetPassword,
      toggleUserStatus
    };
  }
};
</script>

<style scoped>
.admin-users {
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

.pagination {
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
</style>