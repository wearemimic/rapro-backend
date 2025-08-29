import { defineStore } from 'pinia'
import axios from 'axios'
import { apiService } from '@/services/api.js'

export const useClientStore = defineStore('client', {
  state: () => ({
    clients: [],
    currentClient: null,
    loading: false,
    error: null
  }),

  getters: {
    getClientById: (state) => (id) => {
      return state.clients.find(client => client.id === id)
    }
  },

  actions: {
    async fetchClients() {
      this.loading = true
      try {
        const response = await axios.get(apiService.getUrl('/api/clients/'))
        this.clients = response.data
        this.error = null
      } catch (error) {
        console.error('Error fetching clients:', error)
        this.error = error.message || 'Failed to fetch clients'
        this.clients = []
      } finally {
        this.loading = false
      }
    },

    async fetchClient(id) {
      this.loading = true
      try {
        const response = await axios.get(apiService.getUrl(`/api/clients/${id}/`))
        this.currentClient = response.data
        this.error = null
        return response.data
      } catch (error) {
        console.error('Error fetching client:', error)
        this.error = error.message || 'Failed to fetch client'
        this.currentClient = null
        throw error
      } finally {
        this.loading = false
      }
    },

    // Client Portal Management Methods
    async enablePortalAccess(clientId) {
      try {
        const response = await axios.post(
          apiService.getUrl(`/api/client-portal/manage/${clientId}/enable/`),
          {},
          apiService.getConfig()
        )
        
        // Update client in local state
        if (this.currentClient && this.currentClient.id === clientId) {
          this.currentClient.portal_access_enabled = true
        }
        
        // Update in clients list
        const clientIndex = this.clients.findIndex(c => c.id === clientId)
        if (clientIndex !== -1) {
          this.clients[clientIndex].portal_access_enabled = true
        }
        
        return response.data
      } catch (error) {
        console.error('Error enabling portal access:', error)
        throw error
      }
    },

    async revokePortalAccess(clientId) {
      try {
        const response = await axios.post(
          apiService.getUrl(`/api/client-portal/manage/${clientId}/revoke/`),
          {},
          apiService.getConfig()
        )
        
        // Update client in local state
        if (this.currentClient && this.currentClient.id === clientId) {
          this.currentClient.portal_access_enabled = false
          this.currentClient.portal_invitation_sent_at = null
          this.currentClient.portal_invitation_token = null
          this.currentClient.portal_last_login = null
        }
        
        // Update in clients list
        const clientIndex = this.clients.findIndex(c => c.id === clientId)
        if (clientIndex !== -1) {
          this.clients[clientIndex].portal_access_enabled = false
          this.clients[clientIndex].portal_invitation_sent_at = null
          this.clients[clientIndex].portal_invitation_token = null
          this.clients[clientIndex].portal_last_login = null
        }
        
        return response.data
      } catch (error) {
        console.error('Error revoking portal access:', error)
        throw error
      }
    },

    async sendPortalInvitation(clientId) {
      try {
        const response = await axios.post(
          apiService.getUrl(`/api/client-portal/manage/${clientId}/send-invitation/`),
          {},
          apiService.getConfig()
        )
        
        // Update client in local state
        if (this.currentClient && this.currentClient.id === clientId) {
          this.currentClient.portal_invitation_sent_at = response.data.client.portal_invitation_sent_at
        }
        
        // Update in clients list
        const clientIndex = this.clients.findIndex(c => c.id === clientId)
        if (clientIndex !== -1) {
          this.clients[clientIndex].portal_invitation_sent_at = response.data.client.portal_invitation_sent_at
        }
        
        return response.data
      } catch (error) {
        console.error('Error sending portal invitation:', error)
        throw error
      }
    },

    async getClientScenarios(clientId) {
      try {
        const response = await axios.get(
          apiService.getUrl(`/api/clients/${clientId}/scenarios/`),
          apiService.getConfig()
        )
        return response.data
      } catch (error) {
        console.error('Error fetching client scenarios:', error)
        throw error
      }
    }
  }
})