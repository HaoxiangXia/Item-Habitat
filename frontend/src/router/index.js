import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/IndexPage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/inbound',
    name: 'Inbound',
    component: () => import('../pages/InboundPage.vue'),
    meta: { title: '货物入库' }
  },
  {
    path: '/outbound',
    name: 'Outbound',
    component: () => import('../pages/OutboundPage.vue'),
    meta: { title: '货物出库' }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../pages/SearchPage.vue'),
    meta: { title: '货物检索' }
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

router.afterEach((to) => {
  const suffix = to.meta?.title ? `${to.meta.title} - 仓储管理系统` : '仓储管理系统'
  document.title = suffix
})

export default router
