<!-- src/layouts/DefaultLayout.vue -->
<template>
  <div id="dashboard" class="d-flex">
    <Sidebar />
    <div class="main-content">
      <Header />
      <main style="background-color:rgb(242, 242, 242);">
       <router-view v-slot="{ Component }">
          <transition name="fade">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
</script>

<style scoped>
#dashboard {
  height: 100vh;
  overflow: hidden;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: auto;
}
main {
  flex: 1;
  padding: 2rem;
}
</style>