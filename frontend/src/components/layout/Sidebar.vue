<template>
  <button class="mobile-menu-btn" type="button" aria-label="打开菜单" @click="ui.toggleSidebar()">
    <MenuIcon />
  </button>

  <aside class="sidebar" :class="{ open: ui.sidebarOpen }">
    <div class="sidebar-brand">
      <div class="sidebar-brand-text">
        <div class="sidebar-title">栖物志</div>
        <div class="sidebar-subtitle">给每件物品一个清晰、可追踪的栖息地</div>
      </div>
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
import { HomeIcon, ArrowDownIcon, ArrowUpIcon, SearchIcon, ClockIcon, MapIcon, MenuIcon, ReceiptIcon, LayersIcon } from '../icons'

export default {
  name: 'Sidebar',
  setup() {
    const ui = useUiStore()
    const route = useRoute()
    const isMobile = ref(window.innerWidth < 900)

    const menuItems = [
      { path: '/', label: '首页', icon: HomeIcon },
      { path: '/migration', label: '栖息/迁徙', icon: ArrowDownIcon },
      { path: '/board', label: '看板', icon: LayersIcon },
      { path: '/history', label: '历史记录', icon: ClockIcon },
      { path: '/locations', label: '库存统计', icon: MapIcon },
      { path: '/map', label: '地图', icon: MapIcon },
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

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-width);
  z-index: 50;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border-right: 1px solid rgba(255, 255, 255, 0.5); /* 右侧边框稍微加重 */
  box-shadow: var(--glass-shadow);
  transition: transform 0.3s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  margin-bottom: 32px;
}

.sidebar-logo {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: var(--gradient-brand); /* 这里假设有 gradient-brand 或沿用颜色 */
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 20px;
}

.sidebar-brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-title {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.15rem;
  color: var(--color-text);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.sidebar-subtitle {
  font-size: 0.65rem;
  color: var(--color-text-muted);
  line-height: 1.3;
  opacity: 0.8;
  max-width: 140px;
}

.sidebar-menu {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-menu a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: var(--color-text-secondary);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  font-weight: 500;
}

.sidebar-menu a:hover {
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-brand);
}

.sidebar-menu a.active {
  background: rgba(255, 255, 255, 0.25); /* 激活状态更亮的背景 */
  color: var(--color-brand);
  font-weight: 600;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 60;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  color: var(--color-text);
  cursor: pointer;
  align-items: center;
  justify-content: center;
}

@media (max-width: 900px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.3);
    backdrop-filter: blur(4px);
    z-index: 40;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }
  
  .sidebar-overlay.show {
    opacity: 1;
    pointer-events: auto;
  }
}
</style>
