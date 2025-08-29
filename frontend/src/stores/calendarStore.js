// src/stores/calendarStore.js
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import calendarService from '@/services/calendarService'
import { useTaskStore } from './taskStore'

export const useCalendarStore = defineStore('calendar', () => {
  // State
  const calendarAccounts = ref([])
  const calendarEvents = ref([])
  const meetingTemplates = ref([])
  const selectedAccount = ref(null)
  const currentDate = ref(new Date())
  const currentView = ref('month')
  const loading = ref(false)
  const error = ref(null)
  const syncingAccounts = ref(new Set())

  // Filters
  const filters = ref({
    accounts: [],
    statuses: ['confirmed', 'tentative'],
    privacy: ['public', 'private'],
    showTasks: true,
    showMeetings: true,
    showEvents: true,
    clients: [],
    leads: []
  })

  // Calendar Settings
  const settings = ref({
    defaultView: 'month',
    startHour: 8,
    endHour: 18,
    workDays: [1, 2, 3, 4, 5], // Monday to Friday
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    weekStartsOn: 0, // Sunday = 0, Monday = 1
    defaultMeetingDuration: 60,
    defaultReminders: [15, 60], // minutes before event
    showWeekends: true,
    showDeclined: false,
    autoSync: true,
    syncInterval: 15 // minutes
  })

  // Getters
  const activeAccounts = computed(() => 
    calendarAccounts.value.filter(account => account.is_active)
  )

  const connectedProviders = computed(() =>
    activeAccounts.value.map(account => account.provider)
  )

  const hasCalendarAccounts = computed(() =>
    calendarAccounts.value.length > 0
  )

  const filteredEvents = computed(() => {
    let events = calendarEvents.value

    // Filter by account
    if (filters.value.accounts.length > 0) {
      events = events.filter(event => 
        filters.value.accounts.includes(event.calendar_account?.id)
      )
    }

    // Filter by status
    if (filters.value.statuses.length > 0) {
      events = events.filter(event =>
        filters.value.statuses.includes(event.status)
      )
    }

    // Filter by privacy
    if (filters.value.privacy.length > 0) {
      events = events.filter(event =>
        filters.value.privacy.includes(event.privacy)
      )
    }

    // Filter by client/lead
    if (filters.value.clients.length > 0) {
      events = events.filter(event =>
        event.client && filters.value.clients.includes(event.client.id)
      )
    }

    if (filters.value.leads.length > 0) {
      events = events.filter(event =>
        event.lead && filters.value.leads.includes(event.lead.id)
      )
    }

    return events
  })

  const todayEvents = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    return filteredEvents.value.filter(event => {
      const eventDate = new Date(event.start_datetime)
      return eventDate >= today && eventDate < tomorrow
    }).sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
  })

  const upcomingEvents = computed(() => {
    const now = new Date()
    const nextWeek = new Date()
    nextWeek.setDate(nextWeek.getDate() + 7)

    return filteredEvents.value.filter(event => {
      const eventDate = new Date(event.start_datetime)
      return eventDate >= now && eventDate <= nextWeek
    }).sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
  })

  const eventsForCurrentView = computed(() => {
    const viewStart = getViewStartDate(currentDate.value, currentView.value)
    const viewEnd = getViewEndDate(currentDate.value, currentView.value)

    return filteredEvents.value.filter(event => {
      const eventStart = new Date(event.start_datetime)
      const eventEnd = new Date(event.end_datetime)
      return (eventStart <= viewEnd && eventEnd >= viewStart)
    })
  })

  // Include tasks from task store if enabled
  const combinedEvents = computed(() => {
    let events = [...eventsForCurrentView.value]

    if (filters.value.showTasks) {
      const taskStore = useTaskStore()
      
      const tasksAsEvents = taskStore.tasks
        .filter(task => task.due_date || task.due_datetime)
        .map(task => {
          // Handle different date formats
          let startDateTime, endDateTime
          
          if (task.due_datetime) {
            // If we have a full datetime, use it
            startDateTime = task.due_datetime
            endDateTime = task.due_datetime
          } else if (task.due_date) {
            // Check if due_date already contains time info (ISO format)
            if (task.due_date.includes('T')) {
              // Already has time info, use as is
              startDateTime = task.due_date
              endDateTime = task.due_date
            } else {
              // Pure date, combine with due_time or default to 9 AM
              const timeStr = task.due_time || '09:00:00'
              startDateTime = `${task.due_date}T${timeStr}`
              endDateTime = `${task.due_date}T${timeStr}`
            }
          }

          return {
            id: `task-${task.id}`,
            title: task.title,
            start_datetime: startDateTime,
            end_datetime: endDateTime,
            all_day: !task.due_time && !task.due_datetime?.includes('T'),
            type: 'task',
            priority: task.priority,
            status: task.status,
            client: task.client,
            lead: task.lead,
            due_datetime: task.due_datetime || startDateTime,
            description: task.description,
            extendedProps: {
              taskId: task.id,
              description: task.description,
              isTask: true
            }
          }
        })
      
      events = [...events, ...tasksAsEvents]
    }
    return events
  })

  // Actions
  const fetchCalendarAccounts = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await calendarService.getCalendarAccounts()
      calendarAccounts.value = response.results || response
    } catch (err) {
      error.value = 'Failed to fetch calendar accounts'
      console.error('Error fetching calendar accounts:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchCalendarEvents = async (params = {}) => {
    try {
      loading.value = true
      error.value = null
      
      // Default date range for current view
      if (!params.start_date || !params.end_date) {
        const viewStart = getViewStartDate(currentDate.value, currentView.value)
        const viewEnd = getViewEndDate(currentDate.value, currentView.value)
        params.start_date = viewStart.toISOString().split('T')[0]
        params.end_date = viewEnd.toISOString().split('T')[0]
      }

      const response = await calendarService.getCalendarEvents(params)
      calendarEvents.value = response.results || response
    } catch (err) {
      error.value = 'Failed to fetch calendar events'
      console.error('Error fetching calendar events:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchMeetingTemplates = async () => {
    try {
      const response = await calendarService.getMeetingTemplates()
      meetingTemplates.value = response.results || response
    } catch (err) {
      error.value = 'Failed to fetch meeting templates'
      console.error('Error fetching meeting templates:', err)
    }
  }

  const createCalendarAccount = async (accountData) => {
    try {
      loading.value = true
      const account = await calendarService.createCalendarAccount(accountData)
      calendarAccounts.value.push(account)
      return account
    } catch (err) {
      error.value = 'Failed to create calendar account'
      console.error('Error creating calendar account:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateCalendarAccount = async (accountId, updateData) => {
    try {
      const updatedAccount = await calendarService.updateCalendarAccount(accountId, updateData)
      const index = calendarAccounts.value.findIndex(account => account.id === accountId)
      if (index !== -1) {
        calendarAccounts.value[index] = updatedAccount
      }
      return updatedAccount
    } catch (err) {
      error.value = 'Failed to update calendar account'
      console.error('Error updating calendar account:', err)
      throw err
    }
  }

  const deleteCalendarAccount = async (accountId) => {
    try {
      await calendarService.deleteCalendarAccount(accountId)
      calendarAccounts.value = calendarAccounts.value.filter(account => account.id !== accountId)
      // Remove events from deleted account
      calendarEvents.value = calendarEvents.value.filter(event => 
        event.calendar_account?.id !== accountId
      )
    } catch (err) {
      error.value = 'Failed to delete calendar account'
      console.error('Error deleting calendar account:', err)
      throw err
    }
  }

  const syncCalendarAccount = async (accountId) => {
    try {
      syncingAccounts.value.add(accountId)
      const result = await calendarService.syncCalendarAccount(accountId)
      // Refresh events after sync
      await fetchCalendarEvents()
      return result
    } catch (err) {
      error.value = 'Failed to sync calendar account'
      console.error('Error syncing calendar account:', err)
      throw err
    } finally {
      syncingAccounts.value.delete(accountId)
    }
  }

  const syncAllAccounts = async () => {
    try {
      loading.value = true
      const result = await calendarService.syncAllAccounts()
      // Refresh events after sync
      await fetchCalendarEvents()
      return result
    } catch (err) {
      error.value = 'Failed to sync all calendar accounts'
      console.error('Error syncing all calendar accounts:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const createEvent = async (eventData) => {
    try {
      const event = await calendarService.createCalendarEvent(eventData)
      calendarEvents.value.push(event)
      return event
    } catch (err) {
      error.value = 'Failed to create event'
      console.error('Error creating event:', err)
      throw err
    }
  }

  const updateEvent = async (eventId, updateData) => {
    try {
      const updatedEvent = await calendarService.updateCalendarEvent(eventId, updateData)
      const index = calendarEvents.value.findIndex(event => event.id === eventId)
      if (index !== -1) {
        calendarEvents.value[index] = updatedEvent
      }
      return updatedEvent
    } catch (err) {
      error.value = 'Failed to update event'
      console.error('Error updating event:', err)
      throw err
    }
  }

  const deleteEvent = async (eventId) => {
    try {
      await calendarService.deleteCalendarEvent(eventId)
      calendarEvents.value = calendarEvents.value.filter(event => event.id !== eventId)
    } catch (err) {
      error.value = 'Failed to delete event'
      console.error('Error deleting event:', err)
      throw err
    }
  }

  const scheduleMeeting = async (meetingData) => {
    try {
      const meeting = await calendarService.scheduleMeeting(meetingData)
      calendarEvents.value.push(meeting)
      return meeting
    } catch (err) {
      error.value = 'Failed to schedule meeting'
      console.error('Error scheduling meeting:', err)
      throw err
    }
  }

  const rescheduleMeeting = async (eventId, newDateTime) => {
    try {
      const updatedMeeting = await calendarService.rescheduleMeeting(eventId, newDateTime)
      const index = calendarEvents.value.findIndex(event => event.id === eventId)
      if (index !== -1) {
        calendarEvents.value[index] = updatedMeeting
      }
      return updatedMeeting
    } catch (err) {
      error.value = 'Failed to reschedule meeting'
      console.error('Error rescheduling meeting:', err)
      throw err
    }
  }

  const cancelMeeting = async (eventId) => {
    try {
      const cancelledMeeting = await calendarService.cancelMeeting(eventId)
      const index = calendarEvents.value.findIndex(event => event.id === eventId)
      if (index !== -1) {
        calendarEvents.value[index] = cancelledMeeting
      }
      return cancelledMeeting
    } catch (err) {
      error.value = 'Failed to cancel meeting'
      console.error('Error cancelling meeting:', err)
      throw err
    }
  }

  // Navigation
  const navigateToDate = (date) => {
    currentDate.value = new Date(date)
    fetchCalendarEvents()
  }

  const navigateToToday = () => {
    currentDate.value = new Date()
    fetchCalendarEvents()
  }

  const navigatePrevious = () => {
    const newDate = new Date(currentDate.value)
    if (currentView.value === 'month') {
      newDate.setMonth(newDate.getMonth() - 1)
    } else if (currentView.value === 'week') {
      newDate.setDate(newDate.getDate() - 7)
    } else if (currentView.value === 'day') {
      newDate.setDate(newDate.getDate() - 1)
    }
    currentDate.value = newDate
    fetchCalendarEvents()
  }

  const navigateNext = () => {
    const newDate = new Date(currentDate.value)
    if (currentView.value === 'month') {
      newDate.setMonth(newDate.getMonth() + 1)
    } else if (currentView.value === 'week') {
      newDate.setDate(newDate.getDate() + 7)
    } else if (currentView.value === 'day') {
      newDate.setDate(newDate.getDate() + 1)
    }
    currentDate.value = newDate
    fetchCalendarEvents()
  }

  const changeView = (view) => {
    currentView.value = view
    settings.value.defaultView = view
    fetchCalendarEvents()
  }

  // Filters
  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      accounts: [],
      statuses: ['confirmed', 'tentative'],
      privacy: ['public', 'private'],
      showTasks: true,
      showMeetings: true,
      showEvents: true,
      clients: [],
      leads: []
    }
  }

  // Utility functions
  const getViewStartDate = (date, view) => {
    const d = new Date(date)
    if (view === 'month') {
      d.setDate(1)
      d.setDate(d.getDate() - d.getDay() + settings.value.weekStartsOn)
    } else if (view === 'week') {
      d.setDate(d.getDate() - d.getDay() + settings.value.weekStartsOn)
    }
    d.setHours(0, 0, 0, 0)
    return d
  }

  const getViewEndDate = (date, view) => {
    const d = new Date(date)
    if (view === 'month') {
      d.setMonth(d.getMonth() + 1, 0) // Last day of current month
      d.setDate(d.getDate() + (6 - d.getDay()) + (7 - settings.value.weekStartsOn))
    } else if (view === 'week') {
      d.setDate(d.getDate() - d.getDay() + settings.value.weekStartsOn + 6)
    }
    d.setHours(23, 59, 59, 999)
    return d
  }

  // Task integration methods
  const createTaskFromCalendar = async (taskData) => {
    try {
      const taskStore = useTaskStore()
      const task = await taskStore.createTask(taskData)
      
      // Refresh combined events to include the new task
      await fetchCalendarEvents()
      
      return task
    } catch (err) {
      error.value = 'Failed to create task from calendar'
      console.error('Error creating task from calendar:', err)
      throw err
    }
  }

  const updateTaskFromCalendar = async (taskId, updateData) => {
    try {
      const taskStore = useTaskStore()
      const updatedTask = await taskStore.updateTask(taskId, updateData)
      
      // Refresh combined events to reflect the updated task
      await fetchCalendarEvents()
      
      return updatedTask
    } catch (err) {
      error.value = 'Failed to update task from calendar'
      console.error('Error updating task from calendar:', err)
      throw err
    }
  }

  const formatEventForFullCalendar = (event) => {
    return {
      id: event.id,
      title: event.title,
      start: event.start_datetime,
      end: event.end_datetime,
      allDay: event.all_day,
      backgroundColor: getEventColor(event),
      borderColor: getEventColor(event),
      textColor: getTextColor(event),
      extendedProps: {
        ...event,
        isEditable: calendarService.isEventEditable(event)
      }
    }
  }

  const getEventColor = (event) => {
    if (event.type === 'task') {
      switch (event.priority) {
        case 'high': return '#dc3545'
        case 'medium': return '#ffc107'
        case 'low': return '#17a2b8'
        default: return '#6c757d'
      }
    }
    return calendarService.getEventColor(event)
  }

  const getTextColor = (event) => {
    if (event.type === 'task' && event.priority === 'medium') {
      return '#212529' // Dark text for yellow background
    }
    return '#ffffff'
  }

  // Auto-sync functionality
  let syncInterval = null

  const startAutoSync = () => {
    if (settings.value.autoSync && !syncInterval) {
      syncInterval = setInterval(() => {
        if (hasCalendarAccounts.value) {
          syncAllAccounts().catch(console.error)
        }
      }, settings.value.syncInterval * 60 * 1000)
    }
  }

  const stopAutoSync = () => {
    if (syncInterval) {
      clearInterval(syncInterval)
      syncInterval = null
    }
  }

  // Watch for setting changes
  watch(() => settings.value.autoSync, (enabled) => {
    if (enabled) {
      startAutoSync()
    } else {
      stopAutoSync()
    }
  })

  watch(() => settings.value.syncInterval, () => {
    if (settings.value.autoSync) {
      stopAutoSync()
      startAutoSync()
    }
  })

  // Initialize
  const initialize = async () => {
    try {
      await Promise.all([
        fetchCalendarAccounts(),
        fetchMeetingTemplates()
      ])
      await fetchCalendarEvents()
      
      if (settings.value.autoSync) {
        startAutoSync()
      }
    } catch (err) {
      console.error('Failed to initialize calendar store:', err)
    }
  }

  // Cleanup
  const cleanup = () => {
    stopAutoSync()
  }

  return {
    // State
    calendarAccounts,
    calendarEvents,
    meetingTemplates,
    selectedAccount,
    currentDate,
    currentView,
    loading,
    error,
    syncingAccounts,
    filters,
    settings,

    // Getters
    activeAccounts,
    connectedProviders,
    hasCalendarAccounts,
    filteredEvents,
    todayEvents,
    upcomingEvents,
    eventsForCurrentView,
    combinedEvents,

    // Actions
    fetchCalendarAccounts,
    fetchCalendarEvents,
    fetchMeetingTemplates,
    createCalendarAccount,
    updateCalendarAccount,
    deleteCalendarAccount,
    syncCalendarAccount,
    syncAllAccounts,
    createEvent,
    updateEvent,
    deleteEvent,
    scheduleMeeting,
    rescheduleMeeting,
    cancelMeeting,
    navigateToDate,
    navigateToToday,
    navigatePrevious,
    navigateNext,
    changeView,
    updateFilters,
    clearFilters,
    formatEventForFullCalendar,
    initialize,
    cleanup,

    // Utilities
    startAutoSync,
    stopAutoSync,
    getViewStartDate,
    getViewEndDate,
    
    // Task integration
    createTaskFromCalendar,
    updateTaskFromCalendar
  }
})