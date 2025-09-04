<template>
  <div class="container mt-5">
    <div class="row">
      <div class="col-md-6">
        <div class="card" style="margin-top:60px;">
          <div class="card-header">
            <h3>New Contact</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>First Name</label>
                  <input v-model="form.first_name" class="form-control" required minlength="3" maxlength="30">
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
                  <input 
                    v-model="form.birthdate" 
                    type="date" 
                    class="form-control" 
                    required 
                    :min="minBirthdate"
                    :max="maxBirthdate"
                    @blur="validatePrimaryBirthdate"
                  >
                  <div v-if="primaryBirthdateError" class="text-danger mt-1">{{ primaryBirthdateError }}</div>
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

              <div class="mb-3">
                <label>Advisor Notes</label>
                <textarea v-model="form.notes" class="form-control" rows="4"></textarea>
              </div>
              <button type="submit" class="btn btn-primary">Create Client</button>
            </form>
          </div>
        </div>
      </div>

      <div v-if="showSpouseFields" class="col-md-6">
        <div class="card" style="margin-top:60px;">
          <div class="card-header">
            <h3>Spouse Information</h3>
          </div>
          <div class="card-body">
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
                <input 
                  v-model="form.spouse_birthdate" 
                  type="date" 
                  class="form-control" 
                  required 
                  :min="minBirthdate"
                  :max="maxBirthdate"
                  @blur="validateSpouseBirthdate"
                >
                <div v-if="spouseBirthdateError" class="text-danger mt-1">{{ spouseBirthdateError }}</div>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { API_CONFIG } from '@/config'

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
        notes: "",
        apply_standard_deduction: true
      },
      showSpouseFields: false,
      primaryBirthdateError: "",
      spouseBirthdateError: "",
      minBirthdate: "1900-01-01",
      maxBirthdate: new Date().toISOString().split('T')[0]
    };
  },
  methods: {
    updateSpouseRequirement() {
      this.showSpouseFields = this.form.tax_status !== "Single";
    },
    validatePrimaryBirthdate() {
      this.primaryBirthdateError = "";
      
      if (!this.form.birthdate) {
        return;
      }
      
      const birthDate = new Date(this.form.birthdate);
      const minDate = new Date(this.minBirthdate);
      const maxDate = new Date(this.maxBirthdate);
      
      if (isNaN(birthDate.getTime())) {
        this.primaryBirthdateError = "Please enter a valid date";
        return;
      }
      
      if (birthDate < minDate || birthDate > maxDate) {
        this.primaryBirthdateError = `Birthdate must be between ${minDate.getFullYear()} and ${maxDate.getFullYear()}`;
        return;
      }
      
      // Additional check for reasonable age range (18-120 years old)
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18 || age > 120) {
        this.primaryBirthdateError = `Age (${age}) should be between 18 and 120 years`;
        return;
      }
    },
    validateSpouseBirthdate() {
      this.spouseBirthdateError = "";
      
      if (!this.form.spouse_birthdate) {
        return;
      }
      
      const birthDate = new Date(this.form.spouse_birthdate);
      const minDate = new Date(this.minBirthdate);
      const maxDate = new Date(this.maxBirthdate);
      
      if (isNaN(birthDate.getTime())) {
        this.spouseBirthdateError = "Please enter a valid date";
        return;
      }
      
      if (birthDate < minDate || birthDate > maxDate) {
        this.spouseBirthdateError = `Birthdate must be between ${minDate.getFullYear()} and ${maxDate.getFullYear()}`;
        return;
      }
      
      // Additional check for reasonable age range (18-120 years old)
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18 || age > 120) {
        this.spouseBirthdateError = `Spouse age (${age}) should be between 18 and 120 years`;
        return;
      }
    },
    async submitForm() {
      // Validate primary birthdate before submission
      this.validatePrimaryBirthdate();
      if (this.primaryBirthdateError) {
        alert("Please fix the primary birthdate error before submitting.");
        return;
      }
      
      // Validate spouse birthdate before submission
      if (this.showSpouseFields) {
        this.validateSpouseBirthdate();
        if (this.spouseBirthdateError) {
          alert("Please fix the spouse birthdate error before submitting.");
          return;
        }
      }
      
      try {
        const payload = {
          first_name: this.form.first_name,
          last_name: this.form.last_name,
          email: this.form.email,
          birthdate: this.form.birthdate,
          gender: this.form.gender,
          tax_status: this.form.tax_status,
          notes: this.form.notes,
          apply_standard_deduction: this.form.apply_standard_deduction
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
        if (!token) {
          throw new Error('Authentication token is missing. Please log in again.');
        }

        const headers = { Authorization: `Bearer ${token}` };

        // 🧪 Log payload before sending
        console.log("Payload being sent:", payload);

        const response = await axios.post("${API_CONFIG.API_URL}/clients/create/", payload, { headers });
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
