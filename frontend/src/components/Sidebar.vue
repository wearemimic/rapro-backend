<template>
  <aside id="sidebar" class="sidebar" style="width:250px;">
    <div class="navbar-vertical-container">
      <div class="navbar-vertical-footer-offset">
        <!-- Logo -->

        <a class="navbar-brand" href="./index.html" aria-label="Front">
          
          <!-- <img class="navbar-brand-logo" src="./assets/svg/logos-light/logo.svg" alt="Logo" data-hs-theme-appearance="dark">
          <img class="navbar-brand-logo-mini" src="./assets/svg/logos/logo-short.svg" alt="Logo" data-hs-theme-appearance="default">
          <img class="navbar-brand-logo-mini" src="./assets/svg/logos-light/logo-short.svg" alt="Logo" data-hs-theme-appearance="dark"> -->
        </a>

        <!-- End Logo -->

        <!-- Navbar Vertical Toggle -->
        <button type="button" class="js-navbar-vertical-aside-toggle-invoker navbar-aside-toggler">
          <i class="bi-arrow-bar-left navbar-toggler-short-align" data-bs-template='<div class="tooltip d-none d-md-block" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>' data-bs-toggle="tooltip" data-bs-placement="right" title="Collapse"></i>
          <i class="bi-arrow-bar-right navbar-toggler-full-align" data-bs-template='<div class="tooltip d-none d-md-block" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>' data-bs-toggle="tooltip" data-bs-placement="right" title="Expand"></i>
        </button>

        <!-- End Navbar Vertical Toggle -->

        <!-- Content -->
        <div class="navbar-vertical-content">
          <div id="navbarVerticalMenu" class="nav nav-pills nav-vertical card-navbar-nav">
            <!-- Collapse -->
            <div class="nav-item">
              <a class="nav-link" href="/dashboard" role="button"  aria-expanded="true" aria-controls="navbarVerticalMenuDashboards">
                <i class="bi-people nav-icon"></i>
                <span class="nav-link-title">Dashboard</span>
              </a>

              
            </div>
            <!-- End Collapse -->
            <!-- Collapse -->
            <div class="navbar-nav nav-compact">

            </div>
            <div id="navbarVerticalMenuPagesMenu">
              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle " href="#navbarVerticalMenuPagesUsersMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuPagesUsersMenu" aria-expanded="false" aria-controls="navbarVerticalMenuPagesUsersMenu">
                  <i class="bi-people nav-icon"></i>
                  <span class="nav-link-title">Clients</span>
                </a>

                <div id="navbarVerticalMenuPagesUsersMenu" class="nav-collapse collapse " data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link " href="/clients">Overview</a>
                  <a class="nav-link " href="/clients/create">Add Client <span class="badge bg-info rounded-pill ms-1">Hot</span></a>
                </div>
              </div>
              <!-- End Collapse -->

              

              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle " href="#navbarVerticalMenuPagesAccountMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuPagesAccountMenu" aria-expanded="false" aria-controls="navbarVerticalMenuPagesAccountMenu">
                  <i class="bi-person-badge nav-icon"></i>
                  <span class="nav-link-title">Account</span>
                </a>

                <div id="navbarVerticalMenuPagesAccountMenu" class="nav-collapse collapse " data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link " href="./account-settings.html">Settings</a>
                  <a class="nav-link " href="./account-billing.html">Billing</a>
                  <a class="nav-link " href="./account-white-label.html">White Label</a>
                </div>
              </div>
              <!-- End Collapse -->

              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle" href="#navbarVerticalMenuIntegrationsMenu" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuIntegrationsMenu" aria-expanded="false" aria-controls="navbarVerticalMenuIntegrationsMenu">
                  <i class="bi-plug nav-icon"></i>
                  <span class="nav-link-title">Integrations</span>
                </a>

                <div id="navbarVerticalMenuIntegrationsMenu" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">CRM</a>
                </div>
              </div>
              <!-- End Collapse -->

              <!-- Collapse -->
              <div class="nav-item">
                <a class="nav-link dropdown-toggle" href="#navbarVerticalMenuCurrentClient" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenuCurrentClient" aria-expanded="false" aria-controls="navbarVerticalMenuCurrentClient">
                  <i class="bi-plug nav-icon"></i>
                  <span class="nav-link-title">Current Client</span>
                </a>

                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Financial Overview</a>
                </div>
                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Social Security Overview</a>
                </div>
                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Medicare Overview</a>
                </div>
                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Income Overview</a>
                </div>
                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Roth Conversion</a>
                </div>
                <div id="navbarVerticalMenuCurrentClient" class="nav-collapse collapse" data-bs-parent="#navbarVerticalMenuPagesMenu">
                  <a class="nav-link" href="/integrations/crm">Social Security Tools</a>
                </div>
              </div>
              <!-- End Collapse -->
            </div>
            <!-- End Collapse -->


          

          </div>

        </div>
        <!-- End Content -->
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'Sidebar'
};
</script>

<style scoped>
/* You can move real styles from dist/assets/css or define here */
.sidebar {
  width: 250px;
  background-color: #f8f9fa;
  min-height: 100vh;
  padding-top: 1rem;
  border-right: 1px solid #e3e6f0;
}
</style>