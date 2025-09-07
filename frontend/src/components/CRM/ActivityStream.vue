<template>
  <div class="activity-stream">

    <!-- Full Activity Table -->
    <div class="card border-0 shadow-sm mt-3">
      <div class="card-header bg-transparent border-bottom">
        <div class="d-flex align-items-center">
          <i class="bi bi-table me-2 text-primary"></i>
          <h6 class="mb-0">Complete Activity Log</h6>
          <span class="badge bg-secondary ms-2">{{ rawActivities.length }} Total</span>
        </div>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover table-striped mb-0">
            <thead class="table-light">
              <tr>
                <th scope="col">#</th>
                <th scope="col">Date/Time</th>
                <th scope="col">Activity Type</th>
                <th scope="col">Description</th>
                <th scope="col">Client</th>
                <th scope="col">User</th>
                <th scope="col">Metadata</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading.initial">
                <td colspan="7" class="text-center py-4">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="rawActivities.length === 0">
                <td colspan="7" class="text-center py-4 text-muted">
                  No activities found
                </td>
              </tr>
              <tr v-else v-for="activity in rawActivities" :key="activity.id">
                <th scope="row">{{ activity.id }}</th>
                <td>
                  <small>{{ formatFullDateTime(activity.created_at) }}</small>
                </td>
                <td>
                  <span class="badge" :class="getActivityTypeBadgeClass(getActivityTypeGroup(activity.activity_type))">
                    {{ activity.activity_type_display || activity.activity_type }}
                  </span>
                </td>
                <td>{{ activity.description }}</td>
                <td>
                  <span v-if="activity.client_name" class="text-primary">
                    {{ activity.client_name }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <small>{{ activity.user_name || 'System' }}</small>
                </td>
                <td>
                  <button 
                    v-if="activity.metadata && Object.keys(activity.metadata).length > 0"
                    class="btn btn-sm btn-outline-secondary"
                    @click="showMetadata(activity)"
                  >
                    <i class="bi bi-info-circle"></i> View
                  </button>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Metadata Modal -->
    <div v-if="selectedMetadata" class="modal fade show d-block" tabindex="-1" @click.self="selectedMetadata = null">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Activity Metadata</h5>
            <button type="button" class="btn-close" @click="selectedMetadata = null"></button>
          </div>
          <div class="modal-body">
            <pre class="bg-light p-3 rounded">{{ JSON.stringify(selectedMetadata, null, 2) }}</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="selectedMetadata = null">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCommunicationStore } from '@/stores/communicationStore'
import axios from 'axios'

// Props
const props = defineProps({
  maxItems: {
    type: Number,
    default: 10
  },
  autoRefresh: {
    type: Boolean,
    default: false  // Changed default to false
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30 seconds
  },
  clientFilter: {
    type: [String, Number],
    default: null
  },
  lazyLoad: {
    type: Boolean,
    default: true  // Only load when visible
  }
})

// Emits
const emit = defineEmits(['activity-click', 'action-executed'])

// Store
const communicationStore = useCommunicationStore()

// Component state
const activities = ref([])
const rawActivities = ref([]) // Store raw activities for table
const selectedFilter = ref('All')
const isLive = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const lastActivityTime = ref(null)
const selectedMetadata = ref(null) // For metadata modal
const debugError = ref(null) // For debugging

const loading = ref({
  initial: false,
  refresh: false,
  more: false
})

// Auto-refresh interval
let refreshInterval = null

// Computed
const filteredActivities = computed(() => {
  if (selectedFilter.value === 'All') {
    return activities.value.slice(0, props.maxItems)
  }
  
  return activities.value
    .filter(activity => activity.type === selectedFilter.value)
    .slice(0, props.maxItems)
})

const todayCount = computed(() => {
  const today = new Date().toDateString()
  return activities.value.filter(activity => 
    new Date(activity.timestamp).toDateString() === today
  ).length
})

const unreadCount = computed(() => {
  return activities.value.filter(activity => !activity.read).length
})

const highPriorityCount = computed(() => {
  return activities.value.filter(activity => activity.priority === 'high').length
})

// Visibility tracking for lazy loading - declare before use
const isVisible = ref(false)
const hasLoadedOnce = ref(false)

// Methods
const generateMockActivities = () => {
  const now = new Date()
  const mockActivities = []
  
  // Generate realistic CRM activities
  const activityTypes = [
    {
      type: 'Communications',
      subtype: 'email',
      titles: ['New email received', 'Email sent', 'Email replied to'],
      descriptions: [
        'Email from John Doe regarding portfolio review',
        'Welcome email sent to new client',
        'Response sent to retirement planning inquiry'
      ]
    },
    {
      type: 'AI Analysis',
      subtype: 'sentiment',
      titles: ['AI analysis completed', 'Sentiment analysis updated', 'Priority score calculated'],
      descriptions: [
        'Positive sentiment detected in client communication',
        'High urgency communication flagged for review',
        'AI suggested response generated'
      ]
    },
    {
      type: 'Email Sync',
      subtype: 'sync',
      titles: ['Email sync completed', 'New emails synchronized', 'Sync error resolved'],
      descriptions: [
        'Successfully synchronized 15 new emails',
        'Gmail account sync completed',
        'Outlook connection restored'
      ]
    },
    {
      type: 'System',
      subtype: 'system',
      titles: ['Client created', 'Scenario updated', 'Report generated'],
      descriptions: [
        'New client profile added to system',
        'Retirement scenario calculations updated',
        'Financial report generated successfully'
      ]
    }
  ]
  
  for (let i = 0; i < 20; i++) {
    const typeConfig = activityTypes[Math.floor(Math.random() * activityTypes.length)]
    const titleIndex = Math.floor(Math.random() * typeConfig.titles.length)
    
    const activity = {
      id: i + 1,
      type: typeConfig.type,
      subtype: typeConfig.subtype,
      title: typeConfig.titles[titleIndex],
      description: typeConfig.descriptions[titleIndex],
      timestamp: new Date(now.getTime() - (i * 15 * 60 * 1000)), // 15 minutes apart
      priority: Math.random() > 0.8 ? 'high' : 'normal',
      read: Math.random() > 0.3,
      hasAI: typeConfig.type === 'AI Analysis' || Math.random() > 0.7,
      isNew: i < 2, // First 2 items are "new"
      client: Math.random() > 0.5 ? { 
        name: ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson'][Math.floor(Math.random() * 4)]
      } : null,
      lead: Math.random() > 0.7 ? {
        name: ['Alex Brown', 'Emily Davis', 'Chris Taylor'][Math.floor(Math.random() * 3)]
      } : null,
      actions: generateActivityActions(typeConfig.type, typeConfig.subtype)
    }
    
    mockActivities.push(activity)
  }
  
  return mockActivities
}

const generateActivityActions = (type, subtype) => {
  const actions = []
  
  switch (type) {
    case 'Communications':
      actions.push(
        { id: 'view', label: 'View', icon: 'bi-eye' },
        { id: 'reply', label: 'Reply', icon: 'bi-reply' }
      )
      if (subtype === 'email') {
        actions.push({ id: 'analyze', label: 'Analyze', icon: 'bi-robot' })
      }
      break
      
    case 'AI Analysis':
      actions.push(
        { id: 'view_analysis', label: 'View Analysis', icon: 'bi-graph-up' },
        { id: 'use_suggestion', label: 'Use Suggestion', icon: 'bi-check2' }
      )
      break
      
    case 'Email Sync':
      actions.push(
        { id: 'view_sync', label: 'View Details', icon: 'bi-info-circle' }
      )
      break
      
    case 'System':
      actions.push(
        { id: 'view_item', label: 'View', icon: 'bi-eye' }
      )
      break
  }
  
  return actions
}

const loadActivities = async (append = false) => {
  loading.value.initial = true
  
  try {
    // Filter by client if provided
    const params = {}
    if (props.clientFilter) {
      params.client_id = props.clientFilter
    }
    
    // Add authentication headers
    const token = localStorage.getItem('access_token')
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
    const response = await axios.get(`${apiUrl}/activities/`, { 
      params,
      headers: {
        'Authorization': token ? `Bearer ${token}` : ''
      }
    })
    
    // Handle the response - it's an array
    const activityData = response.data || []
    
    // Store raw activities for the table
    if (append) {
      rawActivities.value.push(...activityData)
    } else {
      rawActivities.value = activityData
    }
    
    // Transform to display format for the stream
    const transformedActivities = activityData.map(activity => ({
      id: activity.id,
      type: getActivityTypeGroup(activity.activity_type),
      subtype: activity.activity_type,
      title: activity.activity_type_display || activity.description,
      description: activity.metadata?.file_name 
        ? `File: ${activity.metadata.file_name} (${formatFileSize(activity.metadata.file_size)})` 
        : activity.description,
      timestamp: activity.created_at,
      user: activity.user_name || 'System',
      client: activity.client_name ? { name: activity.client_name } : null,
      priority: 'normal',
      read: true,
      isNew: false,
      hasAI: false,
      metadata: activity.metadata,
      actions: generateActivityActions('System', activity.activity_type)
    }))
    
    if (append) {
      activities.value.push(...transformedActivities)
    } else {
      activities.value = transformedActivities
    }
    
  } catch (error) {
    console.error('Failed to load activities:', error)
    debugError.value = error.message || 'Unknown error'
    activities.value = []
    rawActivities.value = []
  } finally {
    loading.value.initial = false
    loading.value.more = false
  }
}

// Helper function to format file size
const formatFileSize = (bytes) => {
  if (!bytes) return ''
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// Helper function to map activity types to groups
const getActivityTypeGroup = (activityType) => {
  const typeMap = {
    'email_received': 'Communications',
    'email_sent': 'Communications',
    'sms_received': 'Communications',
    'sms_sent': 'Communications',
    'call_logged': 'Communications',
    'meeting_scheduled': 'Communications',
    'document_uploaded': 'System',
    'scenario_created': 'System',
    'report_generated': 'System',
    'task_created': 'System',
    'task_completed': 'System',
    'note_added': 'System',
    'lead_converted': 'System'
  }
  return typeMap[activityType] || 'System'
}

const refreshActivities = async () => {
  loading.value.refresh = true
  
  try {
    await loadActivities()
    
    // Mark new activities
    activities.value.forEach((activity, index) => {
      if (index < 2) activity.isNew = true
    })
    
    // Remove "new" flag after 5 seconds
    setTimeout(() => {
      activities.value.forEach(activity => activity.isNew = false)
    }, 5000)
    
  } finally {
    loading.value.refresh = false
  }
}

const loadMoreActivities = async () => {
  await loadActivities(true)
  
  // Check if we have more items to load
  hasMore.value = activities.value.length < 50 // Arbitrary limit
}

const setFilter = (filter) => {
  selectedFilter.value = filter
}

const executeAction = async (action, activity) => {
  try {
    console.log('Executing action:', action.id, 'for activity:', activity.id)
    
    // Handle different actions
    switch (action.id) {
      case 'view':
      case 'view_analysis':
      case 'view_sync':
      case 'view_item':
        emit('activity-click', activity)
        break
        
      case 'reply':
        // Open email compose modal
        break
        
      case 'analyze':
        // Trigger AI analysis
        break
        
      case 'use_suggestion':
        // Use AI suggestion
        break
        
      default:
        console.log('Unknown action:', action.id)
    }
    
    // Mark activity as read
    activity.read = true
    
    emit('action-executed', { action, activity })
    
  } catch (error) {
    console.error('Action execution error:', error)
  }
}

const getActivityIcon = (type, subtype) => {
  // Handle specific subtypes first
  switch (subtype) {
    case 'email_received':
    case 'email_sent':
      return 'bi-envelope'
    case 'sms_received':
    case 'sms_sent':
      return 'bi-chat-dots'
    case 'call_logged':
      return 'bi-telephone'
    case 'meeting_scheduled':
      return 'bi-calendar-event'
    case 'document_uploaded':
      return 'bi-file-earmark-arrow-up'
    case 'scenario_created':
      return 'bi-diagram-3'
    case 'report_generated':
      return 'bi-file-earmark-pdf'
    case 'task_created':
    case 'task_completed':
      return 'bi-check2-square'
    case 'note_added':
      return 'bi-sticky'
    case 'lead_converted':
      return 'bi-person-check'
  }
  
  // Fall back to type-based icons
  switch (type) {
    case 'Communications':
      return 'bi-chat'
    case 'AI Analysis':
      return 'bi-robot'
    case 'Email Sync':
      return 'bi-arrow-clockwise'
    case 'System':
      return 'bi-gear'
    default:
      return 'bi-activity'
  }
}

const getActivityAvatarClass = (type, subtype) => {
  switch (type) {
    case 'Communications':
      return 'bg-primary text-white'
    case 'AI Analysis':
      return 'bg-info text-white'
    case 'Email Sync':
      return 'bg-success text-white'
    case 'System':
      return 'bg-secondary text-white'
    default:
      return 'bg-light text-muted'
  }
}

const getActivityTypeBadgeClass = (type) => {
  switch (type) {
    case 'Communications':
      return 'bg-primary'
    case 'AI Analysis':
      return 'bg-info'
    case 'Email Sync':
      return 'bg-success'
    case 'System':
      return 'bg-secondary'
    default:
      return 'bg-light text-dark'
  }
}

const formatActivityTime = (timestamp) => {
  const now = new Date()
  const activityTime = new Date(timestamp)
  const diffMs = now - activityTime
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  
  return activityTime.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatFullDateTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const showMetadata = (activity) => {
  selectedMetadata.value = activity.metadata
}

const forceLoadActivities = async () => {
  console.log('FORCE LOADING ACTIVITIES')
  debugError.value = null
  rawActivities.value = []
  activities.value = []
  await loadActivities()
  console.log('FORCE LOAD COMPLETE. Raw count:', rawActivities.value.length)
}

const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshInterval) {
    refreshInterval = setInterval(() => {
      refreshActivities()
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
    isLive.value = false
  }
}

// Public method for parent component to trigger refresh
const refreshIfNeeded = () => {
  console.log('refreshIfNeeded called, hasLoadedOnce:', hasLoadedOnce.value, 'lazyLoad:', props.lazyLoad)
  // If we haven't loaded yet, load now
  if (!hasLoadedOnce.value) {
    loadActivities()
    hasLoadedOnce.value = true
  } else {
    // Otherwise refresh
    refreshActivities()
  }
}

// Intersection Observer for visibility detection
let observer = null

const checkVisibility = () => {
  // Only load if we haven't loaded yet and lazyLoad is enabled
  if (props.lazyLoad && !hasLoadedOnce.value && isVisible.value) {
    loadActivities()
    hasLoadedOnce.value = true
    
    if (props.autoRefresh) {
      startAutoRefresh()
    }
  } else if (!props.lazyLoad && !hasLoadedOnce.value) {
    // If lazyLoad is disabled, load immediately
    loadActivities()
    hasLoadedOnce.value = true
    
    if (props.autoRefresh) {
      startAutoRefresh()
    }
  }
}

// Lifecycle
onMounted(async () => {
  // JUST FUCKING LOAD THE DATA
  await loadActivities()
})

onUnmounted(() => {
  stopAutoRefresh()
  
  // Clean up observer
  if (observer) {
    observer.disconnect()
    observer = null
  }
})

// Expose methods to parent component - must be at the end after all functions are defined
defineExpose({
  refreshIfNeeded,
  refreshActivities
})
</script>

<style scoped>
.activity-stream {
  height: 100%;
}

.activity-item {
  transition: all 0.2s ease;
  position: relative;
}

.activity-item:hover {
  background-color: #f8f9fa;
}

.activity-item.activity-new {
  background-color: rgba(13, 110, 253, 0.05);
  border-left: 3px solid #0d6efd;
}

.activity-item.activity-new::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(to bottom, #0d6efd, transparent);
}

.activity-list {
  max-height: 500px;
  overflow-y: auto;
}

.activity-title {
  font-weight: 600;
  color: #212529;
}

.activity-description {
  line-height: 1.4;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.875rem;
}

.avatar-sm {
  width: 2rem;
  height: 2rem;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.25em 0.5em;
}

.btn-xs {
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1.2;
}

.live-dot {
  width: 6px;
  height: 6px;
  background-color: #198754;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.min-w-0 {
  min-width: 0;
}

.card-footer {
  padding: 0.75rem 1rem;
}

/* Scrollbar styling */
.activity-list::-webkit-scrollbar {
  width: 4px;
}

.activity-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.activity-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.activity-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

@media (max-width: 768px) {
  .activity-item .d-flex {
    align-items: flex-start;
  }
  
  .btn-xs {
    padding: 0.1rem 0.4rem;
    font-size: 0.7rem;
  }
  
  .activity-list {
    max-height: 400px;
  }
  
  .card-footer .row .col-4 {
    padding: 0.25rem;
  }
  
  .card-footer small {
    font-size: 0.7rem;
  }
}

/* Modal backdrop styles */
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.table-responsive {
  max-height: 600px;
  overflow-y: auto;
}

pre {
  max-height: 400px;
  overflow-y: auto;
  font-size: 0.875rem;
}
</style>