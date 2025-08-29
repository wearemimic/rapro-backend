<template>
  <div class="task-list">
    <!-- Header with bulk select -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div class="d-flex align-items-center">
        <div class="form-check me-3">
          <input
            class="form-check-input"
            type="checkbox"
            id="selectAll"
            :checked="isAllSelected"
            :indeterminate.prop="isSomeSelected"
            @change="handleSelectAll"
          >
          <label class="form-check-label" for="selectAll">
            Select All
          </label>
        </div>
        <span class="text-muted">
          {{ tasks.length }} {{ tasks.length === 1 ? 'task' : 'tasks' }}
        </span>
      </div>
      
      <div class="d-flex align-items-center gap-2">
        <label class="form-label mb-0 me-2">Sort by:</label>
        <select
          class="form-select form-select-sm"
          v-model="sortBy"
          @change="handleSort"
          style="width: auto;"
        >
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="-updated_at">Recently Updated</option>
          <option value="due_date">Due Date</option>
          <option value="-due_date">Due Date (Desc)</option>
          <option value="priority">Priority</option>
          <option value="status">Status</option>
          <option value="title">Title A-Z</option>
          <option value="-title">Title Z-A</option>
        </select>
      </div>
    </div>

    <!-- Task List -->
    <div class="task-items">
      <div
        v-for="task in sortedTasks"
        :key="task.id"
        class="task-item card mb-2"
        :class="getTaskItemClass(task)"
        @click="handleTaskClick(task)"
      >
        <div class="card-body p-3">
          <div class="d-flex align-items-start">
            <!-- Selection Checkbox -->
            <div class="form-check me-3">
              <input
                class="form-check-input"
                type="checkbox"
                :id="`task-${task.id}`"
                :checked="isTaskSelected(task.id)"
                @click.stop
                @change="$emit('task-select', task.id)"
              >
            </div>

            <!-- Task Content -->
            <div class="flex-grow-1 min-width-0">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="task-header">
                  <h6 class="task-title mb-1" :class="{ 'text-decoration-line-through': task.status === 'completed' }">
                    {{ task.title }}
                    <span v-if="task.is_overdue" class="badge bg-danger ms-2">
                      <i class="fas fa-exclamation-triangle me-1"></i>Overdue
                    </span>
                  </h6>
                  
                  <div class="task-meta">
                    <span class="badge me-1" :class="getStatusBadgeClass(task.status)">
                      {{ getStatusLabel(task.status) }}
                    </span>
                    <span class="badge me-1" :class="getPriorityBadgeClass(task.priority)">
                      {{ getPriorityLabel(task.priority) }}
                    </span>
                    <span v-if="task.task_type" class="badge bg-light text-dark me-1">
                      {{ getTaskTypeLabel(task.task_type) }}
                    </span>
                  </div>
                </div>

                <!-- Task Actions -->
                <div class="task-actions">
                  <div class="btn-group btn-group-sm">
                    <button
                      class="btn btn-outline-primary"
                      @click.stop="$emit('task-click', task)"
                      title="Edit Task"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    
                    <div class="btn-group btn-group-sm">
                      <button
                        class="btn btn-outline-secondary dropdown-toggle"
                        type="button"
                        data-bs-toggle="dropdown"
                        @click.stop
                      >
                        <i class="fas fa-ellipsis-h"></i>
                      </button>
                      <ul class="dropdown-menu dropdown-menu-end">
                        <li>
                          <button
                            class="dropdown-item"
                            @click.stop="quickStatusUpdate(task, 'in_progress')"
                            v-if="task.status === 'pending'"
                          >
                            <i class="fas fa-play me-2"></i>Start Task
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click.stop="quickStatusUpdate(task, 'completed')"
                            v-if="task.status !== 'completed'"
                          >
                            <i class="fas fa-check me-2"></i>Mark Complete
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click.stop="quickStatusUpdate(task, 'pending')"
                            v-if="task.status === 'in_progress'"
                          >
                            <i class="fas fa-pause me-2"></i>Mark Pending
                          </button>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                          <button
                            class="dropdown-item"
                            @click.stop="duplicateTask(task)"
                          >
                            <i class="fas fa-copy me-2"></i>Duplicate
                          </button>
                        </li>
                        <li>
                          <button
                            class="dropdown-item text-danger"
                            @click.stop="$emit('task-delete', task.id)"
                          >
                            <i class="fas fa-trash me-2"></i>Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Task Description -->
              <p v-if="task.description" class="task-description text-muted mb-2">
                {{ truncateText(task.description, 150) }}
              </p>

              <!-- Task Details -->
              <div class="task-details d-flex flex-wrap align-items-center gap-3 text-sm text-muted">
                <div v-if="task.due_date" class="d-flex align-items-center">
                  <i class="fas fa-calendar me-1"></i>
                  Due: {{ formatDate(task.due_date) }}
                </div>
                
                <div v-if="task.assigned_to_name" class="d-flex align-items-center">
                  <i class="fas fa-user me-1"></i>
                  {{ task.assigned_to_name }}
                </div>
                
                <div v-if="task.client_name" class="d-flex align-items-center">
                  <i class="fas fa-user-tie me-1"></i>
                  {{ task.client_name }}
                </div>
                
                <div v-if="task.lead_name" class="d-flex align-items-center">
                  <i class="fas fa-user-plus me-1"></i>
                  {{ task.lead_name }}
                </div>
                
                <div class="d-flex align-items-center">
                  <i class="fas fa-clock me-1"></i>
                  Created {{ formatRelativeDate(task.created_at) }}
                </div>
                
                <div v-if="task.comments_count > 0" class="d-flex align-items-center">
                  <i class="fas fa-comments me-1"></i>
                  {{ task.comments_count }} {{ task.comments_count === 1 ? 'comment' : 'comments' }}
                </div>
              </div>

              <!-- Tags -->
              <div v-if="task.tags && task.tags.length > 0" class="task-tags mt-2">
                <span
                  v-for="tag in task.tags"
                  :key="tag"
                  class="badge bg-secondary me-1"
                  style="font-size: 0.7em;"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="tasks.length === 0" class="empty-state text-center py-5">
        <i class="fas fa-tasks fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">No tasks found</h5>
        <p class="text-muted">Create your first task to get started with task management.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-3">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTaskStore } from '@/stores/taskStore.js'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['task-click', 'task-update', 'task-delete', 'task-select'])

const taskStore = useTaskStore()
const sortBy = ref('-created_at')

const sortedTasks = computed(() => {
  if (!props.tasks.length) return []

  const sorted = [...props.tasks].sort((a, b) => {
    const field = sortBy.value.replace('-', '')
    const isDesc = sortBy.value.startsWith('-')
    
    let aVal = a[field]
    let bVal = b[field]
    
    // Handle special sorting cases
    if (field === 'priority') {
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      aVal = priorityOrder[aVal] || 0
      bVal = priorityOrder[bVal] || 0
    } else if (field === 'due_date') {
      aVal = aVal ? new Date(aVal) : new Date('2099-12-31')
      bVal = bVal ? new Date(bVal) : new Date('2099-12-31')
    } else if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal?.toLowerCase() || ''
    }
    
    if (aVal < bVal) return isDesc ? 1 : -1
    if (aVal > bVal) return isDesc ? -1 : 1
    return 0
  })

  return sorted
})

const isAllSelected = computed(() => {
  return props.tasks.length > 0 && props.tasks.every(task => taskStore.selectedTasks.includes(task.id))
})

const isSomeSelected = computed(() => {
  return props.tasks.some(task => taskStore.selectedTasks.includes(task.id)) && !isAllSelected.value
})

const handleSelectAll = () => {
  if (isAllSelected.value) {
    props.tasks.forEach(task => taskStore.deselectTask(task.id))
  } else {
    props.tasks.forEach(task => taskStore.selectTask(task.id))
  }
}

const handleSort = () => {
  taskStore.updateFilter('ordering', sortBy.value)
}

const handleTaskClick = (task) => {
  emit('task-click', task)
}

const isTaskSelected = (taskId) => {
  return taskStore.selectedTasks.includes(taskId)
}

const quickStatusUpdate = (task, status) => {
  emit('task-update', task.id, { status })
}

const duplicateTask = (task) => {
  const duplicateData = {
    title: `Copy of ${task.title}`,
    description: task.description,
    priority: task.priority,
    task_type: task.task_type,
    client: task.client,
    lead: task.lead,
    tags: [...(task.tags || [])]
  }
  
  taskStore.createTask(duplicateData)
}

const getTaskItemClass = (task) => {
  const classes = ['task-item-hover']
  
  if (task.is_overdue) {
    classes.push('border-danger')
  } else if (task.priority === 'high') {
    classes.push('border-warning')
  } else if (task.status === 'completed') {
    classes.push('border-success')
  }
  
  return classes
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'completed': return 'bg-success'
    case 'in_progress': return 'bg-primary'
    case 'pending': return 'bg-secondary'
    case 'cancelled': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
    case 'in_progress': return 'In Progress'
    case 'completed': return 'Completed'
    case 'pending': return 'Pending'
    case 'cancelled': return 'Cancelled'
    default: return status
  }
}

const getPriorityBadgeClass = (priority) => {
  switch (priority) {
    case 'high': return 'bg-danger'
    case 'medium': return 'bg-warning text-dark'
    case 'low': return 'bg-info'
    default: return 'bg-secondary'
  }
}

const getPriorityLabel = (priority) => {
  return priority ? priority.charAt(0).toUpperCase() + priority.slice(1) : 'Medium'
}

const getTaskTypeLabel = (taskType) => {
  return taskType ? taskType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : ''
}

const truncateText = (text, length) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatRelativeDate = (date) => {
  const now = new Date()
  const taskDate = new Date(date)
  const diffInHours = Math.abs(now - taskDate) / (1000 * 60 * 60)
  
  if (diffInHours < 24) {
    return diffInHours < 1 ? 'just now' : `${Math.floor(diffInHours)}h ago`
  } else if (diffInHours < 168) { // 7 days
    return `${Math.floor(diffInHours / 24)}d ago`
  } else {
    return formatDate(date)
  }
}

// Sync sort with store filter
watch(() => taskStore.filters.ordering, (newValue) => {
  sortBy.value = newValue
})
</script>

<style scoped>
.task-item {
  transition: all 0.2s ease;
  cursor: pointer;
  border-left: 4px solid transparent;
}

.task-item-hover:hover {
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.task-title {
  font-weight: 600;
  color: #495057;
}

.task-description {
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.task-meta .badge {
  font-size: 0.7em;
  font-weight: normal;
}

.task-details {
  font-size: 0.85em;
}

.task-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.task-item:hover .task-actions {
  opacity: 1;
}

.text-sm {
  font-size: 0.875rem;
}

.min-width-0 {
  min-width: 0;
}

.border-danger {
  border-left-color: #dc3545 !important;
}

.border-warning {
  border-left-color: #ffc107 !important;
}

.border-success {
  border-left-color: #28a745 !important;
}

.empty-state {
  padding: 3rem 1rem;
}

.form-check-input:indeterminate {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.dropdown-menu {
  font-size: 0.875rem;
}

.task-tags {
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .task-actions {
    opacity: 1;
  }
  
  .task-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem !important;
  }
}
</style>