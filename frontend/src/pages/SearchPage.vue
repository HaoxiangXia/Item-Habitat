<template>
  <PageHeader
    title="货物检索"
    subtitle="按名称、存储位置和日期范围快速筛选货物"
  >
    <template #icon>
      <SearchIcon />
    </template>
  </PageHeader>

  <GlassCard title="筛选条件">
    <form class="search-form" @submit.prevent>
      <div class="filter-row">
        <InputField v-model="filters.name" label="货物名称" placeholder="请输入货物名称" />

        <SelectField
          v-model="filters.storageLocation"
          label="存储位置"
          :options="locationOptions"
          option-label-key="name"
          option-value-key="name"
          placeholder="全部位置"
        />

        <InputField v-model="filters.startDate" label="开始日期" type="date" />
        <InputField v-model="filters.endDate" label="结束日期" type="date" />
      </div>

      <div class="form-actions">
        <Button type="button" @click="clearFilters">清除条件</Button>
      </div>
    </form>
  </GlassCard>

  <GlassCard :title="`搜索结果 · ${results.length} 条`">
    <DataTable
      :columns="columns"
      :data="results"
      row-key="id"
      empty-title="没有找到相关货物"
      empty-description="尝试调整筛选条件后再搜索。"
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
import { computed, reactive } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import Button from '../components/ui/Button.vue'
import InputField from '../components/ui/Input.vue'
import SelectField from '../components/ui/Select.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import { SearchIcon } from '../components/icons'

const inventory = useInventoryStore()

const filters = reactive({
  name: '',
  storageLocation: '',
  startDate: '',
  endDate: ''
})

const locationOptions = computed(() => inventory.locationOptions)
const results = computed(() => inventory.searchProducts(filters))

const columns = [
  { key: 'name', label: '货物名称' },
  { key: 'quantity', label: '库存' },
  { key: 'storageLocation', label: '存储位置' },
  { key: 'createdAt', label: '创建时间' }
]

function clearFilters() {
  filters.name = ''
  filters.storageLocation = ''
  filters.startDate = ''
  filters.endDate = ''
}
</script>
