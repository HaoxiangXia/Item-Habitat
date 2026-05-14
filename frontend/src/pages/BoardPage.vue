<template>
  <div class="page-container board-page">
    <div class="board-header">
      <div>
        <h2 class="view-title">看板</h2>
        <p class="board-subtitle">拖拽卡片在待整理与已归位之间流转</p>
      </div>
      <div class="board-stats">
        共 {{ inventory.products.length }} 件物品 · 待整理 {{ pendingList.length }} · 已归位 {{ storedList.length }}
      </div>
    </div>

    <div class="board-grid">
      <section class="board-column pending" :class="{ 'is-dragging': dragging }">
        <div class="column-header">
          <div class="column-title">
            <h3>待整理</h3>
            <span class="count-badge">{{ pendingList.length }}</span>
          </div>
          <span class="column-tip">支持拖拽与一键归位</span>
        </div>

        <Draggable
          v-model="pendingList"
          item-key="id"
          group="board"
          class="column-content"
          ghost-class="drag-ghost"
          chosen-class="drag-chosen"
          @change="handleDragChange('pending', $event)"
          @start="dragging = true"
          @end="dragging = false"
        >
          <template #item="{ element }">
            <div class="item-card pending" @click="openItem(element)">
              <div class="item-main">
                <div class="item-title-row">
                  <span class="item-name">{{ element.name }}</span>
                  <span class="item-qty">x {{ element.quantity }}</span>
                </div>
                <div class="item-meta">
                  <span class="meta-pill">{{ element.storageLocation || '待整理' }}</span>
                  <span v-if="element.deadline" class="meta-pill warning">截止 {{ formatDateOnly(element.deadline) }}</span>
                </div>
                <div v-if="formatTags(element.tags)" class="item-tags">{{ formatTags(element.tags) }}</div>
              </div>
              <div class="item-footer">
                <ClockIcon class="meta-icon" />
                <span>{{ formatTimeOnly(element.createdAt) }}</span>
              </div>
              <div class="item-actions">
                <Button size="small" @click.stop="quickStore(element)">一键归位</Button>
              </div>
            </div>
          </template>
          <template #footer>
            <div v-if="!pendingList.length" class="empty-state-mini">暂无待整理物品</div>
          </template>
        </Draggable>
      </section>

      <section class="board-column stored" :class="{ 'is-dragging': dragging }">
        <div class="column-header">
          <div class="column-title">
            <h3>已归位</h3>
            <span class="count-badge">{{ storedList.length }}</span>
          </div>
          <span class="column-tip">拖回待整理可重新规划</span>
        </div>

        <Draggable
          v-model="storedList"
          item-key="id"
          group="board"
          class="column-content"
          ghost-class="drag-ghost"
          chosen-class="drag-chosen"
          @change="handleDragChange('stored', $event)"
          @start="dragging = true"
          @end="dragging = false"
        >
          <template #item="{ element }">
            <div class="item-card stored" @click="openItem(element)">
              <div class="item-main">
                <div class="item-title-row">
                  <span class="item-name">{{ element.name }}</span>
                  <span class="item-qty">x {{ element.quantity }}</span>
                </div>
                <div class="item-meta">
                  <span class="meta-pill">{{ element.storageLocation || '未指定空间' }}</span>
                  <span v-if="element.deadline" class="meta-pill warning">截止 {{ formatDateOnly(element.deadline) }}</span>
                </div>
                <div v-if="formatTags(element.tags)" class="item-tags">{{ formatTags(element.tags) }}</div>
              </div>
              <div class="item-footer">
                <ClockIcon class="meta-icon" />
                <span>{{ formatTimeOnly(element.updatedAt || element.createdAt) }}</span>
              </div>
            </div>
          </template>
          <template #footer>
            <div v-if="!storedList.length" class="empty-state-mini">暂无已归位物品</div>
          </template>
        </Draggable>
      </section>
    </div>

    <Modal :open="storeModal.open" title="选择归位空间" @close="cancelStore">
      <div class="store-modal-body">
        <p class="store-hint">选择一个空间后将写入日志，表示该物品已归位。</p>
        <SelectField
          v-model="storeModal.location"
          label="归位空间"
          :options="locationOptions"
          option-label-key="name"
          option-value-key="name"
          placeholder="请选择空间"
        />
        <div class="modal-actions">
          <Button variant="secondary" @click="cancelStore">取消</Button>
          <Button :disabled="!storeModal.location" @click="confirmStore">确认归位</Button>
        </div>
      </div>
    </Modal>

    <ItemDrawer
      v-model:show="drawerOpen"
      :item="selectedItem"
      @refresh="inventory.refresh()"
    />
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import Draggable from 'vuedraggable'
import { useInventoryStore } from '../stores/inventory.store'
import { useUiStore } from '../stores/ui.store'
import { formatDate, formatDateTime, normalizeText } from '../utils/format'
import ItemDrawer from '../components/features/ItemDrawer.vue'
import Modal from '../components/ui/Modal.vue'
import SelectField from '../components/ui/Select.vue'
import Button from '../components/ui/Button.vue'
import { ClockIcon } from '../components/icons'

const inventory = useInventoryStore()
const ui = useUiStore()

const drawerOpen = ref(false)
const selectedItem = ref(null)
const pendingList = ref([])
const storedList = ref([])
const dragging = ref(false)
const statusOverrides = ref({})

const storeModal = reactive({
  open: false,
  item: null,
  location: '',
  dragged: false,
  previousStatus: ''
})

const locationOptions = computed(() => inventory.locationOptions)

function formatTimeOnly(dt) {
  const f = formatDateTime(dt)
  return f ? f.split(' ')[0] : ''
}

function formatDateOnly(value) {
  return formatDate(value)
}

function formatTags(tags) {
  if (!tags) return ''
  if (Array.isArray(tags)) return tags.join(' / ')
  if (typeof tags === 'string') return tags.split(',').filter(Boolean).join(' / ')
  return ''
}

function getBoardStatus(item) {
  const override = statusOverrides.value[item.id]
  if (override) return override
  if (item.status === 'pending' || item.status === 'stored') return item.status
  const location = normalizeText(item.storageLocation)
  return location ? 'stored' : 'pending'
}

function syncBoardLists() {
  const items = [...inventory.products].sort((a, b) => {
    const timeA = String(a.updatedAt || a.createdAt || '')
    const timeB = String(b.updatedAt || b.createdAt || '')
    return timeB.localeCompare(timeA)
  })
  pendingList.value = items.filter((item) => getBoardStatus(item) === 'pending')
  storedList.value = items.filter((item) => getBoardStatus(item) === 'stored')
}

watch(
  () => inventory.products,
  () => syncBoardLists(),
  { immediate: true, deep: true }
)

watch(statusOverrides, () => syncBoardLists(), { deep: true })

function setOverride(itemId, status) {
  const next = { ...statusOverrides.value }
  if (status) {
    next[itemId] = status
  } else {
    delete next[itemId]
  }
  statusOverrides.value = next
}

function openItem(item) {
  selectedItem.value = item
  drawerOpen.value = true
}

function quickStore(item) {
  const location = normalizeText(item.storageLocation)
  if (location) {
    commitStore(item, location, false)
    return
  }
  beginStore(item, true)
}

function beginStore(item, fromDrag) {
  storeModal.item = item
  storeModal.location = normalizeText(item.storageLocation)
  storeModal.open = true
  storeModal.dragged = fromDrag
  storeModal.previousStatus = getBoardStatus(item)
}

function cancelStore() {
  if (storeModal.dragged && storeModal.item) {
    const item = storeModal.item
    storedList.value = storedList.value.filter((entry) => entry.id !== item.id)
    if (!pendingList.value.some((entry) => entry.id === item.id)) {
      pendingList.value.unshift(item)
    }
  }
  storeModal.open = false
  storeModal.item = null
  storeModal.location = ''
  storeModal.dragged = false
  storeModal.previousStatus = ''
}

async function confirmStore() {
  if (!storeModal.item || !storeModal.location) return
  const item = storeModal.item
  const previousOverride = statusOverrides.value[item.id]
  setOverride(item.id, 'stored')
  const result = await inventory.updateProductInfo(item.id, {
    storageLocation: storeModal.location
  })
  if (result.success) {
    ui.success('已归位并写入日志')
  } else {
    setOverride(item.id, previousOverride)
    ui.error(result.message || '归位失败')
  }
  cancelStore()
}

async function commitStore(item, location, fromDrag) {
  const previousOverride = statusOverrides.value[item.id]
  setOverride(item.id, 'stored')
  const result = await inventory.updateProductInfo(item.id, {
    storageLocation: location
  })
  if (result.success) {
    ui.success('已归位并写入日志')
    return
  }
  setOverride(item.id, previousOverride)
  ui.error(result.message || '归位失败')
  if (fromDrag) {
    storedList.value = storedList.value.filter((entry) => entry.id !== item.id)
    pendingList.value.unshift(item)
  }
}

async function moveToPending(item) {
  const previousOverride = statusOverrides.value[item.id]
  setOverride(item.id, 'pending')
  const result = await inventory.updateProductInfo(item.id, {
    storageLocation: ''
  })
  if (result.success) {
    ui.success('已移回待整理并写入日志')
    return
  }
  setOverride(item.id, previousOverride)
  ui.error(result.message || '更新失败')
  pendingList.value = pendingList.value.filter((entry) => entry.id !== item.id)
  storedList.value.unshift(item)
}

function handleDragChange(targetStatus, evt) {
  if (!evt?.added) return
  const item = evt.added.element
  if (!item) return
  if (targetStatus === 'stored') {
    const location = normalizeText(item.storageLocation)
    if (location) {
      commitStore(item, location, true)
    } else {
      beginStore(item, true)
    }
    return
  }
  moveToPending(item)
}
</script>

<style scoped>
.board-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin-bottom: 24px; }
.view-title { font-size: 1.6rem; font-weight: 700; color: var(--color-text); margin-bottom: 6px; }
.board-subtitle { font-size: 13px; color: var(--color-text-muted); }
.board-stats { font-size: 13px; color: var(--color-text-muted); text-align: right; }
.board-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; height: calc(100vh - 180px); min-height: 520px; }
.board-column { background: rgba(255, 255, 255, 0.4); border-radius: 20px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02); }
.column-header { padding: 16px 20px; background: rgba(255, 255, 255, 0.6); border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.column-title { display: flex; align-items: center; gap: 10px; }
.column-header h3 { font-size: 16px; font-weight: 700; color: var(--color-text); }
.column-tip { font-size: 12px; color: var(--color-text-muted); }
.count-badge { background: var(--color-brand); color: white; padding: 2px 8px; border-radius: 100px; font-size: 12px; font-weight: 700; }
.column-content { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; min-height: 200px; }
.item-card { padding: 14px; border-radius: 12px; border: 1px solid #f1f5f9; background: #fcfdfe; cursor: pointer; transition: all 0.2s; display: flex; flex-direction: column; gap: 10px; }
.item-card:hover { border-color: var(--color-brand); background: #f0f7ff; transform: translateX(4px); }
.item-card.pending { border-left: 3px solid #fb923c; }
.item-card.stored { border-left: 3px solid var(--color-brand); }
.item-title-row { display: flex; justify-content: space-between; gap: 12px; }
.item-name { font-weight: 600; font-size: 14px; color: var(--color-text); }
.item-qty { font-size: 12px; font-weight: 700; color: var(--color-brand); }
.item-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.meta-pill { display: inline-flex; padding: 2px 8px; border-radius: 999px; background: #f8fafc; border: 1px solid #e2e8f0; font-size: 11px; color: #475569; }
.meta-pill.warning { background: rgba(249, 115, 22, 0.12); border-color: rgba(249, 115, 22, 0.3); color: #c2410c; }
.item-tags { font-size: 12px; color: var(--color-text-muted); }
.item-footer { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--color-text-muted); }
.meta-icon { width: 12px; height: 12px; }
.item-actions { display: flex; justify-content: flex-end; }
.empty-state-mini { padding: 20px; text-align: center; color: var(--color-text-muted); font-size: 13px; font-style: italic; }
.drag-ghost { opacity: 0.4; }
.drag-chosen { background: #e0f2fe; }
.store-modal-body { display: flex; flex-direction: column; gap: 16px; }
.store-hint { font-size: 13px; color: var(--color-text-muted); }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; }
@media (max-width: 1024px) {
  .board-grid { grid-template-columns: 1fr; height: auto; }
  .board-header { flex-direction: column; align-items: flex-start; }
  .board-stats { text-align: left; }
}
</style>