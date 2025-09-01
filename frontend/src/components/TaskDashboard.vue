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

    <!-- Quick Filters -->
    <div class="card mb-4">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h4 class="card-header-title">Quick Filters</h4>
          <button
            class="btn btn-sm btn-outline-secondary"
            @click="taskStore.clearFilters()"
          >
            Clear All
          </button>
        </div>
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3 mb-3">
            <label class="form-label">Search Tasks</label>
            <input
              type="text"
              class="form-control"
              placeholder="Search by title or description..."
              v-model="searchQuery"
              @input="handleSearch"
            >
          </div>
          <div class="col-md-2 mb-3">
            <label class="form-label">Status</label>
            <select
              class="form-select"
              v-model="taskStore.filters.status"
              @change="taskStore.updateFilter('status', taskStore.filters.status)"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-2 mb-3">
            <label class="form-label">Priority</label>
            <select
              class="form-select"
              v-model="taskStore.filters.priority"
              @change="taskStore.updateFilter('priority', taskStore.filters.priority)"
            >
              <option value="">All Priority</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div class="col-md-2 mb-3">
            <label class="form-label">Assigned To</label>
            <select
              class="form-select"
              v-model="taskStore.filters.assigned_to"
              @change="taskStore.updateFilter('assigned_to', taskStore.filters.assigned_to)"
            >
              <option value="">All Users</option>
              <option value="me">My Tasks</option>
              <option value="unassigned">Unassigned</option>
            </select>
          </div>
          <div class="col-md-3 mb-3">
            <label class="form-label">Options</label>
            <div class="d-flex gap-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="overdue"
                  v-model="taskStore.filters.overdue"
                  @change="taskStore.updateFilter('overdue', taskStore.filters.overdue)"
                >
                <label class="form-check-label" for="overdue">
                  Overdue Only
                </label>
              </div>
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="showCompleted"
                  v-model="taskStore.showCompleted"
                  @change="taskStore.toggleShowCompleted()"
                >
                <label class="form-check-label" for="showCompleted">
                  Show Completed
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Mode Toggle -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div class="btn-group" role="group">
        <input
          type="radio"
          class="btn-check"
          name="viewMode"
          id="listView"
          value="list"
          v-model="taskStore.viewMode"
          @change="taskStore.setViewMode('list')"
        >
        <label class="btn btn-outline-primary" for="listView">
          <i class="bi-list me-1"></i>List
        </label>

        <input
          type="radio"
          class="btn-check"
          name="viewMode"
          id="kanbanView"
          value="kanban"
          v-model="taskStore.viewMode"
          @change="taskStore.setViewMode('kanban')"
        >
        <label class="btn btn-outline-primary" for="kanbanView">
          <i class="bi-columns me-1"></i>Kanban
        </label>

        <input
          type="radio"
          class="btn-check"
          name="viewMode"
          id="calendarView"
          value="calendar"
          v-model="taskStore.viewMode"
          @change="taskStore.setViewMode('calendar')"
        >
        <label class="btn btn-outline-primary" for="calendarView">
          <i class="bi-calendar me-1"></i>Calendar
        </label>
      </div>

      <!-- Bulk Actions -->
      <div v-if="taskStore.hasSelectedTasks" class="d-flex gap-2">
        <select
          class="form-select form-select-sm"
          v-model="bulkAction"
          style="width: auto;"
        >
          <option value="">Bulk Actions</option>
          <option value="status">Update Status</option>
          <option value="priority">Update Priority</option>
          <option value="assign">Assign To</option>
          <option value="delete">Delete Tasks</option>
        </select>
        <button
          class="btn btn-sm btn-primary"
          @click="performBulkAction"
          :disabled="!bulkAction"
        >
          Apply ({{ taskStore.selectedTasks.length }})
        </button>
      </div>
    </div>

    <!-- Task Content -->
    <div class="task-content">
      <!-- Loading State -->
      <div v-if="taskStore.loading.tasks" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading tasks...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="taskStore.error" class="alert alert-danger">
        <h5>Error Loading Tasks</h5>
        <p>{{ taskStore.error }}</p>
        <button class="btn btn-danger" @click="taskStore.fetchTasks()">
          Retry
        </button>
      </div>

      <!-- List View -->
      <TaskList
        v-else-if="taskStore.viewMode === 'list'"
        :tasks="taskStore.filteredTasks"
        :loading="taskStore.loading.updating"
        @task-click="openTaskDetail"
        @task-update="handleTaskUpdate"
        @task-delete="handleTaskDelete"
        @task-select="taskStore.toggleTaskSelection"
      />

      <!-- Kanban View -->
      <TaskKanban
        v-else-if="taskStore.viewMode === 'kanban'"
        :tasks="taskStore.tasksByStatus"
        :loading="taskStore.loading.updating"
        @task-click="openTaskDetail"
        @task-update="handleTaskUpdate"
        @task-delete="handleTaskDelete"
      />

      <!-- Calendar View -->
      <TaskCalendar
        v-else-if="taskStore.viewMode === 'calendar'"
        :tasks="taskStore.calendarTasks"
        :current-date="taskStore.calendarView.currentDate"
        :view-type="taskStore.calendarView.viewType"
        @task-click="openTaskDetail"
        @task-update="handleTaskUpdate"
        @date-change="taskStore.setCalendarDate"
        @view-change="taskStore.setCalendarViewType"
      />
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
import TaskList from '@/components/TaskList.vue'
import TaskKanban from '@/components/TaskKanban.vue'
import TaskCalendar from '@/components/TaskCalendar.vue'
import TaskForm from '@/components/TaskForm.vue'
import TaskTemplateModal from '@/components/TaskTemplateModal.vue'

const taskStore = useTaskStore()

const searchQuery = ref('')
const bulkAction = ref('')
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

const performBulkAction = () => {
  if (!bulkAction.value || !taskStore.hasSelectedTasks) return

  const selectedIds = taskStore.selectedTasks
  
  switch (bulkAction.value) {
    case 'status':
      showBulkStatusModal(selectedIds)
      break
    case 'priority':
      showBulkPriorityModal(selectedIds)
      break
    case 'assign':
      showBulkAssignModal(selectedIds)
      break
    case 'delete':
      handleBulkDelete(selectedIds)
      break
  }
  
  bulkAction.value = ''
}

const showBulkStatusModal = (taskIds) => {
  const status = prompt('Enter new status (pending, in_progress, completed, cancelled):')
  if (status && ['pending', 'in_progress', 'completed', 'cancelled'].includes(status)) {
    taskStore.bulkUpdateTasks(taskIds, { status })
  }
}

const showBulkPriorityModal = (taskIds) => {
  const priority = prompt('Enter new priority (high, medium, low):')
  if (priority && ['high', 'medium', 'low'].includes(priority)) {
    taskStore.bulkUpdateTasks(taskIds, { priority })
  }
}

const showBulkAssignModal = (taskIds) => {
  const assignedTo = prompt('Enter user ID to assign to (or leave empty for unassigned):')
  taskStore.bulkUpdateTasks(taskIds, { assigned_to: assignedTo || null })
}

const handleBulkDelete = (taskIds) => {
  if (confirm(`Are you sure you want to delete ${taskIds.length} tasks?`)) {
    taskIds.forEach(id => taskStore.deleteTask(id))
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

.task-content {
  min-height: 400px;
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

.btn-check:checked + .btn {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.pagination {
  margin-bottom: 0;
}

.form-select-sm {
  min-width: 150px;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>