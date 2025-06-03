<template>
  <div class="container mt-5">
    <h2>Edit Client</h2>
    <form @submit.prevent="submitForm">
      <div class="row">
        <div class="col-md-6 mb-3">
          <label>First Name</label>
          <input v-model="form.first_name" class="form-control" required minlength="3" maxlength="30">
        </div>
        <div class="col-md-6 mb-3">
          <label>Last Name</label>
          <input v-model="form.last_name" class="form-control" required minlength="3" maxlength="30">
        </div>
      </div>

      <div class="mb-3">
        <label>Email</label>
        <input v-model="form.email" type="email" class="form-control" required>
      </div>

      <div class="row">
        <div class="col-md-4 mb-3">
          <label>Birthdate</label>
          <input v-model="form.birthdate" type="date" class="form-control" required>
        </div>
        <div class="col-md-4 mb-3">
          <label>Gender</label>
          <select v-model="form.gender" class="form-control" required>
            <option disabled value="">Choose...</option>
            <option>Male</option>
            <option>Female</option>
            <option>Other</option>
          </select>
        </div>
        <div class="col-md-4 mb-3">
          <label>Tax Status</label>
          <select v-model="form.tax_status" @change="updateSpouseRequirement" class="form-control" required>
            <option disabled value="">Choose...</option>
            <option>Single</option>
            <option>Married Filing Jointly</option>
            <option>Married Filing Separately</option>
          </select>
        </div>
      </div>

      <div v-if="showSpouseFields">
        <h5>Spouse Information</h5>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label>Spouse First Name</label>
            <input v-model="form.spouse_first_name" class="form-control" required>
          </div>
          <div class="col-md-6 mb-3">
            <label>Spouse Last Name</label>
            <input v-model="form.spouse_last_name" class="form-control" required>
          </div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label>Spouse Birthdate</label>
            <input v-model="form.spouse_birthdate" type="date" class="form-control" required>
          </div>
          <div class="col-md-6 mb-3">
            <label>Spouse Gender</label>
            <select v-model="form.spouse_gender" class="form-control" required>
              <option disabled value="">Choose...</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>
        </div>
      </div>

      <div class="mb-3">
        <label>Advisor Notes</label>
        <textarea v-model="form.notes" class="form-control" rows="4"></textarea>
      </div>

      <div class="mb-3">
        <label>Status</label>
        <select v-model="form.status" class="form-control" required>
          <option value="draft">Draft</option>
          <option value="in_progress">In Progress</option>
          <option value="reviewed">Reviewed</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      <button type="submit" class="btn btn-primary">Save Changes</button>
      <button type="button" class="btn btn-secondary ms-2" @click="cancelEdit">Cancel</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "ClientEdit",
  data() {
    return {
      form: {
        first_name: "",
        last_name: "",
        email: "",
        birthdate: "",
        gender: "",
        tax_status: "",
        spouse_first_name: "",
        spouse_last_name: "",
        spouse_birthdate: "",
        spouse_gender: "",
        notes: "",
        status: "draft"
      },
      showSpouseFields: false
    };
  },
  created() {
    this.loadClient();
  },
  methods: {
    updateSpouseRequirement() {
      this.showSpouseFields = this.form.tax_status !== "Single";
    },
    async loadClient() {
      const clientId = this.$route.params.id;
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };

      try {
        const response = await axios.get(`http://localhost:8000/api/clients/${clientId}/`, { headers });
        this.form = {
          ...response.data,
          spouse_first_name: response.data.spouse?.first_name || "",
          spouse_last_name: response.data.spouse?.last_name || "",
          spouse_birthdate: response.data.spouse?.birthdate || "",
          spouse_gender: response.data.spouse?.gender || ""
        };
        this.updateSpouseRequirement();
      } catch (error) {
        console.error("Failed to load client data", error);
        this.$router.push("/clients");
      }
    },
    async submitForm() {
      const clientId = this.$route.params.id;
      const token = localStorage.getItem("token");
      const headers = { Authorization: `Bearer ${token}` };
      const {
        spouse_first_name,
        spouse_last_name,
        spouse_birthdate,
        spouse_gender,
        ...baseForm
      } = this.form;

      const payload = {
        ...baseForm,
        notes: String(this.form.notes || "")
      };

      if (this.showSpouseFields) {
        payload.spouse = {
          first_name: spouse_first_name,
          last_name: spouse_last_name,
          birthdate: spouse_birthdate,
          gender: spouse_gender,
        };
      }

      try {
        await axios.patch(`http://localhost:8000/api/clients/${clientId}/edit/`, payload, { headers });
        this.$router.push(`/clients/${clientId}`);
      } catch (error) {
        if (error.response?.data) {
          console.error("Backend error:", error.response.data);
        } else {
          console.error("Client update failed", error);
        }
      }
    },
    cancelEdit() {
      const clientId = this.$route.params.id;
      this.$router.push(`/clients/${clientId}`);
    }
  }
};
</script>