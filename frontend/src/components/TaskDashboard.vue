<template>
  <div class="task-dashboard">
    <div class="task-dashboard-page-header">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-header-title">Task Management</h1>
          <p class="text-muted mb-0">Manage tasks, templates, and deadlines</p>
        </div>
        <div class="d-flex gap-2">
          <button
            class="btn btn-outline-secondary"
            @click="showTemplateModal = true"
          >
            <i class="bi-file-earmark-text me-1"></i>Templates
          </button>
          <button
            class="btn btn-primary"
            @click="openCreateTask"
          >
            <i class="bi-plus me-1"></i>New Task
          </button>
        </div>
      </div>
    </div>

    <!-- Task Statistics -->
    <div class="row mb-3">
      <div class="col-sm-6 col-lg-3 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-subtitle mb-2 text-center">Total Tasks</h5>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ taskStore.stats.total_tasks }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-subtitle mb-2 text-center">Pending</h5>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ taskStore.stats.pending_tasks }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-subtitle mb-2 text-center">In Progress</h5>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ taskStore.stats.in_progress_tasks }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-subtitle mb-2 text-center">Overdue</h5>
            <div class="row align-items-center gx-2">
              <div class="col text-center">
                <span class="js-counter display-4 text-dark">{{ taskStore.stats.overdue_tasks }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Controls -->
    <div class="card mb-3">
      <div class="card-body">
        <div class="row align-items-end">
          <div class="col-md-3">
            <label class="form-label">Search</label>
            <input
              type="text"
              class="form-control"
              placeholder="Search tasks..."
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
          <div class="col-md-2">
            <label class="form-label">Status</label>
            <select class="form-select" v-model="taskStore.filters.status" @change="taskStore.updateFilter('status', taskStore.filters.status)">
              <option value="">All Tasks</option>
              <option value="active">All Active</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Priority</label>
            <select class="form-select" v-model="taskStore.filters.priority" @change="taskStore.updateFilter('priority', taskStore.filters.priority)">
              <option value="">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">Sort By</label>
            <select class="form-select" v-model="sortBy" @change="handleSort">
              <option value="-created_at">Newest First</option>
              <option value="created_at">Oldest First</option>
              <option value="due_date">Due Date</option>
              <option value="-due_date">Due Date (Desc)</option>
              <option value="priority">Priority</option>
              <option value="title">Title A-Z</option>
              <option value="-title">Title Z-A</option>
            </select>
          </div>
          <div class="col-md-2">
            <div class="form-check mt-4">
              <input
                class="form-check-input"
                type="checkbox"
                id="overdueOnly"
                v-model="taskStore.filters.overdue"
                @change="taskStore.updateFilter('overdue', taskStore.filters.overdue)"
              >
              <label class="form-check-label" for="overdueOnly">
                Overdue Only
              </label>
            </div>
          </div>
          <div class="col-md-1">
            <button 
              class="btn btn-outline-secondary w-100 mt-4"
              @click="taskStore.clearFilters()"
              title="Clear Filters"
            >
              Clear
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Task count and results info -->
    <div class="d-flex justify-content-between align-items-center mb-2">
      <small class="text-muted">
        Showing {{ taskStore.filteredTasks.length }} of {{ taskStore.tasks.length }} tasks
      </small>
    </div>

    <!-- Task Table -->
    <div class="card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" v-if="!taskStore.loading.tasks">
          <thead class="table-light">
            <tr>
              <th scope="col" style="width: 40%">Task</th>
              <th scope="col" style="width: 10%">Status</th>
              <th scope="col" style="width: 10%">Priority</th>
              <th scope="col" style="width: 12%">Assigned To</th>
              <th scope="col" style="width: 10%">Due Date</th>
              <th scope="col" style="width: 8%">Created</th>
              <th scope="col" style="width: 10%">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in taskStore.filteredTasks" 
                :key="task.id" 
                class="task-row"
                :class="{ 'table-danger-light': task.is_overdue }"
                @click="openTaskDetail(task)">
              <td>
                <div>
                  <h6 class="mb-0" :class="{ 'text-decoration-line-through': task.status === 'completed' }">
                    {{ task.title }}
                    <span v-if="task.is_overdue" class="badge bg-danger ms-1">Overdue</span>
                  </h6>
                  <small class="text-muted">{{ truncateText(task.description, 100) }}</small>
                  <div v-if="task.client_name || task.lead_name" class="mt-1">
                    <small class="text-muted">
                      <i v-if="task.client_name" class="bi bi-person me-1"></i>{{ task.client_name }}
                      <i v-if="task.lead_name" class="bi bi-person-plus ms-2 me-1"></i>{{ task.lead_name }}
                    </small>
                  </div>
                  <div v-if="task.tags && task.tags.length > 0" class="mt-1">
                    <span
                      v-for="tag in task.tags.slice(0, 3)"
                      :key="tag"
                      class="badge bg-secondary me-1"
                      style="font-size: 0.7em;"
                    >
                      {{ tag }}
                    </span>
                    <span v-if="task.tags.length > 3" class="badge bg-secondary" style="font-size: 0.7em;">
                      +{{ task.tags.length - 3 }}
                    </span>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge" :class="getStatusBadgeClass(task.status)">
                  {{ getStatusLabel(task.status) }}
                </span>
              </td>
              <td>
                <span class="badge" :class="getPriorityBadgeClass(task.priority)">
                  {{ task.priority || 'Medium' }}
                </span>
              </td>
              <td>
                <small>{{ task.assigned_to_name || '-' }}</small>
              </td>
              <td>
                <small>{{ task.due_date ? formatDate(task.due_date) : '-' }}</small>
              </td>
              <td>
                <small>{{ formatRelativeDate(task.created_at) }}</small>
              </td>
              <td @click.stop>
                <div class="btn-group" role="group">
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click.stop="openTaskDetail(task)"
                    title="Edit Task"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    v-if="task.status !== 'completed'"
                    class="btn btn-sm btn-outline-success"
                    @click.stop="handleTaskUpdate(task.id, { status: 'completed' })"
                    title="Mark Complete"
                  >
                    <i class="bi bi-check"></i>
                  </button>
                  <button
                    class="btn btn-sm btn-outline-danger"
                    @click.stop="handleTaskDelete(task.id)"
                    title="Delete Task"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loading State -->
      <div v-if="taskStore.loading.tasks" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading tasks...</p>
      </div>

      <!-- Empty State -->
      <div v-if="!taskStore.loading.tasks && taskStore.filteredTasks.length === 0" class="text-center py-5">
        <i class="bi bi-clipboard-check fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">No tasks found</h5>
        <p class="text-muted">
          {{ taskStore.tasks.length > 0 ? 'No tasks match your filters' : 'Create your first task to get started' }}
        </p>
        <button v-if="taskStore.tasks.length > 0" class="btn btn-outline-secondary" @click="taskStore.clearFilters()">
          Clear Filters
        </button>
        <button v-else class="btn btn-primary" @click="openCreateTask">
          Create First Task
        </button>
      </div>

      <!-- Error State -->
      <div v-if="taskStore.error" class="alert alert-danger m-3">
        <h5>Error Loading Tasks</h5>
        <p>{{ taskStore.error }}</p>
        <button class="btn btn-danger" @click="taskStore.fetchTasks()">
          Retry
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="taskStore.pagination.totalPages > 1" class="mt-4">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: taskStore.pagination.page === 1 }">
          <button
            class="page-link"
            @click="changePage(taskStore.pagination.page - 1)"
            :disabled="taskStore.pagination.page === 1"
          >
            Previous
          </button>
        </li>
        <li
          class="page-item"
          v-for="page in visiblePages"
          :key="page"
          :class="{ active: page === taskStore.pagination.page }"
        >
          <button class="page-link" @click="changePage(page)">
            {{ page }}
          </button>
        </li>
        <li
          class="page-item"
          :class="{ disabled: taskStore.pagination.page === taskStore.pagination.totalPages }"
        >
          <button
            class="page-link"
            @click="changePage(taskStore.pagination.page + 1)"
            :disabled="taskStore.pagination.page === taskStore.pagination.totalPages"
          >
            Next
          </button>
        </li>
      </ul>
    </nav>

    <!-- Task Form Modal -->
    <TaskForm
      v-if="showTaskModal"
      :task="selectedTask"
      :show="showTaskModal"
      @close="closeTaskModal"
      @task-saved="handleTaskSaved"
    />

    <!-- Template Modal -->
    <TaskTemplateModal
      v-if="showTemplateModal"
      :show="showTemplateModal"
      @close="showTemplateModal = false"
      @template-used="handleTemplateUsed"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useTaskStore } from '@/stores/taskStore.js'
import TaskForm from '@/components/TaskForm.vue'
import TaskTemplateModal from '@/components/TaskTemplateModal.vue'

const taskStore = useTaskStore()

const searchQuery = ref('')
const sortBy = ref('-created_at')
const showTaskModal = ref(false)
const showTemplateModal = ref(false)
const selectedTask = ref(null)

const visiblePages = computed(() => {
  const currentPage = taskStore.pagination.page
  const totalPages = taskStore.pagination.totalPages
  const visibleRange = 5
  
  let start = Math.max(1, currentPage - Math.floor(visibleRange / 2))
  let end = Math.min(totalPages, start + visibleRange - 1)
  
  if (end - start + 1 < visibleRange) {
    start = Math.max(1, end - visibleRange + 1)
  }
  
  const pages = []
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

let searchTimeout = null

const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    taskStore.setSearch(searchQuery.value)
  }, 500)
}

const handleSort = () => {
  taskStore.updateFilter('ordering', sortBy.value)
}

const openCreateTask = () => {
  selectedTask.value = null
  showTaskModal.value = true
}

const openTaskDetail = (task) => {
  selectedTask.value = task
  showTaskModal.value = true
}

const closeTaskModal = () => {
  showTaskModal.value = false
  selectedTask.value = null
}

const handleTaskSaved = () => {
  closeTaskModal()
  taskStore.fetchTasks()
}

const handleTaskUpdate = async (taskId, updates) => {
  try {
    await taskStore.updateTask(taskId, updates)
  } catch (error) {
    console.error('Failed to update task:', error)
  }
}

const handleTaskDelete = async (taskId) => {
  if (confirm('Are you sure you want to delete this task?')) {
    try {
      await taskStore.deleteTask(taskId)
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }
}

const handleTemplateUsed = (templateId, taskData) => {
  taskStore.createTaskFromTemplate(templateId, taskData)
  showTemplateModal.value = false
}

// Helper methods for status and priority badges
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

const truncateText = (text, length) => {
  return text && text.length > length ? text.substring(0, length) + '...' : text
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

const changePage = (page) => {
  if (page >= 1 && page <= taskStore.pagination.totalPages) {
    taskStore.pagination.page = page
    taskStore.fetchTasks()
  }
}

onMounted(() => {
  taskStore.fetchTasks()
  taskStore.fetchTaskStats()
  taskStore.fetchTaskTemplates()
})

watch(() => taskStore.filters.search, (newValue) => {
  searchQuery.value = newValue
})
</script>

<style scoped>
.task-dashboard {
  padding: 1.5rem;
}

.task-dashboard-page-header {
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

/* Task table styling */
.task-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.task-row:hover {
  background-color: #f8f9fa;
}

.table-danger-light {
  background-color: #fff5f5 !important;
}

.table-danger-light:hover {
  background-color: #ffe5e5 !important;
}

/* Using default Bootstrap card styles */

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

.card-subtitle {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.pagination {
  margin-bottom: 0;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>