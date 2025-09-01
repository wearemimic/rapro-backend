<template>
  <div class="calendar-view">
    <div class="calendar-view-page-header">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-header-title">Calendar</h1>
        </div>
        <div class="d-flex gap-2">
          <button
            class="btn btn-primary btn-sm"
            @click="showMeetingScheduler = true"
            :disabled="!hasCalendarAccounts"
          >
            <i class="bi-plus me-1"></i>
            Schedule Meeting
          </button>
        </div>
      </div>
    </div>

    <!-- Calendar Navigation -->
    <div class="calendar-header d-flex justify-content-between align-items-center mb-4">
      <div class="calendar-navigation d-flex align-items-center">
        <button
          class="btn btn-outline-primary btn-sm me-2"
          @click="navigatePrevious"
          :disabled="loading"
        >
          <i class="bi-chevron-left"></i>
        </button>
        <h4 class="mb-0 me-2">
          {{ formatHeaderDate(currentDate, currentView) }}
        </h4>
        <button
          class="btn btn-outline-primary btn-sm me-3"
          @click="navigateNext"
          :disabled="loading"
        >
          <i class="bi-chevron-right"></i>
        </button>
        <button
          class="btn btn-outline-secondary btn-sm me-3"
          @click="goToToday"
          :disabled="loading"
        >
          Today
        </button>
      </div>
      
      <div class="calendar-controls d-flex align-items-center">
        <!-- Sync Status -->
        <div v-if="syncingAccounts.size > 0" class="me-3">
          <span class="text-muted small">
            <i class="bi-arrow-repeat fa-spin me-1"></i>
            Syncing...
          </span>
        </div>

        <!-- View Controls -->
        <div class="btn-group btn-group-sm me-3" role="group">
          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="monthView"
            value="month"
            :checked="currentView === 'month'"
            @change="changeView('month')"
          >
          <label class="btn btn-outline-primary" for="monthView">Month</label>

          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="weekView"
            value="week"
            :checked="currentView === 'week'"
            @change="changeView('week')"
          >
          <label class="btn btn-outline-primary" for="weekView">Week</label>

          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="dayView"
            value="day"
            :checked="currentView === 'day'"
            @change="changeView('day')"
          >
          <label class="btn btn-outline-primary" for="dayView">Day</label>
        </div>

        <!-- Filter Toggle -->
        <button
          class="btn btn-outline-secondary btn-sm me-3"
          @click="showFilters = !showFilters"
        >
          <i class="bi-funnel me-1"></i>
          Filters
          <span v-if="hasActiveFilters" class="badge bg-primary ms-1">{{ activeFilterCount }}</span>
        </button>

        <!-- Settings Dropdown -->
        <div class="dropdown">
          <button
            class="btn btn-outline-secondary btn-sm dropdown-toggle"
            type="button"
            data-bs-toggle="dropdown"
          >
            <i class="fas fa-cog"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li>
              <button class="dropdown-item" @click="showCalendarSetup = true">
                <i class="fas fa-link me-2"></i>
                Calendar Accounts
              </button>
            </li>
            <li>
              <button class="dropdown-item" @click="syncAllAccounts" :disabled="loading">
                <i class="fas fa-sync me-2"></i>
                Sync All Calendars
              </button>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <button class="dropdown-item" @click="showSettings = true">
                <i class="fas fa-cog me-2"></i>
                Settings
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Filters Panel -->
    <div v-show="showFilters" class="calendar-filters mb-4">
      <CalendarFilter
        :filters="filters"
        :calendar-accounts="calendarAccounts"
        @update:filters="updateFilters"
        @clear-filters="clearFilters"
      />
    </div>

    <!-- Calendar Setup Notice -->
    <div v-if="!hasCalendarAccounts && !loading" class="alert alert-info">
      <div class="d-flex align-items-center">
        <i class="fas fa-info-circle me-2"></i>
        <div class="flex-fill">
          <strong>Connect Your Calendar</strong>
          <p class="mb-0">Connect Google Calendar or Outlook to sync your meetings and appointments.</p>
        </div>
        <button class="btn btn-primary btn-sm" @click="showCalendarSetup = true">
          Connect Calendar
        </button>
      </div>
    </div>

    <!-- Calendar Content -->
    <div class="calendar-content">
      <!-- Today's Events Summary -->
      <div v-if="todayEvents.length > 0 && currentView !== 'day'" class="today-events mb-4">
        <div class="card">
          <div class="card-header d-flex align-items-center">
            <i class="fas fa-calendar-day me-2"></i>
            <h6 class="mb-0">Today's Events</h6>
            <span class="badge bg-primary ms-auto">{{ todayEvents.length }}</span>
          </div>
          <div class="card-body">
            <div class="row">
              <div
                v-for="event in todayEvents.slice(0, 3)"
                :key="event.id"
                class="col-md-4 mb-2"
              >
                <div class="event-summary" @click="openEventDetail(event)">
                  <div class="event-time">{{ formatTime(event.start_datetime) }}</div>
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-client" v-if="event.client">
                    <i class="fas fa-user me-1"></i>
                    {{ event.client.name }}
                  </div>
                </div>
              </div>
              <div v-if="todayEvents.length > 3" class="col-md-4">
                <div class="more-events text-muted">
                  +{{ todayEvents.length - 3 }} more events
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month View -->
      <div v-if="currentView === 'month'" class="calendar-month">
        <div class="calendar-grid-header">
          <div
            v-for="day in daysOfWeek"
            :key="day"
            class="calendar-day-header"
          >
            {{ day }}
          </div>
        </div>

        <div class="calendar-grid">
          <div
            v-for="date in monthDates"
            :key="date.toISOString()"
            class="calendar-day"
            :class="getDayClass(date)"
            @click="selectDate(date)"
          >
            <div class="calendar-day-number">
              {{ date.getDate() }}
            </div>
            
            <div class="calendar-events">
              <div
                v-for="event in getEventsForDate(date).slice(0, 3)"
                :key="event.id"
                class="calendar-event"
                :class="getEventClass(event)"
                @click.stop="openEventDetail(event)"
              >
                <div class="event-title">{{ truncateText(event.title, 20) }}</div>
                <div class="event-time" v-if="!event.all_day">
                  {{ formatTime(event.start_datetime) }}
                </div>
              </div>
              
              <div
                v-if="getEventsForDate(date).length > 3"
                class="more-events"
                @click.stop="showDayDetail(date)"
              >
                +{{ getEventsForDate(date).length - 3 }} more
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Week View -->
      <div v-else-if="currentView === 'week'" class="calendar-week">
        <!-- All Day Events -->
        <div class="week-all-day" v-if="weekAllDayEvents.length > 0">
          <div class="all-day-label">All Day</div>
          <div class="all-day-events">
            <div
              v-for="event in weekAllDayEvents"
              :key="event.id"
              class="all-day-event"
              :class="getEventClass(event)"
              @click="openEventDetail(event)"
            >
              {{ event.title }}
            </div>
          </div>
        </div>

        <!-- Week Header -->
        <div class="week-header d-flex">
          <div class="time-column"></div>
          <div
            v-for="date in weekDates"
            :key="date.toISOString()"
            class="week-day-header"
            :class="{ 'today': isToday(date) }"
            @click="selectDate(date)"
          >
            <div class="day-name">{{ formatDayName(date) }}</div>
            <div class="day-number">{{ date.getDate() }}</div>
          </div>
        </div>

        <!-- Week Grid -->
        <div class="week-grid">
          <div
            v-for="hour in displayHours"
            :key="hour"
            class="week-hour-row d-flex"
          >
            <div class="time-column">
              {{ formatHour(hour) }}
            </div>
            <div
              v-for="date in weekDates"
              :key="`${date.toISOString()}-${hour}`"
              class="week-hour-cell"
              @click="createEventAtTime(date, hour)"
            >
              <div
                v-for="event in getEventsForDateTime(date, hour)"
                :key="event.id"
                class="calendar-event timed-event"
                :class="getEventClass(event)"
                :style="getEventStyle(event)"
                @click.stop="openEventDetail(event)"
              >
                <div class="event-title">{{ event.title }}</div>
                <div class="event-time">{{ formatTimeRange(event) }}</div>
                <div class="event-client" v-if="event.client">
                  {{ event.client.name }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'day'" class="calendar-day-view">
        <!-- Day Header -->
        <div class="day-view-header">
          <h5 class="mb-0">{{ formatFullDate(currentDate) }}</h5>
          <div class="day-summary">
            <span class="badge bg-primary me-2">{{ dayEvents.length }} events</span>
            <span v-if="dayTasks.length > 0" class="badge bg-info">{{ dayTasks.length }} tasks</span>
          </div>
        </div>

        <!-- All Day Events -->
        <div v-if="dayAllDayEvents.length > 0" class="all-day-tasks mt-3">
          <h6>All Day Events</h6>
          <div class="d-flex flex-wrap gap-2">
            <div
              v-for="event in dayAllDayEvents"
              :key="event.id"
              class="calendar-event all-day"
              :class="getEventClass(event)"
              @click="openEventDetail(event)"
            >
              <div class="event-title">{{ event.title }}</div>
              <div class="event-client" v-if="event.client">
                {{ event.client.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- Day Content Split Layout -->
        <div class="day-content-split">
          <!-- Calendar Section (2/3 width) -->
          <div class="calendar-section">
            <div class="day-view-content">
              <div
                v-for="hour in displayHours"
                :key="hour"
                class="day-hour-row d-flex"
              >
                <div class="time-column">
                  {{ formatHour(hour) }}
                </div>
                <div
                  class="day-hour-cell"
                  @click="createEventAtTime(currentDate, hour)"
                >
                  <div
                    v-for="event in getEventsForDateTime(currentDate, hour)"
                    :key="event.id"
                    class="calendar-event timed-event"
                    :class="getEventClass(event)"
                    :style="getEventStyle(event)"
                    @click.stop="openEventDetail(event)"
                  >
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-time">{{ formatTimeRange(event) }}</div>
                    <div class="event-details">
                      <div v-if="event.client" class="event-client">
                        <i class="fas fa-user me-1"></i>
                        {{ event.client.name }}
                      </div>
                      <div v-if="event.location" class="event-location">
                        <i class="fas fa-map-marker-alt me-1"></i>
                        {{ event.location }}
                      </div>
                      <div v-if="event.meeting_url" class="event-meeting">
                        <i class="fas fa-video me-1"></i>
                        {{ event.meeting_type || 'Video Meeting' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tasks Section (1/3 width) -->
          <div class="tasks-section">
            <div class="tasks-header">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">
                  <i class="fas fa-tasks me-2"></i>
                  Tasks Due Today
                  <span class="badge bg-secondary ms-2">{{ dayTasks.length }}</span>
                </h6>
                <div class="task-filter-dropdown">
                  <select 
                    v-model="taskFilter" 
                    class="form-select form-select-sm"
                    style="width: auto; min-width: 100px;"
                  >
                    <option value="open">Open</option>
                    <option value="all">Show All</option>
                    <option value="complete">Complete</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div class="tasks-content">
              <!-- Tasks List -->
              <div v-if="dayTasks.length > 0" class="task-list">
                <div
                  v-for="task in dayTasks"
                  :key="task.id"
                  class="task-item"
                  :class="getTaskClass(task)"
                  @click="openEventDetail(task)"
                >
                  <div class="task-header">
                    <div class="task-priority" :class="`priority-${task.priority}`">
                      <i class="fas fa-circle"></i>
                    </div>
                    <div class="task-title">{{ task.title }}</div>
                    <div class="task-status">
                      <span v-if="task.status === 'completed'" class="badge bg-success">
                        <i class="fas fa-check"></i>
                      </span>
                      <span v-else-if="task.priority === 'high'" class="badge bg-danger">High</span>
                      <span v-else-if="task.priority === 'medium'" class="badge bg-warning">Medium</span>
                      <span v-else class="badge bg-info">Low</span>
                    </div>
                  </div>
                  
                  <div class="task-details">
                    <div v-if="task.client" class="task-client">
                      <i class="fas fa-user me-1"></i>
                      {{ task.client.name }}
                    </div>
                    <div v-if="task.due_datetime" class="task-due">
                      <i class="fas fa-clock me-1"></i>
                      Due: {{ formatTime(task.due_datetime) }}
                    </div>
                    <div v-if="task.description" class="task-description">
                      {{ truncateText(task.description, 100) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- No Tasks State -->
              <div v-else class="no-tasks text-center py-4">
                <i 
                  :class="{
                    'fas fa-check-circle fa-2x text-success mb-3': taskFilter === 'open',
                    'fas fa-tasks fa-2x text-muted mb-3': taskFilter === 'all',
                    'fas fa-clipboard-check fa-2x text-info mb-3': taskFilter === 'complete'
                  }"
                ></i>
                <p class="text-muted mb-2">
                  {{ getNoTasksMessage() }}
                </p>
                <p class="text-muted small" v-if="taskFilter === 'open'">
                  Great work staying on top of your tasks!
                </p>
              </div>

              <!-- Add Task Button -->
              <div class="add-task-section mt-3">
                <button
                  class="btn btn-outline-primary btn-sm w-100"
                  @click="createTaskForDay"
                >
                  <i class="fas fa-plus me-1"></i>
                  Add Task for Today
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && combinedEvents.length === 0" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading calendar events...</p>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && combinedEvents.length === 0" class="text-center py-5">
        <i class="fas fa-calendar-alt fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">No events scheduled</h5>
        <p class="text-muted mb-3">Schedule your first meeting or connect a calendar to see events.</p>
        <button
          v-if="hasCalendarAccounts"
          class="btn btn-primary"
          @click="showMeetingScheduler = true"
        >
          <i class="fas fa-plus me-1"></i>
          Schedule Meeting
        </button>
        <button
          v-else
          class="btn btn-primary"
          @click="showCalendarSetup = true"
        >
          <i class="fas fa-link me-1"></i>
          Connect Calendar
        </button>
      </div>
    </div>

    <!-- Modals -->
    <!-- Meeting Scheduler Modal -->
    <MeetingScheduler
      v-if="showMeetingScheduler"
      :initial-date="selectedDate"
      @close="showMeetingScheduler = false"
      @meeting-scheduled="onMeetingScheduled"
    />

    <!-- Calendar Setup Modal -->
    <CalendarSetup
      v-if="showCalendarSetup"
      @close="showCalendarSetup = false"
      @account-connected="onAccountConnected"
    />

    <!-- Meeting Detail Modal -->
    <MeetingDetail
      v-if="showMeetingDetail && selectedEvent"
      :event="selectedEvent"
      @close="closeMeetingDetail"
      @event-updated="onEventUpdated"
      @event-deleted="onEventDeleted"
    />

    <!-- Settings Modal -->
    <div
      v-if="showSettings"
      class="modal fade show"
      style="display: block"
      @click.self="showSettings = false"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Calendar Settings</h5>
            <button
              type="button"
              class="btn-close"
              @click="showSettings = false"
            ></button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label class="form-label">Default View</label>
                <select class="form-select" v-model="settings.defaultView">
                  <option value="month">Month</option>
                  <option value="week">Week</option>
                  <option value="day">Day</option>
                </select>
              </div>

              <div class="row mb-3">
                <div class="col-6">
                  <label class="form-label">Start Hour</label>
                  <select class="form-select" v-model="settings.startHour">
                    <option v-for="hour in 24" :key="hour-1" :value="hour-1">
                      {{ formatHour(hour-1) }}
                    </option>
                  </select>
                </div>
                <div class="col-6">
                  <label class="form-label">End Hour</label>
                  <select class="form-select" v-model="settings.endHour">
                    <option v-for="hour in 24" :key="hour-1" :value="hour-1">
                      {{ formatHour(hour-1) }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="settings.showWeekends"
                    id="showWeekends"
                  >
                  <label class="form-check-label" for="showWeekends">
                    Show Weekends
                  </label>
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="settings.autoSync"
                    id="autoSync"
                  >
                  <label class="form-check-label" for="autoSync">
                    Auto-sync calendars
                  </label>
                </div>
              </div>

              <div v-if="settings.autoSync" class="mb-3">
                <label class="form-label">Sync Interval (minutes)</label>
                <select class="form-select" v-model="settings.syncInterval">
                  <option value="5">5 minutes</option>
                  <option value="15">15 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="60">1 hour</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showSettings = false"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="saveSettings"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div
      v-if="showSettings"
      class="modal-backdrop fade show"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useCalendarStore } from '@/stores/calendarStore'
import { useTaskStore } from '@/stores/taskStore'
import { storeToRefs } from 'pinia'
import CalendarFilter from './CalendarFilter.vue'
import MeetingScheduler from './MeetingScheduler.vue'
import CalendarSetup from './CalendarSetup.vue'
import MeetingDetail from './MeetingDetail.vue'

// Stores
const calendarStore = useCalendarStore()
const taskStore = useTaskStore()
const {
  calendarAccounts,
  currentDate,
  currentView,
  loading,
  error,
  syncingAccounts,
  filters,
  settings,
  hasCalendarAccounts,
  combinedEvents,
  todayEvents,
  upcomingEvents
} = storeToRefs(calendarStore)

// Local state
const showFilters = ref(false)
const showMeetingScheduler = ref(false)
const showCalendarSetup = ref(false)
const showMeetingDetail = ref(false)
const showSettings = ref(false)
const selectedDate = ref(new Date())
const selectedEvent = ref(null)
const taskFilter = ref('open') // 'all', 'complete', 'open'

// Calendar constants
const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Computed properties
const displayHours = computed(() => {
  const hours = []
  for (let i = settings.value.startHour; i <= settings.value.endHour; i++) {
    hours.push(i)
  }
  return hours
})

const monthDates = computed(() => {
  const dates = []
  const firstDay = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1)
  const lastDay = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay() + settings.value.weekStartsOn)

  const endDate = new Date(lastDay)
  endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()) + (7 - settings.value.weekStartsOn))

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    dates.push(new Date(d))
  }

  return dates
})

const weekDates = computed(() => {
  const dates = []
  const startOfWeek = new Date(currentDate.value)
  startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay() + settings.value.weekStartsOn)

  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek)
    date.setDate(date.getDate() + i)
    dates.push(date)
  }

  return dates
})

const weekAllDayEvents = computed(() => {
  return combinedEvents.value.filter(event => 
    event.all_day && isEventInWeek(event, weekDates.value)
  )
})

const dayEvents = computed(() => {
  return getEventsForDate(currentDate.value)
})

const dayAllDayEvents = computed(() => {
  return dayEvents.value.filter(event => event.all_day)
})

const dayTasks = computed(() => {
  let tasks = dayEvents.value.filter(event => event.type === 'task')
  
  // Apply task filter
  if (taskFilter.value === 'complete') {
    tasks = tasks.filter(task => task.status === 'completed')
  } else if (taskFilter.value === 'open') {
    tasks = tasks.filter(task => task.status !== 'completed')
  }
  // 'all' shows all tasks without filtering
  
  return tasks
})

const hasActiveFilters = computed(() => {
  return filters.value.accounts.length > 0 ||
    filters.value.clients.length > 0 ||
    filters.value.leads.length > 0 ||
    !filters.value.showTasks ||
    !filters.value.showMeetings ||
    !filters.value.showEvents
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.accounts.length > 0) count++
  if (filters.value.clients.length > 0) count++
  if (filters.value.leads.length > 0) count++
  if (!filters.value.showTasks) count++
  if (!filters.value.showMeetings) count++
  if (!filters.value.showEvents) count++
  return count
})

// Methods
const navigatePrevious = () => {
  calendarStore.navigatePrevious()
}

const navigateNext = () => {
  calendarStore.navigateNext()
}

const goToToday = () => {
  calendarStore.navigateToToday()
}

const changeView = (view) => {
  calendarStore.changeView(view)
}

const selectDate = (date) => {
  selectedDate.value = new Date(date)
  if (currentView.value === 'month') {
    calendarStore.navigateToDate(date)
    calendarStore.changeView('day')
  }
}

const showDayDetail = (date) => {
  calendarStore.navigateToDate(date)
  calendarStore.changeView('day')
}

const getEventsForDate = (date) => {
  return combinedEvents.value.filter(event => {
    const eventDate = new Date(event.start_datetime)
    return eventDate.toDateString() === date.toDateString()
  })
}

const getEventsForDateTime = (date, hour) => {
  return combinedEvents.value.filter(event => {
    if (event.all_day) return false
    const eventDate = new Date(event.start_datetime)
    const eventHour = eventDate.getHours()
    return eventDate.toDateString() === date.toDateString() && eventHour === hour
  })
}

const isEventInWeek = (event, weekDates) => {
  const eventDate = new Date(event.start_datetime)
  const startDate = weekDates[0]
  const endDate = new Date(weekDates[6])
  endDate.setDate(endDate.getDate() + 1)
  return eventDate >= startDate && eventDate < endDate
}

const createEventAtTime = (date, hour) => {
  selectedDate.value = new Date(date)
  selectedDate.value.setHours(hour, 0, 0, 0)
  showMeetingScheduler.value = true
}

const openEventDetail = (event) => {
  selectedEvent.value = event
  showMeetingDetail.value = true
}

const closeMeetingDetail = () => {
  showMeetingDetail.value = false
  selectedEvent.value = null
}

const onMeetingScheduled = (meeting) => {
  showMeetingScheduler.value = false
  // Refresh events
  calendarStore.fetchCalendarEvents()
}

const onAccountConnected = (account) => {
  showCalendarSetup.value = false
  // Refresh accounts and events
  calendarStore.fetchCalendarAccounts()
  calendarStore.fetchCalendarEvents()
}

const onEventUpdated = (updatedEvent) => {
  // Event is already updated in the store by the MeetingDetail component
}

const onEventDeleted = (deletedEventId) => {
  closeMeetingDetail()
  // Event is already removed from the store by the MeetingDetail component
}

const updateFilters = (newFilters) => {
  calendarStore.updateFilters(newFilters)
}

const clearFilters = () => {
  calendarStore.clearFilters()
}

const syncAllAccounts = async () => {
  try {
    await calendarStore.syncAllAccounts()
  } catch (error) {
    console.error('Failed to sync accounts:', error)
  }
}

const saveSettings = () => {
  showSettings.value = false
  // Settings are automatically saved via reactive binding
}

const createTaskForDay = () => {
  selectedDate.value = new Date(currentDate.value)
  selectedDate.value.setHours(9, 0, 0, 0) // Default to 9 AM
  showMeetingScheduler.value = true
}

const getTaskClass = (task) => {
  const classes = ['task-item']
  
  if (task.status === 'completed') {
    classes.push('completed')
  }
  
  if (task.priority) {
    classes.push(`priority-${task.priority}`)
  }
  
  return classes.join(' ')
}

const getNoTasksMessage = () => {
  switch (taskFilter.value) {
    case 'complete':
      return 'No completed tasks today'
    case 'all':
      return 'No tasks due today'
    case 'open':
    default:
      return 'No open tasks due today'
  }
}

// Utility methods
const getDayClass = (date) => {
  const classes = []
  
  if (date.getMonth() !== currentDate.value.getMonth()) {
    classes.push('other-month')
  }
  
  if (isToday(date)) {
    classes.push('today')
  }
  
  if (date.toDateString() === selectedDate.value.toDateString()) {
    classes.push('selected')
  }
  
  return classes
}

const getEventClass = (event) => {
  const classes = []
  
  if (event.type === 'task') {
    classes.push('task-event', `priority-${event.priority}`)
    if (event.status === 'completed') classes.push('completed')
  } else {
    classes.push('calendar-meeting')
    if (event.status === 'cancelled') classes.push('cancelled')
    if (event.status === 'tentative') classes.push('tentative')
  }
  
  if (event.client) classes.push('has-client')
  if (event.meeting_url) classes.push('has-video')
  
  return classes
}

const getEventStyle = (event) => {
  if (event.type === 'task') return {}
  
  const start = new Date(event.start_datetime)
  const end = new Date(event.end_datetime)
  const durationMinutes = (end - start) / (1000 * 60)
  
  return {
    height: `${Math.max(durationMinutes / 15 * 20, 20)}px`,
    minHeight: '20px'
  }
}

const isToday = (date) => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const formatHeaderDate = (date, view) => {
  if (view === 'month') {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  } else if (view === 'week') {
    const weekDates = calendarStore.getViewStartDate(date, 'week')
    const weekEnd = calendarStore.getViewEndDate(date, 'week')
    return `${weekDates.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  } else {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }
}

const formatFullDate = (date) => {
  return date.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatDayName = (date) => {
  return date.toLocaleDateString('en-US', { weekday: 'short' })
}

const formatHour = (hour) => {
  const period = hour >= 12 ? 'PM' : 'AM'
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
  return `${displayHour}:00 ${period}`
}

const formatTime = (datetime) => {
  const date = new Date(datetime)
  return date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true
  })
}

const formatTimeRange = (event) => {
  const start = formatTime(event.start_datetime)
  const end = formatTime(event.end_datetime)
  return `${start} - ${end}`
}

const truncateText = (text, length) => {
  return text && text.length > length ? text.substring(0, length) + '...' : text
}

// Lifecycle
onMounted(async () => {
  await calendarStore.initialize()
  // Load tasks so they appear in the calendar
  await taskStore.fetchTasks()
})

onUnmounted(() => {
  calendarStore.cleanup()
})

// Watch for date changes to refresh events and tasks
watch(
  () => [currentDate.value, currentView.value],
  () => {
    calendarStore.fetchCalendarEvents()
    // Refresh tasks when view changes to ensure all tasks are loaded
    taskStore.fetchTasks()
  },
  { deep: true }
)

// Watch for task changes to refresh the calendar
watch(
  () => taskStore.tasks,
  () => {
    // Calendar will automatically update through combinedEvents computed property
  },
  { deep: true }
)
</script>

<style scoped>
.calendar-view {
  padding: 1.5rem;
  min-height: 100vh;
}

.calendar-view-page-header {
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

/* Using default Bootstrap card styles */

.card-header-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0;
}

.calendar-header {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.calendar-filters {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.today-events .event-summary {
  padding: 0.5rem;
  border-left: 4px solid #007bff;
  background: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.today-events .event-summary:hover {
  background: #e9ecef;
}

.event-time {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.event-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.event-client {
  font-size: 0.75rem;
  color: #6c757d;
}

/* Calendar Grid */
.calendar-grid-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: #dee2e6;
  border-radius: 0.375rem 0.375rem 0 0;
}

.calendar-day-header {
  background-color: #f8f9fa;
  padding: 0.75rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background-color: #dee2e6;
  border-radius: 0 0 0.375rem 0.375rem;
}

.calendar-day {
  background-color: white;
  min-height: 120px;
  padding: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.calendar-day:hover {
  background-color: #f8f9fa;
}

.calendar-day.other-month {
  background-color: #f8f9fa;
  color: #6c757d;
}

.calendar-day.today {
  background-color: #e3f2fd;
}

.calendar-day.selected {
  background-color: #bbdefb;
}

.calendar-day-number {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.calendar-events {
  max-height: 80px;
  overflow: hidden;
}

.calendar-event {
  padding: 0.125rem 0.25rem;
  margin-bottom: 0.125rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  color: white;
}

.calendar-event:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
}

/* Event Types */
.calendar-event.calendar-meeting {
  background-color: #007bff;
}

.calendar-event.task-event {
  background-color: #6c757d;
}

.calendar-event.task-event.priority-high {
  background-color: #dc3545;
}

.calendar-event.task-event.priority-medium {
  background-color: #ffc107;
  color: #212529;
}

.calendar-event.task-event.priority-low {
  background-color: #17a2b8;
}

.calendar-event.has-client {
  border-left: 3px solid #28a745;
}

.calendar-event.has-video::after {
  content: '🎥';
  float: right;
  font-size: 0.7em;
}

.calendar-event.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.calendar-event.cancelled {
  opacity: 0.6;
  background-color: #dc3545;
}

.calendar-event.tentative {
  opacity: 0.8;
  border: 1px dashed rgba(255, 255, 255, 0.5);
}

.more-events {
  font-size: 0.7rem;
  color: #6c757d;
  font-style: italic;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
}

.more-events:hover {
  background-color: #e9ecef;
  border-radius: 0.25rem;
}

/* Week and Day Views */
.week-header,
.week-hour-row,
.day-hour-row {
  border-bottom: 1px solid #dee2e6;
}

.week-day-header,
.week-hour-cell,
.day-hour-cell {
  flex: 1;
  padding: 0.5rem;
  border-right: 1px solid #dee2e6;
  min-height: 60px;
  position: relative;
}

.week-day-header.today {
  background-color: #e3f2fd;
}

.week-day-header {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.week-day-header:hover {
  background-color: #f8f9fa;
}

.time-column {
  width: 80px;
  padding: 0.5rem;
  border-right: 2px solid #dee2e6;
  background-color: #f8f9fa;
  font-size: 0.875rem;
  text-align: center;
  color: #6c757d;
}

.day-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.day-number {
  font-size: 1.25rem;
  font-weight: 700;
}

.week-all-day,
.all-day-tasks {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem 0;
}

.all-day-label {
  width: 80px;
  padding: 0.5rem;
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
}

.all-day-events,
.all-day-tasks .d-flex {
  flex: 1;
}

.all-day-event,
.calendar-event.all-day {
  background-color: #6c757d;
  margin-bottom: 0.25rem;
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  display: inline-flex;
  align-items: center;
  margin-right: 0.5rem;
}

.timed-event {
  position: absolute;
  left: 0.25rem;
  right: 0.25rem;
  z-index: 1;
  font-size: 0.7rem;
  padding: 0.125rem 0.25rem;
}

.day-view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.day-summary .badge {
  font-size: 0.75rem;
}

.event-details {
  font-size: 0.65rem;
  margin-top: 0.25rem;
  opacity: 0.9;
}

.event-details > div {
  margin-bottom: 0.125rem;
}

/* Day View Split Layout */
.day-content-split {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  min-height: 600px;
}

.calendar-section {
  flex: 2;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  overflow: auto;
}

.tasks-section {
  flex: 1;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  padding: 1rem;
  max-height: 600px;
  overflow: auto;
}

.tasks-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.75rem;
}

.tasks-header h6 {
  color: #495057;
  font-weight: 600;
}

.tasks-content {
  padding-top: 0.75rem;
}

.task-list {
  max-height: 450px;
  overflow-y: auto;
}

.task-item {
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8f9fa;
}

.task-item:hover {
  border-color: #007bff;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 123, 255, 0.15);
  transform: translateY(-1px);
}

.task-item.completed {
  opacity: 0.6;
  background: #e9ecef;
}

.task-item.completed .task-title {
  text-decoration: line-through;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.task-priority {
  font-size: 0.75rem;
}

.task-priority.priority-high {
  color: #dc3545;
}

.task-priority.priority-medium {
  color: #ffc107;
}

.task-priority.priority-low {
  color: #17a2b8;
}

.task-title {
  flex: 1;
  font-weight: 500;
  font-size: 0.875rem;
  color: #212529;
}

.task-status .badge {
  font-size: 0.7rem;
}

.task-details {
  padding-left: 1rem;
  font-size: 0.75rem;
  color: #6c757d;
}

.task-details > div {
  margin-bottom: 0.25rem;
}

.task-client {
  color: #28a745;
}

.task-due {
  color: #fd7e14;
}

.task-description {
  font-style: italic;
  line-height: 1.3;
}

.no-tasks {
  color: #6c757d;
}

.add-task-section {
  border-top: 1px solid #e9ecef;
  padding-top: 0.75rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .calendar-header {
    flex-direction: column;
    gap: 1rem;
  }

  .calendar-navigation,
  .calendar-controls {
    justify-content: center;
  }

  .calendar-day {
    min-height: 80px;
    padding: 0.25rem;
  }
  
  .calendar-day-number {
    font-size: 0.875rem;
  }
  
  .calendar-event {
    font-size: 0.7rem;
    padding: 0.125rem;
  }
  
  .week-hour-cell,
  .day-hour-cell {
    min-height: 40px;
    padding: 0.25rem;
  }
  
  .time-column {
    width: 60px;
    font-size: 0.75rem;
  }

  .today-events .row > div {
    margin-bottom: 1rem;
  }

  /* Mobile Day View Split */
  .day-content-split {
    flex-direction: column;
    gap: 0.75rem;
    min-height: auto;
  }

  .calendar-section {
    flex: none;
    min-height: 400px;
  }

  .tasks-section {
    flex: none;
    max-height: 300px;
  }

  .task-item {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .task-header {
    flex-wrap: wrap;
    gap: 0.25rem;
  }

  .task-title {
    font-size: 0.8rem;
  }
}

@media (max-width: 576px) {
  .calendar-grid {
    gap: 0;
  }
  
  .calendar-day {
    min-height: 60px;
    padding: 0.125rem;
  }
  
  .calendar-events {
    max-height: 40px;
  }
  
  .calendar-event {
    font-size: 0.65rem;
    margin-bottom: 0.0625rem;
  }
}
</style>