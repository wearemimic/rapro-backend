import axios from 'axios'
import { apiService } from './api.js'

export const taskService = {
  // =============================================================================
  // TASK MANAGEMENT
  // =============================================================================
  
  async getTasks(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), { params })
      return response.data
    } catch (error) {
      console.error('Error fetching tasks:', error)
      throw error
    }
  },
  
  async getTask(id) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/tasks/${id}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching task:', error)
      throw error
    }
  },
  
  async createTask(taskData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/tasks/'), taskData)
      return response.data
    } catch (error) {
      console.error('Error creating task:', error)
      throw error
    }
  },
  
  async updateTask(id, updates) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/tasks/${id}/`), updates)
      return response.data
    } catch (error) {
      console.error('Error updating task:', error)
      throw error
    }
  },
  
  async deleteTask(id) {
    try {
      await axios.delete(apiService.getUrl(`/api/tasks/${id}/`))
    } catch (error) {
      console.error('Error deleting task:', error)
      throw error
    }
  },
  
  async bulkUpdateTasks(taskIds, updates) {
    try {
      const response = await axios.post(apiService.getUrl('/api/tasks/bulk_update/'), {
        task_ids: taskIds,
        updates: updates
      })
      return response.data
    } catch (error) {
      console.error('Error bulk updating tasks:', error)
      throw error
    }
  },
  
  async getTaskStats() {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/stats/'))
      return response.data
    } catch (error) {
      console.error('Error fetching task stats:', error)
      throw error
    }
  },
  
  // =============================================================================
  // TASK TEMPLATES
  // =============================================================================
  
  async getTaskTemplates(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/task-templates/'), { params })
      return response.data
    } catch (error) {
      console.error('Error fetching task templates:', error)
      throw error
    }
  },
  
  async getTaskTemplate(id) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/task-templates/${id}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching task template:', error)
      throw error
    }
  },
  
  async createTaskTemplate(templateData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/task-templates/'), templateData)
      return response.data
    } catch (error) {
      console.error('Error creating task template:', error)
      throw error
    }
  },
  
  async updateTaskTemplate(id, updates) {
    try {
      const response = await axios.patch(apiService.getUrl(`/api/task-templates/${id}/`), updates)
      return response.data
    } catch (error) {
      console.error('Error updating task template:', error)
      throw error
    }
  },
  
  async deleteTaskTemplate(id) {
    try {
      await axios.delete(`/api/task-templates/${id}/`)
    } catch (error) {
      console.error('Error deleting task template:', error)
      throw error
    }
  },
  
  async createTaskFromTemplate(templateId, taskData = {}) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/task-templates/${templateId}/create_task_from_template/`), taskData)
      return response.data
    } catch (error) {
      console.error('Error creating task from template:', error)
      throw error
    }
  },
  
  // =============================================================================
  // TASK COMMENTS
  // =============================================================================
  
  async addTaskComment(taskId, content) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/tasks/${taskId}/add_comment/`), {
        content: content
      })
      return response.data
    } catch (error) {
      console.error('Error adding task comment:', error)
      throw error
    }
  },
  
  async getTaskComments(taskId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/tasks/${taskId}/`))
      return response.data.comments || []
    } catch (error) {
      console.error('Error fetching task comments:', error)
      throw error
    }
  },
  
  // =============================================================================
  // TASK ASSOCIATIONS
  // =============================================================================
  
  async getClientTasks(clientId, params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { client: clientId, ...params }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching client tasks:', error)
      throw error
    }
  },
  
  async getLeadTasks(leadId, params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { lead: leadId, ...params }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching lead tasks:', error)
      throw error
    }
  },
  
  // =============================================================================
  // TASK SEARCH AND FILTERING
  // =============================================================================
  
  async searchTasks(query, filters = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { search: query, ...filters }
      })
      return response.data
    } catch (error) {
      console.error('Error searching tasks:', error)
      throw error
    }
  },
  
  async getOverdueTasks() {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { overdue: true }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching overdue tasks:', error)
      throw error
    }
  },
  
  async getDueTodayTasks() {
    try {
      const today = new Date().toISOString().split('T')[0]
      const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { 
          due_from: today,
          due_to: tomorrow,
          status: 'pending,in_progress'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching due today tasks:', error)
      throw error
    }
  },
  
  async getMyTasks() {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/'), {
        params: { assigned_to: 'me' }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching my tasks:', error)
      throw error
    }
  },
  
  // =============================================================================
  // TASK ANALYTICS
  // =============================================================================
  
  async getTaskAnalytics(timeframe = '30d') {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/analytics/'), {
        params: { timeframe }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching task analytics:', error)
      throw error
    }
  },
  
  async getTaskPerformanceMetrics() {
    try {
      const response = await axios.get(apiService.getUrl('/api/tasks/performance/'))
      return response.data
    } catch (error) {
      console.error('Error fetching task performance metrics:', error)
      throw error
    }
  }
}