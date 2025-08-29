<template>
  <div class="task-calendar">
    <!-- Calendar Header -->
    <div class="calendar-header d-flex justify-content-between align-items-center mb-4">
      <div class="calendar-navigation d-flex align-items-center">
        <button
          class="btn btn-outline-primary btn-sm me-2"
          @click="navigateMonth(-1)"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        <h5 class="mb-0 me-2">
          {{ formatMonthYear(currentDate) }}
        </h5>
        <button
          class="btn btn-outline-primary btn-sm me-3"
          @click="navigateMonth(1)"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
        <button
          class="btn btn-outline-secondary btn-sm"
          @click="goToToday"
        >
          Today
        </button>
      </div>
      
      <div class="calendar-view-controls">
        <div class="btn-group btn-group-sm" role="group">
          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="monthView"
            value="month"
            :checked="viewType === 'month'"
            @change="$emit('view-change', 'month')"
          >
          <label class="btn btn-outline-primary" for="monthView">Month</label>

          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="weekView"
            value="week"
            :checked="viewType === 'week'"
            @change="$emit('view-change', 'week')"
          >
          <label class="btn btn-outline-primary" for="weekView">Week</label>

          <input
            type="radio"
            class="btn-check"
            name="viewType"
            id="dayView"
            value="day"
            :checked="viewType === 'day'"
            @change="$emit('view-change', 'day')"
          >
          <label class="btn btn-outline-primary" for="dayView">Day</label>
        </div>
      </div>
    </div>

    <!-- Month View -->
    <div v-if="viewType === 'month'" class="calendar-month">
      <!-- Days of Week Header -->
      <div class="calendar-grid-header">
        <div
          v-for="day in daysOfWeek"
          :key="day"
          class="calendar-day-header"
        >
          {{ day }}
        </div>
      </div>

      <!-- Calendar Grid -->
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
          
          <div class="calendar-tasks">
            <div
              v-for="task in getTasksForDate(date)"
              :key="task.id"
              class="calendar-task"
              :class="getTaskClass(task)"
              @click.stop="$emit('task-click', task)"
            >
              <div class="task-title">{{ truncateText(task.title, 20) }}</div>
              <div class="task-time" v-if="task.due_time">
                {{ formatTime(task.due_time) }}
              </div>
            </div>
            
            <div
              v-if="getTasksForDate(date).length > 2"
              class="more-tasks"
            >
              +{{ getTasksForDate(date).length - 2 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Week View -->
    <div v-else-if="viewType === 'week'" class="calendar-week">
      <div class="week-header d-flex">
        <div class="time-column"></div>
        <div
          v-for="date in weekDates"
          :key="date.toISOString()"
          class="week-day-header"
          :class="{ 'today': isToday(date) }"
        >
          <div class="day-name">{{ formatDayName(date) }}</div>
          <div class="day-number">{{ date.getDate() }}</div>
        </div>
      </div>

      <div class="week-grid">
        <div
          v-for="hour in hours"
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
            @click="createTaskAtTime(date, hour)"
          >
            <div
              v-for="task in getTasksForDateTime(date, hour)"
              :key="task.id"
              class="calendar-task"
              :class="getTaskClass(task)"
              @click.stop="$emit('task-click', task)"
            >
              <div class="task-title">{{ task.title }}</div>
              <div class="task-time">{{ formatTime(task.due_time || '09:00') }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Day View -->
    <div v-else-if="viewType === 'day'" class="calendar-day-view">
      <div class="day-view-header">
        <h6 class="mb-0">{{ formatFullDate(currentDate) }}</h6>
      </div>

      <div class="day-view-content">
        <div
          v-for="hour in hours"
          :key="hour"
          class="day-hour-row d-flex"
        >
          <div class="time-column">
            {{ formatHour(hour) }}
          </div>
          <div
            class="day-hour-cell"
            @click="createTaskAtTime(currentDate, hour)"
          >
            <div
              v-for="task in getTasksForDateTime(currentDate, hour)"
              :key="task.id"
              class="calendar-task"
              :class="getTaskClass(task)"
              @click.stop="$emit('task-click', task)"
            >
              <div class="task-title">{{ task.title }}</div>
              <div class="task-time">{{ formatTime(task.due_time || '09:00') }}</div>
              <div class="task-priority">{{ task.priority }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- All Day Tasks -->
      <div v-if="getAllDayTasksForDate(currentDate).length > 0" class="all-day-tasks mt-3">
        <h6>All Day Tasks</h6>
        <div class="d-flex flex-wrap gap-2">
          <div
            v-for="task in getAllDayTasksForDate(currentDate)"
            :key="task.id"
            class="calendar-task all-day"
            :class="getTaskClass(task)"
            @click="$emit('task-click', task)"
          >
            <div class="task-title">{{ task.title }}</div>
            <span class="badge badge-sm ms-1" :class="getPriorityBadgeClass(task.priority)">
              {{ task.priority }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && tasks.length === 0" class="text-center py-5">
      <i class="fas fa-calendar-alt fa-3x text-muted mb-3"></i>
      <h5 class="text-muted">No tasks scheduled</h5>
      <p class="text-muted">Tasks with due dates will appear on the calendar.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  currentDate: {
    type: Date,
    default: () => new Date()
  },
  viewType: {
    type: String,
    default: 'month'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['task-click', 'task-update', 'date-change', 'view-change'])

const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const hours = Array.from({ length: 24 }, (_, i) => i)

const monthDates = computed(() => {
  const dates = []
  const firstDay = new Date(props.currentDate.getFullYear(), props.currentDate.getMonth(), 1)
  const lastDay = new Date(props.currentDate.getFullYear(), props.currentDate.getMonth() + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())

  const endDate = new Date(lastDay)
  endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()))

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    dates.push(new Date(d))
  }

  return dates
})

const weekDates = computed(() => {
  const dates = []
  const startOfWeek = new Date(props.currentDate)
  startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay())

  for (let i = 0; i < 7; i++) {
    const date = new Date(startOfWeek)
    date.setDate(date.getDate() + i)
    dates.push(date)
  }

  return dates
})

const navigateMonth = (direction) => {
  const newDate = new Date(props.currentDate)
  newDate.setMonth(newDate.getMonth() + direction)
  emit('date-change', newDate)
}

const goToToday = () => {
  emit('date-change', new Date())
}

const selectDate = (date) => {
  emit('date-change', date)
}

const getTasksForDate = (date) => {
  return props.tasks.filter(task => {
    if (!task.due_date) return false
    const taskDate = new Date(task.due_date)
    return taskDate.toDateString() === date.toDateString()
  }).slice(0, 3) // Limit to 3 tasks for month view
}

const getTasksForDateTime = (date, hour) => {
  return props.tasks.filter(task => {
    if (!task.due_date) return false
    const taskDate = new Date(task.due_date)
    const taskHour = task.due_time ? parseInt(task.due_time.split(':')[0]) : 9
    return taskDate.toDateString() === date.toDateString() && taskHour === hour
  })
}

const getAllDayTasksForDate = (date) => {
  return props.tasks.filter(task => {
    if (!task.due_date) return false
    const taskDate = new Date(task.due_date)
    return taskDate.toDateString() === date.toDateString() && !task.due_time
  })
}

const createTaskAtTime = (date, hour) => {
  // This would emit an event to create a new task at the specific date/time
  const taskData = {
    due_date: date.toISOString().split('T')[0],
    due_time: `${hour.toString().padStart(2, '0')}:00`
  }
  // emit('create-task', taskData)
}

const getDayClass = (date) => {
  const classes = []
  
  if (date.getMonth() !== props.currentDate.getMonth()) {
    classes.push('other-month')
  }
  
  if (isToday(date)) {
    classes.push('today')
  }
  
  if (date.toDateString() === props.currentDate.toDateString()) {
    classes.push('selected')
  }
  
  return classes
}

const getTaskClass = (task) => {
  const classes = [`priority-${task.priority}`]
  
  if (task.is_overdue) {
    classes.push('overdue')
  }
  
  if (task.status === 'completed') {
    classes.push('completed')
  }
  
  return classes
}

const getPriorityBadgeClass = (priority) => {
  switch (priority) {
    case 'high': return 'bg-danger'
    case 'medium': return 'bg-warning text-dark'
    case 'low': return 'bg-info'
    default: return 'bg-secondary'
  }
}

const isToday = (date) => {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const formatMonthYear = (date) => {
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
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

const formatTime = (time) => {
  const [hour, minute] = time.split(':')
  const period = parseInt(hour) >= 12 ? 'PM' : 'AM'
  const displayHour = parseInt(hour) === 0 ? 12 : parseInt(hour) > 12 ? parseInt(hour) - 12 : parseInt(hour)
  return `${displayHour}:${minute} ${period}`
}

const truncateText = (text, length) => {
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>

<style scoped>
.task-calendar {
  height: 100%;
}

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

.calendar-tasks {
  max-height: 80px;
  overflow: hidden;
}

.calendar-task {
  background-color: #007bff;
  color: white;
  padding: 0.125rem 0.25rem;
  margin-bottom: 0.125rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.calendar-task:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1);
}

.calendar-task.priority-high {
  background-color: #dc3545;
}

.calendar-task.priority-medium {
  background-color: #ffc107;
  color: #212529;
}

.calendar-task.priority-low {
  background-color: #17a2b8;
}

.calendar-task.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.calendar-task.overdue {
  background-color: #dc3545;
  animation: pulse 2s infinite;
}

.more-tasks {
  font-size: 0.7rem;
  color: #6c757d;
  font-style: italic;
}

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
}

.week-day-header.today {
  background-color: #e3f2fd;
}

.time-column {
  width: 80px;
  padding: 0.5rem;
  border-right: 2px solid #dee2e6;
  background-color: #f8f9fa;
  font-size: 0.875rem;
  text-align: center;
}

.day-name {
  font-weight: 600;
  font-size: 0.875rem;
}

.day-number {
  font-size: 1.25rem;
  font-weight: 700;
}

.all-day-tasks {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.calendar-task.all-day {
  background-color: #6c757d;
  margin-bottom: 0;
  padding: 0.375rem 0.75rem;
  border-radius: 1rem;
  display: inline-flex;
  align-items: center;
}

.task-title {
  font-weight: 500;
}

.task-time {
  font-size: 0.7em;
  opacity: 0.9;
}

.task-priority {
  font-size: 0.6em;
  text-transform: uppercase;
  font-weight: 700;
  opacity: 0.8;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

@media (max-width: 768px) {
  .calendar-day {
    min-height: 80px;
  }
  
  .calendar-day-number {
    font-size: 0.875rem;
  }
  
  .calendar-task {
    font-size: 0.7rem;
    padding: 0.125rem;
  }
  
  .week-header,
  .week-hour-cell,
  .day-hour-cell {
    min-height: 40px;
  }
  
  .time-column {
    width: 60px;
    font-size: 0.75rem;
  }
}
</style>