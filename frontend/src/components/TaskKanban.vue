<template>
  <div class="task-kanban">
    <div class="kanban-board">
      <!-- Kanban Columns -->
      <div
        v-for="(column, status) in kanbanColumns"
        :key="status"
        class="kanban-column"
      >
        <div class="kanban-header">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0 d-flex align-items-center">
              <i :class="column.icon" class="me-2"></i>
              {{ column.title }}
              <span class="badge bg-secondary ms-2">
                {{ tasks[status]?.length || 0 }}
              </span>
            </h6>
            
            <button
              class="btn btn-sm btn-outline-primary"
              @click="createTaskInColumn(status)"
              :title="`Create ${column.title} Task`"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>

        <div
          class="kanban-column-content"
          :class="`status-${status}`"
          @drop="handleDrop($event, status)"
          @dragover.prevent
          @dragenter.prevent
        >
          <!-- Task Cards -->
          <div
            v-for="task in tasks[status] || []"
            :key="task.id"
            class="kanban-card"
            :class="getTaskCardClass(task)"
            draggable="true"
            @dragstart="handleDragStart($event, task)"
            @click="$emit('task-click', task)"
          >
            <!-- Task Header -->
            <div class="card-header d-flex justify-content-between align-items-start">
              <div class="task-meta">
                <span
                  class="priority-indicator"
                  :class="`priority-${task.priority}`"
                ></span>
                <span v-if="task.task_type" class="badge bg-light text-dark badge-sm">
                  {{ getTaskTypeLabel(task.task_type) }}
                </span>
              </div>
              
              <div class="dropdown">
                <button
                  class="btn btn-sm btn-outline-secondary dropdown-toggle"
                  type="button"
                  data-bs-toggle="dropdown"
                  @click.stop
                >
                  <i class="fas fa-ellipsis-v"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <button
                      class="dropdown-item"
                      @click.stop="$emit('task-click', task)"
                    >
                      <i class="fas fa-edit me-2"></i>Edit Task
                    </button>
                  </li>
                  <li>
                    <button
                      class="dropdown-item"
                      @click.stop="duplicateTask(task)"
                    >
                      <i class="fas fa-copy me-2"></i>Duplicate
                    </button>
                  </li>
                  <li><hr class="dropdown-divider"></li>
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

            <!-- Task Content -->
            <div class="card-body">
              <h6 class="task-title mb-2" :class="{ 'text-decoration-line-through': task.status === 'completed' }">
                {{ task.title }}
                <span v-if="task.is_overdue" class="badge bg-danger ms-1 badge-sm">
                  <i class="fas fa-exclamation-triangle"></i>
                </span>
              </h6>

              <p v-if="task.description" class="task-description text-muted mb-2">
                {{ truncateText(task.description, 80) }}
              </p>

              <!-- Task Details -->
              <div class="task-details">
                <div v-if="task.due_date" class="detail-item mb-1">
                  <i class="fas fa-calendar-alt me-2 text-muted"></i>
                  <small :class="{ 'text-danger': task.is_overdue }">
                    Due: {{ formatDate(task.due_date) }}
                  </small>
                </div>

                <div v-if="task.assigned_to_name" class="detail-item mb-1">
                  <i class="fas fa-user me-2 text-muted"></i>
                  <small class="text-muted">{{ task.assigned_to_name }}</small>
                </div>

                <div v-if="task.client_name" class="detail-item mb-1">
                  <i class="fas fa-user-tie me-2 text-muted"></i>
                  <small class="text-muted">{{ task.client_name }}</small>
                </div>

                <div v-if="task.lead_name" class="detail-item mb-1">
                  <i class="fas fa-user-plus me-2 text-muted"></i>
                  <small class="text-muted">{{ task.lead_name }}</small>
                </div>
              </div>

              <!-- Task Tags -->
              <div v-if="task.tags && task.tags.length > 0" class="task-tags mt-2">
                <span
                  v-for="tag in task.tags.slice(0, 3)"
                  :key="tag"
                  class="badge bg-secondary me-1 badge-sm"
                >
                  {{ tag }}
                </span>
                <span v-if="task.tags.length > 3" class="text-muted small">
                  +{{ task.tags.length - 3 }} more
                </span>
              </div>
            </div>

            <!-- Task Footer -->
            <div class="card-footer d-flex justify-content-between align-items-center">
              <div class="task-stats">
                <span v-if="task.comments_count > 0" class="me-2">
                  <i class="fas fa-comments me-1"></i>
                  <small class="text-muted">{{ task.comments_count }}</small>
                </span>
                
                <span class="badge badge-sm" :class="getPriorityBadgeClass(task.priority)">
                  {{ getPriorityLabel(task.priority) }}
                </span>
              </div>

              <small class="text-muted">
                {{ formatRelativeDate(task.updated_at || task.created_at) }}
              </small>
            </div>
          </div>

          <!-- Empty Column State -->
          <div v-if="!tasks[status] || tasks[status].length === 0" class="empty-column">
            <div class="text-center py-4">
              <i :class="column.icon" class="fa-2x text-muted mb-2"></i>
              <p class="text-muted mb-2">No {{ column.title.toLowerCase() }} tasks</p>
              <button
                class="btn btn-sm btn-outline-primary"
                @click="createTaskInColumn(status)"
              >
                <i class="fas fa-plus me-1"></i>Add Task
              </button>
            </div>
          </div>

          <!-- Drop Zone Indicator -->
          <div class="drop-zone" :class="{ 'active': dragOverColumn === status }">
            <i class="fas fa-plus-circle"></i>
            <span>Drop task here</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  tasks: {
    type: Object,
    default: () => ({
      pending: [],
      in_progress: [],
      completed: [],
      cancelled: []
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['task-click', 'task-update', 'task-delete', 'create-task'])

const draggedTask = ref(null)
const dragOverColumn = ref(null)

const kanbanColumns = reactive({
  pending: {
    title: 'Pending',
    icon: 'fas fa-clock',
    color: '#6c757d'
  },
  in_progress: {
    title: 'In Progress',
    icon: 'fas fa-play-circle',
    color: '#007bff'
  },
  completed: {
    title: 'Completed',
    icon: 'fas fa-check-circle',
    color: '#28a745'
  },
  cancelled: {
    title: 'Cancelled',
    icon: 'fas fa-times-circle',
    color: '#dc3545'
  }
})

const handleDragStart = (event, task) => {
  draggedTask.value = task
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/html', event.target.outerHTML)
  event.target.style.opacity = '0.5'
}

const handleDragEnd = (event) => {
  event.target.style.opacity = '1'
  draggedTask.value = null
  dragOverColumn.value = null
}

const handleDrop = (event, newStatus) => {
  event.preventDefault()
  dragOverColumn.value = null

  if (draggedTask.value && draggedTask.value.status !== newStatus) {
    emit('task-update', draggedTask.value.id, { status: newStatus })
  }
}

const handleDragOver = (event, status) => {
  event.preventDefault()
  dragOverColumn.value = status
}

const handleDragLeave = () => {
  dragOverColumn.value = null
}

const createTaskInColumn = (status) => {
  emit('create-task', { status })
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
  
  emit('create-task', duplicateData)
}

const getTaskCardClass = (task) => {
  const classes = []
  
  if (task.is_overdue) {
    classes.push('overdue')
  }
  
  if (task.priority === 'high') {
    classes.push('high-priority')
  }
  
  return classes
}

const getTaskTypeLabel = (taskType) => {
  if (!taskType) return ''
  return taskType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
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
</script>

<style scoped>
.task-kanban {
  height: 100%;
  position: relative;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  height: 100%;
  padding: 1rem;
}

.kanban-column {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.kanban-header {
  padding: 1rem;
  border-bottom: 2px solid #dee2e6;
  background-color: white;
  border-radius: 0.5rem 0.5rem 0 0;
}

.kanban-column-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  position: relative;
}

.kanban-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid transparent;
}

.kanban-card:hover {
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.kanban-card.overdue {
  border-left-color: #dc3545;
  animation: pulse 2s infinite;
}

.kanban-card.high-priority {
  border-left-color: #ffc107;
}

.card-header {
  padding: 0.75rem;
  background-color: transparent;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.card-body {
  padding: 0.75rem;
}

.card-footer {
  padding: 0.5rem 0.75rem;
  background-color: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0 0 0.5rem 0.5rem;
}

.priority-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.priority-indicator.priority-high {
  background-color: #dc3545;
}

.priority-indicator.priority-medium {
  background-color: #ffc107;
}

.priority-indicator.priority-low {
  background-color: #17a2b8;
}

.task-title {
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.task-description {
  font-size: 0.875rem;
  line-height: 1.4;
}

.task-details {
  font-size: 0.8rem;
}

.detail-item {
  display: flex;
  align-items: center;
}

.task-tags .badge {
  font-size: 0.7em;
}

.task-stats {
  display: flex;
  align-items: center;
}

.badge-sm {
  font-size: 0.7em;
  padding: 0.25em 0.5em;
}

.empty-column {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  border: 2px dashed #dee2e6;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.drop-zone {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 123, 255, 0.1);
  border: 2px dashed #007bff;
  border-radius: 0.5rem;
  display: none;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #007bff;
  font-weight: 600;
}

.drop-zone.active {
  display: flex;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.status-pending .kanban-card {
  border-left-color: #6c757d;
}

.status-in_progress .kanban-card {
  border-left-color: #007bff;
}

.status-completed .kanban-card {
  border-left-color: #28a745;
}

.status-cancelled .kanban-card {
  border-left-color: #dc3545;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

@media (max-width: 1200px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kanban-board {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .kanban-column {
    min-height: 400px;
  }
  
  .kanban-card {
    margin-bottom: 0.75rem;
  }
  
  .card-header,
  .card-body,
  .card-footer {
    padding: 0.5rem;
  }
}
</style>