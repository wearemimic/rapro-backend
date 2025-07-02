<template>
  <div class="container-fluid">
    <!-- Row 1: Social Security Findings & Documents/Dates -->
    <div class="row mb-4">
      <!-- Social Security Findings Card -->
      <div class="col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Social Security Findings</h5>
          </div>
          <div class="card-body">
            <ul>
              <li>Key Social Security analysis results will appear here.</li>
              <li>Claiming age recommendations, breakeven points, and benefit estimates.</li>
              <li>Any special considerations (e.g., WEP/GPO, spousal, survivor, etc.).</li>
            </ul>
          </div>
        </div>
      </div>
      <!-- Documents Needed & Dates to Remember Card (split) -->
      <div class="col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Documents Needed</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <!-- Documents Needed -->
              <div class="mb-3">
                <ul class="list-group">
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Social Security Statement</strong>
                      <div class="text-muted small">Verifies earnings history and benefit estimates.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Birth Certificate(s)</strong>
                      <div class="text-muted small">Proof of age and citizenship for benefit eligibility.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Marriage/Divorce/Death Certificates</strong>
                      <div class="text-muted small">Needed for spousal, survivor, or divorced spouse benefits.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Recent Tax Returns</strong>
                      <div class="text-muted small">Confirms income for IRMAA, benefit calculations, and eligibility.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Other Relevant Documents</strong>
                      <div class="text-muted small">Any additional paperwork supporting the client's case.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Row 2: Medicare / IRMAA Findings & Documents/Dates -->
    <div class="row mb-4">
      <!-- Medicare / IRMAA Findings Card -->
      <div class="col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Medicare / IRMAA Findings</h5>
          </div>
          <div class="card-body">
            <ul>
              <li>Key Medicare and IRMAA analysis results will appear here.</li>
              <li>IRMAA bracket status, projected premium surcharges, and planning opportunities.</li>
              <li>Medicare enrollment reminders and special considerations (e.g., late enrollment penalties, IRMAA appeals, etc.).</li>
            </ul>
          </div>
        </div>
      </div>
      <!-- Documents Needed & Dates to Remember Card (split, same as above) -->
      <div class="col-md-6 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Documents Needed</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <!-- Documents Needed -->
              <div class="mb-3">
                
                <ul class="list-group">
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Social Security Statement</strong>
                      <div class="text-muted small">Verifies earnings history and benefit estimates.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Birth Certificate(s)</strong>
                      <div class="text-muted small">Proof of age and citizenship for benefit eligibility.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Marriage/Divorce/Death Certificates</strong>
                      <div class="text-muted small">Needed for spousal, survivor, or divorced spouse benefits.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Recent Tax Returns</strong>
                      <div class="text-muted small">Confirms income for IRMAA, benefit calculations, and eligibility.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                  <li class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Other Relevant Documents</strong>
                      <div class="text-muted small">Any additional paperwork supporting the client's case.</div>
                    </div>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                  </li>
                </ul>
              </div>
              <!-- Dates to Remember -->
              <div class="col-12 col-lg-6">
                <h6>Dates to Remember</h6>
                <ul>
                  <li>Full Retirement Age: <span class="text-muted">(TBD)</span></li>
                  <li>Earliest Claiming Age: <span class="text-muted">(TBD)</span></li>
                  <li>Medicare Enrollment: <span class="text-muted">(TBD)</span></li>
                  <li>Other key deadlines</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Future rows will go here -->
  </div>
</template>

<script>
export default {
  name: 'NextStepsTab',
};
</script>

<style scoped>
/* Add any styles for Next Steps here if needed */
</style> 