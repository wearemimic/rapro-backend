// affiliateService.js
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance with auth headers
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: refreshToken
        })
        
        const { access } = response.data
        localStorage.setItem('access_token', access)
        
        originalRequest.headers.Authorization = `Bearer ${access}`
        return api(originalRequest)
      } catch (refreshError) {
        // Redirect to login if refresh fails
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

const affiliateService = {
  // Affiliate CRUD operations
  getAffiliates(params = {}) {
    return api.get('/affiliates/', { params })
  },
  
  getAffiliate(id) {
    return api.get(`/affiliates/${id}/`)
  },
  
  createAffiliate(data) {
    return api.post('/affiliates/', data)
  },
  
  updateAffiliate(id, data) {
    return api.put(`/affiliates/${id}/`, data)
  },
  
  deleteAffiliate(id) {
    return api.delete(`/affiliates/${id}/`)
  },
  
  // Affiliate actions
  approveAffiliate(id) {
    return api.post(`/affiliates/${id}/approve/`)
  },
  
  suspendAffiliate(id) {
    return api.post(`/affiliates/${id}/suspend/`)
  },
  
  getDashboard(id) {
    return api.get(`/affiliates/${id}/dashboard/`)
  },
  
  // Affiliate Links
  getAffiliateLinks(affiliateId, params = {}) {
    if (affiliateId) {
      return api.get(`/affiliates/${affiliateId}/links/`, { params })
    }
    return api.get('/affiliate-links/', { params })
  },
  
  getLink(id) {
    return api.get(`/affiliate-links/${id}/`)
  },
  
  createLink(data) {
    return api.post('/affiliate-links/', data)
  },
  
  generateLink(affiliateId, data) {
    return api.post(`/affiliates/${affiliateId}/generate_link/`, data)
  },
  
  updateLink(id, data) {
    return api.put(`/affiliate-links/${id}/`, data)
  },
  
  deleteLink(id) {
    return api.delete(`/affiliate-links/${id}/`)
  },
  
  activateLink(id) {
    return api.post(`/affiliate-links/${id}/activate/`)
  },
  
  deactivateLink(id) {
    return api.post(`/affiliate-links/${id}/deactivate/`)
  },
  
  // Commissions
  getCommissions(affiliateId = null, params = {}) {
    if (affiliateId) {
      return api.get(`/affiliates/${affiliateId}/commissions/`, { params })
    }
    return api.get('/commissions/', { params })
  },
  
  getCommission(id) {
    return api.get(`/commissions/${id}/`)
  },
  
  getPendingCommissions() {
    return api.get('/commissions/pending/')
  },
  
  approveCommission(id) {
    return api.post(`/commissions/${id}/approve/`)
  },
  
  calculateMonthlyCommissions() {
    return api.post('/commissions/calculate_monthly/')
  },
  
  // Payouts
  getPayouts(params = {}) {
    return api.get('/affiliate-payouts/', { params })
  },
  
  getPayout(id) {
    return api.get(`/affiliate-payouts/${id}/`)
  },
  
  createBatchPayouts() {
    return api.post('/affiliate-payouts/create_batch/')
  },
  
  processPayout(id) {
    return api.post(`/affiliate-payouts/${id}/process/`)
  },
  
  // Discount Codes
  getDiscountCodes(affiliateId = null, params = {}) {
    if (affiliateId) {
      params.affiliate = affiliateId
    }
    return api.get('/discount-codes/', { params })
  },
  
  getDiscountCode(id) {
    return api.get(`/discount-codes/${id}/`)
  },
  
  createDiscountCode(data) {
    return api.post('/discount-codes/', data)
  },
  
  updateDiscountCode(id, data) {
    return api.put(`/discount-codes/${id}/`, data)
  },
  
  deleteDiscountCode(id) {
    return api.delete(`/discount-codes/${id}/`)
  },
  
  validateDiscountCode(code) {
    return api.get('/discount-codes/validate/', { params: { code } })
  },
  
  // Analytics & Reports
  getAffiliateAnalytics(id, params = {}) {
    return api.get(`/affiliates/${id}/analytics/`, { params })
  },
  
  getConversionReport(affiliateId, params = {}) {
    return api.get(`/affiliates/${affiliateId}/conversions/`, { params })
  },
  
  getClickReport(affiliateId, params = {}) {
    return api.get(`/affiliates/${affiliateId}/clicks/`, { params })
  },
  
  exportReport(affiliateId, format = 'csv', params = {}) {
    return api.get(`/affiliates/${affiliateId}/export/`, {
      params: { format, ...params },
      responseType: 'blob'
    })
  },
  
  // Bulk operations
  bulkApproveAffiliates(ids) {
    return api.post('/affiliates/bulk_approve/', { ids })
  },
  
  bulkSuspendAffiliates(ids) {
    return api.post('/affiliates/bulk_suspend/', { ids })
  },
  
  bulkApproveCommissions(ids) {
    return api.post('/commissions/bulk_approve/', { ids })
  },
  
  // Helper functions
  getTrackingUrl(trackingCode) {
    const baseUrl = window.location.origin
    return `${baseUrl}/r/${trackingCode}/`
  },
  
  copyTrackingLink(trackingCode) {
    const url = this.getTrackingUrl(trackingCode)
    
    // Use modern clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(url)
    }
    
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = url
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    return new Promise((resolve, reject) => {
      try {
        document.execCommand('copy')
        textArea.remove()
        resolve()
      } catch (error) {
        textArea.remove()
        reject(error)
      }
    })
  },
  
  // Format currency
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  },
  
  // Format percentage
  formatPercentage(value, decimals = 2) {
    return `${parseFloat(value).toFixed(decimals)}%`
  },
  
  // Format date
  formatDate(date) {
    if (!date) return ''
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  },
  
  // Format date time
  formatDateTime(date) {
    if (!date) return ''
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

export default affiliateService