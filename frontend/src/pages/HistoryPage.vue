<template>
  <div class="page-container">
    <div class="history-header">
      <h2 class="view-title">历史记录</h2>
      
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <label>物品名称</label>
          <input v-model="filters.name" type="text" placeholder="搜索物品..." class="filter-input">
        </div>
        <div class="filter-item">
          <label>操作类型</label>
          <select v-model="filters.type" class="filter-select">
            <option value="">全部</option>
            <option value="IN">栖息 (入库)</option>
            <option value="OUT">迁徙 (出库)</option>
          </select>
        </div>
      </div>
    </div>

    <div class="timeline-container">
      <div v-for="group in groupedTransactions" :key="group.date" class="timeline-group">
        <div class="timeline-date">{{ group.date }}</div>
        <div class="timeline-items">
          <div v-for="item in group.items" :key="item.id" class="timeline-item">
            <div class="timeline-marker" :class="item.type.toLowerCase()"></div>
            <div class="timeline-content">
              <div class="timeline-time">{{ formatTimeOnly(item.createdAt) }}</div>
              <div class="timeline-desc">
                <span class="action-type" :class="item.type.toLowerCase()">
                  {{ item.type === "IN" ? "栖息" : "迁徙" }}
                </span>
                <span class="item-link" @click="openItemDetail(item.productId)">
                  {{ item.productName }}
                </span>
                <span v-if="item.type === 'IN'">
                  进入了 <span class="location-tag">「{{ item.storageLocation || '待整理' }}」</span>
                </span>
                <span v-else>
                  从 <span class="location-tag">「{{ item.storageLocation || '待整理' }}」</span> 移出
                </span>
                <span class="qty-badge">{{ item.quantity }} 件</span>
                <div v-if="item.note" class="item-note">“{{ item.note }}”</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="filteredTransactions.length === 0" class="empty-state">
        <EmptyState 
          title="暂无匹配记录" 
          description="尝试调整筛选条件或进行一次栖息/迁徙操作。"
        />
      </div>
    </div>

    <!-- 物品详情抽屉 -->
    <ItemDrawer 
      v-model:show="drawer.show" 
      :item="drawer.selectedItem" 
      @refresh="inventory.refresh()"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive } from "vue"
import { useInventoryStore } from "../stores/inventory.store"
import { formatDateTime } from "../utils/format"
import EmptyState from "../components/ui/EmptyState.vue"
import ItemDrawer from "../components/features/ItemDrawer.vue"

const inventory = useInventoryStore()

const filters = reactive({
  name: "",
  type: ""
})

const drawer = reactive({
  show: false,
  selectedItem: null
})

const filteredTransactions = computed(() => {
  return inventory.recentTransactions.filter(t => {
    const nameMatch = !filters.name || (t.productName && t.productName.toLowerCase().includes(filters.name.toLowerCase()))
    const typeMatch = !filters.type || t.type === filters.type
    return nameMatch && typeMatch
  })
})

const groupedTransactions = computed(() => {
  const groups = {}
  filteredTransactions.value.forEach(t => {
    const formatted = formatDateTime(t.createdAt)
    const date = formatted ? formatted.split(" ")[0] : "未知日期"
    if (!groups[date]) groups[date] = []
    groups[date].push(t)
  })
  
  return Object.keys(groups).sort((a, b) => b.localeCompare(a)).map(date => ({
    date,
    items: groups[date]
  }))
})

const formatTimeOnly = (dateTimeStr) => {
  const formatted = formatDateTime(dateTimeStr)
  const parts = formatted ? formatted.split(" ") : []
  return parts.length > 1 ? parts[1].substring(0, 5) : ""
}

const openItemDetail = (productId) => {
  const item = inventory.getProductById(productId)
  if (item) {
    drawer.selectedItem = item
    drawer.show = true
  }
}
</script>

<style scoped>
.page-container { max-width: 800px; margin: 0 auto; }
.history-header { margin-bottom: 32px; }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 24px; }
.filter-bar { display: flex; gap: 24px; background: white; padding: 16px 24px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.filter-item { display: flex; flex-direction: column; gap: 6px; }
.filter-item label { font-size: 12px; font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.filter-input, .filter-select { padding: 8px 12px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc; color: var(--color-text); outline: none; font-size: 14px; }
.filter-input:focus, .filter-select:focus { border-color: var(--color-brand); background: white; }
.timeline-container { display: flex; flex-direction: column; gap: 40px; }
.timeline-date { font-size: 14px; font-weight: 700; color: var(--color-text-muted); margin-bottom: 16px; position: sticky; top: 0; background: var(--color-bg); padding: 8px 0; z-index: 10; }
.timeline-items { display: flex; flex-direction: column; gap: 0; border-left: 2px solid #e2e8f0; margin-left: 8px; padding-left: 24px; }
.timeline-item { position: relative; padding-bottom: 24px; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-marker { position: absolute; left: -31px; top: 4px; width: 12px; height: 12px; border-radius: 50%; background: white; border: 2px solid #cbd5e1; }
.timeline-marker.in { border-color: var(--color-success); background: var(--color-success); }
.timeline-marker.out { border-color: var(--color-error); background: var(--color-error); }
.timeline-content { display: flex; flex-direction: column; gap: 4px; }
.timeline-time { font-size: 12px; font-weight: 600; color: var(--color-text-muted); font-family: var(--font-mono); }
.timeline-desc { font-size: 15px; color: var(--color-text); line-height: 1.6; }
.action-type { font-weight: 700; margin-right: 6px; }
.action-type.in { color: var(--color-success); }
.action-type.out { color: var(--color-error); }
.item-link { font-weight: 600; color: var(--color-brand); cursor: pointer; text-decoration: underline; text-underline-offset: 4px; margin: 0 4px; }
.item-link:hover { background: rgba(59, 130, 246, 0.1); border-radius: 4px; }
.location-tag { font-weight: 600; color: #64748b; }
.qty-badge { display: inline-block; background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #475569; margin-left: 8px; }
.item-note { margin-top: 6px; font-size: 13px; font-style: italic; color: var(--color-text-muted); background: #f8fafc; padding: 6px 12px; border-radius: 6px; border-left: 3px solid #e2e8f0; }
.empty-state { padding: 48px; text-align: center; }
</style>