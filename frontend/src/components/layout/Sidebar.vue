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

    <div class="sidebar-footer">
      <div v-if="auth.isAuthenticated" class="user-info">
        <img :src="auth.user.avatar" alt="User Avatar" class="user-avatar" />
        <div class="user-details">
          <div class="user-name">{{ auth.user.username }}</div>
          <div class="user-role">{{ auth.user.role }}</div>
        </div>
        <button class="logout-btn" title="退出登录" @click="handleLogout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
          </svg>
        </button>
      </div>
    </div>
  </aside>

  <div 
    class="sidebar-overlay" 
    :class="{ show: ui.sidebarOpen && isMobile }"
    @click="ui.closeSidebar()"
  ></div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUiStore } from '../../stores/ui.store'
import { useAuthStore } from '../../stores/auth.store'
import { HomeIcon, ArrowDownIcon, ArrowUpIcon, SearchIcon, ClockIcon, MapIcon, MenuIcon, ReceiptIcon, LayersIcon } from '../icons'

export default {
  name: 'Sidebar',
  setup() {
    const ui = useUiStore()
    const auth = useAuthStore()
    const route = useRoute()
    const router = useRouter()
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

    const handleLogout = () => {
      auth.logout()
      router.push('/login')
      ui.showFlash('已安全退出登录', 'info')
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
      auth,
      isMobile,
      menuItems,
      MenuIcon,
      closeOnMobile,
      handleLogout
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
  background: var(--glass-bg, white);
  backdrop-filter: blur(var(--glass-blur, 10px));
  border-right: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: var(--glass-shadow, none);
  transition: transform 0.3s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  margin-bottom: 32px;
}

.sidebar-title {
  font-weight: 800;
  font-size: 1.25rem;
  color: var(--color-primary, #3b82f6);
  letter-spacing: -0.5px;
}

.sidebar-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.2;
}

.sidebar-menu {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  padding: 0;
  margin: 0;
}

.sidebar-menu a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  text-decoration: none;
  color: #64748b;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.sidebar-menu a:hover {
  background: #f8fafc;
  color: #1e293b;
}

.sidebar-menu a.active {
  background: #eff6ff;
  color: #3b82f6;
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2e8f0;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.user-role {
  font-size: 0.7rem;
  color: #94a3b8;
}

.logout-btn {
  background: none;
  border: none;
  color: #94a3b8;
  padding: 5px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
}

.logout-btn:hover {
  color: #ef4444;
  background: #fee2e2;
}

.logout-btn svg {
  width: 18px;
  height: 18px;
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 100;
  width: 40px;
  height: 40px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
}

@media (max-width: 900px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .mobile-menu-btn { display: flex; align-items: center; justify-content: center; }
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    z-index: 40;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s;
  }
  .sidebar-overlay.show { opacity: 1; visibility: visible; }
}
</style>
