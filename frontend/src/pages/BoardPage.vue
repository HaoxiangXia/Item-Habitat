<template>
  <div class="page-container">
    <div class="board-header">
      <h2 class="view-title">记录板</h2>
      <div class="board-stats">
        共 {{ inventory.products.length }} 件栖息物
      </div>
    </div>

    <div class="board-grid">
      <!-- 待整理列 -->
      <div class="board-column">
        <div class="column-header">
          <h3>待整理</h3>
          <span class="count-badge">{{ pendingItems.length }}</span>
        </div>
        <div class="column-content">
          <div class="group-section">
            <div class="group-title" @click="toggleGroup('pending-all')">
              <component :is="isExpanded('pending-all') ? ChevronDownIcon : ChevronRightIcon" class="toggle-icon" />
              <span>未分类 ({{ pendingItems.length }})</span>
            </div>
            <div v-if="isExpanded('pending-all')" class="group-items">
              <div v-for="item in pendingItems" :key="item.id" class="item-card pending" @click="openItem(item)">
                <div class="item-main">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-qty">x {{ item.quantity }}</span>
                </div>
                <div class="item-footer">
                  <ClockIcon class="meta-icon" />
                  <span>{{ formatTimeOnly(item.createdAt) }}</span>
                </div>
              </div>
              <div v-if="!pendingItems.length" class="empty-state-mini">暂无待整理物品</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 已收纳列 -->
      <div class="board-column">
        <div class="column-header">
          <h3>已收纳</h3>
          <span class="count-badge">{{ totalSettledCount }}</span>
        </div>
        <div class="column-content">
          <div v-for="group in settledGroups" :key="group.name" class="group-section">
            <div class="group-title" @click="toggleGroup(group.name)">
              <component :is="isExpanded(group.name) ? ChevronDownIcon : ChevronRightIcon" class="toggle-icon" />
              <span>{{ group.name }} ({{ group.items.length }})</span>
            </div>
            <div v-if="isExpanded(group.name)" class="group-items">
              <div v-for="item in group.items" :key="item.id" class="item-card settled" @click="openItem(item)">
                <div class="item-main">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-qty">x {{ item.quantity }}</span>
                </div>
                <div class="item-footer">
                  <ClockIcon class="meta-icon" />
                  <span>{{ formatTimeOnly(item.updatedAt || item.createdAt) }}</span>
                </div>
              </div>
              <div v-if="!group.items.length" class="empty-state-mini">该空间暂无物品</div>
            </div>
          </div>
          <div v-if="!settledGroups.length" class="empty-state-mini">暂无已收纳物品</div>
        </div>
      </div>
    </div>

    <ItemDrawer
      v-model:show="drawerOpen"
      :item="selectedItem"
      @refresh="inventory.refresh()"
    />
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { useInventoryStore } from "../stores/inventory.store"
import { formatDateTime } from "../utils/format"
import ItemDrawer from "../components/features/ItemDrawer.vue"
import { ClockIcon, ChevronDownIcon, ChevronRightIcon } from "../components/icons"

const inventory = useInventoryStore()

const drawerOpen = ref(false)
const selectedItem = ref(null)
const expandedGroups = ref(new Set(["pending-all"]))

const pendingItems = computed(() => {
  return inventory.products.filter(p => !p.storageLocation || p.storageLocation === "待整理")
})

const settledGroups = computed(() => {
  const groups = []
  inventory.locationOptions.forEach(loc => {
    if (loc.name === "待整理") return
    const items = inventory.products.filter(p => p.storageLocation === loc.name)
    if (items.length > 0) {
      groups.push({
        name: loc.name,
        itemsToProcess: items
      })
    }
  })
  
  const sortedGroups = groups.sort((a, b) => b.itemsToProcess.length - a.itemsToProcess.length)
  
  return sortedGroups.map(g => ({
    name: g.name,
    items: g.itemsToProcess
  }))
})

const totalSettledCount = computed(() => {
  return settledGroups.value.reduce((sum, g) => sum + g.items.length, 0)
})

const toggleGroup = (name) => {
  if (expandedGroups.value.has(name)) {
    expandedGroups.value.delete(name)
  } else {
    expandedGroups.value.add(name)
  }
}

const isExpanded = (name) => expandedGroups.value.has(name)

const openItem = (item) => {
  selectedItem.value = item
  drawerOpen.value = true
}

const formatTimeOnly = (dt) => {
  const f = formatDateTime(dt)
  return f ? f.split(" ")[0] : ""
}
</script>

<style scoped>
.board-header { margin-bottom: 24px; }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 4px; }
.board-stats { font-size: 14px; color: var(--color-text-muted); }
.board-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; height: calc(100vh - 160px); min-height: 500px; }
.board-column { background: rgba(255, 255, 255, 0.4); border-radius: 20px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02); }
.column-header { padding: 16px 20px; background: rgba(255, 255, 255, 0.6); border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; }
.column-header h3 { font-size: 16px; font-weight: 700; color: var(--color-text); }
.count-badge { background: var(--color-brand); color: white; padding: 2px 8px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.column-content { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
.group-section { background: white; border-radius: 12px; border: 1px solid #f1f5f9; overflow: hidden; }
.group-title { padding: 12px 16px; display: flex; align-items: center; gap: 10px; cursor: pointer; background: #fcfdfe; font-weight: 600; font-size: 14px; user-select: none; transition: background 0.2s; }
.group-title:hover { background: #f8fafc; }
.toggle-icon { width: 16px; height: 16px; color: var(--color-text-muted); }
.group-items { padding: 12px; display: flex; flex-direction: column; gap: 10px; background: #ffffff; border-top: 1px solid #f1f5f9; }
.item-card { padding: 12px; border-radius: 10px; border: 1px solid #f1f5f9; background: #fcfdfe; cursor: pointer; transition: all 0.2s; }
.item-card:hover { border-color: var(--color-brand); background: #f0f7ff; transform: translateX(4px); }
.item-card.pending { border-left: 3px solid #fb923c; }
.item-card.settled { border-left: 3px solid var(--color-brand); }
.item-main { display: flex; justify-content: space-between; margin-bottom: 6px; }
.item-name { font-weight: 600; font-size: 14px; color: var(--color-text); }
.item-qty { font-size: 12px; font-weight: 700; color: var(--color-brand); }
.item-footer { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--color-text-muted); }
.meta-icon { width: 12px; height: 12px; }
.empty-state-mini { padding: 20px; text-align: center; color: var(--color-text-muted); font-size: 13px; font-style: italic; }
@media (max-width: 1024px) { .board-grid { grid-template-columns: 1fr; height: auto; } }
</style>