<template>
  <div class="admin-support-tickets">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Support Tickets</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Support Ticket Management</h1>
        </div>
        <div class="col-auto">
          <!-- Ticket Controls -->
          <div class="btn-group me-2">
            <button @click="showCreateTicketModal = true" class="btn btn-primary">
              <i class="bi-plus-circle me-1"></i>Create Ticket
            </button>
            <button @click="refreshTickets" :disabled="loading" class="btn btn-outline-primary">
              <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
              Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="row mb-4">
      <div class="col">
        <div class="card">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label">Search</label>
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search tickets..."
                  v-model="filters.search"
                  @input="debouncedSearch"
                >
              </div>
              <div class="col-md-2">
                <label class="form-label">Status</label>
                <select class="form-select" v-model="filters.status" @change="refreshTickets">
                  <option value="">All Status</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="waiting_user">Waiting for User</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">Priority</label>
                <select class="form-select" v-model="filters.priority" @change="refreshTickets">
                  <option value="">All Priority</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">Category</label>
                <select class="form-select" v-model="filters.category" @change="refreshTickets">
                  <option value="">All Categories</option>
                  <option value="billing">Billing</option>
                  <option value="technical">Technical</option>
                  <option value="feature_request">Feature Request</option>
                  <option value="bug_report">Bug Report</option>
                  <option value="account">Account</option>
                  <option value="data">Data Issue</option>
                  <option value="integration">Integration</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Assigned To</label>
                <select class="form-select" v-model="filters.assigned_to" @change="refreshTickets">
                  <option value="">All Assignments</option>
                  <option value="unassigned">Unassigned</option>
                  <option v-for="admin in adminUsers" :key="admin.id" :value="admin.id">
                    {{ admin.name }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tickets Summary Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <div class="h3 text-danger">{{ summary.openTickets || 0 }}</div>
            <div class="text-muted">Open Tickets</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <div class="h3 text-warning">{{ summary.inProgressTickets || 0 }}</div>
            <div class="text-muted">In Progress</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <div class="h3 text-info">{{ summary.slaBreach || 0 }}</div>
            <div class="text-muted">SLA Breaches</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center">
          <div class="card-body">
            <div class="h3 text-success">{{ summary.resolvedToday || 0 }}</div>
            <div class="text-muted">Resolved Today</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && tickets.length === 0" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading support tickets...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <!-- Tickets Table -->
    <div v-else class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="card-title mb-0">Support Tickets ({{ pagination.totalCount }} total)</h5>
        <div class="d-flex align-items-center">
          <span class="text-muted me-2">Show:</span>
          <select class="form-select form-select-sm" v-model="pagination.limit" @change="refreshTickets" style="width: auto;">
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="tickets.length > 0" class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Ticket ID</th>
                <th>Subject</th>
                <th>User</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Category</th>
                <th>Assigned To</th>
                <th>Created</th>
                <th>SLA</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="ticket in tickets" 
                :key="ticket.id"
                :class="{ 'table-warning': ticket.is_sla_breached }"
              >
                <td>
                  <router-link 
                    :to="`/admin/support/tickets/${ticket.id}`"
                    class="text-decoration-none fw-bold"
                  >
                    {{ ticket.ticket_id }}
                  </router-link>
                </td>
                <td>
                  <div class="text-truncate" style="max-width: 250px;" :title="ticket.subject">
                    {{ ticket.subject }}
                  </div>
                  <div class="text-muted small">
                    {{ ticket.description.substring(0, 50) }}...
                  </div>
                </td>
                <td>
                  <div>{{ ticket.user.name }}</div>
                  <div class="text-muted small">{{ ticket.user.email }}</div>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                    {{ ticket.status_display }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="getPriorityBadgeClass(ticket.priority)">
                    {{ ticket.priority_display }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ ticket.category_display }}</span>
                </td>
                <td>
                  <div v-if="ticket.assigned_admin">
                    <div>{{ ticket.assigned_admin.name }}</div>
                  </div>
                  <div v-else class="text-muted">Unassigned</div>
                </td>
                <td>
                  <div>{{ formatDate(ticket.created_at) }}</div>
                  <div class="text-muted small">{{ formatTime(ticket.created_at) }}</div>
                </td>
                <td>
                  <div v-if="ticket.is_sla_breached" class="text-danger">
                    <i class="bi-exclamation-triangle"></i> Breached
                  </div>
                  <div v-else class="text-success">
                    <i class="bi-check-circle"></i> On Track
                  </div>
                  <div class="text-muted small" v-if="ticket.time_to_first_response">
                    {{ Math.round(ticket.time_to_first_response) }}h response
                  </div>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <router-link 
                      :to="`/admin/support/tickets/${ticket.id}`"
                      class="btn btn-outline-primary"
                    >
                      <i class="bi-eye"></i>
                    </router-link>
                    <button 
                      @click="showQuickUpdateModal(ticket)"
                      class="btn btn-outline-secondary"
                    >
                      <i class="bi-pencil"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- No Tickets State -->
        <div v-else class="text-center py-5">
          <i class="bi-ticket display-4 text-muted"></i>
          <p class="mt-3">No support tickets found</p>
          <button @click="showCreateTicketModal = true" class="btn btn-primary">
            Create First Ticket
          </button>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="pagination.totalPages > 1" class="card-footer">
        <nav aria-label="Tickets pagination">
          <ul class="pagination pagination-sm justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
              <button class="page-link" @click="changePage(pagination.page - 1)" :disabled="pagination.page <= 1">
                Previous
              </button>
            </li>
            <li 
              v-for="page in visiblePages" 
              :key="page"
              class="page-item" 
              :class="{ active: page === pagination.page }"
            >
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>
            <li class="page-item" :class="{ disabled: pagination.page >= pagination.totalPages }">
              <button 
                class="page-link" 
                @click="changePage(pagination.page + 1)"
                :disabled="pagination.page >= pagination.totalPages"
              >
                Next
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Create Ticket Modal -->
    <div class="modal fade" :class="{ show: showCreateTicketModal }" style="display: block;" v-if="showCreateTicketModal">
      <div class="modal-backdrop" @click="showCreateTicketModal = false"></div>
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Support Ticket</h5>
            <button type="button" class="btn-close" @click="showCreateTicketModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createTicket">
              <div class="mb-3">
                <label class="form-label">User *</label>
                <select class="form-select" v-model="newTicket.user_id" required>
                  <option value="">Select User</option>
                  <option v-for="user in availableUsers" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.email }})
                  </option>
                </select>
              </div>
              <div class="row">
                <div class="col-md-8">
                  <div class="mb-3">
                    <label class="form-label">Subject *</label>
                    <input type="text" class="form-control" v-model="newTicket.subject" required>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label class="form-label">Priority</label>
                    <select class="form-select" v-model="newTicket.priority">
                      <option value="low">Low</option>
                      <option value="medium" selected>Medium</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Category</label>
                <select class="form-select" v-model="newTicket.category">
                  <option value="other">Other</option>
                  <option value="billing">Billing Issue</option>
                  <option value="technical">Technical Problem</option>
                  <option value="feature_request">Feature Request</option>
                  <option value="bug_report">Bug Report</option>
                  <option value="account">Account Issue</option>
                  <option value="data">Data Issue</option>
                  <option value="integration">Integration Problem</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Description *</label>
                <textarea 
                  class="form-control" 
                  rows="4" 
                  v-model="newTicket.description"
                  placeholder="Describe the issue or request..."
                  required
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showCreateTicketModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="createTicket" :disabled="creatingTicket">
              <span v-if="creatingTicket" class="spinner-border spinner-border-sm me-1"></span>
              Create Ticket
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Update Modal -->
    <div class="modal fade" :class="{ show: showQuickUpdate }" style="display: block;" v-if="showQuickUpdate">
      <div class="modal-backdrop" @click="showQuickUpdate = false"></div>
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Quick Update - {{ selectedTicket?.ticket_id }}</h5>
            <button type="button" class="btn-close" @click="showQuickUpdate = false"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="ticketUpdate.status">
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="waiting_user">Waiting for User</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Priority</label>
                  <select class="form-select" v-model="ticketUpdate.priority">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Assign To</label>
              <select class="form-select" v-model="ticketUpdate.assigned_admin_id">
                <option value="">Unassigned</option>
                <option v-for="admin in adminUsers" :key="admin.id" :value="admin.id">
                  {{ admin.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showQuickUpdate = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="updateTicket" :disabled="updatingTicket">
              <span v-if="updatingTicket" class="spinner-border spinner-border-sm me-1"></span>
              Update
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { debounce } from 'lodash-es'

export default {
  name: 'AdminSupportTickets',
  setup() {
    const router = useRouter()
    
    // Reactive state
    const loading = ref(false)
    const error = ref(null)
    const tickets = ref([])
    const summary = ref({})
    const adminUsers = ref([])
    const availableUsers = ref([])
    
    // Pagination
    const pagination = ref({
      page: 1,
      limit: 20,
      totalCount: 0,
      totalPages: 0
    })
    
    // Filters
    const filters = ref({
      search: '',
      status: '',
      priority: '',
      category: '',
      assigned_to: ''
    })
    
    // Modals
    const showCreateTicketModal = ref(false)
    const showQuickUpdate = ref(false)
    const selectedTicket = ref(null)
    const creatingTicket = ref(false)
    const updatingTicket = ref(false)
    
    // New ticket form
    const newTicket = ref({
      user_id: '',
      subject: '',
      description: '',
      category: 'other',
      priority: 'medium'
    })
    
    // Ticket update form
    const ticketUpdate = ref({
      status: '',
      priority: '',
      assigned_admin_id: ''
    })

    // Computed properties
    const visiblePages = computed(() => {
      const pages = []
      const totalPages = pagination.value.totalPages
      const currentPage = pagination.value.page
      
      // Show up to 5 pages around current page
      const start = Math.max(1, currentPage - 2)
      const end = Math.min(totalPages, currentPage + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    // Methods
    const refreshTickets = async () => {
      loading.value = true
      error.value = null
      
      try {
        const params = {
          page: pagination.value.page,
          limit: pagination.value.limit,
          ...filters.value
        }
        
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const response = await axios.get('/api/admin/support/tickets/', { params })
        
        tickets.value = response.data.tickets
        pagination.value = {
          page: response.data.page,
          limit: response.data.limit,
          totalCount: response.data.totalCount,
          totalPages: response.data.totalPages
        }
        
        // Update summary
        updateSummary()
        
      } catch (err) {
        console.error('Failed to fetch tickets:', err)
        error.value = err.response?.data?.error || 'Failed to load support tickets'
      } finally {
        loading.value = false
      }
    }

    const updateSummary = () => {
      summary.value = {
        openTickets: tickets.value.filter(t => t.status === 'open').length,
        inProgressTickets: tickets.value.filter(t => t.status === 'in_progress').length,
        slaBreach: tickets.value.filter(t => t.is_sla_breached).length,
        resolvedToday: tickets.value.filter(t => {
          const today = new Date().toDateString()
          return t.resolved_at && new Date(t.resolved_at).toDateString() === today
        }).length
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= pagination.value.totalPages) {
        pagination.value.page = page
        refreshTickets()
      }
    }

    const debouncedSearch = debounce(() => {
      pagination.value.page = 1 // Reset to first page
      refreshTickets()
    }, 300)

    const showQuickUpdateModal = (ticket) => {
      selectedTicket.value = ticket
      ticketUpdate.value = {
        status: ticket.status,
        priority: ticket.priority,
        assigned_admin_id: ticket.assigned_admin?.id || ''
      }
      showQuickUpdate.value = true
    }

    const createTicket = async () => {
      if (!newTicket.value.user_id || !newTicket.value.subject || !newTicket.value.description) {
        return
      }
      
      creatingTicket.value = true
      
      try {
        await axios.post('/api/admin/support/tickets/create/', newTicket.value)
        
        // Reset form
        newTicket.value = {
          user_id: '',
          subject: '',
          description: '',
          category: 'other',
          priority: 'medium'
        }
        
        showCreateTicketModal.value = false
        refreshTickets()
        
      } catch (err) {
        console.error('Failed to create ticket:', err)
        error.value = err.response?.data?.error || 'Failed to create ticket'
      } finally {
        creatingTicket.value = false
      }
    }

    const updateTicket = async () => {
      if (!selectedTicket.value) return
      
      updatingTicket.value = true
      
      try {
        await axios.put(`/api/admin/support/tickets/${selectedTicket.value.id}/update/`, ticketUpdate.value)
        
        showQuickUpdate.value = false
        refreshTickets()
        
      } catch (err) {
        console.error('Failed to update ticket:', err)
        error.value = err.response?.data?.error || 'Failed to update ticket'
      } finally {
        updatingTicket.value = false
      }
    }

    const loadAdminUsers = async () => {
      try {
        const response = await axios.get('/api/admin/users/', {
          params: { role: 'admin' }
        })
        adminUsers.value = response.data.users.map(u => ({
          id: u.id,
          name: u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.email
        }))
      } catch (err) {
        console.error('Failed to load admin users:', err)
      }
    }

    const loadAvailableUsers = async () => {
      try {
        const response = await axios.get('/api/admin/users/', {
          params: { limit: 100 }
        })
        availableUsers.value = response.data.users.map(u => ({
          id: u.id,
          name: u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.email,
          email: u.email
        }))
      } catch (err) {
        console.error('Failed to load users:', err)
      }
    }

    // Helper methods
    const getStatusBadgeClass = (status) => {
      const classes = {
        open: 'bg-danger',
        in_progress: 'bg-warning', 
        waiting_user: 'bg-info',
        resolved: 'bg-success',
        closed: 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
    }

    const getPriorityBadgeClass = (priority) => {
      const classes = {
        low: 'bg-success',
        medium: 'bg-primary',
        high: 'bg-warning',
        urgent: 'bg-danger'
      }
      return classes[priority] || 'bg-secondary'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    // Watch for filter changes
    watch(() => filters.value.status, () => refreshTickets())
    watch(() => filters.value.priority, () => refreshTickets())
    watch(() => filters.value.category, () => refreshTickets())
    watch(() => filters.value.assigned_to, () => refreshTickets())

    // Initialize
    onMounted(() => {
      refreshTickets()
      loadAdminUsers()
      loadAvailableUsers()
    })

    return {
      // State
      loading,
      error,
      tickets,
      summary,
      adminUsers,
      availableUsers,
      pagination,
      filters,
      showCreateTicketModal,
      showQuickUpdate,
      selectedTicket,
      creatingTicket,
      updatingTicket,
      newTicket,
      ticketUpdate,
      
      // Computed
      visiblePages,
      
      // Methods
      refreshTickets,
      changePage,
      debouncedSearch,
      showQuickUpdateModal,
      createTicket,
      updateTicket,
      getStatusBadgeClass,
      getPriorityBadgeClass,
      formatDate,
      formatTime
    }
  }
}
</script>

<style scoped>
.admin-support-tickets {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
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

.table-warning {
  --bs-table-accent-bg: var(--bs-warning-bg-subtle);
}
</style>