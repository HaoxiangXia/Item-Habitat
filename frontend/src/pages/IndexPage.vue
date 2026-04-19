<template>
  <div class="page-container">
    <div class="stat-grid">
      <StatCard :value="summary.totalProducts" label="栖息物件" description="当前记录的物品总数">
      </StatCard>

      <StatCard :value="summary.totalQuantity" label="库存总量" description="所有栖息地的物品汇总" tone="accent">
      </StatCard>

      <StatCard :value="summary.totalLocations" label="栖息领地" description="已定义的存放位置数量" tone="success">
      </StatCard>

      <StatCard :value="summary.totalTransactions" label="流转归档" description="累计物品流向记录" tone="warning">
      </StatCard>
    </div>

    <!-- 快速操作大按钮 -->
    <div class="quick-actions-grid">
      <router-link to="/migration" class="action-btn">
        <div class="action-text">
          <span class="action-title">栖息/迁徙</span>
          <span class="action-desc">物品进入与移出</span>
        </div>
      </router-link>

      <router-link to="/receipt-imports" class="action-btn">
        <div class="action-text">
          <span class="action-title">截图导入</span>
          <span class="action-desc">AI 识别购物截图</span>
        </div>
      </router-link>

      <router-link to="/board" class="action-btn">
        <div class="action-text">
          <span class="action-title">查看看板</span>
          <span class="action-desc">流程化物品管理</span>
        </div>
      </router-link>

      <router-link to="/locations" class="action-btn">
        <div class="action-text">
          <span class="action-title">添加空间</span>
          <span class="action-desc">新增栖息地领地</span>
        </div>
      </router-link>
    </div>

    <div class="dashboard-grid">
      <GlassCard title="最近动态">
        <div v-if="recentTransactions.length">
          <div class="timeline">
            <div v-for="t in recentTransactions.slice(0, 5)" :key="t.id" class="timeline-item">
              <div class="timeline-marker" :class="t.type.toLowerCase()"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-action">{{ t.type === 'IN' ? '入库' : '出库' }}</span>
                  <span class="timeline-time">{{ formatDateTime(t.createdAt) }}</span>
                </div>
                <div class="timeline-body">
                  <strong>{{ t.productName }}</strong> x {{ t.quantity }}
                  <span class="timeline-loc" v-if="t.storageLocation"> @ {{ t.storageLocation }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="view-all-footer">
            <router-link to="/history" class="view-all-link">查看全部历史 →</router-link>
          </div>
        </div>
        <EmptyState
          v-else
          title="暂无动态"
          description="开始进行第一次入库吧。"
        >
          <template #icon>
          </template>
        </EmptyState>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import DataTable from '../components/ui/DataTable.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import StatCard from '../components/ui/StatCard.vue'
import {
  HomeIcon,
  PackageIcon,
  TrendIcon,
  MapIcon,
  ClockIcon,
  ArrowDownIcon,
  ArrowUpIcon,
  SearchIcon,
  HistoryIcon,
  LayersIcon,
  CheckIcon,
  ReceiptIcon
} from '../components/icons'

const inventory = useInventoryStore()

const summary = computed(() => inventory.summary)
const lowStockProducts = computed(() => inventory.lowStockProducts)
const recentTransactions = computed(() => inventory.recentTransactions)

const functions = [
  { path: '/inbound', title: '货物入库', description: '录入新货物并登记库存', icon: ArrowDownIcon },
  { path: '/outbound', title: '货物出库', description: '选择货物并减少库存', icon: ArrowUpIcon },
  { path: '/search', title: '货物检索', description: '按名称、位置、日期筛选', icon: SearchIcon },
  { path: '/history', title: '历史记录', description: '查看全部出入库交易', icon: HistoryIcon },
  { path: '/locations', title: '库存统计', description: '按存储位置查看库存', icon: LayersIcon },
  { path: '/receipt-imports', title: '截图导入', description: '上传购物截图并整理待整理商品', icon: ReceiptIcon }
]

const lowStockColumns = [
  { key: 'name', label: '货物名称' },
  { key: 'quantity', label: '库存' },
  { key: 'storageLocation', label: '存储位置' }
]

const transactionColumns = [
  { key: 'time', label: '时间' },
  { key: 'productName', label: '货物名称' },
  { key: 'type', label: '类型' },
  { key: 'quantity', label: '数量' }
]
</script>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-bottom: 20px;
}

.stat-grid {
  flex-shrink: 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.dashboard-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr;
}

:deep(.glass-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.card-content) {
  flex: 1;
  overflow-y: auto;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: var(--glass-shadow);
}

.action-btn:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.4);
  border-color: var(--color-brand);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.action-icon.inbound { background: var(--color-primary); }
.action-icon.receipt { background: var(--color-accent); }
.action-icon.board { background: var(--color-success); }
.action-icon.locations { background: var(--color-warning); }

.action-text {
  display: flex;
  flex-direction: column;
}

.action-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--color-text);
}

.action-desc {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.timeline-item {
  display: flex;
  gap: 12px;
  position: relative;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.timeline-marker.in { background: var(--color-primary); }
.timeline-marker.out { background: #ff4d4f; }

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.timeline-action {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.timeline-time {
  font-size: 0.7rem;
  color: var(--color-text-muted);
}

.timeline-body {
  font-size: 0.9rem;
  color: var(--color-text);
}

.timeline-loc {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.view-all-footer {
  margin-top: 20px;
  text-align: right;
}

.view-all-link {
  font-size: 0.85rem;
  color: var(--color-brand);
  text-decoration: none;
  font-weight: 500;
}

.view-all-link:hover {
  text-decoration: underline;
}
</style>
