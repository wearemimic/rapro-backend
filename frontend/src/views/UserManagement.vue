<template>
  <div class="container-fluid py-4">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="card-title mb-0">User Management</h3>
            <button class="btn btn-primary" @click="refreshUsers">
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
          
          <div class="card-body">
            <!-- Search and Filter -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="input-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Search users..."
                    v-model="searchQuery"
                    @input="searchUsers"
                  >
                  <button class="btn btn-outline-secondary" type="button" @click="searchUsers">
                    <i class="bi bi-search"></i>
                  </button>
                </div>
              </div>
              <div class="col-md-6 text-end">
                <span class="text-muted">{{ totalUsers }} users total</span>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <!-- Error State -->
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>

            <!-- Users Table -->
            <div v-if="!loading && !error" class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Subscription</th>
                    <th>Date Joined</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar avatar-sm rounded-circle bg-primary text-white me-2">
                          {{ user.first_name.charAt(0) }}{{ user.last_name.charAt(0) }}
                        </div>
                        <div>
                          <div class="fw-bold">{{ user.first_name }} {{ user.last_name }}</div>
                          <small class="text-muted">{{ user.username }}</small>
                        </div>
                      </div>
                    </td>
                    <td>{{ user.email }}</td>
                    <td>
                      <span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">
                        {{ user.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ user.subscription_status || 'None' }}</span>
                    </td>
                    <td>{{ formatDate(user.date_joined) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm" role="group">
                        <button 
                          class="btn btn-outline-primary" 
                          @click="viewUser(user)"
                          title="View User"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button 
                          class="btn btn-outline-secondary" 
                          @click="editUser(user)"
                          title="Edit User"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button 
                          class="btn btn-outline-warning" 
                          @click="resetPassword(user)"
                          title="Reset Password"
                        >
                          <i class="bi bi-key"></i>
                        </button>
                        <button 
                          class="btn btn-outline-danger" 
                          @click="deleteUser(user)"
                          title="Delete User"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <nav v-if="totalPages > 1" aria-label="User pagination">
              <ul class="pagination justify-content-center">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <button class="page-link" @click="changePage(currentPage - 1)" :disabled="currentPage === 1">
                    Previous
                  </button>
                </li>
                <li 
                  v-for="page in visiblePages" 
                  :key="page" 
                  class="page-item" 
                  :class="{ active: page === currentPage }"
                >
                  <button class="page-link" @click="changePage(page)">{{ page }}</button>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <button class="page-link" @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
                    Next
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- User Detail Modal -->
    <div class="modal fade" id="userModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditing ? 'Edit User' : 'User Details' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form v-if="selectedUser" @submit.prevent="saveUser">
              <div class="mb-3">
                <label class="form-label">First Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="selectedUser.first_name"
                  :readonly="!isEditing"
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Last Name</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="selectedUser.last_name"
                  :readonly="!isEditing"
                >
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="selectedUser.email"
                  readonly
                >
              </div>
              <div class="mb-3" v-if="isEditing">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="selectedUser.is_active"
                    id="isActive"
                  >
                  <label class="form-check-label" for="isActive">
                    Active User
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              {{ isEditing ? 'Cancel' : 'Close' }}
            </button>
            <button 
              v-if="isEditing" 
              type="button" 
              class="btn btn-primary" 
              @click="saveUser"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

// Reactive data
const users = ref([]);
const loading = ref(false);
const error = ref(null);
const searchQuery = ref('');
const currentPage = ref(1);
const totalUsers = ref(0);
const totalPages = ref(0);
const pageSize = ref(10);
const selectedUser = ref(null);
const isEditing = ref(false);

// Computed properties
const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, currentPage.value + 2);
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

// Methods
const loadUsers = async (page = 1, search = '') => {
  loading.value = true;
  error.value = null;
  
  try {
    const params = {
      page,
      page_size: pageSize.value,
      search
    };
    
    const response = await authStore.getUsers(params);
    users.value = response.users;
    totalUsers.value = response.total;
    totalPages.value = response.pages;
    currentPage.value = response.page;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const refreshUsers = () => {
  loadUsers(currentPage.value, searchQuery.value);
};

const searchUsers = () => {
  loadUsers(1, searchQuery.value);
};

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    loadUsers(page, searchQuery.value);
  }
};

const viewUser = (user) => {
  selectedUser.value = { ...user };
  isEditing.value = false;
  // Show modal (Bootstrap 5)
  const modal = new bootstrap.Modal(document.getElementById('userModal'));
  modal.show();
};

const editUser = (user) => {
  selectedUser.value = { ...user };
  isEditing.value = true;
  // Show modal (Bootstrap 5)
  const modal = new bootstrap.Modal(document.getElementById('userModal'));
  modal.show();
};

const saveUser = async () => {
  try {
    await authStore.updateUser(selectedUser.value.id, {
      first_name: selectedUser.value.first_name,
      last_name: selectedUser.value.last_name,
      is_active: selectedUser.value.is_active
    });
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('userModal'));
    modal.hide();
    
    // Refresh users list
    refreshUsers();
    
    alert('User updated successfully!');
  } catch (err) {
    alert('Failed to update user: ' + err.message);
  }
};

const resetPassword = async (user) => {
  if (confirm(`Send password reset email to ${user.email}?`)) {
    try {
      await authStore.resetUserPassword(user.id);
      alert('Password reset email sent successfully!');
    } catch (err) {
      alert('Failed to send password reset email: ' + err.message);
    }
  }
};

const deleteUser = async (user) => {
  if (confirm(`Are you sure you want to delete ${user.first_name} ${user.last_name}? This action cannot be undone.`)) {
    try {
      await authStore.deleteUser(user.id);
      alert('User deleted successfully!');
      refreshUsers();
    } catch (err) {
      alert('Failed to delete user: ' + err.message);
    }
  }
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

// Lifecycle
onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.375rem;
}
</style>