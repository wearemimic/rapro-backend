<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ isEditing ? 'Edit Task' : 'Create New Task' }}
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('close')"
          ></button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <!-- Task Title -->
            <div class="mb-3">
              <label for="title" class="form-label required">Task Title</label>
              <input
                type="text"
                id="title"
                class="form-control"
                :class="{ 'is-invalid': errors.title }"
                v-model="form.title"
                placeholder="Enter task title..."
                required
              >
              <div v-if="errors.title" class="invalid-feedback">
                {{ errors.title }}
              </div>
            </div>

            <!-- Task Description -->
            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <textarea
                id="description"
                class="form-control"
                :class="{ 'is-invalid': errors.description }"
                v-model="form.description"
                placeholder="Enter task description..."
                rows="4"
              ></textarea>
              <div v-if="errors.description" class="invalid-feedback">
                {{ errors.description }}
              </div>
            </div>

            <div class="row">
              <!-- Status -->
              <div class="col-md-6 mb-3">
                <label for="status" class="form-label required">Status</label>
                <select
                  id="status"
                  class="form-select"
                  :class="{ 'is-invalid': errors.status }"
                  v-model="form.status"
                  required
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <div v-if="errors.status" class="invalid-feedback">
                  {{ errors.status }}
                </div>
              </div>

              <!-- Priority -->
              <div class="col-md-6 mb-3">
                <label for="priority" class="form-label required">Priority</label>
                <select
                  id="priority"
                  class="form-select"
                  :class="{ 'is-invalid': errors.priority }"
                  v-model="form.priority"
                  required
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <div v-if="errors.priority" class="invalid-feedback">
                  {{ errors.priority }}
                </div>
              </div>
            </div>

            <div class="row">
              <!-- Task Type -->
              <div class="col-md-6 mb-3">
                <label for="taskType" class="form-label">Task Type</label>
                <select
                  id="taskType"
                  class="form-select"
                  :class="{ 'is-invalid': errors.task_type }"
                  v-model="form.task_type"
                >
                  <option value="">Select task type</option>
                  <option value="follow_up">Follow Up</option>
                  <option value="meeting">Meeting</option>
                  <option value="call">Phone Call</option>
                  <option value="email">Email</option>
                  <option value="review">Review</option>
                  <option value="analysis">Analysis</option>
                  <option value="administrative">Administrative</option>
                  <option value="prospecting">Prospecting</option>
                  <option value="client_service">Client Service</option>
                </select>
                <div v-if="errors.task_type" class="invalid-feedback">
                  {{ errors.task_type }}
                </div>
              </div>

              <!-- Due Date -->
              <div class="col-md-6 mb-3">
                <label for="dueDate" class="form-label">Due Date</label>
                <input
                  type="date"
                  id="dueDate"
                  class="form-control"
                  :class="{ 'is-invalid': errors.due_date }"
                  v-model="form.due_date"
                  :min="today"
                >
                <div v-if="errors.due_date" class="invalid-feedback">
                  {{ errors.due_date }}
                </div>
              </div>
            </div>

            <!-- Contact Assignment -->
            <div class="mb-3">
              <label for="client" class="form-label">Associated Contact</label>
              <select
                id="client"
                class="form-select"
                :class="{ 'is-invalid': errors.client }"
                v-model="form.client"
                :disabled="clientsLoading"
              >
                <option value="">{{ clientsLoading ? 'Loading contacts...' : 'No contact' }}</option>
                <option
                  v-for="client in clients"
                  :key="client.id"
                  :value="client.id"
                >
                  {{ client.first_name }} {{ client.last_name }}
                </option>
              </select>
              <div v-if="errors.client" class="invalid-feedback">
                {{ errors.client }}
              </div>
            </div>

            <!-- Assigned To -->
            <div class="mb-3">
              <label for="assignedTo" class="form-label">Assigned To</label>
              <select
                id="assignedTo"
                class="form-select"
                :class="{ 'is-invalid': errors.assigned_to }"
                v-model="form.assigned_to"
              >
                <option value="">Unassigned</option>
                <option
                  v-for="user in users"
                  :key="user.id"
                  :value="user.id"
                >
                  {{ user.first_name }} {{ user.last_name }} ({{ user.email }})
                </option>
              </select>
              <div v-if="errors.assigned_to" class="invalid-feedback">
                {{ errors.assigned_to }}
              </div>
            </div>

            <!-- Reminder Settings -->
            <div class="mb-3">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="setReminder"
                  v-model="form.set_reminder"
                >
                <label class="form-check-label" for="setReminder">
                  Set Reminder
                </label>
              </div>
              
              <div v-if="form.set_reminder" class="mt-2">
                <label for="reminderTime" class="form-label">Reminder Time</label>
                <select
                  id="reminderTime"
                  class="form-select"
                  v-model="form.reminder_minutes"
                >
                  <option value="15">15 minutes before</option>
                  <option value="30">30 minutes before</option>
                  <option value="60">1 hour before</option>
                  <option value="1440">1 day before</option>
                  <option value="10080">1 week before</option>
                </select>
              </div>
            </div>

            <!-- Tags -->
            <div class="mb-3">
              <label for="tags" class="form-label">Tags</label>
              <input
                type="text"
                id="tags"
                class="form-control"
                v-model="tagInput"
                @keydown.enter.prevent="addTag"
                @keydown.comma.prevent="addTag"
                placeholder="Add tags (press Enter or comma to add)..."
              >
              
              <div v-if="form.tags.length > 0" class="mt-2">
                <span
                  v-for="(tag, index) in form.tags"
                  :key="index"
                  class="badge bg-secondary me-1 mb-1"
                >
                  {{ tag }}
                  <button
                    type="button"
                    class="btn-close btn-close-white btn-sm ms-1"
                    @click="removeTag(index)"
                  ></button>
                </span>
              </div>
            </div>

            <!-- Notes -->
            <div class="mb-3">
              <label for="notes" class="form-label">Additional Notes</label>
              <textarea
                id="notes"
                class="form-control"
                v-model="form.notes"
                placeholder="Any additional notes or context..."
                rows="3"
              ></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="$emit('close')"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEditing ? 'Update Task' : 'Create Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTaskStore } from '@/stores/taskStore.js'
import { useClientStore } from '@/stores/clientStore.js'
import { useAuthStore } from '@/stores/auth.js'

const props = defineProps({
  task: {
    type: Object,
    default: null
  },
  show: {
    type: Boolean,
    default: false
  },
  preselectedClientId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['close', 'task-saved'])

const taskStore = useTaskStore()
const clientStore = useClientStore()
const authStore = useAuthStore()

const form = ref({
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  task_type: '',
  due_date: '',
  client: '',
  lead: '',
  assigned_to: '',
  set_reminder: false,
  reminder_minutes: 60,
  tags: [],
  notes: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const tagInput = ref('')
const clients = ref([])
const clientsLoading = ref(false)
const users = ref([])

const isEditing = computed(() => !!props.task)
const today = computed(() => new Date().toISOString().split('T')[0])

const initializeForm = () => {
  if (props.task) {
    form.value = {
      title: props.task.title || '',
      description: props.task.description || '',
      status: props.task.status || 'pending',
      priority: props.task.priority || 'medium',
      task_type: props.task.task_type || '',
      due_date: props.task.due_date ? props.task.due_date.split('T')[0] : '',
      client: props.task.client || '',
      assigned_to: props.task.assigned_to || '',
      set_reminder: !!props.task.reminder_minutes,
      reminder_minutes: props.task.reminder_minutes || 60,
      tags: props.task.tags || [],
      notes: props.task.notes || ''
    }
  } else {
    form.value = {
      title: '',
      description: '',
      status: 'pending',
      priority: 'medium',
      task_type: '',
      due_date: today.value,
      client: props.preselectedClientId || '',
      assigned_to: authStore.user?.id || '',
      set_reminder: false,
      reminder_minutes: 60,
      tags: [],
      notes: ''
    }
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.value.title.trim()) {
    errors.value.title = 'Task title is required'
  }

  if (!form.value.status) {
    errors.value.status = 'Status is required'
  }

  if (!form.value.priority) {
    errors.value.priority = 'Priority is required'
  }

  if (form.value.due_date && new Date(form.value.due_date) < new Date(today.value)) {
    errors.value.due_date = 'Due date cannot be in the past'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const taskData = {
      ...form.value,
      client: form.value.client || null,
      assigned_to: form.value.assigned_to || authStore.user?.id,
      reminder_minutes: form.value.set_reminder ? form.value.reminder_minutes : null
    }

    console.log('Submitting task data:', taskData)
    console.log('Current user:', authStore.user)

    if (isEditing.value) {
      const updatedTask = await taskStore.updateTask(props.task.id, taskData)
      console.log('Task updated:', updatedTask)
    } else {
      const createdTask = await taskStore.createTask(taskData)
      console.log('Task created:', createdTask)
    }

    console.log('Emitting task-saved event')
    emit('task-saved')
  } catch (error) {
    console.error('Failed to save task:', error)
    if (error.response?.data) {
      errors.value = error.response.data
    }
  } finally {
    isSubmitting.value = false
  }
}

const addTag = () => {
  const tag = tagInput.value.trim().replace(',', '')
  if (tag && !form.value.tags.includes(tag)) {
    form.value.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index) => {
  form.value.tags.splice(index, 1)
}

const fetchData = async () => {
  try {
    // Fetch clients
    clientsLoading.value = true
    console.log('Fetching clients...', { clientStore })
    
    if (clientStore?.fetchClients) {
      await clientStore.fetchClients()
      clients.value = clientStore.clients || []
      console.log('Clients fetched:', clients.value)
    } else {
      console.warn('clientStore.fetchClients not available')
    }

    // Fetch users for assignment
    // This would need to be implemented based on your user management
    users.value = []
  } catch (error) {
    console.error('Failed to fetch form data:', error)
    clients.value = []
  } finally {
    clientsLoading.value = false
  }
}

watch(() => props.show, (newValue) => {
  if (newValue) {
    initializeForm()
    fetchData()
  }
})

onMounted(() => {
  if (props.show) {
    initializeForm()
    fetchData()
  }
})
</script>

<style scoped>
.required::after {
  content: ' *';
  color: red;
}

.modal {
  display: block;
}

.badge .btn-close {
  font-size: 0.6em;
  padding: 0;
  margin-left: 0.25rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.form-check {
  margin-bottom: 0.5rem;
}

.invalid-feedback {
  display: block;
}
</style>