<template>
  <div class="affiliate-detail">
    <!-- Loading State -->
    <div v-if="loading" class="text-center p-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Affiliate Details -->
    <div v-else-if="affiliate">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 class="h3 mb-2">{{ affiliate.business_name }}</h1>
          <div class="text-muted">
            <span class="me-3">
              <i class="fas fa-envelope me-1"></i>
              {{ affiliate.email }}
            </span>
            <span class="me-3">
              <i class="fas fa-tag me-1"></i>
              <code>{{ affiliate.affiliate_code }}</code>
            </span>
            <span
              class="badge"
              :class="{
                'bg-success': affiliate.status === 'active',
                'bg-warning': affiliate.status === 'pending',
                'bg-danger': affiliate.status === 'suspended'
              }"
            >
              {{ affiliate.status }}
            </span>
          </div>
        </div>
        <div>
          <button class="btn btn-outline-primary me-2" @click="editAffiliate">
            <i class="fas fa-edit me-2"></i>Edit
          </button>
          <button class="btn btn-primary" @click="showLinkModal = true">
            <i class="fas fa-link me-2"></i>Generate Link
          </button>
        </div>
      </div>

      <!-- Nav Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'overview' }"
            href="#"
            @click.prevent="activeTab = 'overview'"
          >
            Overview
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'performance' }"
            href="#"
            @click.prevent="activeTab = 'performance'"
          >
            Performance
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'links' }"
            href="#"
            @click.prevent="activeTab = 'links'"
          >
            Links
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: activeTab === 'commissions' }"
            href="#"
            @click.prevent="activeTab = 'commissions'"
          >
            Commissions
          </a>
        </li>
      </ul>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'overview'" class="tab-pane active">
          <div class="row">
            <div class="col-md-6">
              <div class="card mb-4">
                <div class="card-header">
                  <h5 class="mb-0">Contact Information</h5>
                </div>
                <div class="card-body">
                  <dl class="row mb-0">
                    <dt class="col-sm-4">Contact Name</dt>
                    <dd class="col-sm-8">{{ affiliate.contact_name || '-' }}</dd>
                    
                    <dt class="col-sm-4">Email</dt>
                    <dd class="col-sm-8">{{ affiliate.email }}</dd>
                    
                    <dt class="col-sm-4">Phone</dt>
                    <dd class="col-sm-8">{{ affiliate.phone || '-' }}</dd>
                    
                    <dt class="col-sm-4">Website</dt>
                    <dd class="col-sm-8">
                      <a v-if="affiliate.website_url" :href="affiliate.website_url" target="_blank">
                        {{ affiliate.website_url }}
                      </a>
                      <span v-else>-</span>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            
            <div class="col-md-6">
              <div class="card mb-4">
                <div class="card-header">
                  <h5 class="mb-0">Commission Settings</h5>
                </div>
                <div class="card-body">
                  <dl class="row mb-0">
                    <dt class="col-sm-6">Commission Type</dt>
                    <dd class="col-sm-6">{{ affiliate.commission_type }}</dd>
                    
                    <dt class="col-sm-6">First Month Rate</dt>
                    <dd class="col-sm-6">{{ affiliate.commission_rate_first_month }}%</dd>
                    
                    <dt class="col-sm-6">Recurring Rate</dt>
                    <dd class="col-sm-6">{{ affiliate.commission_rate_recurring }}%</dd>
                    
                    <dt class="col-sm-6">Minimum Payout</dt>
                    <dd class="col-sm-6">${{ affiliate.minimum_payout }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats Cards -->
          <div class="row">
            <div class="col-md-3">
              <div class="card">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ affiliate.total_clicks || 0 }}</h3>
                  <small class="text-muted">Total Clicks</small>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ affiliate.total_conversions || 0 }}</h3>
                  <small class="text-muted">Conversions</small>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card">
                <div class="card-body text-center">
                  <h3 class="mb-0">${{ formatNumber(affiliate.total_revenue_generated || 0) }}</h3>
                  <small class="text-muted">Revenue Generated</small>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card">
                <div class="card-body text-center">
                  <h3 class="mb-0">${{ formatNumber(affiliate.total_commissions_earned || 0) }}</h3>
                  <small class="text-muted">Commissions Earned</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Tab -->
        <div v-if="activeTab === 'performance'" class="tab-pane active">
          <div v-if="dashboardData">
            <div class="card">
              <div class="card-header">
                <h5 class="mb-0">Performance Metrics (Last 30 Days)</h5>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-3">
                    <strong>Clicks:</strong> {{ dashboardData.performance_metrics?.clicks_last_30_days || 0 }}
                  </div>
                  <div class="col-md-3">
                    <strong>Conversions:</strong> {{ dashboardData.performance_metrics?.conversions_last_30_days || 0 }}
                  </div>
                  <div class="col-md-3">
                    <strong>Revenue:</strong> ${{ dashboardData.performance_metrics?.revenue_last_30_days || 0 }}
                  </div>
                  <div class="col-md-3">
                    <strong>Conversion Rate:</strong> {{ dashboardData.performance_metrics?.conversion_rate || 0 }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center p-5">
            <button class="btn btn-primary" @click="loadDashboard">
              Load Performance Data
            </button>
          </div>
        </div>

        <!-- Links Tab -->
        <div v-if="activeTab === 'links'" class="tab-pane active">
          <div class="card">
            <div class="card-body">
              <div v-if="links.length === 0" class="text-center p-4">
                <p>No tracking links created yet.</p>
                <button class="btn btn-primary" @click="showLinkModal = true">
                  <i class="fas fa-plus me-2"></i>Create First Link
                </button>
              </div>
              <div v-else class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Campaign</th>
                      <th>Tracking Code</th>
                      <th>Clicks</th>
                      <th>Conversions</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="link in links" :key="link.id">
                      <td>{{ link.campaign_name }}</td>
                      <td>
                        <code>{{ link.tracking_code }}</code>
                        <button
                          class="btn btn-sm btn-link"
                          @click="copyLink(link.tracking_code)"
                        >
                          <i class="fas fa-copy"></i>
                        </button>
                      </td>
                      <td>{{ link.total_clicks || 0 }}</td>
                      <td>{{ link.conversions || 0 }}</td>
                      <td>
                        <span
                          class="badge"
                          :class="link.is_active ? 'bg-success' : 'bg-secondary'"
                        >
                          {{ link.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>
                        <button
                          class="btn btn-sm btn-outline-secondary"
                          @click="toggleLinkStatus(link)"
                        >
                          {{ link.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Commissions Tab -->
        <div v-if="activeTab === 'commissions'" class="tab-pane active">
          <div class="card">
            <div class="card-body">
              <div v-if="commissions.length === 0" class="text-center p-4">
                <p>No commissions earned yet.</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="commission in commissions" :key="commission.id">
                      <td>{{ formatDate(commission.created_at) }}</td>
                      <td>{{ commission.commission_type }}</td>
                      <td>{{ commission.description }}</td>
                      <td>${{ formatNumber(commission.commission_amount) }}</td>
                      <td>
                        <span
                          class="badge"
                          :class="{
                            'bg-warning': commission.status === 'pending',
                            'bg-info': commission.status === 'approved',
                            'bg-success': commission.status === 'paid'
                          }"
                        >
                          {{ commission.status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAffiliateStore } from '@/stores/affiliateStore'
import affiliateService from '@/services/affiliateService'

export default {
  name: 'AffiliateDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const affiliateStore = useAffiliateStore()
    
    // Data
    const activeTab = ref('overview')
    const showLinkModal = ref(false)
    const links = ref([])
    const commissions = ref([])
    const dashboardData = ref(null)
    
    // Computed
    const affiliate = computed(() => affiliateStore.currentAffiliate)
    const loading = computed(() => affiliateStore.loading)
    const error = computed(() => affiliateStore.error)
    const affiliateId = computed(() => route.params.id)
    
    // Methods
    const loadAffiliate = async () => {
      await affiliateStore.fetchAffiliateDetails(affiliateId.value)
    }
    
    const loadDashboard = async () => {
      dashboardData.value = await affiliateStore.fetchDashboardData(affiliateId.value)
    }
    
    const loadLinks = async () => {
      links.value = await affiliateStore.fetchAffiliateLinks(affiliateId.value)
    }
    
    const loadCommissions = async () => {
      commissions.value = await affiliateStore.fetchCommissions(affiliateId.value)
    }
    
    const editAffiliate = () => {
      router.push(`/affiliates/${affiliateId.value}/edit`)
    }
    
    const copyLink = async (trackingCode) => {
      try {
        await affiliateService.copyTrackingLink(trackingCode)
        alert('Link copied to clipboard!')
      } catch (error) {
        alert('Failed to copy link')
      }
    }
    
    const toggleLinkStatus = async (link) => {
      await affiliateStore.toggleLinkStatus(link.id, !link.is_active)
      await loadLinks()
    }
    
    const formatNumber = (num) => {
      return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }
    
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
    
    // Watch tab changes
    watch(activeTab, (newTab) => {
      if (newTab === 'performance' && !dashboardData.value) {
        loadDashboard()
      } else if (newTab === 'links' && links.value.length === 0) {
        loadLinks()
      } else if (newTab === 'commissions' && commissions.value.length === 0) {
        loadCommissions()
      }
    })
    
    // Lifecycle
    onMounted(() => {
      loadAffiliate()
    })
    
    return {
      activeTab,
      showLinkModal,
      links,
      commissions,
      dashboardData,
      affiliate,
      loading,
      error,
      editAffiliate,
      loadDashboard,
      copyLink,
      toggleLinkStatus,
      formatNumber,
      formatDate
    }
  }
}
</script>

<style scoped>
.affiliate-detail {
  padding: 20px;
}

code {
  padding: 2px 6px;
  background-color: #f5f5f5;
  border-radius: 3px;
}
</style>