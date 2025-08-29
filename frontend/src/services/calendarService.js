import axios from 'axios'
import { apiService } from './api.js'

class CalendarService {
  
  // Calendar Account Management
  async getCalendarAccounts() {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-accounts/'))
      return response.data
    } catch (error) {
      console.error('Error fetching calendar accounts:', error)
      throw error
    }
  }

  async createCalendarAccount(accountData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/calendar-accounts/'), accountData)
      return response.data
    } catch (error) {
      console.error('Error creating calendar account:', error)
      throw error
    }
  }

  async updateCalendarAccount(accountId, updateData) {
    try {
      const response = await axios.put(apiService.getUrl(`/api/calendar-accounts/${accountId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating calendar account:', error)
      throw error
    }
  }

  async deleteCalendarAccount(accountId) {
    try {
      await axios.delete(apiService.getUrl(`/api/calendar-accounts/${accountId}/`))
    } catch (error) {
      console.error('Error deleting calendar account:', error)
      throw error
    }
  }

  // OAuth Integration
  async initiateOAuthFlow(provider) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/calendar-accounts/oauth/${provider}/initiate/`))
      return response.data
    } catch (error) {
      console.error('Error initiating OAuth flow:', error)
      throw error
    }
  }

  async completeOAuthFlow(provider, code, state) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/calendar-accounts/oauth/${provider}/callback/`), {
        code,
        state
      })
      return response.data
    } catch (error) {
      console.error('Error completing OAuth flow:', error)
      throw error
    }
  }

  // Calendar Events
  async getCalendarEvents(params = {}) {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-events/'), { params })
      return response.data
    } catch (error) {
      console.error('Error fetching calendar events:', error)
      throw error
    }
  }

  async getCalendarEvent(eventId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/calendar-events/${eventId}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching calendar event:', error)
      throw error
    }
  }

  async createCalendarEvent(eventData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/calendar-events/'), eventData)
      return response.data
    } catch (error) {
      console.error('Error creating calendar event:', error)
      throw error
    }
  }

  async updateCalendarEvent(eventId, updateData) {
    try {
      const response = await axios.put(apiService.getUrl(`/api/calendar-events/${eventId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating calendar event:', error)
      throw error
    }
  }

  async deleteCalendarEvent(eventId) {
    try {
      await axios.delete(apiService.getUrl(`/api/calendar-events/${eventId}/`))
    } catch (error) {
      console.error('Error deleting calendar event:', error)
      throw error
    }
  }

  // Meeting Scheduling
  async scheduleMeeting(meetingData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/calendar-events/schedule-meeting/'), meetingData)
      return response.data
    } catch (error) {
      console.error('Error scheduling meeting:', error)
      throw error
    }
  }

  // Meeting Templates
  async getMeetingTemplates() {
    try {
      const response = await axios.get(apiService.getUrl('/api/meeting-templates/'))
      return response.data
    } catch (error) {
      console.error('Error fetching meeting templates:', error)
      throw error
    }
  }

  async getMeetingTemplate(templateId) {
    try {
      const response = await axios.get(apiService.getUrl(`/api/meeting-templates/${templateId}/`))
      return response.data
    } catch (error) {
      console.error('Error fetching meeting template:', error)
      throw error
    }
  }

  async createMeetingTemplate(templateData) {
    try {
      const response = await axios.post(apiService.getUrl('/api/meeting-templates/'), templateData)
      return response.data
    } catch (error) {
      console.error('Error creating meeting template:', error)
      throw error
    }
  }

  async updateMeetingTemplate(templateId, updateData) {
    try {
      const response = await axios.put(apiService.getUrl(`/api/meeting-templates/${templateId}/`), updateData)
      return response.data
    } catch (error) {
      console.error('Error updating meeting template:', error)
      throw error
    }
  }

  async deleteMeetingTemplate(templateId) {
    try {
      await axios.delete(apiService.getUrl(`/api/meeting-templates/${templateId}/`))
    } catch (error) {
      console.error('Error deleting meeting template:', error)
      throw error
    }
  }

  // Calendar Synchronization
  async syncCalendarAccount(accountId) {
    try {
      const response = await axios.post(apiService.getUrl(`/api/calendar-accounts/${accountId}/sync/`))
      return response.data
    } catch (error) {
      console.error('Error syncing calendar account:', error)
      throw error
    }
  }

  async syncAllAccounts() {
    try {
      const response = await axios.post(apiService.getUrl('/api/calendar-accounts/sync-all/'))
      return response.data
    } catch (error) {
      console.error('Error syncing all accounts:', error)
      throw error
    }
  }

  // Availability and Free/Busy
  async checkAvailability(startDate, endDate, duration = 60) {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-events/check-availability/'), {
        params: {
          start_date: startDate,
          end_date: endDate,
          duration
        }
      })
      return response.data
    } catch (error) {
      console.error('Error checking availability:', error)
      throw error
    }
  }

  async getFreeBusyInfo(startDate, endDate, emails = []) {
    try {
      const response = await axios.post(apiService.getUrl('/api/calendar-events/free-busy/'), {
        start_date: startDate,
        end_date: endDate,
        emails
      })
      return response.data
    } catch (error) {
      console.error('Error fetching free/busy info:', error)
      throw error
    }
  }

  // Analytics and Reporting
  async getCalendarAnalytics(startDate, endDate) {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-events/analytics/'), {
        params: {
          start_date: startDate,
          end_date: endDate
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching calendar analytics:', error)
      throw error
    }
  }

  // Utility Methods
  async getUpcomingEvents(days = 7) {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-events/upcoming/'), {
        params: { days }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching upcoming events:', error)
      throw error
    }
  }

  async getTodaysEvents() {
    try {
      const response = await axios.get(apiService.getUrl('/api/calendar-events/today/'))
      return response.data
    } catch (error) {
      console.error('Error fetching today\'s events:', error)
      throw error
    }
  }

  // Helper methods for calendar operations
  getEventColor(event) {
    if (event.calendar_account) {
      return event.calendar_account.color || '#007bff'
    }
    return '#007bff'
  }

  getTextColor(event) {
    return '#ffffff'
  }

  isEventEditable(event) {
    return event.calendar_account && event.calendar_account.can_edit
  }

  formatEventDuration(startTime, endTime) {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const duration = (end - start) / (1000 * 60) // minutes
    
    if (duration < 60) {
      return `${duration} min`
    } else {
      const hours = Math.floor(duration / 60)
      const minutes = duration % 60
      return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`
    }
  }
}

export default new CalendarService()