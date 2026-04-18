<template>
  <AuroraBackground />

  <div v-if="!inventory.isReady" class="bootstrap-state">
    <div class="glass-card bootstrap-state-card">
      <p class="bootstrap-state-kicker">正在连接后端</p>
      <h1>正在加载真实库存数据</h1>
      <p>请稍候，系统正在从 FastAPI 后端读取 <code>warehouse.db</code>。</p>
    </div>
  </div>

  <div v-else-if="fatalError" class="bootstrap-state">
    <div class="glass-card bootstrap-state-card">
      <p class="bootstrap-state-kicker bootstrap-state-kicker-error">后端未启动</p>
      <h1>无法连接到 FastAPI 后端</h1>
      <p class="bootstrap-state-message">{{ inventory.errorMessage }}</p>
      <p class="bootstrap-state-hint">
        请先在根目录运行 <code>uv run .\app.py</code>，或在 <code>backend</code> 目录运行
        <code>uv run .\main.py</code>。
      </p>
      <button class="btn btn-primary" type="button" @click="retry">重新连接</button>
    </div>
  </div>

  <template v-else>
    <Sidebar />

    <main class="main-content">
      <FlashMessageStack />
      <router-view v-slot="{ Component }">
        <transition name="fade-transform" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </template>
</template>

<script setup>
import { computed } from 'vue'
import { useInventoryStore } from './stores/inventory.store'
import AuroraBackground from './components/layout/AuroraBackground.vue'
import FlashMessageStack from './components/layout/FlashMessageStack.vue'
import Sidebar from './components/layout/Sidebar.vue'

const inventory = useInventoryStore()

const fatalError = computed(() => inventory.isReady && Boolean(inventory.errorMessage))

async function retry() {
  await inventory.loadBootstrap()
}
</script>
