<template>
  <div class="page-container">
    <PageHeader title="库存统计" subtitle="按存储位置汇总当前库存">
      <template #icon>
        <MapIcon />
      </template>
    </PageHeader>

  <div class="stat-grid">
    <StatCard :value="summary.totalLocations" label="有效位置" description="当前可用的存储位置总数">
      <template #icon>
        <LayersIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalProducts" label="货物条目" description="当前登记的货物记录数量" tone="accent">
      <template #icon>
        <PackageIcon />
      </template>
    </StatCard>

    <StatCard :value="summary.totalQuantity" label="总库存" description="全仓库存数量汇总" tone="success">
      <template #icon>
        <TrendIcon />
      </template>
    </StatCard>
  </div>

  <GlassCard :title="`存储位置 · ${locationStats.length} 个`">
    <DataTable
      :columns="columns"
      :data="locationStats"
      row-key="storageLocation"
      empty-title="暂无库存数据"
      empty-description="还没有任何带位置的货物记录。"
    >
      <template #storageLocation="{ row }">
        <router-link
          class="inline-link"
          :to="{ name: 'LocationDetail', params: { locationId: row.storageLocation } }"
        >
          {{ row.storageLocation }}
        </router-link>
      </template>

      <template #totalQuantity="{ row }">
        <StatusIndicator :label="`${row.totalQuantity} 件`" :status="row.totalQuantity > 0 ? 'normal' : 'offline'" />
      </template>

      <template #actions="{ row }">
        <router-link class="img-btn" :to="{ name: 'LocationDetail', params: { locationId: row.storageLocation } }">
          查看详情
        </router-link>
      </template>
    </DataTable>
    </GlassCard>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import StatCard from '../components/ui/StatCard.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import { MapIcon, LayersIcon, PackageIcon, TrendIcon } from '../components/icons'

const inventory = useInventoryStore()
const summary = computed(() => inventory.summary)
const locationStats = computed(() => inventory.locationStats)

const columns = [
  { key: 'storageLocation', label: '存储位置' },
  { key: 'productCount', label: '货物种类' },
  { key: 'totalQuantity', label: '总库存' },
  { key: 'actions', label: '操作' }
]
</script>
