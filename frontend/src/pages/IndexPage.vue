<template>
  <div class="page-container">
    <PageHeader
      title="栖物志"
      subtitle="给每件物品一个清晰、可追踪的栖息地"
    >
      <template #actions>
        <router-link to="/inbound" class="btn btn-primary">登记新成员</router-link>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard :value="summary.totalProducts" label="栖息物件" description="当前记录的物品总数">
        <template #icon>
          <PackageIcon />
        </template>
      </StatCard>

      <StatCard :value="summary.totalQuantity" label="库存总量" description="所有栖息地的物品汇总" tone="accent">
        <template #icon>
          <TrendIcon />
        </template>
      </StatCard>

      <StatCard :value="summary.totalLocations" label="栖息领地" description="已定义的存放位置数量" tone="success">
        <template #icon>
          <MapIcon />
        </template>
      </StatCard>

      <StatCard :value="summary.totalTransactions" label="流转归档" description="累计物品流向记录" tone="warning">
        <template #icon>
          <ClockIcon />
        </template>
      </StatCard>
    </div>

    <div class="dashboard-grid">
      <GlassCard title="短缺预警">
        <EmptyState
          v-if="!lowStockProducts.length"
          title="当前物件充足"
          description="所有栖息地的物品数量均在理想范围内。"
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
