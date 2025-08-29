<template>
  <div class="row g-3">
    <!-- Unread Communications -->
    <div class="col-xl-3 col-md-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div class="flex-shrink-0">
              <div class="avatar avatar-sm avatar-circle bg-primary text-white">
                <i class="bi-envelope"></i>
              </div>
            </div>
            <div class="flex-grow-1 ms-3">
              <span class="d-block h5 mb-0">{{ summary.unreadCount || 0 }}</span>
              <span class="d-block fs-6 text-muted">Unread</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- High Priority -->
    <div class="col-xl-3 col-md-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div class="flex-shrink-0">
              <div class="avatar avatar-sm avatar-circle bg-warning text-white">
                <i class="bi-exclamation-triangle"></i>
              </div>
            </div>
            <div class="flex-grow-1 ms-3">
              <span class="d-block h5 mb-0">{{ summary.highPriorityCount || 0 }}</span>
              <span class="d-block fs-6 text-muted">High Priority</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="col-xl-3 col-md-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div class="flex-shrink-0">
              <div class="avatar avatar-sm avatar-circle bg-info text-white">
                <i class="bi-clock-history"></i>
              </div>
            </div>
            <div class="flex-grow-1 ms-3">
              <span class="d-block h5 mb-0">{{ summary.recentCount || 0 }}</span>
              <span class="d-block fs-6 text-muted">Recent (24h)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sentiment Score -->
    <div class="col-xl-3 col-md-6">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div class="flex-shrink-0">
              <div class="avatar avatar-sm avatar-circle text-white" :class="sentimentBadgeClass">
                <i :class="sentimentIcon"></i>
              </div>
            </div>
            <div class="flex-grow-1 ms-3">
              <span class="d-block h5 mb-0">{{ sentimentDisplay }}</span>
              <span class="d-block fs-6 text-muted">Avg Sentiment</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="col-12 mt-3">
      <div class="d-flex gap-2 flex-wrap">
        <router-link 
          to="/communication-center" 
          class="btn btn-primary btn-sm"
        >
          <i class="bi-envelope me-1"></i>
          View All Communications
        </router-link>
        <button 
          @click="composeEmail" 
          class="btn btn-outline-primary btn-sm"
          :disabled="!client || !client.email"
        >
          <i class="bi-pencil me-1"></i>
          Compose Email
        </button>
        <button 
          @click="refreshData" 
          class="btn btn-outline-secondary btn-sm"
          :disabled="isLoading"
        >
          <i class="bi-arrow-clockwise me-1" :class="{ 'spin': isLoading }"></i>
          Refresh
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useCommunicationStore } from '@/stores/communicationStore';

export default {
  name: 'CommunicationSummaryWidget',
  props: {
    client: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      summary: {
        unreadCount: 0,
        highPriorityCount: 0,
        recentCount: 0,
        averageSentiment: 0
      },
      isLoading: false,
      communicationStore: null
    };
  },
  computed: {
    sentimentDisplay() {
      const sentiment = this.summary.averageSentiment || 0;
      if (sentiment >= 0.7) return 'Positive';
      if (sentiment >= 0.4) return 'Neutral';
      if (sentiment >= 0.2) return 'Negative';
      return 'Mixed';
    },
    sentimentBadgeClass() {
      const sentiment = this.summary.averageSentiment || 0;
      if (sentiment >= 0.7) return 'bg-success';
      if (sentiment >= 0.4) return 'bg-info';
      if (sentiment >= 0.2) return 'bg-warning';
      return 'bg-danger';
    },
    sentimentIcon() {
      const sentiment = this.summary.averageSentiment || 0;
      if (sentiment >= 0.7) return 'bi-emoji-smile';
      if (sentiment >= 0.4) return 'bi-emoji-neutral';
      if (sentiment >= 0.2) return 'bi-emoji-frown';
      return 'bi-emoji-angry';
    }
  },
  async created() {
    this.communicationStore = useCommunicationStore();
    await this.loadSummary();
  },
  watch: {
    client: {
      handler() {
        if (this.client) {
          this.loadSummary();
        }
      },
      deep: true
    }
  },
  methods: {
    async loadSummary() {
      if (!this.client) return;
      
      this.isLoading = true;
      try {
        // Load various communication counts for this client
        const promises = [
          // Unread communications
          this.communicationStore.fetchCommunications({
            client_id: this.client.id,
            is_read: false,
            limit: 1
          }),
          // High priority communications
          this.communicationStore.fetchCommunications({
            client_id: this.client.id,
            priority: 'high',
            limit: 1
          }),
          // Recent communications (24h)
          this.communicationStore.fetchCommunications({
            client_id: this.client.id,
            created_after: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            limit: 1
          })
        ];

        await Promise.all(promises);

        // Get analytics for sentiment
        const analytics = await this.communicationStore.getAnalytics({
          client_id: this.client.id,
          days: 30
        });

        this.summary = {
          unreadCount: this.getCountFromStore('unread'),
          highPriorityCount: this.getCountFromStore('priority'),
          recentCount: this.getCountFromStore('recent'),
          averageSentiment: analytics?.sentiment_stats?.average || 0
        };

      } catch (error) {
        console.error('Error loading communication summary:', error);
        // Use fallback values
        this.summary = {
          unreadCount: 0,
          highPriorityCount: 0,
          recentCount: 0,
          averageSentiment: 0
        };
      } finally {
        this.isLoading = false;
      }
    },
    getCountFromStore(type) {
      // This is a simplified approach - in a real implementation,
      // you might want to store separate counts in the store
      return this.communicationStore.totalCount || 0;
    },
    async refreshData() {
      await this.loadSummary();
    },
    composeEmail() {
      // Emit event to parent or navigate to compose
      this.$emit('compose-email', this.client);
      
      // Or navigate directly
      this.$router.push({
        path: '/communication-center',
        query: { 
          compose: 'true',
          to: this.client.email,
          client_id: this.client.id
        }
      });
    }
  }
};
</script>

<style scoped>
.avatar {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.avatar i {
  font-size: 1.1rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.h5 {
  font-weight: 600;
  color: #212529;
}

.text-muted {
  font-size: 0.875rem;
}

.btn-sm {
  font-size: 0.875rem;
  padding: 0.375rem 0.75rem;
}
</style>