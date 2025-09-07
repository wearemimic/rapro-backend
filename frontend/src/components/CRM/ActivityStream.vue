<template>
  <div class="activity-stream">
    <div class="card border-0 shadow-sm h-100">
      <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <i class="bi bi-activity me-2 text-primary"></i>
          <h6 class="mb-0">Recent Activity</h6>
        </div>
        <div class="d-flex align-items-center gap-2">
          <!-- Live indicator -->
          <div v-if="isLive" class="d-flex align-items-center text-success">
            <div class="live-dot me-1"></div>
            <small>Live</small>
          </div>
          
          <!-- Refresh button -->
          <button 
            class="btn btn-sm btn-outline-secondary"
            @click="refreshActivities"
            :disabled="loading.refresh"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spin': loading.refresh }"></i>
          </button>

          <!-- Filter dropdown -->
          <div class="dropdown">
            <button 
              class="btn btn-sm btn-outline-secondary dropdown-toggle" 
              data-bs-toggle="dropdown"
            >
              {{ selectedFilter }}
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><button class="dropdown-item" @click="setFilter('All')">All Activities</button></li>
              <li><button class="dropdown-item" @click="setFilter('Communications')">Communications</button></li>
              <li><button class="dropdown-item" @click="setFilter('AI Analysis')">AI Analysis</button></li>
              <li><button class="dropdown-item" @click="setFilter('Email Sync')">Email Sync</button></li>
              <li><button class="dropdown-item" @click="setFilter('System')">System Events</button></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="card-body p-0">
        <!-- Loading State -->
        <div v-if="loading.initial" class="text-center py-4">
          <div class="spinner-border spinner-border-sm text-primary mb-2" role="status">
            <span class="visually-hidden">Loading activities...</span>
          </div>
          <p class="text-muted mb-0 small">Loading recent activities...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredActivities.length === 0" class="text-center py-4">
          <i class="bi bi-clock-history text-muted display-4 mb-2"></i>
          <p class="text-muted mb-0">No recent activity</p>
          <small class="text-muted">Activities will appear here as they happen</small>
        </div>

        <!-- Activity List -->
        <div v-else class="activity-list">
          <div 
            v-for="activity in filteredActivities" 
            :key="activity.id"
            class="activity-item border-bottom"
            :class="{ 'activity-new': activity.isNew }"
          >
            <div class="d-flex align-items-start p-3">
              <!-- Activity Icon -->
              <div class="flex-shrink-0 me-3">
                <div 
                  class="avatar avatar-sm avatar-circle"
                  :class="getActivityAvatarClass(activity.type, activity.subtype)"
                >
                  <i :class="getActivityIcon(activity.type, activity.subtype)"></i>
                </div>
              </div>

              <!-- Activity Content -->
              <div class="flex-grow-1 min-w-0">
                <div class="d-flex align-items-center justify-content-between mb-1">
                  <h6 class="mb-0 text-truncate activity-title">
                    {{ activity.title }}
                  </h6>
                  <div class="d-flex align-items-center gap-1">
                    <!-- Priority indicator -->
                    <span 
                      v-if="activity.priority === 'high'"
                      class="badge bg-danger badge-sm"
                      title="High Priority"
                    >
                      <i class="bi bi-exclamation-triangle-fill"></i>
                    </span>
                    
                    <!-- AI indicator -->
                    <span 
                      v-if="activity.hasAI"
                      class="badge bg-info badge-sm"
                      title="AI Processed"
                    >
                      <i class="bi bi-robot"></i>
                    </span>
                  </div>
                </div>

                <!-- Activity Description -->
                <p class="mb-1 text-muted small activity-description">
                  {{ activity.description }}
                </p>

                <!-- Activity Metadata -->
                <div class="d-flex align-items-center justify-content-between">
                  <div class="d-flex align-items-center gap-2">
                    <!-- Client/Lead info -->
                    <span 
                      v-if="activity.client || activity.lead"
                      class="badge bg-light text-dark badge-sm"
                    >
                      <i :class="activity.client ? 'bi-person-fill' : 'bi-person-plus'" class="me-1"></i>
                      {{ activity.client?.name || activity.lead?.name }}
                    </span>

                    <!-- Activity type badge -->
                    <span 
                      class="badge badge-sm"
                      :class="getActivityTypeBadgeClass(activity.type)"
                    >
                      {{ activity.type }}
                    </span>
                  </div>

                  <!-- Timestamp -->
                  <small class="text-muted">{{ formatActivityTime(activity.timestamp) }}</small>
                </div>

                <!-- Quick Actions -->
                <div v-if="activity.actions && activity.actions.length > 0" class="mt-2">
                  <div class="d-flex gap-1">
                    <button 
                      v-for="action in activity.actions.slice(0, 2)" 
                      :key="action.id"
                      class="btn btn-xs btn-outline-primary"
                      @click="executeAction(action, activity)"
                    >
                      <i :class="action.icon" class="me-1"></i>
                      {{ action.label }}
                    </button>
                    
                    <div v-if="activity.actions.length > 2" class="dropdown">
                      <button 
                        class="btn btn-xs btn-outline-secondary dropdown-toggle" 
                        data-bs-toggle="dropdown"
                      >
                        More
                      </button>
                      <ul class="dropdown-menu">
                        <li v-for="action in activity.actions.slice(2)" :key="action.id">
                          <button 
                            class="dropdown-item"
                            @click="executeAction(action, activity)"
                          >
                            <i :class="action.icon" class="me-2"></i>
                            {{ action.label }}
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Load More -->
          <div v-if="hasMore" class="text-center p-3 border-top">
            <button 
              class="btn btn-sm btn-outline-primary"
              @click="loadMoreActivities"
              :disabled="loading.more"
            >
              <i class="bi bi-arrow-down me-1" :class="{ 'spin': loading.more }"></i>
              {{ loading.more ? 'Loading...' : 'Load More' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Footer with summary stats -->
      <div class="card-footer bg-light border-top">
        <div class="row text-center">
          <div class="col-4">
            <div class="d-flex flex-column">
              <small class="text-muted">Today</small>
              <strong class="text-primary">{{ todayCount }}</strong>
            </div>
          </div>
          <div class="col-4">
            <div class="d-flex flex-column">
              <small class="text-muted">Unread</small>
              <strong class="text-warning">{{ unreadCount }}</strong>
            </div>
          </div>
          <div class="col-4">
            <div class="d-flex flex-column">
              <small class="text-muted">High Priority</small>
              <strong class="text-danger">{{ highPriorityCount }}</strong>
            </div>
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
const selectedFilter = ref('All')
const isLive = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const lastActivityTime = ref(null)

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
  if (append) {
    loading.value.more = true
  } else {
    loading.value.initial = true
  }
  
  try {
    // Just fucking get the activities for this client
    const params = {
      client_id: props.clientFilter
    }
    
    const response = await axios.get('/api/activities/', { params })
    console.log('Activities response:', response.data)
    
    // If it's an array, use it directly. If it has results, use that
    const activityData = Array.isArray(response.data) ? response.data : (response.data.results || [])
    
    // Transform to display format
    const transformedActivities = activityData.map(activity => ({
      id: activity.id,
      type: 'System',
      subtype: activity.activity_type,
      title: activity.description,
      description: activity.metadata?.file_name ? `File: ${activity.metadata.file_name}` : activity.description,
      timestamp: activity.created_at,
      user: activity.user_name || 'System',
      client: activity.client_name,
      priority: 'normal',
      read: false,
      isNew: false,
      hasAI: false,
      metadata: activity.metadata
    }))
    
    if (append) {
      activities.value.push(...transformedActivities)
    } else {
      activities.value = transformedActivities
    }
    
  } catch (error) {
    console.error('Failed to load activities:', error)
    activities.value = []
  } finally {
    loading.value.initial = false
    loading.value.more = false
  }
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
  // Only refresh if we've already loaded once and lazy loading is enabled
  if (hasLoadedOnce.value && props.lazyLoad) {
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
  // Set up intersection observer for lazy loading
  if (props.lazyLoad) {
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        isVisible.value = entry.isIntersecting
        if (entry.isIntersecting) {
          checkVisibility()
        }
      })
    }, {
      threshold: 0.1 // Trigger when 10% visible
    })
    
    // Start observing the component's root element
    const rootElement = document.querySelector('.activity-stream')
    if (rootElement) {
      observer.observe(rootElement)
    }
  } else {
    // Load immediately if lazy loading is disabled
    await loadActivities()
    
    if (props.autoRefresh) {
      startAutoRefresh()
    }
  }
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
</style>