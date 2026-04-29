import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/LoginPage.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/IndexPage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/migration',
    name: 'Migration',
    component: () => import('../pages/MigrationPage.vue'),
    meta: { title: '栖息/迁徙' }
  },
  {
    path: '/board',
    name: 'Board',
    component: () => import('../pages/BoardPage.vue'),
    meta: { title: '看板' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../pages/HistoryPage.vue'),
    meta: { title: '历史记录' }
  },
  {
    path: '/locations',
    name: 'LocationStats',
    component: () => import('../pages/LocationStatsPage.vue'),
    meta: { title: '库存统计' }
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('../pages/MapPage.vue'),
    meta: { title: '地图' }
  },
  {
    path: '/receipt-imports',
    name: 'ReceiptImports',
    component: () => import('../pages/ReceiptImportPage.vue'),
    meta: { title: '购物截图导入' }
  },
  {
    path: '/locations/:locationId',
    name: 'LocationDetail',
    component: () => import('../pages/LocationDetailPage.vue'),
    meta: { title: '位置详情' },
    props: true
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return '/'
  }
})

router.afterEach((to) => {
  const suffix = to.meta?.title ? `${to.meta.title} - 栖物志` : '栖物志'
  document.title = suffix
})

export default router
