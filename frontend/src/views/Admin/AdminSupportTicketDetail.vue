<template>
  <div class="admin-support-ticket-detail">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item"><router-link to="/admin/support/tickets">Support Tickets</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">{{ ticket?.ticket_id || 'Loading...' }}</li>
            </ol>
          </nav>
          <h1 class="page-header-title">
            Support Ticket Detail
            <span v-if="ticket" class="badge" :class="getStatusBadgeClass(ticket.status)">{{ ticket.status_display }}</span>
          </h1>
        </div>
        <div class="col-auto">
          <router-link to="/admin/support/tickets" class="btn btn-outline-secondary">
            <i class="bi-arrow-left me-1"></i>Back to Tickets
          </router-link>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading ticket details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <!-- Ticket Content -->
    <div v-else-if="ticket">
      <div class="row">
        <!-- Main Content -->
        <div class="col-lg-8">
          <!-- Ticket Details -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">{{ ticket.subject }}</h5>
              <div class="d-flex align-items-center">
                <span class="badge me-2" :class="getPriorityBadgeClass(ticket.priority)">
                  {{ ticket.priority_display }}
                </span>
                <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                  {{ ticket.status_display }}
                </span>
              </div>
            </div>
            <div class="card-body">
              <div class="row mb-3">
                <div class="col-md-6">
                  <strong>User:</strong> {{ ticket.user.name }}<br>
                  <span class="text-muted">{{ ticket.user.email }}</span><br>
                  <span class="text-muted" v-if="ticket.user.company_name">{{ ticket.user.company_name }}</span>
                </div>
                <div class="col-md-6">
                  <strong>Created:</strong> {{ formatDateTime(ticket.created_at) }}<br>
                  <strong>Category:</strong> {{ ticket.category_display }}<br>
                  <strong>Subscription:</strong> 
                  <span class="badge bg-info">{{ ticket.user.subscription_status }}</span>
                </div>
              </div>
              
              <div class="mb-3">
                <strong>Description:</strong>
                <div class="border p-3 mt-2 bg-light rounded">
                  {{ ticket.description }}
                </div>
              </div>
              
              <div class="row" v-if="ticket.user_agent || ticket.ip_address">
                <div class="col">
                  <small class="text-muted">
                    <strong>Technical Details:</strong><br>
                    <span v-if="ticket.ip_address">IP: {{ ticket.ip_address }}</span><br>
                    <span v-if="ticket.user_agent">User Agent: {{ ticket.user_agent }}</span>
                  </small>
                </div>
              </div>
            </div>
          </div>

          <!-- Comments/Responses -->
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0">Comments & Responses</h5>
              <button @click="showAddCommentModal = true" class="btn btn-primary btn-sm">
                <i class="bi-plus-circle me-1"></i>Add Response
              </button>
            </div>
            <div class="card-body">
              <div v-if="ticket.comments && ticket.comments.length > 0">
                <div v-for="comment in ticket.comments" :key="comment.id" class="mb-4">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center">
                      <div class="avatar avatar-sm rounded-circle bg-primary text-white me-2">
                        {{ comment.user.name.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <strong>{{ comment.user.name }}</strong>
                        <div class="text-muted small">{{ formatDateTime(comment.created_at) }}</div>
                      </div>
                    </div>
                    <div>
                      <span v-if="comment.is_internal" class="badge bg-warning">Internal</span>
                      <span v-if="comment.is_automated" class="badge bg-info">Automated</span>
                    </div>
                  </div>
                  <div class="ps-4">
                    <div class="border-start border-3 border-primary ps-3">
                      {{ comment.content }}
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-muted">
                <i class="bi-chat display-4"></i>
                <p class="mt-2">No responses yet</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-lg-4">
          <!-- Ticket Management -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="card-title mb-0">Ticket Management</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="updateTicket">
                <div class="mb-3">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="updateForm.status">
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="waiting_user">Waiting for User</option>
                    <option value="resolved">Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Priority</label>
                  <select class="form-select" v-model="updateForm.priority">
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Assigned To</label>
                  <select class="form-select" v-model="updateForm.assigned_admin_id">
                    <option value="">Unassigned</option>
                    <option v-for="admin in adminUsers" :key="admin.id" :value="admin.id">
                      {{ admin.name }}
                    </option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Customer Satisfaction (1-5)</label>
                  <input type="number" class="form-control" v-model="updateForm.customer_satisfaction" min="1" max="5">
                </div>
                
                <div class="d-grid">
                  <button type="submit" class="btn btn-primary" :disabled="updating">
                    <span v-if="updating" class="spinner-border spinner-border-sm me-1"></span>
                    Update Ticket
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- SLA Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="card-title mb-0">SLA Information</h5>
            </div>
            <div class="card-body">
              <div class="mb-2">
                <strong>Response SLA:</strong> {{ ticket.response_sla_hours }} hours<br>
                <div v-if="ticket.time_to_first_response" class="text-success">
                  Responded in {{ Math.round(ticket.time_to_first_response) }} hours
                </div>
                <div v-else-if="ticket.is_sla_breached" class="text-danger">
                  <i class="bi-exclamation-triangle"></i> Response SLA breached
                </div>
                <div v-else class="text-warning">
                  Awaiting first response
                </div>
              </div>
              
              <div class="mb-2">
                <strong>Resolution SLA:</strong> {{ ticket.resolution_sla_hours }} hours<br>
                <div v-if="ticket.time_to_resolution" class="text-success">
                  Resolved in {{ Math.round(ticket.time_to_resolution) }} hours
                </div>
                <div v-else-if="ticket.is_sla_breached" class="text-danger">
                  <i class="bi-exclamation-triangle"></i> Resolution SLA at risk
                </div>
                <div v-else class="text-info">
                  Working towards resolution
                </div>
              </div>
              
              <div v-if="ticket.escalated" class="alert alert-warning mt-3">
                <i class="bi-arrow-up-circle"></i> This ticket has been escalated
              </div>
            </div>
          </div>

          <!-- Internal Notes -->
          <div class="card">
            <div class="card-header">
              <h5 class="card-title mb-0">Internal Notes</h5>
            </div>
            <div class="card-body">
              <textarea 
                class="form-control" 
                rows="4"
                v-model="updateForm.internal_notes"
                placeholder="Add internal notes (not visible to user)"
              ></textarea>
              <button @click="saveInternalNotes" class="btn btn-outline-primary btn-sm mt-2" :disabled="updating">
                Save Notes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Comment Modal -->
    <div class="modal fade" :class="{ show: showAddCommentModal }" style="display: block;" v-if="showAddCommentModal">
      <div class="modal-backdrop" @click="showAddCommentModal = false"></div>
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Response</h5>
            <button type="button" class="btn-close" @click="showAddCommentModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addComment">
              <div class="mb-3">
                <label class="form-label">Response</label>
                <textarea 
                  class="form-control" 
                  rows="4"
                  v-model="commentForm.content"
                  placeholder="Type your response..."
                  required
                ></textarea>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="commentForm.is_internal" id="internalCheck">
                <label class="form-check-label" for="internalCheck">
                  Internal note (not visible to user)
                </label>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAddCommentModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="addComment" :disabled="addingComment">
              <span v-if="addingComment" class="spinner-border spinner-border-sm me-1"></span>
              Add Response
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'AdminSupportTicketDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Reactive state
    const loading = ref(false)
    const updating = ref(false)
    const addingComment = ref(false)
    const error = ref(null)
    const ticket = ref(null)
    const adminUsers = ref([])
    
    // Modals
    const showAddCommentModal = ref(false)
    
    // Forms
    const updateForm = ref({
      status: '',
      priority: '',
      assigned_admin_id: '',
      customer_satisfaction: null,
      internal_notes: ''
    })
    
    const commentForm = ref({
      content: '',
      is_internal: false
    })

    // Methods
    const loadTicket = async () => {
      loading.value = true
      error.value = null
      
      try {
        const ticketId = route.params.ticketId
        const response = await axios.get(`/api/admin/support/tickets/${ticketId}/`)
        
        ticket.value = response.data
        
        // Populate update form
        updateForm.value = {
          status: ticket.value.status,
          priority: ticket.value.priority,
          assigned_admin_id: ticket.value.assigned_admin?.id || '',
          customer_satisfaction: ticket.value.customer_satisfaction,
          internal_notes: ticket.value.internal_notes || ''
        }
        
      } catch (err) {
        console.error('Failed to load ticket:', err)
        if (err.response?.status === 404) {
          error.value = 'Ticket not found'
        } else {
          error.value = err.response?.data?.error || 'Failed to load ticket'
        }
      } finally {
        loading.value = false
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

    const updateTicket = async () => {
      updating.value = true
      
      try {
        await axios.put(`/api/admin/support/tickets/${ticket.value.id}/update/`, updateForm.value)
        
        // Reload ticket to get updated data
        await loadTicket()
        
      } catch (err) {
        console.error('Failed to update ticket:', err)
        error.value = err.response?.data?.error || 'Failed to update ticket'
      } finally {
        updating.value = false
      }
    }

    const saveInternalNotes = async () => {
      updating.value = true
      
      try {
        await axios.put(`/api/admin/support/tickets/${ticket.value.id}/update/`, {
          internal_notes: updateForm.value.internal_notes
        })
        
      } catch (err) {
        console.error('Failed to save notes:', err)
        error.value = err.response?.data?.error || 'Failed to save notes'
      } finally {
        updating.value = false
      }
    }

    const addComment = async () => {
      if (!commentForm.value.content.trim()) return
      
      addingComment.value = true
      
      try {
        await axios.post(`/api/admin/support/tickets/${ticket.value.id}/comment/`, commentForm.value)
        
        // Reset form and close modal
        commentForm.value = {
          content: '',
          is_internal: false
        }
        showAddCommentModal.value = false
        
        // Reload ticket to show new comment
        await loadTicket()
        
      } catch (err) {
        console.error('Failed to add comment:', err)
        error.value = err.response?.data?.error || 'Failed to add comment'
      } finally {
        addingComment.value = false
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

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString()
    }

    // Watch for route changes
    watch(() => route.params.ticketId, () => {
      loadTicket()
    })

    // Initialize
    onMounted(() => {
      loadTicket()
      loadAdminUsers()
    })

    return {
      // State
      loading,
      updating,
      addingComment,
      error,
      ticket,
      adminUsers,
      showAddCommentModal,
      updateForm,
      commentForm,
      
      // Methods
      updateTicket,
      saveInternalNotes,
      addComment,
      getStatusBadgeClass,
      getPriorityBadgeClass,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.admin-support-ticket-detail {
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

.avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
</style>