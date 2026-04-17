<template>
  <button class="mobile-menu-btn" type="button" aria-label="打开菜单" @click="ui.toggleSidebar()">
    <MenuIcon />
  </button>

  <aside class="sidebar" :class="{ open: ui.sidebarOpen }">
    <div class="sidebar-brand">
      <div class="sidebar-logo">H</div>
      <div class="sidebar-title">栖物志</div>
    </div>

    <ul class="sidebar-menu">
      <li v-for="item in menuItems" :key="item.path">
        <router-link
          :to="item.path"
          active-class="active"
          exact-active-class="active"
          @click="closeOnMobile"
        >
          <div class="nav-icon">
            <component :is="item.icon" />
          </div>
          <span>{{ item.label }}</span>
        </router-link>
      </li>
    </ul>
  </aside>

  <div 
    class="sidebar-overlay" 
    :class="{ show: ui.sidebarOpen && isMobile }"
    @click="ui.closeSidebar()"
  ></div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '../../stores/ui.store'
import { HomeIcon, ArrowDownIcon, ArrowUpIcon, SearchIcon, ClockIcon, MapIcon, MenuIcon, ReceiptIcon } from '../icons'

export default {
  name: 'Sidebar',
  setup() {
    const ui = useUiStore()
    const route = useRoute()
    const isMobile = ref(window.innerWidth < 900)

    const menuItems = [
      { path: '/', label: '首页', icon: HomeIcon },
      { path: '/inbound', label: '入库', icon: ArrowDownIcon },
      { path: '/outbound', label: '出库', icon: ArrowUpIcon },
      { path: '/search', label: '检索', icon: SearchIcon },
      { path: '/history', label: '历史', icon: ClockIcon },
      { path: '/locations', label: '库存统计', icon: MapIcon },
      { path: '/receipt-imports', label: '截图导入', icon: ReceiptIcon },
    ]

    const handleResize = () => {
      isMobile.value = window.innerWidth < 900
      if (!isMobile.value) {
        ui.closeSidebar()
      }
    }

    const closeOnMobile = () => {
      if (isMobile.value) {
        ui.closeSidebar()
      }
    }

    onMounted(() => {
      window.addEventListener('resize', handleResize)
      handleResize()
    })

    watch(
      () => route.fullPath,
      () => {
        closeOnMobile()
      }
    )

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      ui,
      isMobile,
      menuItems,
      MenuIcon,
      closeOnMobile
    }
  }
}
</script>
