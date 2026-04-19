<template>
  <Transition name="drawer">
    <div v-if="show" class="drawer-overlay" @click.self="emit('update:show', false)">
      <div class="drawer-content">
        <div class="drawer-header">
          <button class="close-btn" @click="emit('update:show', false)">✕</button>
          <h3>物品档案</h3>
        </div>

        <div v-if="item" class="drawer-body">
          <!-- 物品图片/占位 -->
          <div class="info-section">
            <div class="item-image-container">
              <div class="item-image-placeholder">
                {{ item.name?.[0] || '?' }}
              </div>
            </div>
          </div>

          <!-- 基础信息 -->
          <div class="info-section">
            <div class="info-row">
              <label>名称</label>
              <div class="info-value name">{{ item.name }}</div>
            </div>

            <div class="info-row">
              <label>数量</label>
              <div class="qty-control">
                <button @click="adjustQty(-1)">-</button>
                <div class="qty-num">{{ item.quantity }}</div>
                <button @click="adjustQty(1)">+</button>
              </div>
            </div>

            <div class="info-row">
              <label>存储位置</label>
              <div class="info-value location-link" @click="goToLocation">
                {{ item.storageLocation }}
              </div>
            </div>

            <div class="info-row">
              <label>状态</label>
              <div class="info-value">
                <span class="status-dot" :class="item.quantity > 5 ? 'normal' : 'alarm'"></span>
                {{ item.quantity > 5 ? '栖息中' : '库存预警' }}
              </div>
            </div>
          </div>

          <!-- 标签 -->
          <div class="tag-section">
            <label>标签</label>
            <div class="tags-container">
              <span v-for="tag in itemTags" :key="tag" class="tag">
                {{ tag }}
                <button class="remove-tag" @click="removeTag(tag)">×</button>
              </span>
              <input 
                v-model="newTag" 
                type="text" 
                placeholder="+ 新标签" 
                class="tag-input"
                @keyup.enter="addTag"
              >
            </div>
          </div>

          <!-- 备忘 -->
          <div class="note-section">
            <label>备忘</label>
            <textarea 
              :value="item.note || '暂无备注'" 
              class="note-display"
              placeholder="添加备注..."
              readonly
            ></textarea>
          </div>

          <!-- 变更日志 -->
          <div class="logs-section">
            <label>变更日志</label>
            <div class="logs-list">
              <div v-for="log in itemLogs" :key="log.id" class="log-item">
                <span class="log-time">{{ formatTime(log.createdAt) }}</span>
                <span class="log-type" :class="log.type === 'IN' ? 'in' : 'out'">
                  {{ log.type === 'IN' ? '栖息' : '迁徙' }}
                </span>
                <span class="log-qty">{{ log.type === 'IN' ? '+' : '-' }}{{ log.quantity }}</span>
              </div>
              <div v-if="!itemLogs.length" class="empty-logs">暂无近日变动</div>
            </div>
          </div>

          <!-- 操作 -->
          <div class="actions-section">
            <button class="action-btn delete" @click="deleteItem">删除该物品</button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useInventoryStore } from '../../stores/inventory.store'
import { formatDateTime } from '../../utils/format'

const props = defineProps({
  show: Boolean,
  item: Object
})

const emit = defineEmits(['update:show', 'refresh'])

const inventory = useInventoryStore()
const router = useRouter()
const newTag = ref('')

const itemTags = computed(() => {
  if (!props.item?.tags) return []
  return typeof props.item.tags === 'string' ? props.item.tags.split(',').filter(Boolean) : props.item.tags
})

const itemLogs = computed(() => {
  if (!props.item) return []
  return inventory.recentTransactions.filter(t => t.productId === props.item.id).slice(0, 5)
})

const adjustQty = async (delta) => {
  if (!props.item) return
  const newQty = props.item.quantity + delta
  if (newQty < 0) return
  
  const res = await inventory.updateProductInfo(props.item.id, { quantity: newQty })
  if (res.success) {
    emit('refresh')
  }
}

const goToLocation = () => {
  if (props.item?.storageLocation) {
    router.push({ name: 'LocationDetail', params: { locationId: props.item.storageLocation } })
    emit('update:show', false)
  }
}

const deleteItem = async () => {
  if (!props.item) return
  if (!confirm(`确定要由生命之网中抹去「${props.item.name}」吗？这一操作不可撤销。`)) return
  
  const res = await inventory.removeProduct(props.item.id)
  if (res.success) {
    emit('update:show', false)
    emit('refresh')
  }
}

const addTag = async () => {
  if (!newTag.value.trim() || !props.item) return
  const currentTags = [...itemTags.value]
  if (!currentTags.includes(newTag.value.trim())) {
    currentTags.push(newTag.value.trim())
    const res = await inventory.updateProductInfo(props.item.id, { tags: currentTags.join(',') })
    if (res.success) {
      emit('refresh')
    }
  }
  newTag.value = ''
}

const removeTag = async (tagToRemove) => {
  if (!props.item) return
  const currentTags = itemTags.value.filter(t => t !== tagToRemove)
  const res = await inventory.updateProductInfo(props.item.id, { tags: currentTags.join(',') })
  if (res.success) {
    emit('refresh')
  }
}

const formatTime = (time) => formatDateTime(time).split(' ')[0]
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.drawer-content {
  width: 400px;
  height: 100%;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--glass-border);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.item-image-container {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--glass-border);
}

.item-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  font-weight: 700;
  color: var(--color-brand);
  opacity: 0.3;
}

.info-section label, .tag-section label, .note-section label, .logs-section label {
  display: block;
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.info-row {
  margin-bottom: 16px;
}

.info-value.name {
  font-size: 1.25rem;
  font-weight: 700;
}

.qty-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.qty-control button {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text);
  cursor: pointer;
}

.qty-num {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.2rem;
}

.location-link {
  color: var(--color-brand);
  text-decoration: underline;
  cursor: pointer;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.status-dot.normal { background: var(--color-success); }
.status-dot.alarm { background: var(--color-alarm); }

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: rgba(var(--color-brand-rgb), 0.1);
  color: var(--color-brand);
  padding: 2px 10px;
  border-radius: 100px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.remove-tag {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  font-size: 1rem;
}

.tag-input {
  background: transparent;
  border: 1px dashed var(--glass-border);
  border-radius: 100px;
  padding: 2px 12px;
  font-size: 0.8rem;
  color: var(--color-text);
  outline: none;
  width: 80px;
}

.note-display {
  width: 100%;
  min-height: 80px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 12px;
  color: var(--color-text);
  font-family: inherit;
  resize: none;
}

.logs-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
}

.log-time { color: var(--color-text-muted); font-size: 0.8rem; }
.log-type.in { color: var(--color-success); }
.log-type.out { color: var(--color-alarm); }
.log-qty { font-weight: 700; margin-left: auto; }

.actions-section {
  margin-top: auto;
  padding-top: 24px;
  border-top: 1px solid var(--glass-border);
}

.action-btn {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.delete {
  color: var(--color-alarm);
  border-color: rgba(var(--color-alarm-rgb), 0.3);
}

.action-btn.delete:hover {
  background: rgba(var(--color-alarm-rgb), 0.1);
}

/* Transitions */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-content {
  transform: translateX(100%);
}

.drawer-leave-to .drawer-content {
  transform: translateX(100%);
}
</style>
