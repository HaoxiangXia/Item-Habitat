<template>
  <PageHeader
    :title="locationName || '位置详情'"
    subtitle="查看该存储位置下的全部货物"
  >
    <template #icon>
      <LayersIcon />
    </template>

    <template #actions>
      <router-link to="/locations" class="nav-btn">
        <BackIcon />
        返回统计
      </router-link>
    </template>
  </PageHeader>

  <div class="stat-grid">
    <StatCard :value="summary.productCount" label="货物种类" description="该位置下的货物条目数">
      <template #icon>
        <PackageIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalQuantity" label="总库存" description="该位置下库存总量" tone="accent">
      <template #icon>
        <TrendIcon />
      </template>
    </StatCard>
  </div>

  <GlassCard :title="`货物列表 · ${products.length} 条`">
    <DataTable
      :columns="columns"
      :data="products"
      row-key="id"
      empty-title="该存储位置暂无货物"
      empty-description="你可以先从入库页面添加新的货物。"
    >
      <template #quantity="{ row }">
        <StatusIndicator
          :label="`${row.quantity} 件`"
          :status="row.quantity === 0 ? 'alarm' : row.quantity < 10 ? 'alarm' : 'normal'"
        />
      </template>

      <template #createdAt="{ row }">
        <span class="time-col">{{ formatDateTime(row.createdAt) }}</span>
      </template>
    </DataTable>
  </GlassCard>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useInventoryStore } from '../stores/inventory.store'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import StatCard from '../components/ui/StatCard.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import { LayersIcon, PackageIcon, TrendIcon, BackIcon } from '../components/icons'

const route = useRoute()
const inventory = useInventoryStore()

const locationName = computed(() => decodeURIComponent(route.params.locationId || ''))
const products = computed(() => inventory.getProductsByLocation(locationName.value))
const summary = computed(() => inventory.getLocationSummary(locationName.value))

const columns = [
  { key: 'name', label: '货物名称' },
  { key: 'quantity', label: '库存' },
  { key: 'createdAt', label: '创建时间' }
]
</script>
