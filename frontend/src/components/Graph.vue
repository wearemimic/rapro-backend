<template>
  <div :style="`height: ${height}px;`">
    <canvas ref="canvas" :height="height" :style="`height: ${height}px;`"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  props: {
    data: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    height: {
      type: Number,
      default: 200
    },
    type: {
      type: String,
      default: 'line'
    },
    // Add a unique ID prop to distinguish between different graph instances
    graphId: {
      type: String,
      default: () => `graph-${Math.random().toString(36).substr(2, 9)}`
    }
  },
  data() {
    return {
      chartInstance: null,
      resizeObserver: null,
      // Track registered plugins to avoid duplicate registration
      registeredPlugins: new Set()
    };
  },
  mounted() {
    console.log('🔧 Graph component mounted with data:', this.data);
    console.log('🔧 Graph component canvas ref:', this.$refs.canvas);
    this.renderChart();
  },
  watch: {
    data: {
      handler(newData, oldData) {
        console.log('📊 Graph data watcher triggered:', {
          newData,
          oldData,
          hasNewLabels: newData?.labels?.length,
          hasNewDatasets: newData?.datasets?.length
        });
        
        // Skip if component is unmounting or canvas not available
        if (!this.$refs.canvas) {
          console.log('⏭️ Skipping data update - canvas not available');
          return;
        }
        
        // Add small delay to ensure tab is visible and canvas is ready
        setTimeout(() => {
          // Double-check canvas is still available after delay
          if (!this.$refs.canvas) {
            console.log('⏭️ Canvas disappeared during delay');
            return;
          }
          // Create a deep copy of the data to avoid reference issues
          const dataCopy = JSON.parse(JSON.stringify(newData));
          this.renderChart(dataCopy);
        }, 50);
      },
      deep: true
    },
    options: {
      handler(newOptions) {
        // Skip if component is unmounting or canvas not available
        if (!this.$refs.canvas) {
          console.log('⏭️ Skipping options update - canvas not available');
          return;
        }
        // Create a deep copy of the options to avoid reference issues
        const optionsCopy = JSON.parse(JSON.stringify(newOptions));
        this.renderChart(undefined, optionsCopy);
      },
      deep: true
    }
  },
  methods: {
    renderChart(dataCopy, optionsCopy) {
      try {
        console.log('🔧 renderChart called with:', { dataCopy, optionsCopy });
        console.log('🔧 this.data:', this.data);
        console.log('🔧 Canvas ref available:', !!this.$refs.canvas);
        
        // CRITICAL: Check if canvas is available before doing anything
        if (!this.$refs.canvas) {
          console.warn('⚠️ Canvas not available, component may be unmounting');
          return;
        }
        
        // Use provided data copies or make copies of the props
        const safeData = dataCopy || (this.data ? JSON.parse(JSON.stringify(this.data)) : null);
        const safeOptions = optionsCopy || (this.options ? JSON.parse(JSON.stringify(this.options)) : {});
        
        console.log('🔧 Safe data:', safeData);
        console.log('🔧 Safe options:', safeOptions);
        
        // Always destroy previous chart instance first to prevent conflicts
        if (this.chartInstance) {
          console.log('🗑️ Destroying previous chart instance');
          try {
            this.chartInstance.destroy();
          } catch (destroyError) {
            console.warn('⚠️ Error destroying chart:', destroyError);
          }
          this.chartInstance = null;
        }
        
        // Validate data before creating new chart
        if (!safeData || !safeData.labels || !safeData.datasets || !safeData.datasets.length) {
          console.warn('⚠️ Invalid or empty chart data, skipping chart creation');
          console.log('🔍 Data details:', {
            safeData,
            hasLabels: safeData?.labels?.length,
            hasDatasets: safeData?.datasets?.length,
            datasets: safeData?.datasets
          });
          return;
        }
        
        // Double-check canvas is still available
        if (!this.$refs.canvas) {
          console.warn('⚠️ Canvas lost during chart setup');
          return;
        }
        
        const options = {
          responsive: true,
          maintainAspectRatio: false,
          ...safeOptions,
          animation: false // Disable animations to prevent canvas context errors
        };
        
        // Support mixed chart types: if any dataset has a 'type', use 'bar' as root type
        let chartType = this.type || 'line';
        if (safeData.datasets.some(ds => ds.type)) {
          chartType = 'bar';
        }
        
        // Register custom plugins if they exist, using the graphId to make them unique
        if (options.plugins && options.plugins.totalColumnHighlight) {
          const pluginId = `totalColumnHighlight-${this.graphId}`;
          
          // Only register if not already registered
          if (!this.registeredPlugins.has(pluginId)) {
            Chart.register({
              id: pluginId,
              beforeDraw: options.plugins.totalColumnHighlight.beforeDraw
            });
            this.registeredPlugins.add(pluginId);
          }
          
          // Update plugin reference in options to use our unique ID
          options.plugins.totalColumnHighlight = {
            ...options.plugins.totalColumnHighlight,
            id: pluginId
          };
        }
        
        // Final canvas check before creating chart
        const canvasEl = this.$refs.canvas;
        if (!canvasEl) {
          console.error('❌ Canvas element disappeared before chart creation');
          return;
        }
        
        // Get 2D context and verify it's available
        const ctx = canvasEl.getContext('2d');
        if (!ctx) {
          console.error('❌ Could not get 2D context from canvas');
          return;
        }
        
        // Check if context is still valid (not lost)
        if (ctx.isContextLost && ctx.isContextLost()) {
          console.error('❌ Canvas context is lost');
          return;
        }
        
        console.log('🚀 Creating Chart.js instance with:', {
          type: chartType,
          data: safeData,
          options,
          canvas: canvasEl,
          ctx: ctx
        });
        
        this.chartInstance = new Chart(ctx, {
          type: chartType,
          data: safeData,
          options
        });
        
        console.log('✅ Chart instance created successfully:', this.chartInstance);
        console.log('📏 Canvas dimensions:', {
          width: canvasEl.width,
          height: canvasEl.height,
          offsetWidth: canvasEl.offsetWidth,
          offsetHeight: canvasEl.offsetHeight,
          clientWidth: canvasEl.clientWidth,
          clientHeight: canvasEl.clientHeight
        });
        
        // If canvas has 0 dimensions, set up a resize observer to fix it when visible
        if (canvasEl.offsetWidth === 0 || canvasEl.offsetHeight === 0) {
          console.log('🔄 Canvas has 0 dimensions, setting up resize observer');
          this.setupResizeObserver();
        }
      } catch (error) {
        console.error('❌ Error rendering chart:', error);
        console.error('❌ Error stack:', error.stack);
      }
    },
    setupResizeObserver() {
      const canvasEl = this.$refs.canvas;
      if (!canvasEl) {
        console.warn('⚠️ Cannot setup resize observer - canvas not available');
        return;
      }

      // Clean up existing observer if any
      if (this.resizeObserver) {
        this.resizeObserver.disconnect();
      }

      console.log('🔄 Setting up ResizeObserver for canvas');
      
      // Create a ResizeObserver to detect when canvas becomes visible
      this.resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          const { width, height } = entry.contentRect;
          console.log('📏 ResizeObserver triggered - Canvas dimensions changed:', { width, height });
          
          // If canvas now has dimensions and we have a chart instance, resize it
          if (width > 0 && height > 0 && this.chartInstance) {
            console.log('✅ Canvas is now visible, resizing chart');
            try {
              this.chartInstance.resize();
              console.log('✅ Chart resized successfully');
              
              // Disconnect observer after successful resize since we only need it once
              this.resizeObserver.disconnect();
              this.resizeObserver = null;
            } catch (error) {
              console.error('❌ Error resizing chart:', error);
            }
          }
        }
      });

      // Start observing the canvas element
      this.resizeObserver.observe(canvasEl);
      console.log('🔄 ResizeObserver started observing canvas');
    }
  },
  beforeUnmount() {
    console.log('🧹 Graph component unmounting, cleaning up chart');
    
    // Clean up resize observer
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
      console.log('✅ ResizeObserver cleaned up');
    }
    
    // Clean up chart instance
    if (this.chartInstance) {
      try {
        this.chartInstance.destroy();
        console.log('✅ Chart destroyed successfully');
      } catch (error) {
        console.warn('⚠️ Error destroying chart on unmount:', error);
      }
      this.chartInstance = null;
    }
  }
};
</script>