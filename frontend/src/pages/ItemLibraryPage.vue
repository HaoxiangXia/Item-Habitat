<template>
  <div class="page-container item-library-page">
    <PageHeader title="物品库" subtitle="全量物品浏览与快速取还">
      <template #actions>
        <div class="header-actions">
          <div class="view-toggle">
            <button
              class="toggle-btn"
              :class="{ active: viewMode === 'table' }"
              type="button"
              @click="viewMode = 'table'"
            >
              列表
            </button>
            <button
              class="toggle-btn"
              :class="{ active: viewMode === 'grid' }"
              type="button"
              @click="viewMode = 'grid'"
            >
              网格
            </button>
          </div>
          <Button variant="secondary" size="small" @click="inventory.refresh()">刷新数据</Button>
        </div>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard :value="summary.totalProducts" label="物品总数" description="当前录入的物品条目" />
      <StatCard :value="summary.totalQuantity" label="库存总量" description="全部物品的数量汇总" tone="accent" />
      <StatCard :value="pendingCount" label="待整理" description="尚未归位的物品" tone="warning" />
      <StatCard :value="lowStockCount" label="低库存" description="库存不足提醒" tone="success" />
    </div>

    <GlassCard title="筛选与检索" compact>
      <div class="filters-grid">
        <InputField
          v-model="filters.keyword"
          label="关键词"
          placeholder="名称 / 标签 / 位置"
        />
        <InputField
          v-model="filters.semantic"
          label="语义搜索"
          placeholder="例如：最近没用的无线设备在哪"
        />
        <SelectField
          v-model="filters.location"
          label="存放位置"
          :options="locationOptions"
          option-label-key="name"
          option-value-key="name"
          placeholder="全部位置"
        />
        <SelectField
          v-model="filters.status"
          label="归位状态"
          :options="statusOptions"
          option-label-key="label"
          option-value-key="value"
        />
        <SelectField
          v-model="filters.stock"
          label="库存状态"
          :options="stockOptions"
          option-label-key="label"
          option-value-key="value"
        />
        <div class="filter-actions">
          <Button variant="secondary" size="small" @click="clearFilters">清除条件</Button>
        </div>
      </div>
    </GlassCard>

    <GlassCard :title="`物品清单 · ${filteredProducts.length} 件`">
      <template #actions>
        <div class="list-summary">显示 {{ filteredProducts.length }} / {{ summary.totalProducts }}</div>
      </template>

      <div v-if="!filteredProducts.length" class="empty-state-wrapper">
        <EmptyState
          title="暂无匹配物品"
          description="尝试调整筛选条件或先进行一次栖息记录。"
        />
      </div>

      <DataTable
        v-else-if="viewMode === 'table'"
        :columns="columns"
        :data="filteredProducts"
        row-key="id"
        empty-title="暂无物品"
        empty-description="还没有任何物品记录。"
      >
        <template #name="{ row }">
          <div class="item-name-cell">
            <div class="item-name">{{ row.name }}</div>
            <div v-if="row.tags" class="item-tags">{{ formatTags(row.tags) }}</div>
          </div>
        </template>
        <template #quantity="{ row }">
          <StatusIndicator
            :label="`${row.quantity} 件`"
            :status="getQuantityStatus(row)"
          />
        </template>
        <template #storageLocation="{ row }">
          <span class="location-pill">{{ row.storageLocation || '待整理' }}</span>
        </template>
        <template #status="{ row }">
          <span class="status-pill" :class="getPlacementStatus(row)">{{ getPlacementLabel(row) }}</span>
        </template>
        <template #actions="{ row }">
          <div class="row-actions">
            <Button
              size="small"
              variant="secondary"
              :disabled="row.quantity <= 0"
              @click.stop="adjustQuantity(row, -1)"
            >
              取出
            </Button>
            <Button size="small" @click.stop="adjustQuantity(row, 1)">归还</Button>
            <Button size="small" variant="secondary" @click.stop="openItem(row)">详情</Button>
          </div>
        </template>
      </DataTable>

      <div v-else class="grid-wrapper">
        <div class="item-grid">
          <div v-for="item in filteredProducts" :key="item.id" class="item-card">
            <div class="item-card-header">
              <div>
                <div class="item-card-title">{{ item.name }}</div>
                <div class="item-card-subtitle">{{ item.storageLocation || '待整理' }}</div>
              </div>
              <span class="status-pill" :class="getPlacementStatus(item)">{{ getPlacementLabel(item) }}</span>
            </div>
            <div class="item-card-body">
              <div class="item-card-qty">
                <StatusIndicator
                  :label="`${item.quantity} 件`"
                  :status="getQuantityStatus(item)"
                />
              </div>
              <div v-if="item.tags" class="item-tags">{{ formatTags(item.tags) }}</div>
            </div>
            <div class="item-card-actions">
              <Button
                size="small"
                variant="secondary"
                :disabled="item.quantity <= 0"
                @click="adjustQuantity(item, -1)"
              >
                取出
              </Button>
              <Button size="small" @click="adjustQuantity(item, 1)">归还</Button>
              <Button size="small" variant="secondary" @click="openItem(item)">详情</Button>
            </div>
          </div>
        </div>
      </div>
    </GlassCard>

    <ItemDrawer v-model:show="drawerOpen" :item="selectedItem" @refresh="inventory.refresh()" />
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { useUiStore } from '../stores/ui.store'
import { normalizeText } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import DataTable from '../components/ui/DataTable.vue'
import InputField from '../components/ui/Input.vue'
import SelectField from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'
import StatusIndicator from '../components/ui/StatusIndicator.vue'
import StatCard from '../components/ui/StatCard.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import ItemDrawer from '../components/features/ItemDrawer.vue'

const inventory = useInventoryStore()
const ui = useUiStore()

const viewMode = ref('table')
const drawerOpen = ref(false)
const selectedItem = ref(null)

const filters = reactive({
  keyword: '',
  semantic: '',
  location: '',
  status: '',
  stock: ''
})

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '待整理', value: 'pending' },
  { label: '已归位', value: 'stored' }
]

const stockOptions = [
  { label: '全部库存', value: '' },
  { label: '低库存 (<=10)', value: 'low' },
  { label: '充足 (>10)', value: 'safe' },
  { label: '无库存', value: 'empty' }
]

const summary = computed(() => inventory.summary)
const locationOptions = computed(() => inventory.locationOptions)
const pendingCount = computed(() => inventory.products.filter((item) => isPending(item)).length)
const lowStockCount = computed(() => inventory.lowStockProducts.length)

const columns = [
  { key: 'name', label: '物品名称' },
  { key: 'quantity', label: '库存' },
  { key: 'storageLocation', label: '栖息地' },
  { key: 'status', label: '归位状态' },
  { key: 'actions', label: '快速操作', width: '220px' }
]

const filteredProducts = computed(() => {
  const keyword = normalizeText(filters.keyword).toLowerCase()
  const semantic = normalizeText(filters.semantic).toLowerCase()
  const location = normalizeText(filters.location)

  return inventory.productOptions.filter((item) => {
    if (keyword) {
      const haystack = buildSearchText(item)
      if (!haystack.includes(keyword)) return false
    }

    if (semantic) {
      const haystack = buildSearchText(item)
      const tokens = semantic.split(/\s+/).filter(Boolean)
      if (!tokens.every((token) => haystack.includes(token))) return false
    }

    if (location && normalizeText(item.storageLocation) !== location) {
      return false
    }

    if (filters.status) {
      const status = isPending(item) ? 'pending' : 'stored'
      if (status !== filters.status) return false
    }

    if (filters.stock) {
      if (filters.stock === 'empty' && item.quantity > 0) return false
      if (filters.stock === 'low' && (item.quantity <= 0 || item.quantity > 10)) return false
      if (filters.stock === 'safe' && item.quantity <= 10) return false
    }

    return true
  })
})

function buildSearchText(item) {
  const tagText = formatTags(item.tags)
  return `${item.name || ''} ${item.storageLocation || ''} ${tagText}`.toLowerCase()
}

function formatTags(tags) {
  if (!tags) return ''
  if (Array.isArray(tags)) return tags.join(' / ')
  if (typeof tags === 'string') return tags.split(',').filter(Boolean).join(' / ')
  return ''
}

function isPending(item) {
  const location = normalizeText(item.storageLocation)
  return !location || location === '待整理'
}

function getPlacementLabel(item) {
  return isPending(item) ? '待整理' : '已归位'
}

function getPlacementStatus(item) {
  return isPending(item) ? 'pending' : 'stored'
}

function getQuantityStatus(item) {
  if (item.quantity <= 0) return 'offline'
  if (item.quantity <= 10) return 'alarm'
  return 'normal'
}

function clearFilters() {
  filters.keyword = ''
  filters.semantic = ''
  filters.location = ''
  filters.status = ''
  filters.stock = ''
}

function openItem(item) {
  selectedItem.value = item
  drawerOpen.value = true
}

async function adjustQuantity(item, delta) {
  const next = Number(item.quantity || 0) + delta
  if (next < 0) return

  const result = await inventory.updateProductInfo(item.id, { quantity: next })
  if (result.success) {
    ui.success(result.message || '已更新库存')
  } else {
    ui.error(result.message || '库存更新失败')
  }
}
</script>

<style scoped>
.item-library-page {
  padding-bottom: 24px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-toggle {
  display: inline-flex;
  background: #f8fafc;
  border-radius: 999px;
  padding: 4px;
  border: 1px solid #e2e8f0;
}

.toggle-btn {
  border: none;
  background: transparent;
  padding: 6px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-muted);
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: white;
  color: var(--color-text);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
  padding-bottom: 6px;
}

.list-summary {
  font-size: 12px;
  color: var(--color-text-muted);
}

.item-name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 600;
  color: var(--color-text);
}

.item-tags {
  font-size: 12px;
  color: var(--color-text-muted);
}

.location-pill {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 12px;
  color: #475569;
}

.status-pill {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  background: #e2e8f0;
}

.status-pill.pending {
  background: rgba(251, 146, 60, 0.15);
  color: #b45309;
}

.status-pill.stored {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.grid-wrapper {
  margin-top: 8px;
}

.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.item-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.item-card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.item-card-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--color-text);
}

.item-card-subtitle {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.item-card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-state-wrapper {
  padding: 32px 0;
}

@media (max-width: 960px) {
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
