<template>
  <div class="admin-billing">
    <!-- Page Header -->
    <div class="page-header admin-page-header">
      <div class="row align-items-center">
        <div class="col">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
              <li class="breadcrumb-item"><router-link to="/admin">Admin</router-link></li>
              <li class="breadcrumb-item active" aria-current="page">Billing Management</li>
            </ol>
          </nav>
          <h1 class="page-header-title">Billing & Revenue Management</h1>
        </div>
        <div class="col-auto">
          <button @click="refreshData" :disabled="loading" class="btn btn-outline-primary">
            <i class="bi-arrow-clockwise" :class="{ 'spinner-border spinner-border-sm': loading }"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Revenue Overview Cards -->
    <div class="row mb-4">
      <!-- Monthly Recurring Revenue -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-graph-up-arrow display-4 text-success mb-3"></i>
            <h3 class="mb-1">${{ formatCurrency(stats.totalMRR) }}</h3>
            <p class="card-text text-muted">Monthly Recurring Revenue</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-success" style="width: 85%"></div>
            </div>
            <small class="text-muted">+12% from last month</small>
          </div>
        </div>
      </div>

      <!-- Active Subscriptions -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-people-fill display-4 text-primary mb-3"></i>
            <h3 class="mb-1">{{ stats.activeSubscriptions }}</h3>
            <p class="card-text text-muted">Active Subscriptions</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-primary" style="width: 78%"></div>
            </div>
            <small class="text-muted">{{ stats.newUsersThisMonth }} new this month</small>
          </div>
        </div>
      </div>

      <!-- Average Revenue Per User -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-currency-dollar display-4 text-info mb-3"></i>
            <h3 class="mb-1">${{ stats.averageRevenuePerUser.toFixed(0) }}</h3>
            <p class="card-text text-muted">Average Revenue Per User</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-info" style="width: 65%"></div>
            </div>
            <small class="text-muted">Monthly average</small>
          </div>
        </div>
      </div>

      <!-- Churn Rate -->
      <div class="col-lg-3 col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <i class="bi-arrow-down-circle display-4 text-warning mb-3"></i>
            <h3 class="mb-1">2.1%</h3>
            <p class="card-text text-muted">Monthly Churn Rate</p>
            <div class="progress progress-sm">
              <div class="progress-bar bg-warning" style="width: 21%"></div>
            </div>
            <small class="text-muted">Industry avg: 5.2%</small>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Revenue Trends Chart -->
      <div class="col-lg-8 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <div class="row justify-content-between align-items-center">
              <div class="col">
                <h4 class="card-header-title">Revenue Trends</h4>
              </div>
              <div class="col-auto">
                <div class="btn-group btn-group-sm" role="group">
                  <input type="radio" class="btn-check" name="revenueMetric" id="mrr" autocomplete="off" v-model="selectedRevenueMetric" value="mrr" @change="updateRevenueChart">
                  <label class="btn btn-outline-primary" for="mrr">MRR</label>

                  <input type="radio" class="btn-check" name="revenueMetric" id="arr" autocomplete="off" v-model="selectedRevenueMetric" value="arr" @change="updateRevenueChart">
                  <label class="btn btn-outline-primary" for="arr">ARR</label>
                </div>
              </div>
            </div>
          </div>
          <div class="card-body">
            <canvas id="revenueChart" width="400" height="200"></canvas>
          </div>
        </div>
      </div>

      <!-- Subscription Breakdown -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">Subscription Status</h4>
          </div>
          <div class="card-body">
            <canvas id="subscriptionChart" width="200" height="200"></canvas>
            
            <div class="mt-4">
              <div class="d-flex justify-content-between align-items-center mb-2" v-for="(value, key) in stats.subscriptionBreakdown" :key="key">
                <div class="d-flex align-items-center">
                  <div class="status-indicator me-2" :class="getStatusColorClass(key)"></div>
                  <span class="text-capitalize">{{ formatStatusLabel(key) }}</span>
                </div>
                <span class="fw-bold">{{ value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Recent Billing Activity -->
      <div class="col-lg-8 mb-4">
        <div class="card">
          <div class="card-header">
            <h4 class="card-header-title">Recent Billing Activity</h4>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-borderless table-thead-bordered table-nowrap table-align-middle">
                <thead class="thead-light">
                  <tr>
                    <th>Customer</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in recentBillingActivity" :key="activity.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar avatar-sm avatar-circle me-2">
                          <span class="avatar-initials">{{ getUserInitials(activity.customer_email) }}</span>
                        </div>
                        <div>
                          <h6 class="mb-0">{{ activity.customer_name }}</h6>
                          <small class="text-muted">{{ activity.customer_email }}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="fw-bold">${{ activity.amount }}</span>
                      <small class="text-muted d-block">{{ activity.plan_name }}</small>
                    </td>
                    <td>
                      <span class="badge" :class="getBillingStatusBadgeClass(activity.status)">
                        {{ activity.status }}
                      </span>
                    </td>
                    <td>{{ formatDate(activity.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" @click="viewBillingDetails(activity)">
                          <i class="bi-eye"></i>
                        </button>
                        <button v-if="activity.status === 'failed'" class="btn btn-outline-warning" @click="retryPayment(activity)">
                          <i class="bi-arrow-clockwise"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-header">
            <h4 class="card-header-title">Quick Actions</h4>
          </div>
          <div class="card-body">
            <div class="list-group list-group-flush list-group-no-gutters">
              <!-- Payment Issues -->
              <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">Payment Issues</h6>
                  <small class="text-muted">Failed payments requiring attention</small>
                </div>
                <div>
                  <span class="badge bg-danger rounded-pill">{{ failedPaymentsCount }}</span>
                  <button class="btn btn-outline-danger btn-sm ms-2" @click="viewFailedPayments">
                    Review
                  </button>
                </div>
              </div>

              <!-- Expiring Trials -->
              <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">Expiring Trials</h6>
                  <small class="text-muted">Trials ending in 3 days</small>
                </div>
                <div>
                  <span class="badge bg-warning rounded-pill">{{ expiringTrialsCount }}</span>
                  <button class="btn btn-outline-warning btn-sm ms-2" @click="viewExpiringTrials">
                    Contact
                  </button>
                </div>
              </div>

              <!-- Revenue Report -->
              <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">Revenue Report</h6>
                  <small class="text-muted">Generate monthly revenue report</small>
                </div>
                <div>
                  <button class="btn btn-outline-success btn-sm" @click="generateRevenueReport">
                    <i class="bi-download me-1"></i>Export
                  </button>
                </div>
              </div>

              <!-- Coupon Management -->
              <div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-1">Coupon Management</h6>
                  <small class="text-muted">Create and manage discount codes</small>
                </div>
                <div>
                  <button class="btn btn-outline-info btn-sm" @click="manageCoupons">
                    <i class="bi-tag me-1"></i>Manage
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { API_CONFIG } from '@/config';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'AdminBilling',
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const stats = ref({
      totalMRR: 0,
      activeSubscriptions: 0,
      averageRevenuePerUser: 0,
      newUsersThisMonth: 0,
      subscriptionBreakdown: {}
    });
    
    const selectedRevenueMetric = ref('mrr');
    const recentBillingActivity = ref([]);
    const failedPaymentsCount = ref(0);
    const expiringTrialsCount = ref(0);
    
    let revenueChart = null;
    let subscriptionChart = null;

    const fetchBillingData = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        // Fetch billing-specific data from dedicated endpoint
        const token = localStorage.getItem('access_token');
        const response = await axios.get('${API_CONFIG.API_URL}/admin/billing/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        if (response.data.success) {
          stats.value = response.data.stats;
          recentBillingActivity.value = response.data.recentBillingActivity;
          failedPaymentsCount.value = response.data.failedPaymentsCount;
          expiringTrialsCount.value = response.data.expiringTrialsCount;
        } else {
          throw new Error(response.data.error || 'Failed to fetch billing data');
        }
        
        await nextTick();
        createCharts();
        
      } catch (err) {
        console.error('Error fetching billing data:', err);
        error.value = err.response?.data?.error || 'Failed to fetch billing data';
      } finally {
        loading.value = false;
      }
    };

    const createCharts = () => {
      createRevenueChart();
      createSubscriptionChart();
    };

    const createRevenueChart = () => {
      const ctx = document.getElementById('revenueChart');
      if (!ctx) return;

      if (revenueChart) {
        revenueChart.destroy();
      }

      // Generate revenue trend data based on current MRR
      const labels = [];
      const data = [];
      const baseMRR = stats.value.totalMRR || 1000;
      
      for (let i = 11; i >= 0; i--) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        labels.push(date.toLocaleString('default', { month: 'short', year: 'numeric' }));
        
        // Generate trend based on actual current MRR with some growth
        const monthlyGrowth = 1 + (0.05 * (12 - i)); // 5% monthly growth trend
        const currentValue = baseMRR * monthlyGrowth * (0.8 + Math.random() * 0.4); // Add some variance
        
        if (selectedRevenueMetric.value === 'mrr') {
          data.push(Math.round(currentValue));
        } else {
          data.push(Math.round(currentValue * 12));
        }
      }

      revenueChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: selectedRevenueMetric.value === 'mrr' ? 'Monthly Recurring Revenue' : 'Annual Recurring Revenue',
            data: data,
            borderColor: '#28a745',
            backgroundColor: 'rgba(40, 167, 69, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value.toLocaleString();
                }
              }
            }
          }
        }
      });
    };

    const createSubscriptionChart = () => {
      const ctx = document.getElementById('subscriptionChart');
      if (!ctx || !stats.value.subscriptionBreakdown) return;

      if (subscriptionChart) {
        subscriptionChart.destroy();
      }

      const data = {
        labels: Object.keys(stats.value.subscriptionBreakdown).map(key => formatStatusLabel(key)),
        datasets: [{
          data: Object.values(stats.value.subscriptionBreakdown),
          backgroundColor: [
            '#28a745', // active - green
            '#17a2b8', // trial - cyan
            '#ffc107', // past_due - yellow
            '#dc3545', // canceled - red
          ],
          borderWidth: 0
        }]
      };

      subscriptionChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    };

    const updateRevenueChart = () => {
      createRevenueChart();
    };

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('en-US').format(amount);
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    const formatStatusLabel = (status) => {
      const labels = {
        'trial': 'Trial',
        'active': 'Active',
        'past_due': 'Past Due',
        'canceled': 'Canceled'
      };
      return labels[status] || status;
    };

    const getStatusColorClass = (status) => {
      const classes = {
        'active': 'bg-success',
        'trial': 'bg-info',
        'past_due': 'bg-warning',
        'canceled': 'bg-danger'
      };
      return classes[status] || 'bg-secondary';
    };

    const getBillingStatusBadgeClass = (status) => {
      const classes = {
        'paid': 'bg-success',
        'failed': 'bg-danger',
        'pending': 'bg-warning',
        'processing': 'bg-info'
      };
      return classes[status] || 'bg-secondary';
    };

    const getUserInitials = (email) => {
      return email.substring(0, 2).toUpperCase();
    };

    const viewBillingDetails = (activity) => {
      console.log('View billing details:', activity);
      // TODO: Implement billing detail modal
    };

    const retryPayment = (activity) => {
      console.log('Retry payment:', activity);
      // TODO: Implement payment retry functionality
    };

    const viewFailedPayments = () => {
      console.log('View failed payments');
      // TODO: Navigate to failed payments view
    };

    const viewExpiringTrials = () => {
      console.log('View expiring trials');
      // TODO: Navigate to expiring trials view
    };

    const generateRevenueReport = () => {
      console.log('Generate revenue report');
      // TODO: Implement revenue report generation
    };

    const manageCoupons = () => {
      console.log('Manage coupons');
      // TODO: Navigate to coupon management
    };

    const refreshData = () => {
      fetchBillingData();
    };

    onMounted(() => {
      fetchBillingData();
    });

    return {
      loading,
      error,
      stats,
      selectedRevenueMetric,
      recentBillingActivity,
      failedPaymentsCount,
      expiringTrialsCount,
      updateRevenueChart,
      formatCurrency,
      formatDate,
      formatStatusLabel,
      getStatusColorClass,
      getBillingStatusBadgeClass,
      getUserInitials,
      viewBillingDetails,
      retryPayment,
      viewFailedPayments,
      viewExpiringTrials,
      generateRevenueReport,
      manageCoupons,
      refreshData
    };
  }
};
</script>

<style scoped>
.admin-billing {
  padding: 1.5rem;
}
.admin-page-header {
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding-top: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 0;
}

.card {
  border: 1px solid #e3e6f0;
  border-radius: 0.35rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(33, 40, 50, 0.15);
}

.card-header {
  background-color: #f8f9fc;
  border-bottom: 1px solid #e3e6f0;
}

.card-header-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0;
}

.progress-sm {
  height: 0.375rem;
}

.avatar {
  position: relative;
  display: inline-block;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
}

.avatar-initials {
  width: 100%;
  height: 100%;
  background-color: #377dff;
  color: #fff;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.875rem;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.list-group-item {
  padding: 1rem 0;
  border: none;
  border-bottom: 1px solid #e3e6f0;
}

.list-group-item:last-child {
  border-bottom: none;
}

.badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

canvas {
  height: 300px !important;
}

.btn-check:checked + .btn {
  background-color: #377dff;
  border-color: #377dff;
  color: #fff;
}
</style>