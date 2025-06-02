<template>
  <div class="container mt-5" v-if="client">
    <h2>Client Details: {{ client.first_name }} {{ client.last_name }}</h2>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Basic Info</h5>
        <p><strong>Email:</strong> {{ client.email }}</p>
        <p><strong>Birthdate:</strong> {{ client.birthdate }}</p>
        <p><strong>Gender:</strong> {{ client.gender }}</p>
        <p><strong>Tax Status:</strong> {{ client.tax_status }}</p>
        <p><strong>Status:</strong> {{ client.status }}</p>
      </div>
    </div>

    <div v-if="client.spouse" class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Spouse Info</h5>
        <p><strong>Name:</strong> {{ client.spouse.first_name }} {{ client.spouse.last_name }}</p>
        <p><strong>Birthdate:</strong> {{ client.spouse.birthdate }}</p>
        <p><strong>Gender:</strong> {{ client.spouse.gender }}</p>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Notes</h5>
        <div v-html="client.notes"></div>
      </div>
    </div>
    <div class="card mb-4">
        <div class="card-body">
            <h5 class="card-title">CRM Integration</h5>
            <p><i class="bi bi-check-circle text-success"></i> Connected to Wealthbox</p>
            <!-- or -->
            <p><i class="bi bi-x-circle text-muted"></i> Client not in CRM</p>
        </div>
    </div>
    <div class="card mb-4" v-if="client.scenarios && client.scenarios.length">
        <div class="card-body">
            <h5 class="card-title">Scenarios</h5>
            <ul>
            <li v-for="scenario in client.scenarios" :key="scenario.id">
                {{ scenario.name }} - Last Updated: {{ scenario.updated_at }}
            </li>
            </ul>
            <button class="btn btn-outline-primary mt-2" disabled>Compare Scenarios (Coming Soon)</button>
        </div>
    </div>

    <div class="mb-3">
      <router-link :to="`/clients/${client.id}/edit`" class="btn btn-secondary">Edit</router-link>
      <button @click="deleteClient" class="btn btn-danger">Delete</button>
      <router-link :to="`/clients/${client.id}/scenarios/new`" class="btn btn-primary">Add Scenario</router-link>
    </div>
  </div>
 
  
  <div v-else class="text-center mt-5">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ClientDetail',
  data() {
    return {
      client: null,
    };
  },
  async created() {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const id = this.$route.params.id;
      const response = await axios.get(`http://localhost:8000/api/clients/${id}/`, { headers });
      this.client = response.data;
    } catch (error) {
      console.error('Error loading client:', error);
      this.$router.push('/clients');
    }
  },
  methods: {
    async deleteClient() {
      if (!confirm('Are you sure you want to delete this client?')) return;
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        await axios.delete(`http://localhost:8000/api/clients/${this.client.id}/`, { headers });
        this.$router.push('/clients');
      } catch (error) {
        console.error('Failed to delete client:', error);
      }
    }
  }
};
</script>

<style scoped>
.card-title {
  font-weight: bold;
}
</style>