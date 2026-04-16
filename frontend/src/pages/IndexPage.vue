<template>
  <PageHeader
    title="仓储管理系统"
    subtitle="使用 Vue3 重构后的单页仓储管理界面"
  >
    <template #icon>
      <HomeIcon />
    </template>

    <template #actions>
      <router-link to="/inbound" class="btn btn-primary">快速入库</router-link>
    </template>
  </PageHeader>

  <div class="stat-grid">
    <StatCard :value="summary.totalProducts" label="货物总数" description="当前系统中记录的货物条目">
      <template #icon>
        <PackageIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalQuantity" label="总库存" description="所有货物库存数量汇总" tone="accent">
      <template #icon>
        <TrendIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalLocations" label="存储位置" description="已启用的货位数量" tone="success">
      <template #icon>
        <MapIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalTransactions" label="操作记录" description="累计出入库交易次数" tone="warning">
      <template #icon>
        <ClockIcon />
      </template>
    </StatCard>
  </div>

  <GlassCard title="功能入口">
    <div class="function-grid">
      <router-link
        v-for="item in functions"
        :key="item.path"
        :to="item.path"
        class="function-card"
      >
        <component :is="item.icon" />
        <h3>{{ item.title }}</h3>
        <p>{{ item.description }}</p>
      </router-link>
    </div>
  </GlassCard>

  <div class="dashboard-grid">
    <GlassCard title="低库存提醒">
      <EmptyState
        v-if="!lowStockProducts.length"
        title="当前没有低库存货物"
        description="所有货物库存都处于安全区间。"
      >
        <template #icon>
          <CheckIcon />
        </template>
      </EmptyState>

      <DataTable
        v-else
        :columns="lowStockColumns"
        :data="lowStockProducts"
        row-key="id"
      >
        <template #quantity="{ row }">
          <StatusIndicator
            :label="`${row.quantity} 件`"
            :status="row.quantity === 0 ? 'alarm' : 'alarm'"
          />
        </template>
      </DataTable>
    </GlassCard>

    <GlassCard title="最近交易">
      <DataTable
        :columns="transactionColumns"
        :data="recentTransactions.slice(0, 6)"
        row-key="id"
        empty-title="暂无交易记录"
      >
        <template #time="{ row }">
          <span class="time-col">{{ formatDateTime(row.createdAt) }}</span>
        </template>

        <template #type="{ row }">
          <span :class="['badge', row.type === 'IN' ? 'badge-in' : 'badge-out']">
            {{ row.type === 'IN' ? '入库' : '出库' }}
          </span>
        </template>
      </DataTable>
    </GlassCard>
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
  { path: '/receipt-imports', title: '截图导入', description: '上传购物截图并整理待入库条目', icon: ReceiptIcon }
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
