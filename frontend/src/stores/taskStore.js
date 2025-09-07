import { defineStore } from 'pinia'
import { taskService } from '@/services/taskService.js'
import { useAuthStore } from './auth.js'

export const useTaskStore = defineStore('task', {
  state: () => ({
    // Tasks data
    tasks: [],
    currentTask: null,
    
    // Task templates
    taskTemplates: [],
    currentTemplate: null,
    
    // Filtering and search
    filters: {
      status: 'active',  // Default to showing only active tasks
      priority: '',
      assigned_to: '',
      client: '',
      lead: '',
      task_type: '',
      search: '',
      overdue: false,
      due_from: '',
      due_to: '',
      ordering: '-created_at'
    },
    
    // Pagination
    pagination: {
      page: 1,
      pageSize: 20,
      total: 0,
      totalPages: 0
    },
    
    // Task statistics
    stats: {
      total_tasks: 0,
      completed_tasks: 0,
      pending_tasks: 0,
      in_progress_tasks: 0,
      high_priority: 0,
      medium_priority: 0,
      low_priority: 0,
      overdue_tasks: 0,
      due_soon: 0,
      completion_rate: 0
    },
    
    // Loading states
    loading: {
      tasks: false,
      task: false,
      templates: false,
      creating: false,
      updating: false,
      deleting: false,
      stats: false,
      bulkUpdate: false
    },
    
    // Error handling
    error: null,
    
    // UI State
    viewMode: 'list', // 'list', 'kanban', 'calendar'
    selectedTasks: [],
    showCompleted: false,
    
    // Comments and collaboration
    taskComments: {},
    
    // Calendar view state
    calendarView: {
      currentDate: new Date(),
      viewType: 'month' // 'month', 'week', 'day'
    }
  }),
  
  persist: {
    paths: ['filters', 'viewMode', 'showCompleted', 'calendarView']
  },
  
  getters: {
    // Task filtering getters
    filteredTasks: (state) => {
      // Backend now handles all filtering, including 'active' status
      // Just return the tasks as-is since they're already filtered by the API
      return state.tasks
    },
    
    // Task grouping getters
    tasksByStatus: (state) => {
      const tasks = state.filteredTasks || []
      return {
        pending: tasks.filter(task => task.status === 'pending'),
        in_progress: tasks.filter(task => task.status === 'in_progress'),
        completed: tasks.filter(task => task.status === 'completed'),
        cancelled: tasks.filter(task => task.status === 'cancelled')
      }
    },
    
    tasksByPriority: (state) => {
      const tasks = state.filteredTasks || []
      return {
        high: tasks.filter(task => task.priority === 'high'),
        medium: tasks.filter(task => task.priority === 'medium'),
        low: tasks.filter(task => task.priority === 'low')
      }
    },
    
    // Due date getters
    overdueTasks: (state) => {
      return state.tasks.filter(task => task.is_overdue && task.status !== 'completed')
    },
    
    dueTodayTasks: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.tasks.filter(task => {
        if (!task.due_date) return false
        const dueDate = new Date(task.due_date).toISOString().split('T')[0]
        return dueDate === today && task.status !== 'completed'
      })
    },
    
    dueSoonTasks: (state) => {
      const now = new Date()
      const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
      
      return state.tasks.filter(task => {
        if (!task.due_date) return false
        const dueDate = new Date(task.due_date)
        return dueDate >= now && dueDate <= nextWeek && task.status !== 'completed'
      })
    },
    
    // Calendar view getters
    calendarTasks: (state) => {
      return state.tasks.filter(task => task.due_date).map(task => ({
        ...task,
        start: task.due_date,
        title: task.title,
        color: state.getPriorityColor(task.priority),
        extendedProps: {
          task: task
        }
      }))
    },
    
    // Template getters
    activeTemplates: (state) => {
      return state.taskTemplates.filter(template => template.is_active)
    },
    
    // UI state getters
    hasSelectedTasks: (state) => {
      return state.selectedTasks.length > 0
    },
    
    isLoading: (state) => {
      return Object.values(state.loading).some(loading => loading)
    }
  },
  
  actions: {
    // =============================================================================
    // TASK MANAGEMENT ACTIONS
    // =============================================================================
    
    async fetchTasks(params = {}) {
      this.loading.tasks = true
      this.error = null
      
      try {
        const queryParams = {
          ...this.filters,
          ...params,
          page: this.pagination.page,
          page_size: this.pagination.pageSize
        }
        
        const response = await taskService.getTasks(queryParams)
        
        this.tasks = response.results || response.data || response
        
        // Update pagination if response has pagination info
        if (response.count !== undefined) {
          this.pagination.total = response.count
          this.pagination.totalPages = Math.ceil(response.count / this.pagination.pageSize)
        }
        
        return response
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch tasks:', error)
        throw error
      } finally {
        this.loading.tasks = false
      }
    },
    
    async fetchTask(id) {
      this.loading.task = true
      this.error = null
      
      try {
        const task = await taskService.getTask(id)
        this.currentTask = task
        
        // Update task in list if exists
        const index = this.tasks.findIndex(t => t.id === id)
        if (index !== -1) {
          this.tasks[index] = task
        }
        
        return task
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch task:', error)
        throw error
      } finally {
        this.loading.task = false
      }
    },
    
    async createTask(taskData) {
      this.loading.creating = true
      this.error = null
      
      try {
        const task = await taskService.createTask(taskData)
        this.tasks.unshift(task)
        this.currentTask = task
        
        // Update stats
        this.fetchTaskStats()
        
        return task
      } catch (error) {
        this.error = error.message
        console.error('Failed to create task:', error)
        throw error
      } finally {
        this.loading.creating = false
      }
    },
    
    async updateTask(id, updates) {
      this.loading.updating = true
      this.error = null
      
      try {
        const task = await taskService.updateTask(id, updates)
        
        // Update in list
        const index = this.tasks.findIndex(t => t.id === id)
        if (index !== -1) {
          this.tasks[index] = task
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === id) {
          this.currentTask = task
        }
        
        // Update stats if status changed
        if (updates.status) {
          this.fetchTaskStats()
        }
        
        return task
      } catch (error) {
        this.error = error.message
        console.error('Failed to update task:', error)
        throw error
      } finally {
        this.loading.updating = false
      }
    },
    
    async deleteTask(id) {
      this.loading.deleting = true
      this.error = null
      
      try {
        await taskService.deleteTask(id)
        
        // Remove from list
        this.tasks = this.tasks.filter(t => t.id !== id)
        
        // Clear current task if it's the same
        if (this.currentTask && this.currentTask.id === id) {
          this.currentTask = null
        }
        
        // Update stats
        this.fetchTaskStats()
        
      } catch (error) {
        this.error = error.message
        console.error('Failed to delete task:', error)
        throw error
      } finally {
        this.loading.deleting = false
      }
    },
    
    async bulkUpdateTasks(taskIds, updates) {
      this.loading.bulkUpdate = true
      this.error = null
      
      try {
        const result = await taskService.bulkUpdateTasks(taskIds, updates)
        
        // Refresh tasks to get updated data
        await this.fetchTasks()
        
        // Clear selection
        this.selectedTasks = []
        
        return result
      } catch (error) {
        this.error = error.message
        console.error('Failed to bulk update tasks:', error)
        throw error
      } finally {
        this.loading.bulkUpdate = false
      }
    },
    
    // =============================================================================
    // TASK TEMPLATE ACTIONS
    // =============================================================================
    
    async fetchTaskTemplates() {
      this.loading.templates = true
      this.error = null
      
      try {
        const templates = await taskService.getTaskTemplates()
        this.taskTemplates = templates.results || templates.data || templates
        return templates
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch task templates:', error)
        throw error
      } finally {
        this.loading.templates = false
      }
    },
    
    async createTaskTemplate(templateData) {
      this.loading.templates = true
      this.error = null
      
      try {
        const template = await taskService.createTaskTemplate(templateData)
        this.taskTemplates.unshift(template)
        return template
      } catch (error) {
        this.error = error.message
        console.error('Failed to create task template:', error)
        throw error
      } finally {
        this.loading.templates = false
      }
    },

    async updateTaskTemplate(id, updates) {
      this.loading.templates = true
      this.error = null
      
      try {
        const template = await taskService.updateTaskTemplate(id, updates)
        
        // Update in list
        const index = this.taskTemplates.findIndex(t => t.id === id)
        if (index !== -1) {
          this.taskTemplates[index] = template
        }
        
        return template
      } catch (error) {
        this.error = error.message
        console.error('Failed to update task template:', error)
        throw error
      } finally {
        this.loading.templates = false
      }
    },

    async deleteTaskTemplate(id) {
      this.loading.templates = true
      this.error = null
      
      try {
        await taskService.deleteTaskTemplate(id)
        
        // Remove from list
        this.taskTemplates = this.taskTemplates.filter(t => t.id !== id)
        
      } catch (error) {
        this.error = error.message
        console.error('Failed to delete task template:', error)
        throw error
      } finally {
        this.loading.templates = false
      }
    },

    async createTaskFromTemplate(templateId, taskData = {}) {
      this.loading.creating = true
      this.error = null
      
      try {
        const task = await taskService.createTaskFromTemplate(templateId, taskData)
        this.tasks.unshift(task)
        this.currentTask = task
        
        // Update stats
        this.fetchTaskStats()
        
        return task
      } catch (error) {
        this.error = error.message
        console.error('Failed to create task from template:', error)
        throw error
      } finally {
        this.loading.creating = false
      }
    },
    
    // =============================================================================
    // TASK COMMENTS ACTIONS
    // =============================================================================
    
    async addTaskComment(taskId, content) {
      try {
        const comment = await taskService.addTaskComment(taskId, content)
        
        // Update task comments
        if (!this.taskComments[taskId]) {
          this.taskComments[taskId] = []
        }
        this.taskComments[taskId].unshift(comment)
        
        // Update comments count in task
        const task = this.tasks.find(t => t.id === taskId)
        if (task) {
          task.comments_count = (task.comments_count || 0) + 1
        }
        
        return comment
      } catch (error) {
        this.error = error.message
        console.error('Failed to add task comment:', error)
        throw error
      }
    },
    
    // =============================================================================
    // STATISTICS ACTIONS
    // =============================================================================
    
    async fetchTaskStats() {
      this.loading.stats = true
      this.error = null
      
      try {
        const stats = await taskService.getTaskStats()
        this.stats = stats
        return stats
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch task stats:', error)
        throw error
      } finally {
        this.loading.stats = false
      }
    },
    
    // =============================================================================
    // FILTER AND SEARCH ACTIONS
    // =============================================================================
    
    updateFilter(filterName, value) {
      this.filters[filterName] = value
      
      // Reset pagination when filters change
      this.pagination.page = 1
      
      // Auto-fetch tasks with new filters
      this.fetchTasks()
    },
    
    clearFilters() {
      this.filters = {
        status: 'active',  // Reset to showing only active tasks
        priority: '',
        assigned_to: '',
        client: '',
        lead: '',
        task_type: '',
        search: '',
        overdue: false,
        due_from: '',
        due_to: '',
        ordering: '-created_at'
      }
      
      // Reset pagination
      this.pagination.page = 1
      
      // Fetch tasks with cleared filters
      this.fetchTasks()
    },
    
    setSearch(searchQuery) {
      this.filters.search = searchQuery
      this.pagination.page = 1
      
      // Debounce search to avoid too many requests
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.fetchTasks()
      }, 500)
    },
    
    // =============================================================================
    // UI STATE ACTIONS
    // =============================================================================
    
    setViewMode(mode) {
      this.viewMode = mode
    },
    
    toggleShowCompleted() {
      this.showCompleted = !this.showCompleted
    },
    
    selectTask(taskId) {
      if (!this.selectedTasks.includes(taskId)) {
        this.selectedTasks.push(taskId)
      }
    },
    
    deselectTask(taskId) {
      this.selectedTasks = this.selectedTasks.filter(id => id !== taskId)
    },
    
    toggleTaskSelection(taskId) {
      if (this.selectedTasks.includes(taskId)) {
        this.deselectTask(taskId)
      } else {
        this.selectTask(taskId)
      }
    },
    
    clearSelection() {
      this.selectedTasks = []
    },
    
    selectAllTasks() {
      this.selectedTasks = this.filteredTasks.map(task => task.id)
    },
    
    // =============================================================================
    // CALENDAR ACTIONS
    // =============================================================================
    
    setCalendarDate(date) {
      this.calendarView.currentDate = date
    },
    
    setCalendarViewType(viewType) {
      this.calendarView.viewType = viewType
    },
    
    // =============================================================================
    // UTILITY ACTIONS
    // =============================================================================
    
    getPriorityColor(priority) {
      switch (priority) {
        case 'high':
          return '#dc3545' // red
        case 'medium':
          return '#ffc107' // yellow
        case 'low':
          return '#28a745' // green
        default:
          return '#6c757d' // gray
      }
    },
    
    getStatusColor(status) {
      switch (status) {
        case 'completed':
          return '#28a745' // green
        case 'in_progress':
          return '#007bff' // blue
        case 'pending':
          return '#6c757d' // gray
        case 'cancelled':
          return '#dc3545' // red
        default:
          return '#6c757d'
      }
    },
    
    clearError() {
      this.error = null
    },
    
    reset() {
      this.tasks = []
      this.currentTask = null
      this.taskTemplates = []
      this.currentTemplate = null
      this.selectedTasks = []
      this.taskComments = {}
      this.clearFilters()
      this.clearError()
    }
  }
})