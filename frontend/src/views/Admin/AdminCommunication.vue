<template>
  <div class="admin-communication">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 admin-page-header">
      <div>
        <h2 class="mb-0">Communication Tools</h2>
        <p class="text-muted mb-0">Broadcast messages, email campaigns, and user feedback</p>
      </div>
      <div>
        <button class="btn btn-primary me-2" @click="showCreateBroadcastModal = true">
          <i class="fas fa-bullhorn me-1"></i>Create Broadcast
        </button>
        <button class="btn btn-outline-primary" @click="showCreateCampaignModal = true">
          <i class="fas fa-envelope me-1"></i>Create Campaign
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="row mb-4" v-if="summary">
      <div class="col-md-3">
        <div class="card border-0 bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Broadcasts Sent</h6>
                <h3 class="mb-0">{{ summary.broadcasts_sent }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-bullhorn fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.broadcasts_pending }} pending</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Email Campaigns</h6>
                <h3 class="mb-0">{{ summary.campaigns_sent }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-envelope fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.campaign_avg_open_rate }}% avg open rate</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Open Feedback</h6>
                <h3 class="mb-0">{{ summary.feedback_open }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-comments fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.avg_response_time_hours }}h avg response</small>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 bg-warning text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h6 class="card-title mb-0">Maintenance</h6>
                <h3 class="mb-0">{{ summary.maintenance_scheduled }}</h3>
              </div>
              <div class="align-self-center">
                <i class="fas fa-tools fa-2x opacity-75"></i>
              </div>
            </div>
            <small class="opacity-75">{{ summary.maintenance_active }} active now</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'broadcasts' }" @click="activeTab = 'broadcasts'">
          <i class="fas fa-bullhorn me-1"></i>Broadcasts
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'campaigns' }" @click="activeTab = 'campaigns'">
          <i class="fas fa-envelope me-1"></i>Email Campaigns
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'notifications' }" @click="activeTab = 'notifications'">
          <i class="fas fa-bell me-1"></i>Notifications
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'feedback' }" @click="activeTab = 'feedback'">
          <i class="fas fa-comments me-1"></i>Feedback
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" :class="{ active: activeTab === 'maintenance' }" @click="activeTab = 'maintenance'">
          <i class="fas fa-tools me-1"></i>Maintenance
        </a>
      </li>
    </ul>

    <!-- Broadcasts Tab -->
    <div v-if="activeTab === 'broadcasts'">
      <div class="card">
        <div class="card-header">
          <div class="row align-items-center">
            <div class="col">
              <h5 class="mb-0">Broadcast Messages</h5>
            </div>
            <div class="col-auto">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search broadcasts..." 
                  v-model="broadcastSearchQuery"
                >
                <button class="btn btn-outline-secondary" type="button">
                  <i class="fas fa-search"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Recipients</th>
                  <th>Status</th>
                  <th>Sent At</th>
                  <th>Open Rate</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="broadcast in filteredBroadcasts" :key="broadcast.id">
                  <td>
                    <div>
                      <strong>{{ broadcast.title }}</strong>
                      <div class="text-muted small">{{ truncateText(broadcast.message, 50) }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="badge bg-secondary">{{ formatMessageType(broadcast.message_type) }}</span>
                  </td>
                  <td>{{ broadcast.total_recipients }}</td>
                  <td>
                    <span class="badge" :class="getStatusClass(broadcast.status)">
                      {{ broadcast.status }}
                    </span>
                  </td>
                  <td>{{ formatDate(broadcast.sent_at) }}</td>
                  <td>{{ broadcast.delivery_stats ? broadcast.delivery_stats.open_rate.toFixed(1) : '0' }}%</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-primary" 
                        @click="viewBroadcastDetails(broadcast)"
                        title="View Details"
                      >
                        <i class="fas fa-eye"></i>
                      </button>
                      <button 
                        class="btn btn-outline-success" 
                        @click="sendBroadcast(broadcast)"
                        v-if="broadcast.status === 'draft'"
                        title="Send Now"
                      >
                        <i class="fas fa-paper-plane"></i>
                      </button>
                      <button 
                        class="btn btn-outline-info" 
                        @click="duplicateBroadcast(broadcast)"
                        title="Duplicate"
                      >
                        <i class="fas fa-copy"></i>
                      </button>
                      <button 
                        class="btn btn-outline-danger" 
                        @click="deleteBroadcast(broadcast)"
                        title="Delete"
                      >
                        <i class="fas fa-trash"></i>
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

    <!-- Email Campaigns Tab -->
    <div v-if="activeTab === 'campaigns'">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">Email Campaigns</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Campaign Name</th>
                  <th>Type</th>
                  <th>Subject</th>
                  <th>Recipients</th>
                  <th>Status</th>
                  <th>Open Rate</th>
                  <th>Click Rate</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="campaign in campaigns" :key="campaign.id">
                  <td>
                    <strong>{{ campaign.campaign_name }}</strong>
                  </td>
                  <td>
                    <span class="badge bg-info">{{ formatCampaignType(campaign.campaign_type) }}</span>
                  </td>
                  <td class="text-muted">{{ truncateText(campaign.subject_line, 40) }}</td>
                  <td>{{ campaign.total_sent }}</td>
                  <td>
                    <span class="badge" :class="getStatusClass(campaign.status)">
                      {{ campaign.status }}
                    </span>
                  </td>
                  <td>{{ campaign.open_rate || 0 }}%</td>
                  <td>{{ campaign.click_rate || 0 }}%</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button 
                        class="btn btn-outline-primary" 
                        @click="viewCampaignAnalytics(campaign)"
                        title="View Analytics"
                      >
                        <i class="fas fa-chart-bar"></i>
                      </button>
                      <button 
                        class="btn btn-outline-success" 
                        @click="sendCampaign(campaign)"
                        v-if="campaign.status === 'draft'"
                        title="Send Campaign"
                      >
                        <i class="fas fa-paper-plane"></i>
                      </button>
                      <button 
                        class="btn btn-outline-secondary" 
                        @click="editCampaign(campaign)"
                        title="Edit"
                      >
                        <i class="fas fa-edit"></i>
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

    <!-- Notifications Tab -->
    <div v-if="activeTab === 'notifications'">
      <div class="card">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">In-App Notifications</h5>
            <button class="btn btn-sm btn-primary" @click="showCreateNotificationModal = true">
              <i class="fas fa-plus me-1"></i>Create Notification
            </button>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="bg-light">
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>User</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="notification in notifications" :key="notification.id">
                  <td>
                    <div>
                      <strong>{{ notification.title }}</strong>
                      <div class="text-muted small">{{ truncateText(notification.message, 50) }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="badge bg-secondary">{{ formatNotificationType(notification.notification_type) }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="getPriorityClass(notification.priority)">
                      {{ notification.priority }}
                    </span>
                  </td>
                  <td>{{ notification.user_name || 'All Users' }}</td>
                  <td>
                    <span v-if="notification.is_read" class="badge bg-success">Read</span>
                    <span v-else-if="notification.is_dismissed" class="badge bg-warning">Dismissed</span>
                    <span v-else class="badge bg-primary">Unread</span>
                  </td>
                  <td>{{ formatDate(notification.created_at) }}</td>
                  <td>
                    <div class="btn-group btn-group-sm">
                      <button class="btn btn-outline-primary" @click="viewNotification(notification)">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="btn btn-outline-danger" @click="deleteNotification(notification)">
                        <i class="fas fa-trash"></i>
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

    <!-- Feedback Tab -->
    <div v-if="activeTab === 'feedback'">
      <FeedbackManagement />
    </div>

    <!-- Maintenance Tab -->
    <div v-if="activeTab === 'maintenance'">
      <MaintenanceManagement />
    </div>

    <!-- Create Broadcast Modal -->
    <div class="modal fade" tabindex="-1" v-if="showCreateBroadcastModal" style="display: block;" @click.self="showCreateBroadcastModal = false">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Broadcast Message</h5>
            <button type="button" class="btn-close" @click="showCreateBroadcastModal = false"></button>
          </div>
          <div class="modal-body">
            <BroadcastComposer @save="saveBroadcast" @cancel="showCreateBroadcastModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Campaign Modal -->
    <div class="modal fade" tabindex="-1" v-if="showCreateCampaignModal" style="display: block;" @click.self="showCreateCampaignModal = false">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Email Campaign</h5>
            <button type="button" class="btn-close" @click="showCreateCampaignModal = false"></button>
          </div>
          <div class="modal-body">
            <CampaignComposer @save="saveCampaign" @cancel="showCreateCampaignModal = false" />
          </div>
        </div>
      </div>
    </div>

    <!-- Create Notification Modal -->
    <div class="modal fade" tabindex="-1" v-if="showCreateNotificationModal" style="display: block;" @click.self="showCreateNotificationModal = false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create Notification</h5>
            <button type="button" class="btn-close" @click="showCreateNotificationModal = false"></button>
          </div>
          <div class="modal-body">
            <NotificationComposer @save="saveNotification" @cancel="showCreateNotificationModal = false" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'
import BroadcastComposer from '@/components/Communication/BroadcastComposer.vue'
import CampaignComposer from '@/components/Communication/CampaignComposer.vue'
import NotificationComposer from '@/components/Communication/NotificationComposer.vue'
import FeedbackManagement from '@/components/Communication/FeedbackManagement.vue'
import MaintenanceManagement from '@/components/Communication/MaintenanceManagement.vue'

export default {
  name: 'AdminCommunication',
  components: {
    BroadcastComposer,
    CampaignComposer,
    NotificationComposer,
    FeedbackManagement,
    MaintenanceManagement
  },
  setup() {
    const activeTab = ref('broadcasts')
    const summary = ref(null)
    const broadcasts = ref([])
    const campaigns = ref([])
    const notifications = ref([])
    const broadcastSearchQuery = ref('')
    const showCreateBroadcastModal = ref(false)
    const showCreateCampaignModal = ref(false)
    const showCreateNotificationModal = ref(false)
    const loading = ref(false)

    const filteredBroadcasts = computed(() => {
      if (!broadcastSearchQuery.value) return broadcasts.value
      const query = broadcastSearchQuery.value.toLowerCase()
      return broadcasts.value.filter(broadcast => 
        broadcast.title.toLowerCase().includes(query) ||
        broadcast.message.toLowerCase().includes(query)
      )
    })

    const loadSummary = async () => {
      try {
        const response = await api.get('/api/admin/communication-summary/')
        summary.value = response.data
      } catch (error) {
        console.error('Error loading communication summary:', error)
      }
    }

    const loadBroadcasts = async () => {
      try {
        const response = await api.get('/api/admin/broadcasts/')
        broadcasts.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading broadcasts:', error)
      }
    }

    const loadCampaigns = async () => {
      try {
        const response = await api.get('/api/admin/campaigns/')
        campaigns.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading campaigns:', error)
      }
    }

    const loadNotifications = async () => {
      try {
        const response = await api.get('/api/notifications/?all_users=true')
        notifications.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading notifications:', error)
      }
    }

    const sendBroadcast = async (broadcast) => {
      if (!confirm(`Are you sure you want to send "${broadcast.title}" to ${broadcast.total_recipients} recipients?`)) return
      
      try {
        loading.value = true
        const response = await api.post(`/api/admin/broadcasts/${broadcast.id}/send_now/`)
        
        // Update local data
        const index = broadcasts.value.findIndex(b => b.id === broadcast.id)
        if (index !== -1) {
          broadcasts.value[index] = response.data
        }
        
        alert('Broadcast sent successfully!')
      } catch (error) {
        console.error('Error sending broadcast:', error)
        alert('Failed to send broadcast')
      } finally {
        loading.value = false
      }
    }

    const sendCampaign = async (campaign) => {
      if (!confirm(`Are you sure you want to send "${campaign.campaign_name}"?`)) return
      
      try {
        loading.value = true
        const response = await api.post(`/api/admin/campaigns/${campaign.id}/send/`)
        
        // Update local data
        const index = campaigns.value.findIndex(c => c.id === campaign.id)
        if (index !== -1) {
          campaigns.value[index] = response.data
        }
        
        alert('Campaign sent successfully!')
      } catch (error) {
        console.error('Error sending campaign:', error)
        alert('Failed to send campaign')
      } finally {
        loading.value = false
      }
    }

    const saveBroadcast = async (broadcastData) => {
      try {
        const response = await api.post('/api/admin/broadcasts/', broadcastData)
        broadcasts.value.push(response.data)
        showCreateBroadcastModal.value = false
        alert('Broadcast created successfully')
      } catch (error) {
        console.error('Error creating broadcast:', error)
        alert('Failed to create broadcast')
      }
    }

    const saveCampaign = async (campaignData) => {
      try {
        const response = await api.post('/api/admin/campaigns/', campaignData)
        campaigns.value.push(response.data)
        showCreateCampaignModal.value = false
        alert('Campaign created successfully')
      } catch (error) {
        console.error('Error creating campaign:', error)
        alert('Failed to create campaign')
      }
    }

    const saveNotification = async (notificationData) => {
      try {
        const response = await api.post('/api/notifications/', notificationData)
        notifications.value.push(response.data)
        showCreateNotificationModal.value = false
        alert('Notification created successfully')
      } catch (error) {
        console.error('Error creating notification:', error)
        alert('Failed to create notification')
      }
    }

    // Utility functions
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString()
    }

    const formatMessageType = (type) => {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatCampaignType = (type) => {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatNotificationType = (type) => {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const getStatusClass = (status) => {
      const statusClasses = {
        draft: 'bg-secondary',
        scheduled: 'bg-warning',
        sending: 'bg-primary',
        sent: 'bg-success',
        cancelled: 'bg-danger',
        active: 'bg-success',
        paused: 'bg-warning',
        completed: 'bg-success',
        failed: 'bg-danger'
      }
      return statusClasses[status] || 'bg-secondary'
    }

    const getPriorityClass = (priority) => {
      const priorityClasses = {
        low: 'bg-secondary',
        medium: 'bg-info',
        high: 'bg-warning',
        urgent: 'bg-danger'
      }
      return priorityClasses[priority] || 'bg-secondary'
    }

    // Placeholder functions for actions that need implementation
    const viewBroadcastDetails = (broadcast) => {
      console.log('View broadcast details:', broadcast)
      // TODO: Implement details modal
    }

    const duplicateBroadcast = async (broadcast) => {
      try {
        // Create a copy
        const broadcastCopy = {
          ...broadcast,
          title: `${broadcast.title} (Copy)`,
          status: 'draft',
          sent_at: null,
          total_recipients: 0
        }
        delete broadcastCopy.id
        
        const response = await api.post('/api/admin/broadcasts/', broadcastCopy)
        broadcasts.value.push(response.data)
        alert('Broadcast duplicated successfully')
      } catch (error) {
        console.error('Error duplicating broadcast:', error)
        alert('Failed to duplicate broadcast')
      }
    }

    const deleteBroadcast = async (broadcast) => {
      if (!confirm(`Are you sure you want to delete "${broadcast.title}"?`)) return
      
      try {
        await api.delete(`/api/admin/broadcasts/${broadcast.id}/`)
        broadcasts.value = broadcasts.value.filter(b => b.id !== broadcast.id)
      } catch (error) {
        console.error('Error deleting broadcast:', error)
        alert('Failed to delete broadcast')
      }
    }

    const viewCampaignAnalytics = (campaign) => {
      console.log('View campaign analytics:', campaign)
      // TODO: Navigate to analytics page
    }

    const editCampaign = (campaign) => {
      console.log('Edit campaign:', campaign)
      // TODO: Implement edit modal
    }

    const viewNotification = (notification) => {
      console.log('View notification:', notification)
      // TODO: Show notification details
    }

    const deleteNotification = async (notification) => {
      if (!confirm('Are you sure you want to delete this notification?')) return
      
      try {
        await api.delete(`/api/notifications/${notification.id}/`)
        notifications.value = notifications.value.filter(n => n.id !== notification.id)
      } catch (error) {
        console.error('Error deleting notification:', error)
        alert('Failed to delete notification')
      }
    }

    onMounted(() => {
      loadSummary()
      loadBroadcasts()
      loadCampaigns()
      loadNotifications()
    })

    return {
      activeTab,
      summary,
      broadcasts,
      campaigns,
      notifications,
      broadcastSearchQuery,
      showCreateBroadcastModal,
      showCreateCampaignModal,
      showCreateNotificationModal,
      loading,
      filteredBroadcasts,
      sendBroadcast,
      sendCampaign,
      saveBroadcast,
      saveCampaign,
      saveNotification,
      truncateText,
      formatDate,
      formatMessageType,
      formatCampaignType,
      formatNotificationType,
      getStatusClass,
      getPriorityClass,
      viewBroadcastDetails,
      duplicateBroadcast,
      deleteBroadcast,
      viewCampaignAnalytics,
      editCampaign,
      viewNotification,
      deleteNotification
    }
  }
}
</script>

<style scoped>
.admin-communication {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.nav-link {
  cursor: pointer;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.badge {
  font-size: 0.75em;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.opacity-75 {
  opacity: 0.75 !important;
}

.text-muted.small {
  font-size: 0.8rem;
}
</style>