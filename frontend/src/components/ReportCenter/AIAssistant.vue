<template>
  <div class="ai-assistant" :class="{ 'expanded': isExpanded }">
    <!-- AI Assistant Toggle Button -->
    <button 
      @click="toggleAssistant"
      class="ai-toggle-btn"
      :class="{ 'active': isExpanded }"
      title="AI Assistant"
    >
      <i class="bi-robot"></i>
      <span v-if="!isExpanded" class="assistant-label">AI Assistant</span>
      <i v-if="isExpanded" class="bi-x-lg ms-2"></i>
    </button>

    <!-- AI Assistant Panel -->
    <div v-if="isExpanded" class="ai-panel">
      <div class="panel-header">
        <h6 class="mb-0">
          <i class="bi-robot me-2"></i>AI Assistant
        </h6>
        <small class="text-muted">Intelligent content generation</small>
      </div>

      <div class="panel-content">
        <!-- Quick Actions -->
        <div class="quick-actions mb-4">
          <h6 class="section-title">Quick Actions</h6>
          <div class="action-buttons">
            <button 
              @click="generateExecutiveSummary"
              :disabled="loading || !canGenerateContent"
              class="btn btn-outline-primary btn-sm w-100 mb-2"
            >
              <i class="bi-file-text me-2"></i>
              <span v-if="!loading">Generate Executive Summary</span>
              <span v-else class="d-flex align-items-center justify-content-center">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Generating...
              </span>
            </button>
            
            <button 
              @click="recommendSlideOrder"
              :disabled="loading || !canGenerateContent"
              class="btn btn-outline-success btn-sm w-100 mb-2"
            >
              <i class="bi-list-ol me-2"></i>Recommend Slide Order
            </button>
            
            <button 
              @click="generateClientInsights"
              :disabled="loading || !canGenerateContent"
              class="btn btn-outline-info btn-sm w-100 mb-2"
            >
              <i class="bi-lightbulb me-2"></i>Generate Client Insights
            </button>
          </div>
        </div>

        <!-- Content Generation -->
        <div class="content-generation mb-4" v-if="showContentGeneration">
          <h6 class="section-title">Content Generation</h6>
          
          <div class="mb-3">
            <label class="form-label">Section Type</label>
            <select v-model="selectedSectionType" class="form-select form-select-sm">
              <option value="">Select section type...</option>
              <option value="risk_explanation">Risk Explanation</option>
              <option value="irmaa_impact">IRMAA Impact</option>
              <option value="roth_strategy">Roth Strategy</option>
              <option value="tax_optimization">Tax Optimization</option>
              <option value="social_security">Social Security</option>
              <option value="monte_carlo_interpretation">Monte Carlo Analysis</option>
            </select>
          </div>

          <div class="mb-3">
            <label class="form-label">Tone</label>
            <select v-model="selectedTone" class="form-select form-select-sm">
              <option value="professional">Professional</option>
              <option value="friendly">Friendly</option>
              <option value="technical">Technical</option>
              <option value="simple">Simple</option>
            </select>
          </div>

          <button 
            @click="generateSectionContent"
            :disabled="loading || !selectedSectionType"
            class="btn btn-primary btn-sm w-100"
          >
            <i class="bi-magic me-2"></i>Generate Content
          </button>
        </div>

        <!-- AI Recommendations -->
        <div class="ai-recommendations" v-if="recommendations.length > 0">
          <h6 class="section-title">
            <i class="bi-stars me-2"></i>AI Recommendations
          </h6>
          
          <div class="recommendation-list">
            <div 
              v-for="(rec, index) in recommendations" 
              :key="index"
              class="recommendation-item"
            >
              <div class="d-flex justify-content-between align-items-start">
                <div class="recommendation-content">
                  <strong>{{ rec.slide_type || rec.title }}</strong>
                  <p class="small text-muted mb-1">{{ rec.reason || rec.description }}</p>
                  <span class="badge bg-primary badge-sm">Priority {{ rec.priority }}</span>
                </div>
                <button 
                  @click="applyRecommendation(rec)"
                  class="btn btn-outline-primary btn-sm"
                  title="Apply Recommendation"
                >
                  <i class="bi-plus"></i>
                </button>
              </div>
            </div>
          </div>
          
          <div class="mt-3">
            <button @click="applyAllRecommendations" class="btn btn-success btn-sm w-100">
              <i class="bi-check-all me-2"></i>Apply All Recommendations
            </button>
          </div>
        </div>

        <!-- Generated Content Display -->
        <div class="generated-content" v-if="generatedContent">
          <h6 class="section-title">Generated Content</h6>
          
          <div class="content-preview">
            <div class="content-text">{{ generatedContent.content }}</div>
            <div class="content-meta mt-2">
              <small class="text-muted">
                Type: {{ generatedContent.section_type }} | 
                Tone: {{ generatedContent.tone }} |
                <i class="bi-clock me-1"></i>{{ formatDate(generatedContent.generated_at) }}
              </small>
            </div>
          </div>
          
          <div class="content-actions mt-3">
            <button 
              @click="insertContent"
              class="btn btn-primary btn-sm me-2"
            >
              <i class="bi-plus-square me-1"></i>Insert
            </button>
            <button 
              @click="copyContent"
              class="btn btn-outline-secondary btn-sm me-2"
            >
              <i class="bi-clipboard me-1"></i>Copy
            </button>
            <button 
              @click="regenerateContent"
              class="btn btn-outline-warning btn-sm"
            >
              <i class="bi-arrow-clockwise me-1"></i>Regenerate
            </button>
          </div>
        </div>

        <!-- Usage Statistics -->
        <div class="usage-stats" v-if="showUsageStats">
          <h6 class="section-title">AI Usage</h6>
          <div class="stats-summary">
            <div class="stat-item">
              <span class="stat-value">${{ usageStats.totalCost?.toFixed(4) || '0.0000' }}</span>
              <span class="stat-label">This Month</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ usageStats.totalRequests || 0 }}</span>
              <span class="stat-label">Requests</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useReportCenterStore } from '@/stores/reportCenterStore'

export default {
  name: 'AIAssistant',
  props: {
    clientId: {
      type: Number,
      default: null
    },
    scenarioId: {
      type: Number,
      default: null
    },
    reportId: {
      type: String,
      default: null
    }
  },
  emits: [
    'content-generated',
    'recommendations-applied',
    'executive-summary-generated'
  ],
  setup(props, { emit }) {
    const reportStore = useReportCenterStore()
    
    // State
    const isExpanded = ref(false)
    const loading = ref(false)
    const showContentGeneration = ref(false)
    const showUsageStats = ref(false)
    
    // Form data
    const selectedSectionType = ref('')
    const selectedTone = ref('professional')
    
    // Generated content
    const generatedContent = ref(null)
    const recommendations = ref([])
    const executiveSummary = ref(null)
    const clientInsights = ref(null)
    const usageStats = ref({})
    
    // Computed properties
    const canGenerateContent = computed(() => {
      return props.clientId && props.scenarioId
    })
    
    // Methods
    const toggleAssistant = () => {
      isExpanded.value = !isExpanded.value
      if (isExpanded.value) {
        loadUsageStats()
      }
    }
    
    const generateExecutiveSummary = async () => {
      if (!canGenerateContent.value) return
      
      loading.value = true
      try {
        const response = await reportStore.generateExecutiveSummary({
          client_id: props.clientId,
          scenario_id: props.scenarioId,
          report_id: props.reportId
        })
        
        executiveSummary.value = response
        emit('executive-summary-generated', response)
        
        // Show success message
        console.log('Executive summary generated successfully')
        
      } catch (error) {
        console.error('Failed to generate executive summary:', error)
        // Show error message
      } finally {
        loading.value = false
      }
    }
    
    const recommendSlideOrder = async () => {
      if (!canGenerateContent.value) return
      
      loading.value = true
      try {
        const response = await reportStore.generateSlideRecommendations({
          client_id: props.clientId,
          scenario_id: props.scenarioId,
          report_id: props.reportId
        })
        
        recommendations.value = response.recommendations || []
        
        // Show success message
        console.log(`Generated ${recommendations.value.length} slide recommendations`)
        
      } catch (error) {
        console.error('Failed to generate slide recommendations:', error)
        // Show error message
      } finally {
        loading.value = false
      }
    }
    
    const generateClientInsights = async () => {
      if (!canGenerateContent.value) return
      
      loading.value = true
      try {
        const response = await reportStore.generateClientInsights({
          client_id: props.clientId,
          scenario_id: props.scenarioId,
          report_id: props.reportId
        })
        
        clientInsights.value = response
        
        // Show success message
        console.log('Client insights generated successfully')
        
      } catch (error) {
        console.error('Failed to generate client insights:', error)
        // Show error message
      } finally {
        loading.value = false
      }
    }
    
    const generateSectionContent = async () => {
      if (!selectedSectionType.value) return
      
      loading.value = true
      try {
        const response = await reportStore.generateSectionContent({
          section_type: selectedSectionType.value,
          tone: selectedTone.value,
          data: {}, // You might need to pass specific data based on section type
          report_id: props.reportId
        })
        
        generatedContent.value = response
        emit('content-generated', response)
        
        // Show success message
        console.log('Section content generated successfully')
        
      } catch (error) {
        console.error('Failed to generate section content:', error)
        // Show error message
      } finally {
        loading.value = false
      }
    }
    
    const applyRecommendation = (recommendation) => {
      emit('recommendations-applied', [recommendation])
      // Remove applied recommendation from list
      const index = recommendations.value.findIndex(r => r === recommendation)
      if (index > -1) {
        recommendations.value.splice(index, 1)
      }
    }
    
    const applyAllRecommendations = () => {
      emit('recommendations-applied', recommendations.value)
      recommendations.value = []
    }
    
    const insertContent = () => {
      if (generatedContent.value) {
        emit('content-generated', generatedContent.value)
        generatedContent.value = null
      }
    }
    
    const copyContent = async () => {
      if (generatedContent.value?.content) {
        try {
          await navigator.clipboard.writeText(generatedContent.value.content)
          // Show success message
          console.log('Content copied to clipboard')
        } catch (error) {
          console.error('Failed to copy content:', error)
        }
      }
    }
    
    const regenerateContent = () => {
      generatedContent.value = null
      generateSectionContent()
    }
    
    const loadUsageStats = async () => {
      try {
        const stats = await reportStore.getAIUsageAnalytics()
        usageStats.value = stats.totals || {}
        showUsageStats.value = true
      } catch (error) {
        console.error('Failed to load usage stats:', error)
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString()
    }
    
    // Lifecycle
    onMounted(() => {
      // Auto-expand if we have client and scenario data
      if (canGenerateContent.value) {
        showContentGeneration.value = true
      }
    })
    
    return {
      // State
      isExpanded,
      loading,
      showContentGeneration,
      showUsageStats,
      selectedSectionType,
      selectedTone,
      generatedContent,
      recommendations,
      executiveSummary,
      clientInsights,
      usageStats,
      
      // Computed
      canGenerateContent,
      
      // Methods
      toggleAssistant,
      generateExecutiveSummary,
      recommendSlideOrder,
      generateClientInsights,
      generateSectionContent,
      applyRecommendation,
      applyAllRecommendations,
      insertContent,
      copyContent,
      regenerateContent,
      formatDate
    }
  }
}
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  transition: all 0.3s ease;
}

.ai-toggle-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 12px 16px;
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  cursor: pointer;
  min-width: 60px;
  justify-content: center;
}

.ai-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.ai-toggle-btn.active {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  border-radius: 12px 12px 0 0;
}

.assistant-label {
  margin-left: 8px;
  font-weight: 500;
}

.ai-panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 350px;
  max-height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  text-align: center;
}

.panel-content {
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 12px;
  padding-bottom: 4px;
  border-bottom: 2px solid #e9ecef;
}

.action-buttons button {
  transition: all 0.2s ease;
}

.action-buttons button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.recommendation-list {
  max-height: 200px;
  overflow-y: auto;
}

.recommendation-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  border-left: 4px solid #667eea;
}

.recommendation-content strong {
  color: #495057;
  font-size: 0.875rem;
}

.content-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #28a745;
}

.content-text {
  font-size: 0.875rem;
  line-height: 1.5;
  color: #495057;
}

.content-meta {
  font-size: 0.75rem;
  opacity: 0.8;
}

.content-actions button {
  font-size: 0.75rem;
}

.usage-stats {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stats-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ai-assistant {
    bottom: 10px;
    right: 10px;
  }
  
  .ai-panel {
    width: 300px;
    max-height: 400px;
  }
  
  .panel-content {
    padding: 15px;
    max-height: 300px;
  }
}

/* Loading states */
.spinner-border-sm {
  width: 0.75rem;
  height: 0.75rem;
}

/* Form controls */
.form-select-sm,
.btn-sm {
  font-size: 0.875rem;
}

/* Badge styling */
.badge-sm {
  font-size: 0.65rem;
  padding: 0.25rem 0.4rem;
}
</style>