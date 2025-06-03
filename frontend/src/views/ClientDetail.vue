<template>
    <main id="content" role="main" class="main">
    <!-- Content -->
        <div class="content container-fluid">
            <div class="row justify-content-lg-center">
                <h2>Client Details: {{ client.first_name }} {{ client.last_name }}</h2>
                <div class="col-lg-12">
                    <div class="row">
                        <div class="col-lg-4">  
                            <div class="container mt-5" v-if="client">
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
                        </div>
                        <div class="col-lg-8">
                            <div class="card mb-4">
                                <div class="card-body">
                                    <div class="card-header">
                                        <h4 class="card-header-title">Scenarios</h4>
                                    </div>
                                    <!-- End Header -->

                                    <!-- Body -->
                                    <div class="card-body">
                                        <!-- Table -->
                                        <table class="table">
                                            <thead class="thead-light">
                                                <tr>
                                                <th scope="col">#</th>
                                                <th scope="col">First</th>
                                                <th scope="col">Last</th>
                                                <th scope="col">Handle</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                <th scope="row">1</th>
                                                <td>Mark</td>
                                                <td>Otto</td>
                                                <td>@mdo</td>
                                                </tr>
                                                <tr>
                                                <th scope="row">2</th>
                                                <td>Jacob</td>
                                                <td>Thornton</td>
                                                <td>@fat</td>
                                                </tr>
                                                <tr>
                                                <th scope="row">3</th>
                                                <td>Larry</td>
                                                <td>the Bird</td>
                                                <td>@twitter</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        <!-- End Table -->
                                    </div>
                                    
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
  
  
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