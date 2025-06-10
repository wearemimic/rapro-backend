<template>
    <div class="row" style="margin-top:50px;">
        <div class="col-lg-4" style="margin-top:-30px;">  
            <div class="container mt-5" v-if="client">
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Basic Info</h5>
                        <h2>{{ client.first_name }} {{ client.last_name }}</h2>
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
                

                <div class="mb-3">
                <router-link :to="`/clients/${client.id}/edit`" class="btn btn-secondary">Edit</router-link>
                <button @click="deleteClient" class="btn btn-danger" style="margin-left:10px;margin-right:10px;">Delete</button>
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
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h4 class="card-header-title">Scenarios</h4>
                        <div v-if="client && client.scenarios && client.scenarios.length">
                            <router-link :to="`/clients/${client.id}/scenarios/new`" class="btn btn-primary">Add Scenario</router-link>
                        </div>
                    </div>

                    <div class="card-body">
                      <div v-if="client && client.scenarios && client.scenarios.length">
                        <table class="table">
                          <thead class="thead-light">
                            <tr>
                              <th scope="col">#</th>
                              <th scope="col">Name</th>
                              <th scope="col">Last Updated</th>
                              <th scope="col">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(scenario, index) in client.scenarios" :key="scenario.id">
                              <th scope="row">{{ index + 1 }}</th>
                              <td>{{ scenario.name }}</td>
                              <td>{{ scenario.updated_at }}</td>
                              <td>
                                <router-link :to="{ 
                                  name: 'ScenarioDetail',
                                  params: { clientId: client.id, scenarioid: scenario.id },
                                  state: { scenarios: client.scenarios }
                                  }"
                                  class="btn btn-sm btn-outline-primary">
                                  View
                                </router-link>
                                <!-- <router-link :to="`/clients/${client.id}/scenarios/detail/${scenario.id}`" class="btn btn-sm btn-outline-primary">View</router-link>-->
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else>
                        <div class="text-center d-flex flex-column align-items-center" style="margin:50px;">
                          <img src="/assets/svg/illustrations/oc-project-development.svg" alt="No Scenarios" class="mb-3" style="max-width: 50%; height: auto;"/>
                          <router-link :to="`/clients/${client.id}/scenarios/new`" class="btn btn-primary mt-3">Create Your First Scenario!</router-link>
                        </div>
                      </div>
                    </div>
                  </div>
            </div>
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
        if (!confirm('Are you sure you want to archive this client?')) return;
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };
            const payload = {
                status: 'archived',
                first_name: this.client.first_name,
                last_name: this.client.last_name,
                email: this.client.email,
                birthdate: this.client.birthdate,
                gender: this.client.gender,
                tax_status: this.client.tax_status,
                notes: this.client.notes || '',
                spouse: this.client.spouse && this.client.tax_status !== 'Single' ? {
                  first_name: this.client.spouse.first_name,
                  last_name: this.client.spouse.last_name,
                  birthdate: this.client.spouse.birthdate,
                  gender: this.client.spouse.gender,
                } : null
            };

            console.log("Payload being sent:", payload);
            if (payload.spouse === null) {
                delete payload.spouse;
            }

            await axios.patch(`http://localhost:8000/api/clients/${this.client.id}/edit/`, payload, { headers });
            this.$router.push('/clients');
        } catch (error) {
            console.error('Failed to archive client:', error.response?.data || error.message);
        }
    }
  }
};
</script>

<style scoped>
.card-title {
  font-weight: bold;
}

.card-header {
  padding-top: 0.5rem; /* Reduce padding to decrease whitespace */
  padding-bottom: 0.5rem;
}
</style>