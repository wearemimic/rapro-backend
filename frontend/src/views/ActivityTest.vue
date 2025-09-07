<template>
  <div class="container mt-4">
    <h1>ACTIVITY DATABASE TEST PAGE</h1>
    
    <div class="card bg-warning mb-3">
      <div class="card-body">
        <button class="btn btn-danger btn-lg" @click="testDirectAPI">
          CLICK TO LOAD ALL ACTIVITIES
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger">
      <h3>ERROR:</h3>
      <pre>{{ error }}</pre>
    </div>

    <div v-if="loading" class="alert alert-info">
      LOADING...
    </div>

    <div class="card">
      <div class="card-header bg-primary text-white">
        <h3>RAW DATA FROM /api/activities/ ({{ activities.length }} items)</h3>
      </div>
      <div class="card-body">
        <pre style="background: black; color: lime; padding: 20px; max-height: 600px; overflow-y: auto;">{{ JSON.stringify(activities, null, 2) }}</pre>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-header bg-success text-white">
        <h3>ACTIVITY TABLE</h3>
      </div>
      <div class="card-body p-0">
        <table class="table table-bordered table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Description</th>
              <th>Client</th>
              <th>Created</th>
              <th>Metadata</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="act in activities" :key="act.id">
              <td>{{ act.id }}</td>
              <td>{{ act.activity_type }}</td>
              <td>{{ act.description }}</td>
              <td>{{ act.client_name || 'N/A' }}</td>
              <td>{{ act.created_at }}</td>
              <td><pre>{{ JSON.stringify(act.metadata, null, 2) }}</pre></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const activities = ref([])
const loading = ref(false)
const error = ref(null)

const testDirectAPI = async () => {
  loading.value = true
  error.value = null
  activities.value = []
  
  try {
    const token = localStorage.getItem('access_token')
    console.log('Using token:', token)
    
    const response = await axios.get('/api/activities/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    console.log('Response:', response)
    activities.value = response.data
    
  } catch (err) {
    console.error('Error:', err)
    error.value = err.message + '\n' + JSON.stringify(err.response?.data, null, 2)
  } finally {
    loading.value = false
  }
}
</script>