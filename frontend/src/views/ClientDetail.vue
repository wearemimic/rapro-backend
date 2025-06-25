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
               
                

                <div class="mb-3">
                <router-link :to="`/clients/${client.id}/edit`" class="btn btn-secondary">Edit</router-link>
                <button @click="deleteClient" class="btn btn-danger" style="margin-left:10px;margin-right:10px;">Delete</button>
                </div>

                <!-- Real Estate Card -->
                <div class="card mb-4">
                  <div class="card-body">
                    <h5 class="card-title">Real Estate</h5>
                    <div v-if="realEstateList.length === 0" class="mb-2">
                      <p>Add Real Estate</p>
                    </div>
                    <div v-else>
                      <div v-for="(estate, idx) in realEstateList" :key="estate.id" class="mb-3 p-2 border rounded">
                        <div class="d-flex align-items-center">
                          <img v-if="estate.image_url || estate.image" :src="estate.image_url || estate.image" alt="Home" style="width:80px;height:80px;object-fit:cover;margin-right:15px;cursor:pointer;" @click="openImageModal(estate.image_url || estate.image)"/>
                          <div>
                            <div><strong>Address:</strong> {{ estate.address }}, {{ estate.city }}, {{ estate.state }} {{ estate.zip }}</div>
                            <div><strong>Value:</strong> ${{ estate.value }}</div>
                          </div>
                          <button class="btn btn-sm btn-primary ms-3" @click="editRealEstate(estate, idx)">Edit</button>
                          <button class="btn btn-sm btn-danger ms-2" @click="deleteRealEstate(estate, idx)">Delete</button>
                        </div>
                      </div>
                    </div>
                    <button class="btn btn-primary mt-2" @click="showRealEstateModal = true">Add</button>
                  </div>
                </div>

                <!-- Real Estate Modal -->
                <div v-if="showRealEstateModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.5);">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Add Real Estate</h5>
                        <button type="button" class="btn-close" @click="closeRealEstateModal"></button>
                      </div>
                      <div class="modal-body">
                        <form @submit.prevent="addRealEstate">
                          <div class="mb-3">
                            <label for="addressInput" class="form-label">Street Address</label>
                            <input v-model="realEstateAddress" type="text" class="form-control" id="addressInput" required />
                          </div>
                          <div class="mb-3">
                            <label for="cityInput" class="form-label">City</label>
                            <input v-model="realEstateCity" type="text" class="form-control" id="cityInput" required />
                          </div>
                          <div class="mb-3">
                            <label for="stateInput" class="form-label">State</label>
                            <input v-model="realEstateState" type="text" class="form-control" id="stateInput" required />
                          </div>
                          <div class="mb-3">
                            <label for="zipInput" class="form-label">Zip Code</label>
                            <input v-model="realEstateZip" type="text" class="form-control" id="zipInput" required />
                          </div>
                          <div class="mb-3">
                            <label for="valueInput" class="form-label">Estimated Value</label>
                            <input v-model="realEstateValue" type="number" class="form-control" id="valueInput" required min="0" />
                          </div>
                          <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="closeRealEstateModal">Cancel</button>
                            <button type="submit" class="btn btn-primary">{{ editingRealEstateId !== null ? 'Save' : 'Add' }}</button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Image Modal for Large View -->
                <div v-if="showImageModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.7);">
                  <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content" style="background:transparent; border:none; box-shadow:none;">
                      <div class="modal-body text-center p-0">
                        <img :src="selectedImage" alt="Large Home" style="max-width:90vw; max-height:80vh; border-radius:8px;" />
                      </div>
                      <div class="modal-footer justify-content-center" style="background:transparent; border:none;">
                        <button type="button" class="btn btn-light" @click="closeImageModal">Close</button>
                      </div>
                    </div>
                  </div>
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
      // Real estate state
      realEstateList: [],
      showRealEstateModal: false,
      realEstateAddress: '',
      realEstateCity: '',
      realEstateState: '',
      realEstateZip: '',
      realEstateValue: '',
      showImageModal: false,
      selectedImage: '',
      editingRealEstateIdx: null,
      editingRealEstateId: null,
    };
  },
  async created() {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const id = this.$route.params.id;
      const response = await axios.get(`http://localhost:8000/api/clients/${id}/`, { headers });
      this.client = response.data;
      // Fetch real estate list for this client
      const realEstateRes = await axios.get(`http://localhost:8000/api/clients/${id}/realestate/`, { headers });
      this.realEstateList = realEstateRes.data;
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
    },
    closeRealEstateModal() {
      this.showRealEstateModal = false;
      this.realEstateAddress = '';
      this.realEstateCity = '';
      this.realEstateState = '';
      this.realEstateZip = '';
      this.realEstateValue = '';
      this.editingRealEstateIdx = null;
      this.editingRealEstateId = null;
    },
    editRealEstate(estate, idx) {
      this.realEstateAddress = estate.address;
      this.realEstateCity = estate.city;
      this.realEstateState = estate.state;
      this.realEstateZip = estate.zip;
      this.realEstateValue = estate.value;
      this.editingRealEstateIdx = idx;
      this.editingRealEstateId = estate.id;
      this.showRealEstateModal = true;
    },
    async addRealEstate() {
      const address = this.realEstateAddress;
      const city = this.realEstateCity;
      const state = this.realEstateState;
      const zip = this.realEstateZip;
      const value = this.realEstateValue;
      // Insert your Google Street View API key below
      const GOOGLE_API_KEY = 'AIzaSyCsvoEjQW68CWwwMlCcbUfZIHTSPKW54Bc';
      // Generate Street View image URL
      const fullAddress = `${address}, ${city}, ${state} ${zip}`;
      const image = `https://maps.googleapis.com/maps/api/streetview?size=400x400&location=${encodeURIComponent(fullAddress)}&key=${GOOGLE_API_KEY}`;
      if (this.editingRealEstateId !== null) {
        // Edit mode: update backend and local list
        try {
          const token = localStorage.getItem('token');
          const headers = { Authorization: `Bearer ${token}` };
          const payload = { address, city, state, zip, value: value.toString(), image_url: image };
          // Defensive: remove client field if present
          if ('client' in payload) delete payload.client;
          const res = await axios.put(`http://localhost:8000/api/realestate/${this.editingRealEstateId}/`, payload, { headers });
          this.$set(this.realEstateList, this.editingRealEstateIdx, res.data);
        } catch (err) {
          console.error('Failed to update real estate:', err.response?.data || err.message, err.response);
        }
      } else {
        // Add mode: save to backend
        try {
          const token = localStorage.getItem('token');
          const headers = { Authorization: `Bearer ${token}` };
          const clientId = this.client.id;
          const payload = { address, city, state, zip, value: value.toString(), image_url: image };
          // Defensive: remove client field if present
          if ('client' in payload) delete payload.client;
          const res = await axios.post(`http://localhost:8000/api/clients/${clientId}/realestate/`, payload, { headers });
          this.realEstateList.push(res.data);
        } catch (err) {
          console.error('Failed to save real estate:', err.response?.data || err.message, err.response);
        }
      }
      this.showRealEstateModal = false;
      this.realEstateAddress = '';
      this.realEstateCity = '';
      this.realEstateState = '';
      this.realEstateZip = '';
      this.realEstateValue = '';
      this.editingRealEstateIdx = null;
      this.editingRealEstateId = null;
    },
    openImageModal(imageUrl) {
      this.selectedImage = imageUrl;
      this.showImageModal = true;
    },
    closeImageModal() {
      this.showImageModal = false;
      this.selectedImage = '';
    },
    async deleteRealEstate(estate, idx) {
      if (!confirm('Are you sure you want to delete this real estate entry?')) return;
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        await axios.delete(`http://localhost:8000/api/realestate/${estate.id}/`, { headers });
        this.realEstateList.splice(idx, 1);
      } catch (err) {
        console.error('Failed to delete real estate:', err.response?.data || err.message);
      }
    },
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