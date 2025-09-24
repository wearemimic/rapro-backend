/**
 * Secure Cookie-based Authentication Store
 * Replaces localStorage with httpOnly cookies
 */

import { defineStore } from 'pinia'
import cookieAuthService from '@/services/cookieAuth'
import router from '@/router'

export const useCookieAuthStore = defineStore('cookieAuth', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    isAuthenticated: false,

    // Migration state
    migrationNeeded: false,
    migrationAttempted: false
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => state.isAuthenticated && !!state.user,
    userDisplayName: (state) => {
      if (!state.user) return ''
      return `${state.user.first_name} ${state.user.last_name}`.trim() || state.user.email
    },
    isAdminUser: (state) => state.user?.is_staff || false
  },

  actions: {
    /**
     * Initialize auth state on app startup
     */
    async init() {
      this.loading = true
      this.error = null

      try {
        // Check if migration is needed
        await this.checkMigration()

        // Verify authentication
        await this.verifyAuth()
      } catch (error) {
        console.log('Not authenticated on init:', error.message)
        this.isAuthenticated = false
        this.user = null
      } finally {
        this.loading = false
      }
    },

    /**
     * Check if user needs to migrate from localStorage to cookies
     */
    async checkMigration() {
      const hasLocalStorageTokens = !!(localStorage.getItem('token') && localStorage.getItem('refresh_token'))
      const hasCookieAuth = cookieAuthService.isAuthenticated()

      if (hasLocalStorageTokens && !hasCookieAuth && !this.migrationAttempted) {
        this.migrationNeeded = true

        try {
          console.log('Migrating to cookie authentication...')
          await this.migrateToSecureAuth()
          console.log('Migration successful')
        } catch (error) {
          console.error('Migration failed:', error)
          // Clear localStorage on failed migration
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        }

        this.migrationAttempted = true
      }
    },

    /**
     * Migrate from localStorage to cookie authentication
     */
    async migrateToSecureAuth() {
      try {
        const userData = await cookieAuthService.migrateTocookies()

        this.user = userData.user
        this.isAuthenticated = true
        this.migrationNeeded = false

        // Show success message
        console.log('Successfully migrated to secure cookie authentication!')

        return userData
      } catch (error) {
        console.error('Migration to cookie auth failed:', error)
        throw error
      }
    },

    /**
     * Verify current authentication status
     */
    async verifyAuth() {
      try {
        const authData = await cookieAuthService.verifyAuth()

        this.user = authData.user
        this.isAuthenticated = true
        this.error = null

        return authData
      } catch (error) {
        this.isAuthenticated = false
        this.user = null
        throw error
      }
    },

    /**
     * Login with email and password
     */
    async login(email, password) {
      this.loading = true
      this.error = null

      try {
        const userData = await cookieAuthService.login(email, password)

        this.user = userData.user
        this.isAuthenticated = true

        return userData
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Exchange Auth0 code for authentication
     */
    async auth0Exchange(code, flowType = 'login', affiliateCode = null) {
      this.loading = true
      this.error = null

      try {
        const userData = await cookieAuthService.auth0Exchange(code, flowType, affiliateCode)

        this.user = userData.user
        this.isAuthenticated = true

        return userData
      } catch (error) {
        this.error = error.response?.data?.error || 'Auth0 authentication failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Logout user
     */
    async logout() {
      this.loading = true

      try {
        await cookieAuthService.logout()
      } catch (error) {
        console.warn('Logout request failed:', error)
      } finally {
        // Always clear local state
        this.user = null
        this.isAuthenticated = false
        this.error = null
        this.loading = false

        // Clear any cached data
        cookieAuthService.clearUserCache()

        // Redirect to login
        router.push('/login')
      }
    },

    /**
     * Refresh user data
     */
    async refreshUser() {
      try {
        const user = await cookieAuthService.getCurrentUser()
        this.user = user
        return user
      } catch (error) {
        console.error('Failed to refresh user:', error)
        throw error
      }
    },

    /**
     * Clear error state
     */
    clearError() {
      this.error = null
    },

    /**
     * Force logout (for expired sessions, etc.)
     */
    forceLogout() {
      this.user = null
      this.isAuthenticated = false
      this.error = null

      cookieAuthService.clearUserCache()
      router.push('/login')
    }
  }
})