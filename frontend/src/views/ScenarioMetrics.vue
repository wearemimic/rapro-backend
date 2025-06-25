<template>
  <div class="row" id="scenariometrics">
    <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
      <!-- Card -->
      <div class="card card-sm h-100">
        <div class="card-body">
          <div class="row d-flex align-items-stretch">
            <div class="col">
              <!-- Media -->
              <div class="d-flex">
                <div class="flex-shrink-0">
                  <i class="bi-receipt nav-icon"></i>
                </div>
                <div class="flex-grow-1 ms-3">
                  <h4 class="mb-1">Federal Taxes</h4>
                  <span class="d-block" style="font-size: 1.5rem;">{{ formatCurrency(totalFederalTaxes) }}</span>
                </div>
              </div>
              <!-- End Media -->
            </div>
          </div>
          <!-- End Row -->
        </div>
      </div>
      <!-- End Card -->
    </div>

    <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
      <!-- Card -->
      <div class="card card-sm h-100">
        <div class="card-body">
          <div class="row d-flex align-items-stretch">
            <div class="col">
              <!-- Media -->
              <div class="d-flex">
                <div class="flex-shrink-0">
                  <i class="bi-bar-chart nav-icon"></i>
                </div>

                <div class="flex-grow-1 ms-3">
                  <h4 class="mb-1">Medicare Costs</h4>
                  <span class="d-block" style="font-size: 1.5rem;">{{ formatCurrency(totalMedicareCosts) }}</span>
                </div>
              </div>
              <!-- End Media -->
            </div>
            <!-- End Col -->

            <div class="col-auto">
              <!-- Circle -->

              <!-- End Circle -->
            </div>
            <!-- End Col -->
          </div>
          <!-- End Row -->
        </div>
      </div>
      <!-- End Card -->
    </div>

    <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
      <!-- Card -->
      <div class="card card-sm h-100">
        <div class="card-body">
          <div class="row d-flex align-items-stretch">
            <div class="col">
              <!-- Media -->
              <div class="d-flex">
                <div class="flex-shrink-0">
                  <i class="bi-check2-circle nav-icon"></i>
                </div>

                <div class="flex-grow-1 ms-3">
                  <h4 class="mb-1">Out Of Pocket</h4>
                  <span class="d-block" style="font-size: 1.5rem;">$50,000</span>
                </div>
              </div>
              <!-- End Media -->
            </div>
            <!-- End Col -->

            <div class="col-auto">
              <!-- Circle -->

              <!-- End Circle -->
            </div>
            <!-- End Col -->
          </div>
          <!-- End Row -->
        </div>
      </div>
      <!-- End Card -->
    </div>
    <div class="col-sm-6 col-xl-3 mb-3 mb-xl-6">
      <!-- Card -->
      <div class="card card-sm h-100">
        <div class="card-body">
          <div class="row d-flex align-items-stretch">
            <div class="col">
              <!-- Media -->
              <div class="d-flex">
                <div class="flex-shrink-0">
                  <i class="bi-check2-circle nav-icon"></i>
                </div>

                <div class="flex-grow-1 ms-3">
                  <h4 class="mb-1">IRMAA Status</h4>
                  <!-- Dynamic Rectangle -->
                  <div :style="{width: '90%', height: '30px', backgroundColor: irmaaColor, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'}">
                  </div>
                  <!-- End Dynamic Rectangle -->
                </div>
              </div>
              <!-- End Media -->
            </div>
            <!-- End Col -->

          </div>
          <!-- End Row -->
        </div>
      </div>
      <!-- End Card -->
    </div>
  </div>
</template>

<script>
export default {
  props: {
    totalFederalTaxes: {
      type: Number,
      required: true
    },
    totalMedicareCosts: {
      type: Number,
      required: true
    },
    totalIrmaaSurcharge: {
      type: Number,
      required: true
    },
    totalMedicareCost: {
      type: Number,
      required: true
    }
  },
  computed: {
    irmaaPercentage() {
      if (!this.totalMedicareCost) return 0;
      return Math.round((this.totalIrmaaSurcharge / this.totalMedicareCost) * 100);
    },
    irmaaColor() {
      const pct = this.irmaaPercentage;
      if (pct > 50) {
        return '#ff0000'; // Red
      } else if (pct > 25) {
        return '#ffa500'; // Orange
      } else if (pct > 15) {
        return '#ffff00'; // Yellow
      } else {
        return '#00ff00'; // Green
      }
    }
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    }
  }
};
</script> 