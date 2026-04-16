<template>
  <PageHeader
    title="历史记录"
    subtitle="查看全部出入库交易明细"
  >
    <template #icon>
      <ClockIcon />
    </template>
  </PageHeader>

  <GlassCard :title="`交易记录 · ${transactions.length} 条`">
    <DataTable
      :columns="columns"
      :data="transactions"
      row-key="id"
      empty-title="暂无交易记录"
      empty-description="完成一次入库或出库后，这里会显示完整历史。"
    >
      <template #time="{ row }">
        <span class="time-col">{{ formatDateTime(row.createdAt) }}</span>
      </template>

      <template #type="{ row }">
        <span :class="['badge', row.type === 'IN' ? 'badge-in' : 'badge-out']">
          {{ row.type === 'IN' ? '入库' : '出库' }}
        </span>
      </template>

      <template #quantity="{ row }">
        <StatusIndicator :label="`${row.quantity} 件`" :status="row.type === 'IN' ? 'normal' : 'alarm'" />
      </template>
    </DataTable>
  </GlassCard>
</template>

<script setup>
import { computed } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import { ClockIcon } from '../components/icons'

const inventory = useInventoryStore()
const transactions = computed(() => inventory.recentTransactions)

const columns = [
  { key: 'time', label: '时间' },
  { key: 'productName', label: '货物名称' },
  { key: 'type', label: '类型' },
  { key: 'quantity', label: '数量' },
  { key: 'storageLocation', label: '存储位置' },
  { key: 'note', label: '备注' }
]
</script>
