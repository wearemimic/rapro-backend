<template>
  <div class="integrations">
    <h1>Integrations</h1>
    <p>Connect to various services to enhance your experience.</p>
    <form @submit.prevent="saveApiKey">
      <label for="apiKey">Wealthbox API Key:</label>
      <input type="text" id="apiKey" v-model="apiKey" placeholder="Enter your API key" required />
      <button type="submit">Save API Key</button>
    </form>

    <button @click="connectToWealthbox">Connect to Wealthbox</button>

    <div v-if="connectionStatus" :class="{'success': connectionStatus === 'Connected successfully!', 'error': connectionStatus !== 'Connected successfully!'}">
      {{ connectionStatus }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Integrations',
  data() {
    return {
      apiKey: localStorage.getItem('wealthboxApiKey') || '',
      connectionStatus: ''
    };
  },
  methods: {
    saveApiKey() {
      localStorage.setItem('wealthboxApiKey', this.apiKey);
      alert('API Key saved successfully!');
      this.testConnection();
    },
    testConnection() {
      const apiKey = localStorage.getItem('wealthboxApiKey');
      console.log('Attempting to connect to Wealthbox with API key:', apiKey);
      axios.get('http://localhost:8000/proxy/v1/me/')
        .then(response => {
          console.log('Connected successfully:', response.data);
          this.connectionStatus = 'Connected successfully!';
        })
        .catch(error => {
          console.error('Failed to connect to Wealthbox:', error);
          if (error.response) {
            console.error('Error response data:', error.response.data);
            console.error('Error response status:', error.response.status);
            console.error('Error response headers:', error.response.headers);
            this.connectionStatus = `Failed to connect. Status: ${error.response.status} - ${error.response.data.message || 'Unknown error'}`;
          } else if (error.request) {
            console.error('Error request:', error.request);
            this.connectionStatus = 'No response received from Wealthbox. Please check your network connection.';
          } else {
            console.error('Error message:', error.message);
            this.connectionStatus = `Error: ${error.message}`;
          }
        });
    },
    connectToWealthbox() {
      const apiKey = localStorage.getItem('wealthboxApiKey');
      if (!apiKey) {
        alert('Please enter and save your API key first.');
        return;
      }
      axios.get('https://api.crmworkspace.com/v1/contacts', {  // Example endpoint to retrieve contacts
        headers: {
          'ACCESS_TOKEN': apiKey
        }
      })
      .then(response => {
        console.log('Data from Wealthbox:', response.data);
        // Process the data as needed
      })
      .catch(error => {
        console.error('Error connecting to Wealthbox:', error);
      });
    }
  }
}
</script>

<style scoped>
.integrations {
  padding: 20px;
}

.success {
  color: green;
}

.error {
  color: red;
}
</style> 