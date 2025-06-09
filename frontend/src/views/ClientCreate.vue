<template>
  <div class="container mt-5">
    <form @submit.prevent="submitForm">
      <div class="card card-hover-shadow h-100" style="margin-top:60px;">
        <div class="card-title">
        <h3>New Contact</h3>
        </div>
        <div class="card-body">
          <div class="row">
            
            <div class="col-md-6 mb-3">
              <label>First Name</label>
              <input v-model="form.first_name" class="form-control" required minlength="5" maxlength="30">
            </div>
            <div class="col-md-6 mb-3">
              <label>Last Name</label>
              <input v-model="form.last_name" class="form-control" required minlength="5" maxlength="30">
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
        </div>
      </div>
      <button type="submit" class="btn btn-primary">Create Client</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: "ClientCreate",
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
        notes: ""
      },
      showSpouseFields: false
    };
  },
  methods: {
    updateSpouseRequirement() {
      this.showSpouseFields = this.form.tax_status !== "Single";
    },
    async submitForm() {
      try {
        const payload = {
          first_name: this.form.first_name,
          last_name: this.form.last_name,
          email: this.form.email,
          birthdate: this.form.birthdate,
          gender: this.form.gender,
          tax_status: this.form.tax_status,
          notes: this.form.notes,
        };

        if (this.showSpouseFields) {
          payload.spouse = {
            first_name: this.form.spouse_first_name,
            last_name: this.form.spouse_last_name,
            birthdate: this.form.spouse_birthdate,
            gender: this.form.spouse_gender,
          };
        }

        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };

        // 🧪 Log payload before sending
        console.log("Payload being sent:", payload);

        const response = await axios.post("http://localhost:8000/api/clients/create/", payload, { headers });
        this.$router.push(`/clients/${response.data.id}`);
      } catch (error) {
        // 🧪 Log backend response clearly
        if (error.response && error.response.data) {
          console.error("Backend responded with error:", error.response.data);
        } else {
          console.error("Client creation failed", error);
        }
      }
    }
  }
};
</script>
