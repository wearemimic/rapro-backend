// affiliateStore.js
import { defineStore } from 'pinia'
import affiliateService from '../services/affiliateService'

export const useAffiliateStore = defineStore('affiliate', {
  state: () => ({
    // Affiliates data
    affiliates: [],
    currentAffiliate: null,
    affiliateDetails: null,
    
    // Links data
    affiliateLinks: [],
    currentLink: null,
    
    // Commissions data
    commissions: [],
    pendingCommissions: [],
    
    // Payouts data
    payouts: [],
    
    // Discount codes
    discountCodes: [],
    
    // Dashboard data
    dashboardData: null,
    performanceMetrics: null,
    
    // UI state
    loading: false,
    error: null,
    searchQuery: '',
    filters: {
      status: '',
      dateRange: {
        start: null,
        end: null
      }
    },
    
    // Pagination
    pagination: {
      page: 1,
      pageSize: 25,
      total: 0,
      totalPages: 0
    }
  }),

  getters: {
    // Get active affiliates only
    activeAffiliates: (state) => {
      return state.affiliates.filter(a => a.status === 'active')
    },
    
    // Get pending affiliates for approval
    pendingAffiliates: (state) => {
      return state.affiliates.filter(a => a.status === 'pending')
    },
    
    // Get filtered affiliates based on search and filters
    filteredAffiliates: (state) => {
      let filtered = state.affiliates
      
      // Apply search filter
      if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase()
        filtered = filtered.filter(a => 
          a.business_name.toLowerCase().includes(query) ||
          a.email.toLowerCase().includes(query) ||
          a.affiliate_code.toLowerCase().includes(query)
        )
      }
      
      // Apply status filter
      if (state.filters.status) {
        filtered = filtered.filter(a => a.status === state.filters.status)
      }
      
      return filtered
    },
    
    // Get total pending commission amount
    totalPendingCommissions: (state) => {
      return state.pendingCommissions.reduce((sum, c) => sum + parseFloat(c.commission_amount), 0)
    },
    
    // Get active links for current affiliate
    activeLinks: (state) => {
      return state.affiliateLinks.filter(l => l.is_active)
    },
    
    // Check if user has admin access
    isAdmin: () => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.is_staff || user.is_platform_admin || user.admin_role
    }
  },

  actions: {
    // Fetch all affiliates
    async fetchAffiliates(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getAffiliates({
          page: this.pagination.page,
          page_size: this.pagination.pageSize,
          search: this.searchQuery,
          status: this.filters.status,
          ...params
        })
        
        this.affiliates = response.data.results || response.data
        
        // Update pagination if provided
        if (response.data.count !== undefined) {
          this.pagination.total = response.data.count
          this.pagination.totalPages = Math.ceil(response.data.count / this.pagination.pageSize)
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch affiliates'
        console.error('Error fetching affiliates:', error)
      } finally {
        this.loading = false
      }
    },
    
    // Fetch single affiliate details
    async fetchAffiliateDetails(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getAffiliate(id)
        this.currentAffiliate = response.data
        this.affiliateDetails = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch affiliate details'
        console.error('Error fetching affiliate:', error)
      } finally {
        this.loading = false
      }
    },
    
    // Create new affiliate
    async createAffiliate(affiliateData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.createAffiliate(affiliateData)
        this.affiliates.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create affiliate'
        console.error('Error creating affiliate:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Update affiliate
    async updateAffiliate(id, affiliateData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.updateAffiliate(id, affiliateData)
        const index = this.affiliates.findIndex(a => a.id === id)
        if (index !== -1) {
          this.affiliates[index] = response.data
        }
        this.currentAffiliate = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update affiliate'
        console.error('Error updating affiliate:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Approve affiliate
    async approveAffiliate(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.approveAffiliate(id)
        await this.fetchAffiliates()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to approve affiliate'
        console.error('Error approving affiliate:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Suspend affiliate
    async suspendAffiliate(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.suspendAffiliate(id)
        await this.fetchAffiliates()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to suspend affiliate'
        console.error('Error suspending affiliate:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Delete affiliate
    async deleteAffiliate(id) {
      this.loading = true
      this.error = null
      
      try {
        await affiliateService.deleteAffiliate(id)
        this.affiliates = this.affiliates.filter(a => a.id !== id)
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to delete affiliate'
        console.error('Error deleting affiliate:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Fetch affiliate dashboard data
    async fetchDashboardData(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getDashboard(id)
        this.dashboardData = response.data
        this.performanceMetrics = response.data.performance_metrics
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch dashboard data'
        console.error('Error fetching dashboard:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Fetch affiliate links
    async fetchAffiliateLinks(affiliateId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getAffiliateLinks(affiliateId)
        this.affiliateLinks = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch links'
        console.error('Error fetching links:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Generate new tracking link
    async generateLink(affiliateId, linkData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.generateLink(affiliateId, linkData)
        this.affiliateLinks.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to generate link'
        console.error('Error generating link:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Activate/Deactivate link
    async toggleLinkStatus(linkId, activate = true) {
      this.loading = true
      this.error = null
      
      try {
        const response = activate 
          ? await affiliateService.activateLink(linkId)
          : await affiliateService.deactivateLink(linkId)
        
        const index = this.affiliateLinks.findIndex(l => l.id === linkId)
        if (index !== -1) {
          this.affiliateLinks[index].is_active = activate
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update link status'
        console.error('Error updating link:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Fetch commissions
    async fetchCommissions(affiliateId = null, params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getCommissions(affiliateId, params)
        this.commissions = response.data
        
        // Filter pending commissions
        this.pendingCommissions = response.data.filter(c => c.status === 'pending')
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch commissions'
        console.error('Error fetching commissions:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Calculate monthly commissions
    async calculateMonthlyCommissions() {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.calculateMonthlyCommissions()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to calculate commissions'
        console.error('Error calculating commissions:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Approve commission
    async approveCommission(commissionId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.approveCommission(commissionId)
        await this.fetchCommissions()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to approve commission'
        console.error('Error approving commission:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Fetch payouts
    async fetchPayouts(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getPayouts(params)
        this.payouts = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch payouts'
        console.error('Error fetching payouts:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Create batch payouts
    async createBatchPayouts() {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.createBatchPayouts()
        await this.fetchPayouts()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create payouts'
        console.error('Error creating payouts:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Process payout
    async processPayout(payoutId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.processPayout(payoutId)
        await this.fetchPayouts()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to process payout'
        console.error('Error processing payout:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Fetch discount codes
    async fetchDiscountCodes(affiliateId = null) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.getDiscountCodes(affiliateId)
        this.discountCodes = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to fetch discount codes'
        console.error('Error fetching discount codes:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Create discount code
    async createDiscountCode(codeData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await affiliateService.createDiscountCode(codeData)
        this.discountCodes.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to create discount code'
        console.error('Error creating discount code:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // Validate discount code
    async validateDiscountCode(code) {
      try {
        const response = await affiliateService.validateDiscountCode(code)
        return response.data
      } catch (error) {
        console.error('Invalid discount code:', error)
        return { valid: false, error: 'Invalid code' }
      }
    },
    
    // Update filters
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },
    
    // Update search query
    setSearchQuery(query) {
      this.searchQuery = query
    },
    
    // Update pagination
    setPagination(page, pageSize = null) {
      this.pagination.page = page
      if (pageSize) {
        this.pagination.pageSize = pageSize
      }
    },
    
    // Clear store
    clearStore() {
      this.affiliates = []
      this.currentAffiliate = null
      this.affiliateDetails = null
      this.affiliateLinks = []
      this.commissions = []
      this.pendingCommissions = []
      this.payouts = []
      this.discountCodes = []
      this.dashboardData = null
      this.performanceMetrics = null
      this.error = null
      this.searchQuery = ''
      this.filters = {
        status: '',
        dateRange: {
          start: null,
          end: null
        }
      }
      this.pagination = {
        page: 1,
        pageSize: 25,
        total: 0,
        totalPages: 0
      }
    }
  }
})