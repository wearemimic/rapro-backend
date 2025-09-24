/**
 * Secure Cookie-based Authentication Service
 * Replaces localStorage with httpOnly cookies for JWT security
 */

import axios from 'axios'
import { API_CONFIG } from '@/config'

class CookieAuthService {
  constructor() {
    this.baseURL = API_CONFIG.API_URL
    this.setupAxiosDefaults()
  }

  setupAxiosDefaults() {
    // Always send cookies with requests
    axios.defaults.withCredentials = true

    // Add CSRF token to requests
    axios.interceptors.request.use(
      async (config) => {
        // Get CSRF token from cookie or fetch if needed
        const csrfToken = this.getCSRFToken()
        if (csrfToken) {
          config.headers['X-CSRFToken'] = csrfToken
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Handle token refresh on 401 errors
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            // Try to refresh the token
            await this.refreshToken()
            // Retry the original request
            return axios(originalRequest)
          } catch (refreshError) {
            // Refresh failed, redirect to login
            this.handleLogout()
            throw refreshError
          }
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * Get CSRF token from cookie
   */
  getCSRFToken() {
    const cookies = document.cookie.split(';')
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'csrftoken') {
        return value
      }
    }
    return null
  }

  /**
   * Fetch CSRF token from server if not available
   */
  async ensureCSRFToken() {
    if (!this.getCSRFToken()) {
      try {
        await axios.get(`${this.baseURL}/auth/cookie/csrf/`)
      } catch (error) {
        console.warn('Failed to get CSRF token:', error)
      }
    }
  }

  /**
   * Login with email and password using cookies
   */
  async login(email, password) {
    await this.ensureCSRFToken()

    const response = await axios.post(`${this.baseURL}/auth/cookie/login/`, {
      email,
      password
    })

    return response.data
  }

  /**
   * Exchange Auth0 code for cookie-based authentication
   */
  async auth0Exchange(code, flowType = 'login', affiliateCode = null) {
    await this.ensureCSRFToken()

    const response = await axios.post(`${this.baseURL}/auth/cookie/auth0/`, {
      code,
      flow_type: flowType,
      affiliate_code: affiliateCode
    })

    return response.data
  }

  /**
   * Logout and clear all cookies
   */
  async logout() {
    try {
      await axios.post(`${this.baseURL}/auth/cookie/logout/`)
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      // Clear any remaining auth state
      this.handleLogout()
    }
  }

  /**
   * Handle logout cleanup (client-side)
   */
  handleLogout() {
    // Clear any cached user data
    sessionStorage.clear()

    // Remove auth-related cookies (browser will handle httpOnly ones)
    document.cookie = 'csrftoken=; Max-Age=0; path=/;'

    // Redirect to login
    window.location.href = '/login'
  }

  /**
   * Refresh access token
   */
  async refreshToken() {
    const response = await axios.post(`${this.baseURL}/auth/cookie/refresh/`)
    return response.data
  }

  /**
   * Verify authentication status
   */
  async verifyAuth() {
    try {
      const response = await axios.get(`${this.baseURL}/auth/cookie/verify/`)
      return response.data
    } catch (error) {
      throw new Error('Not authenticated')
    }
  }

  /**
   * Check if user is authenticated (client-side check)
   * This is a quick check - not as secure as server verification
   */
  isAuthenticated() {
    // Check if access token cookie exists
    const cookies = document.cookie.split(';')
    return cookies.some(cookie => cookie.trim().startsWith('access_token='))
  }

  /**
   * Migrate existing localStorage tokens to cookies
   * This helps transition users from localStorage to cookie auth
   */
  async migrateTocookies() {
    const accessToken = localStorage.getItem('token')
    const refreshToken = localStorage.getItem('refresh_token')

    if (!accessToken || !refreshToken) {
      throw new Error('No tokens found to migrate')
    }

    try {
      await this.ensureCSRFToken()

      const response = await axios.post(`${this.baseURL}/auth/cookie/migrate/`, {
        access_token: accessToken,
        refresh_token: refreshToken
      })

      // Clear localStorage after successful migration
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      return response.data
    } catch (error) {
      console.error('Migration failed:', error)
      throw error
    }
  }

  /**
   * Get current user info (cached in sessionStorage for performance)
   */
  async getCurrentUser() {
    try {
      // Try cache first
      const cachedUser = sessionStorage.getItem('user')
      if (cachedUser) {
        return JSON.parse(cachedUser)
      }

      // Fetch from server
      const authData = await this.verifyAuth()
      const user = authData.user

      // Cache in sessionStorage (not localStorage for security)
      sessionStorage.setItem('user', JSON.stringify(user))

      return user
    } catch (error) {
      // Clear any stale cache
      sessionStorage.removeItem('user')
      throw error
    }
  }

  /**
   * Clear cached user data
   */
  clearUserCache() {
    sessionStorage.removeItem('user')
  }
}

// Create singleton instance
const cookieAuthService = new CookieAuthService()

export default cookieAuthService

// Named exports for convenience
export const {
  login,
  auth0Exchange,
  logout,
  refreshToken,
  verifyAuth,
  isAuthenticated,
  migrateTocookies,
  getCurrentUser,
  clearUserCache
} = cookieAuthService