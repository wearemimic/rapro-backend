<template>
    <div class="container-fluid" style="margin-top:80px;">
        <!-- Client Header Card spanning full width -->
        <div class="row mb-3" v-if="client">
            <div class="col-12">
                <div class="card">
                    <div class="card-body d-flex align-items-center justify-content-between">
                        <div class="d-flex align-items-center">
                            <h2 class="mb-0 me-3">{{ client.first_name }} {{ client.last_name }}</h2>
                            <span class="badge bg-primary">{{ client.status || 'Active' }}</span>
                        </div>
                        <div>
                            <router-link :to="`/clients/${client.id}/edit`" class="btn btn-secondary me-2">Edit</router-link>
                            <button @click="deleteClient" class="btn btn-danger">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Two column layout with reduced spacing -->
        <div class="row gx-3">
            <div class="col-lg-4">  
                <div v-if="client">
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Basic Info</h5>
                        <p><strong>Email:</strong> {{ client.email }}</p>
                        <p><strong>Birthdate:</strong> {{ client.birthdate }}</p>
                        <p><strong>Gender:</strong> {{ client.gender }}</p>
                        <p><strong>Tax Status:</strong> {{ client.tax_status }}</p>
                        <p><strong>Status:</strong> {{ client.status }}</p>
                        
                        <div v-if="client.spouse">
                            <hr class="my-3" style="border-color: #e7eaf3;">
                            <h6 class="mb-3">Spouse Information</h6>
                            <p><strong>Name:</strong> {{ client.spouse.first_name }} {{ client.spouse.last_name }}</p>
                            <p><strong>Birthdate:</strong> {{ client.spouse.birthdate }}</p>
                            <p><strong>Gender:</strong> {{ client.spouse.gender }}</p>
                        </div>
                    </div>
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

                <!-- Report Template Upload Modal -->
                <div v-if="showReportTemplateModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.5);">
                  <div class="modal-dialog">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Add PowerPoint Template</h5>
                        <button type="button" class="btn-close" @click="closeReportTemplateModal"></button>
                      </div>
                      <div class="modal-body">
                        <form @submit.prevent="uploadReportTemplate" id="reportTemplateForm" ref="reportTemplateForm">
                          <div class="mb-3">
                            <label for="templateNameInput" class="form-label">Template Name</label>
                            <input v-model="reportTemplateName" type="text" class="form-control" id="templateNameInput" required />
                          </div>
                          <div class="mb-3">
                            <label class="form-label">PowerPoint Template (.pptx)</label>
                            
                            <!-- Drag & Drop Area -->
                            <div 
                              class="drop-zone p-4 text-center border rounded"
                              :class="{ 'border-primary bg-light': isDragOver }"
                              @dragover.prevent="onDragOver"
                              @dragleave.prevent="() => isDragOver = false"
                              @drop.prevent="onFileDrop"
                              @click="triggerFileInput"
                            >
                              <div v-if="reportTemplateFile">
                                <i class="bi bi-file-earmark-ppt fs-2 text-primary"></i>
                                <p class="mb-0">{{ reportTemplateFile.name }}</p>
                                <p class="text-muted small">{{ formatFileSize(reportTemplateFile.size) }}</p>
                                <button type="button" class="btn btn-sm btn-outline-danger" @click.stop="clearSelectedFile">
                                  Remove
                                </button>
                              </div>
                              <div v-else>
                                <i class="bi bi-cloud-arrow-up fs-1 text-muted"></i>
                                <p>Drag & drop your PowerPoint file here</p>
                                <p class="text-muted">or</p>
                                <button type="button" class="btn btn-outline-primary" @click.stop="triggerFileInput">
                                  Choose File
                                </button>
                              </div>
                              
                              <!-- Hidden file input - the key is to NOT use v-model on file inputs -->
                              <input 
                                type="file" 
                                class="visually-hidden" 
                                id="templateFileInput" 
                                name="file"
                                @change="handleFileUpload" 
                                accept=".pptx" 
                                ref="fileInput"
                              />
                            </div>
                            
                            <div class="form-text mt-2">Upload a PowerPoint (.pptx) file as your report template.</div>
                          </div>
                          <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="closeReportTemplateModal">Cancel</button>
                            <button 
                              type="button" 
                              class="btn btn-primary" 
                              :disabled="isUploading"
                              @click="manualUpload">
                              <span v-if="isUploading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              {{ isUploading ? 'Uploading...' : 'Upload' }}
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Scenario Deletion Confirmation Modal -->
                <div v-if="showDeleteConfirmModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.5);">
                  <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Confirm Deletion</h5>
                        <button type="button" class="btn-close" @click="showDeleteConfirmModal = false"></button>
                      </div>
                      <div class="modal-body">
                        <p>Are you sure you want to delete the scenario "{{ scenarioToDelete?.name || 'this scenario' }}"?</p>
                        <p class="text-danger"><strong>This action cannot be undone.</strong></p>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="showDeleteConfirmModal = false">Cancel</button>
                        <button type="button" class="btn btn-danger" @click="confirmDeleteScenario">Delete Scenario</button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Slide Editor Modal -->
                <div v-if="showSlideEditorModal" class="modal fade show" tabindex="-1" style="display:block; background:rgba(0,0,0,0.5);">
                  <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Edit Template Slides</h5>
                        <button type="button" class="btn-close" @click="closeSlideEditorModal"></button>
                      </div>
                      <div class="modal-body">
                        <p class="text-muted mb-3">Drag and drop to rearrange slides. Click on a slide to remove it from the template.</p>
                        
                        <div v-if="isLoadingSlides" class="text-center py-5">
                          <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading slides...</span>
                          </div>
                          <p class="mt-3">Loading slides from your PowerPoint template...</p>
                        </div>
                        
                        <div v-else class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-xl-4 g-3" ref="slidesContainer">
                          <div v-for="(slide, index) in templateSlides" :key="index" class="col slide-item" :data-slide-index="index">
                            <div class="card h-100 position-relative slide-card" :class="{ 'border-primary': selectedSlides.includes(index) }">
                              <img :src="slide.thumbnail" class="card-img-top" alt="Slide preview" style="height: 150px; object-fit: contain;" />
                              <div class="card-body p-2">
                                <p class="card-text small text-truncate">Slide {{ index + 1 }}</p>
                              </div>
                              <div class="position-absolute top-0 end-0 p-2">
                                <button class="btn btn-sm btn-danger" @click.stop="removeSlide(index)">
                                  <i class="bi bi-x"></i>
                                </button>
                              </div>
                              <div class="position-absolute top-0 start-0 p-2">
                                <div class="form-check">
                                  <input class="form-check-input" type="checkbox" :id="'slide-check-'+index" 
                                    :checked="selectedSlides.includes(index)" 
                                    @change="toggleSlideSelection(index)">
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="closeSlideEditorModal">Cancel</button>
                        <button type="button" class="btn btn-danger" :disabled="selectedSlides.length === 0" @click="removeSelectedSlides">
                          Remove Selected
                        </button>
                        <button type="button" class="btn btn-primary" @click="saveTemplateChanges">Save Template</button>
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
                            <router-link :to="`/clients/${client.id}/scenarios/new`" class="btn btn-primary text-white">Add Scenario</router-link>
                        </div>
                    </div>

                    <div class="card-body">
                      <div v-if="client && client.scenarios && client.scenarios.length">
                        <table class="table scenarios-table">
                          <thead class="thead-light">
                            <tr>
                              <th scope="col">Name</th>
                              <th scope="col">Income vs Cost %</th>
                              <th scope="col">Medicare/IRMAA %</th>
                              <th scope="col">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(scenario, index) in client.scenarios" :key="scenario.id">
                              <td class="scenario-name">{{ scenario.name }}</td>
                              <td>
                                <div class="progress-container">
                                  <div class="progress" style="height: 25px; position: relative;">
                                    <div 
                                      class="progress-bar" 
                                      :class="getProgressBarClass(scenario.income_vs_cost_percent || 0)"
                                      role="progressbar" 
                                      :style="{ width: (scenario.income_vs_cost_percent || 0) + '%' }"
                                      :aria-valuenow="scenario.income_vs_cost_percent || 0"
                                      aria-valuemin="0" 
                                      aria-valuemax="100">
                                    </div>
                                    <div class="progress-label">
                                      <strong>{{ scenario.income_vs_cost_percent || 0 }}%</strong>
                                    </div>
                                  </div>
                                </div>
                              </td>
                              <td>
                                <div class="progress-container">
                                  <div class="progress" style="height: 25px; position: relative;">
                                    <div 
                                      class="progress-bar" 
                                      :class="getProgressBarClass(scenario.medicare_irmaa_percent || 0)"
                                      role="progressbar" 
                                      :style="{ width: (scenario.medicare_irmaa_percent || 0) + '%' }"
                                      :aria-valuenow="scenario.medicare_irmaa_percent || 0"
                                      aria-valuemin="0" 
                                      aria-valuemax="100">
                                    </div>
                                    <div class="progress-label">
                                      <strong>{{ scenario.medicare_irmaa_percent || 0 }}%</strong>
                                    </div>
                                  </div>
                                </div>
                              </td>
                              <td>
                                <div class="btn-group" role="group">
                                  <router-link :to="{ 
                                    name: 'ScenarioDetail',
                                    params: { clientId: client.id, scenarioid: scenario.id },
                                    state: { scenarios: client.scenarios }
                                    }"
                                    class="btn btn-sm btn-outline-primary">
                                    View
                                  </router-link>
                                  <button @click="showDeleteModal(scenario)" class="btn btn-sm btn-outline-danger">Delete</button>
                                </div>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else>
                        <div class="text-center d-flex flex-column align-items-center" style="margin:50px;">
                          <img src="/assets/svg/illustrations/oc-project-development.svg" alt="No Scenarios" class="mb-3" style="max-width: 50%; height: auto;"/>
                          <router-link :to="`/clients/${client ? client.id : ''}/scenarios/new`" class="btn btn-primary mt-3">Create Your First Scenario!</router-link>
                        </div>
                      </div>
                    </div>
                  </div>
            </div>

            <!-- Reports Card -->
            <!-- <div class="card mb-4">
                <div class="card-body">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h4 class="card-header-title">Reports</h4>
                        <div>
                            <button @click="openReportTemplateModal" class="btn btn-primary">Add Template</button>
                        </div>
                    </div>

                    <div class="card-body">
                      <div v-if="reportTemplates.length > 0">
                        <table class="table">
                          <thead class="thead-light">
                            <tr>
                              <th scope="col">#</th>
                              <th scope="col">Template Name</th>
                              <th scope="col">Added Date</th>
                              <th scope="col">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(template, index) in reportTemplates" :key="template.id">
                              <th scope="row">{{ index + 1 }}</th>
                              <td>{{ template.name }}</td>
                              <td>{{ template.created_at }}</td>
                              <td>
                                <button @click="editReportTemplate(template)" class="btn btn-sm btn-outline-primary me-2">Edit</button>
                                <button @click="deleteReportTemplate(template.id)" class="btn btn-sm btn-outline-danger">Delete</button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else>
                        <div class="text-center d-flex flex-column align-items-center" style="margin:50px;">
                          <img src="http://localhost:3001/assets/svg/illustrations/oc-personal-preferences.svg" alt="No Templates" class="mb-3" style="max-width: 50%; height: auto;"/>
                          <button @click="openReportTemplateModal" class="btn btn-primary mt-3">Add Your First PowerPoint Template</button>
                        </div>
                      </div>
                    </div>
                </div>
            </div> -->
        </div>
    </div>
    </div>

 
  
  
</template>

<script>
import axios from 'axios';
import Sortable from 'sortablejs';
// CircleGraph removed - using progress bars instead

export default {
  name: 'ClientDetail',
  components: { },
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
      // Report template state
      reportTemplates: [],
      showReportTemplateModal: false,
      reportTemplateName: '',
      reportTemplateFile: null,
      showSlideEditorModal: false,
      isUploading: false,
      isLoadingSlides: true,
      templateSlides: [],
      selectedSlides: [],
      currentTemplateId: null,
      sortableInstance: null,
      isDragOver: false,
      // Scenario deletion modal state
      showDeleteConfirmModal: false,
      scenarioToDelete: null,
    };
  },
  watch: {
    // Initialize sortable when slides are loaded
    templateSlides(newSlides) {
      if (newSlides.length > 0 && !this.isLoadingSlides) {
        this.$nextTick(() => {
          this.initSortable();
        });
      }
    },
    isLoadingSlides(isLoading) {
      if (!isLoading && this.templateSlides.length > 0) {
        this.$nextTick(() => {
          this.initSortable();
        });
      }
    },
    // Add watcher for modal visibility
    showReportTemplateModal(visible) {
      console.log("Report template modal visibility changed:", visible);
    }
  },
  async created() {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      const id = this.$route.params.id;
      
      if (!id) {
        console.error('Client ID is missing from route parameters');
        this.$router.push('/clients');
        return;
      }
      
      try {
        const response = await axios.get(`http://localhost:8000/api/clients/${id}/`, { headers });
        this.client = response.data;
      } catch (clientError) {
        console.error('Error loading client details:', clientError);
        this.$router.push('/clients');
        return;
      }
      
      // Fetch real estate list for this client
      try {
        const realEstateRes = await axios.get(`http://localhost:8000/api/clients/${id}/realestate/`, { headers });
        this.realEstateList = realEstateRes.data;
      } catch (realEstateError) {
        console.error('Error loading real estate:', realEstateError);
        this.realEstateList = [];
      }
      
      // Fetch report templates for this client
      try {
        console.log("Fetching report templates for client:", id);
        const reportTemplatesRes = await axios.get(`http://localhost:8000/api/clients/${id}/reporttemplates/`, { headers });
        console.log("Report templates response:", reportTemplatesRes.data);
        this.reportTemplates = reportTemplatesRes.data;
      } catch (templateError) {
        console.error('Error loading report templates:', templateError);
        this.reportTemplates = [];
      }
    } catch (error) {
      console.error('Error in created lifecycle hook:', error);
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
    async deleteReportTemplate(templateId) {
      if (!confirm('Are you sure you want to delete this template?')) return;
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        await axios.delete(`http://localhost:8000/api/reporttemplates/${templateId}/`, { headers });
        
        // Remove from local array
        this.reportTemplates = this.reportTemplates.filter(t => t.id !== templateId);
      } catch (error) {
        console.error('Error deleting template:', error);
        alert('Failed to delete template. Please try again.');
      }
    },
    editReportTemplate(template) {
      this.currentTemplateId = template.id;
      this.loadTemplateSlides(template.id);
    },
    openReportTemplateModal() {
      console.log("Opening report template modal");
      // Reset form fields first
      this.reportTemplateName = '';
      this.reportTemplateFile = null;
      this.isDragOver = false;
      
      // Reset the file input if it exists
      const fileInput = document.getElementById('templateFileInput');
      if (fileInput) {
        fileInput.value = '';
      }
      
      // Then show the modal
      this.$nextTick(() => {
        this.showReportTemplateModal = true;
        console.log("Modal visibility set to:", this.showReportTemplateModal);
      });
    },
    onDragOver(event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'copy';
      this.isDragOver = true;
    },
    
    onFileDrop(event) {
      this.isDragOver = false;
      console.log("File dropped on drop zone");
      
      const files = event.dataTransfer.files;
      
      if (files && files.length > 0) {
        const file = files[0];
        console.log("Dropped file:", file.name, file.type, file.size);
        
        // Check if the file is a PowerPoint file
        if (file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' || 
            file.name.toLowerCase().endsWith('.pptx')) {
          console.log("Valid PowerPoint file detected from drop");
          
          // Store the original file directly
          this.reportTemplateFile = file;
          console.log("File set in component data:", this.reportTemplateFile.name);
          
          // Force a reactive update to ensure Vue recognizes the change
          this.$forceUpdate();
          
          try {
            // Update the file input element to reflect the selected file
            if (this.$refs.fileInput) {
              // Try DataTransfer API first (modern browsers)
              try {
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                this.$refs.fileInput.files = dataTransfer.files;
                console.log("File added to input element using DataTransfer API");
              } catch (err) {
                console.log("DataTransfer API not supported, using alternative approach", err);
                // If DataTransfer is not supported, we'll still use the file directly
                console.log("File will be used directly from reportTemplateFile");
              }
            } else {
              console.warn("File input reference not found");
            }
          } catch (err) {
            console.error("Error setting file input:", err);
            // Even if this fails, we still have the file in reportTemplateFile
          }
          
          // Add a verification step to make sure the file was set correctly
          setTimeout(() => {
            console.log("Verification check - reportTemplateFile after drop:", 
              this.reportTemplateFile ? {
                name: this.reportTemplateFile.name,
                type: this.reportTemplateFile.type,
                size: this.reportTemplateFile.size
              } : 'Not set');
            
            if (this.$refs.fileInput && this.$refs.fileInput.files.length > 0) {
              console.log("File in input element:", this.$refs.fileInput.files[0].name);
            } else {
              console.log("No file in input element");
            }
          }, 100);
        } else {
          console.log("Invalid file type rejected:", file.type);
          alert('Please upload a PowerPoint (.pptx) file only.');
          this.reportTemplateFile = null;
        }
      } else {
        console.log("No files in drop event");
      }
    },
    handleFileUpload(event) {
      console.log("File input change detected", event);
      try {
        if (event.target.files && event.target.files.length > 0) {
          const file = event.target.files[0];
          console.log("File selected:", file.name, file.type, "Size:", file.size, "bytes");
          
          // Check if the file is a PowerPoint file
          if (file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation' || 
              file.name.toLowerCase().endsWith('.pptx')) {
            console.log("Valid PowerPoint file detected");
            this.reportTemplateFile = file;
            
            // Set a flag to indicate the file was successfully selected
            window.setTimeout(() => {
              console.log("reportTemplateFile is set:", !!this.reportTemplateFile);
              console.log("File details:", this.reportTemplateFile ? {
                name: this.reportTemplateFile.name,
                type: this.reportTemplateFile.type,
                size: this.reportTemplateFile.size
              } : 'No file');
            }, 100);
          } else {
            console.log("Invalid file type rejected:", file.type);
            alert('Please upload a PowerPoint (.pptx) file only.');
            event.target.value = ''; // Clear the file input
            this.reportTemplateFile = null;
          }
        } else {
          console.log("No files selected in the input element");
          this.reportTemplateFile = null;
        }
      } catch (error) {
        console.error("Error in handleFileUpload:", error);
        this.reportTemplateFile = null;
      }
    },
    manualUpload() {
      console.log("Manual upload button clicked");
      
      // Check if we have a file name but no file object
      if (this.$refs.fileInput && this.$refs.fileInput.files && this.$refs.fileInput.files.length > 0) {
        console.log("File found in DOM input element:", this.$refs.fileInput.files[0].name);
        this.reportTemplateFile = this.$refs.fileInput.files[0];
      } else {
        console.log("No file found in DOM input element");
      }
      
      console.log("Current file in data:", this.reportTemplateFile ? this.reportTemplateFile.name : "None");
      console.log("Template name:", this.reportTemplateName);
      
      // Check if we have the required data
      if (!this.reportTemplateName) {
        alert('Please enter a template name');
        return;
      }
      
      if (!this.reportTemplateFile) {
        alert('Please select a PowerPoint file (.pptx)');
        return;
      }
      
      // Now call the original upload method
      this.uploadReportTemplate();
    },
    async uploadReportTemplate() {
      console.log("Upload function called");
      
      // Get the file either from the component data or from the file input
      let fileToUpload = this.reportTemplateFile;
      
      // Double check the file input element
      if (!fileToUpload && this.$refs.fileInput && this.$refs.fileInput.files && this.$refs.fileInput.files.length > 0) {
        fileToUpload = this.$refs.fileInput.files[0];
        console.log("Using file from input element instead of component data");
      }
      
      console.log("File to upload:", fileToUpload ? {
        name: fileToUpload.name,
        type: fileToUpload.type,
        size: fileToUpload.size
      } : "No file found");
      
      console.log("Template name:", this.reportTemplateName);
      
      if (!fileToUpload) {
        alert('Please select a PowerPoint file (.pptx)');
        return;
      }
      
      if (!this.reportTemplateName) {
        alert('Please enter a template name');
        return;
      }
      
      if (!this.client || !this.client.id) {
        alert('Client information is missing. Please try refreshing the page.');
        return;
      }
      
      this.isUploading = true;
      try {
        const token = localStorage.getItem('token');
        const headers = { 
          Authorization: `Bearer ${token}`
          // Don't set Content-Type - axios will set it with the boundary
        };
        
        // Create a fresh FormData instance
        const formData = new FormData();
        formData.append('name', this.reportTemplateName);
        
        // Log file details before adding to FormData
        console.log("Adding file to FormData:", {
          name: fileToUpload.name,
          type: fileToUpload.type,
          size: fileToUpload.size
        });
        
        // Add the file to the FormData object
        formData.append('file', fileToUpload);
        
        // Log what's in the FormData (this is limited but helpful)
        console.log("FormData contents:");
        for (let pair of formData.entries()) {
          console.log(pair[0], pair[1] instanceof File ? 
            `File: ${pair[1].name}, type: ${pair[1].type}, size: ${pair[1].size}` : pair[1]);
        }
        
        console.log("Uploading template for client:", this.client.id);
        console.log("API endpoint:", `http://localhost:8000/api/clients/${this.client.id}/reporttemplates/`);
        
        // Make the API request
        const response = await axios.post(
          `http://localhost:8000/api/clients/${this.client.id}/reporttemplates/`, 
          formData,
          { 
            headers,
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              console.log(`Upload progress: ${percentCompleted}%`);
            }
          }
        );
        
        console.log("Upload successful! Response:", response.data);
        
        // After successful upload, add to the templates list and open the slide editor modal
        this.currentTemplateId = response.data.id;
        this.reportTemplates.push(response.data);
        this.closeReportTemplateModal();
        
        // Load the template slides for editing
        this.loadTemplateSlides(response.data.id);
      } catch (error) {
        console.error('Error uploading template:', error);
        
        if (error.response) {
          console.error('Server response data:', error.response.data);
          console.error('Server response status:', error.response.status);
          console.error('Server response headers:', error.response.headers);
          
          let errorMessage = 'Failed to upload template: ';
          if (error.response.data && error.response.data.detail) {
            errorMessage += error.response.data.detail;
          } else if (error.response.data && typeof error.response.data === 'object') {
            errorMessage += JSON.stringify(error.response.data);
          } else {
            errorMessage += `Server returned ${error.response.status} ${error.response.statusText}`;
          }
          alert(errorMessage);
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received:', error.request);
          alert('Failed to upload template: No response from server. Please check your network connection and try again.');
        } else {
          // Something happened in setting up the request
          console.error('Error message:', error.message);
          alert(`Failed to upload template: ${error.message}. Please try again.`);
        }
      } finally {
        this.isUploading = false;
      }
    },
    closeReportTemplateModal() {
      this.showReportTemplateModal = false;
      this.reportTemplateName = '';
      this.reportTemplateFile = null;
      this.isDragOver = false;
      
      // Also reset the file input element
      const fileInput = document.getElementById('templateFileInput');
      if (fileInput) {
        fileInput.value = '';
      }
    },
    async loadTemplateSlides(templateId) {
      this.showSlideEditorModal = true;
      this.isLoadingSlides = true;
      this.templateSlides = [];
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        const response = await axios.get(
          `http://localhost:8000/api/reporttemplates/${templateId}/slides/`,
          { headers }
        );
        
        // Set the slides data
        this.templateSlides = response.data.slides.map(slide => ({
          id: slide.id,
          thumbnail: slide.thumbnail_url,
          order: slide.order
        }));
        
      } catch (error) {
        console.error('Error loading template slides:', error);
        alert('Failed to load slides. Please try again.');
      } finally {
        this.isLoadingSlides = false;
      }
    },
    removeSlide(index) {
      // Mark this slide for removal
      this.templateSlides[index].toBeRemoved = true;
      // Visually hide it
      this.$set(this.templateSlides, index, {
        ...this.templateSlides[index],
        hidden: true
      });
    },
    toggleSlideSelection(index) {
      const selectedIndex = this.selectedSlides.indexOf(index);
      if (selectedIndex === -1) {
        this.selectedSlides.push(index);
      } else {
        this.selectedSlides.splice(selectedIndex, 1);
      }
    },
    removeSelectedSlides() {
      // Mark selected slides for removal
      this.selectedSlides.forEach(index => {
        if (this.templateSlides[index]) {
          this.templateSlides[index].toBeRemoved = true;
          this.$set(this.templateSlides, index, {
            ...this.templateSlides[index],
            hidden: true
          });
        }
      });
      this.selectedSlides = [];
    },
    async saveTemplateChanges() {
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        
        // Filter out removed slides and prepare payload
        const remainingSlides = this.templateSlides
          .filter(slide => !slide.hidden && !slide.toBeRemoved)
          .map((slide, index) => ({
            id: slide.id,
            order: index
          }));
        
        // Send the updated order and removed slides to the backend
        await axios.post(
          `http://localhost:8000/api/reporttemplates/${this.currentTemplateId}/update_slides/`,
          { slides: remainingSlides },
          { headers }
        );
        
        // Close the modal
        this.closeSlideEditorModal();
        
        // Optionally reload the template list
        const reportTemplatesRes = await axios.get(
          `http://localhost:8000/api/clients/${this.client.id}/reporttemplates/`, 
          { headers }
        );
        this.reportTemplates = reportTemplatesRes.data;
        
      } catch (error) {
        console.error('Error saving template changes:', error);
        alert('Failed to save template changes. Please try again.');
      }
    },
    closeSlideEditorModal() {
      this.showSlideEditorModal = false;
      this.templateSlides = [];
      this.selectedSlides = [];
      this.currentTemplateId = null;
    },
    initSortable() {
      // Use this.$nextTick to ensure the DOM is updated before initializing Sortable
      this.$nextTick(() => {
        const container = this.$refs.slidesContainer;
        if (container) {
          if (this.sortableInstance) {
            this.sortableInstance.destroy();
          }
          this.sortableInstance = Sortable.create(container, {
            animation: 150,
            ghostClass: 'slide-ghost',
            chosenClass: 'slide-chosen',
            dragClass: 'slide-drag',
            handle: '.slide-card',
            onEnd: (event) => {
              // Get the new order
              const slideItems = Array.from(container.querySelectorAll('.slide-item'));
              const newOrder = slideItems.map(item => {
                const index = parseInt(item.dataset.slideIndex, 10);
                return this.templateSlides[index];
              });
              
              // Update the templateSlides array
              this.templateSlides = newOrder;
            }
          });
        }
      });
    },
    clearSelectedFile(e) {
      e.stopPropagation(); // Prevent triggering the file input
      console.log("Clearing selected file");
      
      // Clear the file from our data
      this.reportTemplateFile = null;
      
      // Reset the file input element to ensure consistency
      const fileInput = document.getElementById('templateFileInput');
      if (fileInput) {
        fileInput.value = '';
        console.log("File input element cleared");
      }
      
      // Force a reactive update
      this.$forceUpdate();
      console.log("File selection cleared");
    },
    triggerFileInput(e) {
      // Don't trigger if the event came from the remove button
      if (e && e.target.closest('button')) return;
      
      const fileInput = document.getElementById('templateFileInput');
      if (fileInput) {
        fileInput.click();
      }
    },
    formatFileSize(size) {
      if (size < 1024) {
        return size + ' bytes';
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB';
      } else if (size < 1024 * 1024 * 1024) {
        return (size / (1024 * 1024)).toFixed(2) + ' MB';
      } else {
        return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
      }
    },
    showDeleteModal(scenario) {
      this.scenarioToDelete = scenario;
      this.showDeleteConfirmModal = true;
    },
    async confirmDeleteScenario() {
      if (!this.scenarioToDelete) return;
      
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };
        
        // Fix the API endpoint to include client_id
        const response = await axios.delete(
          `http://localhost:8000/api/clients/${this.client.id}/scenarios/${this.scenarioToDelete.id}/`, 
          { headers }
        );
        
        // Remove from local array
        this.client.scenarios = this.client.scenarios.filter(s => s.id !== this.scenarioToDelete.id);
        
        // Close modal and reset
        this.showDeleteConfirmModal = false;
        this.scenarioToDelete = null;
        
        // Show success message (optional)
        console.log('Scenario deleted successfully');
      } catch (error) {
        console.error('Error deleting scenario:', error);
        console.error('Response:', error.response);
        
        // Close modal
        this.showDeleteConfirmModal = false;
        
        // Show error message
        let errorMessage = 'Failed to delete scenario. ';
        if (error.response && error.response.status === 404) {
          errorMessage += 'Scenario not found.';
        } else if (error.response && error.response.data && error.response.data.detail) {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += 'Please try again.';
        }
        alert(errorMessage);
        
        this.scenarioToDelete = null;
      }
    },
    // Color helper method
    getColorForPercent(percent) {
      if (percent > 50) {
        return '#ff0000'; // Red
      } else if (percent > 25) {
        return '#ffa500'; // Orange
      } else if (percent > 15) {
        return '#ffff00'; // Yellow
      } else {
        return '#00ff00'; // Green
      }
    },
    getProgressBarClass(percent) {
      if (percent > 50) {
        return 'bg-danger'; // Red
      } else if (percent > 25) {
        return 'bg-warning'; // Orange/Yellow
      } else if (percent > 15) {
        return 'bg-info'; // Light blue
      } else {
        return 'bg-success'; // Green
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

/* Slide editor styles */
.slide-item {
  cursor: move;
  transition: transform 0.2s ease;
}

.slide-item:hover {
  transform: translateY(-5px);
}

.slide-card {
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.slide-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.slide-card.border-primary {
  box-shadow: 0 0 0 2px #0d6efd;
}

/* Hide slides marked for removal but keep them in the DOM for ordering purposes */
.slide-item [data-hidden="true"] {
  opacity: 0.3;
  filter: grayscale(100%);
}

/* Sortable.js related styles */
.slide-ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

.slide-chosen {
  background-color: #f0f8ff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.slide-drag {
  opacity: 0.8;
}

/* File upload drag & drop styles */
.drop-zone {
  min-height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px dashed #ccc;
  background-color: #f8f9fa;
}

.drop-zone:hover {
  border-color: #0d6efd;
  background-color: #f1f8ff;
}

.drop-zone.border-primary {
  border: 2px dashed #0d6efd;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.progress-container {
  min-width: 150px;
}

.progress {
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: visible;
}

.progress-bar {
  transition: width 0.6s ease;
  border-radius: 10px;
}

.progress-label {
  position: absolute;
  width: 100%;
  text-align: center;
  line-height: 25px;
  top: 0;
  color: #333;
  pointer-events: none;
}

.progress-label strong {
  font-size: 1rem;
  font-weight: 600;
}

.scenarios-table td, .scenarios-table th {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  vertical-align: middle;
}
.scenarios-table tr {
  height: auto;
}
.scenarios-table .scenario-name {
  line-height: 1.2;
  margin-bottom: 0.1rem;
}

/* Ensure Add Scenario button text is always white */
.btn-primary.text-white,
.btn-primary.text-white:hover,
.btn-primary.text-white:focus,
.btn-primary.text-white:active {
  color: #fff !important;
}
</style>