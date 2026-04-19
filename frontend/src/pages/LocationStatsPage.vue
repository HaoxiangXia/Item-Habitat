<template>
  <div class="page-container">
    <div class="stat-grid">
      <StatCard :value="summary.totalLocations" label="有效位置" description="当前可用的存储位置总数">
      </StatCard>

      <StatCard :value="summary.totalProducts" label="货物条目" description="当前登记的货物记录数量" tone="accent">
      </StatCard>

      <StatCard :value="summary.totalQuantity" label="总库存" description="全仓库存数量汇总" tone="success">
      </StatCard>
    </div>

    <GlassCard title="货物检索">
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

    <div class="stats-results-grid">
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

      <GlassCard v-if="hasFilters" :title="`检索结果 · ${searchResults.length} 条`">
        <DataTable
          :columns="searchColumns"
          :data="searchResults"
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
        </DataTable>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import StatCard from '../components/ui/StatCard.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import InputField from '../components/ui/Input.vue'
import SelectField from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'

const inventory = useInventoryStore()
const summary = computed(() => inventory.summary)
const locationStats = computed(() => inventory.locationStats)

const filters = reactive({
  name: '',
  storageLocation: '',
  startDate: '',
  endDate: ''
})

const hasFilters = computed(() => {
  return filters.name || filters.storageLocation || filters.startDate || filters.endDate
})

const locationOptions = computed(() => inventory.locationOptions)
const searchResults = computed(() => inventory.searchProducts(filters))

const clearFilters = () => {
  filters.name = ''
  filters.storageLocation = ''
  filters.startDate = ''
  filters.endDate = ''
}

const columns = [
  { key: 'storageLocation', label: '存储位置' },
  { key: 'productCount', label: '货物种类' },
  { key: 'totalQuantity', label: '总库存' },
  { key: 'actions', label: '操作' }
]

const searchColumns = [
  { key: 'name', label: '货物名称' },
  { key: 'quantity', label: '库存' },
  { key: 'storageLocation', label: '存储位置' }
]
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-form {
  margin-bottom: 0;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.stats-results-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1200px) {
  .stats-results-grid {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}

.inline-link {
  color: var(--color-brand);
  text-decoration: none;
  font-weight: 600;
}

.img-btn {
  color: var(--color-brand);
  font-size: 0.85rem;
  text-decoration: none;
  font-weight: 500;
}
</style>
