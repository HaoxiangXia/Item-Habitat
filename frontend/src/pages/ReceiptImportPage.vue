<template>
  <div class="page-container">
    <div class="receipt-import-page">
    <div class="receipt-split-layout">
      <!-- 左侧：纵向 9:21 预览舞台 -->
      <aside class="receipt-preview-aside">
        <GlassCard class="receipt-stage-card" title="截图预览 (9:21 Vertical)">
          <div class="receipt-stage-container">
            <div
              class="receipt-dropzone"
              :class="{ 'is-dragging': isDragging, 'is-disabled': uploading }"
              @click="openPicker"
              @dragenter.prevent="isDragging = true"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
            >
              <input
                ref="fileInput"
                class="receipt-file-input"
                type="file"
                accept="image/*"
                @change="handleFileChange"
              />

              <template v-if="receiptMeta.imageUrl">
                <div class="receipt-preview-wrapper">
                  <img class="receipt-preview-bg" :src="receiptMeta.imageUrl" aria-hidden="true" />
                  <img class="receipt-preview-image" :src="receiptMeta.imageUrl" :alt="receiptMeta.originalFilename" />
                </div>
              </template>

              <template v-else>
                <div class="receipt-dropzone-placeholder">
                  <ReceiptIcon />
                  <h3>投放纵向截图</h3>
                  <p>支持 9:21 比例长截图</p>
                </div>
              </template>
            </div>
          </div>

          <div v-if="receiptMeta.imageUrl" class="receipt-preview-meta">
            <strong class="receipt-filename">{{ receiptMeta.originalFilename }}</strong>
            <Button size="small" variant="secondary" @click="openPicker">更换截图</Button>
          </div>
        </GlassCard>
      </aside>

      <!-- 右侧：详情编辑与控制台 -->
      <main class="receipt-content-main">
        <div class="receipt-main-grid">
          <section class="receipt-editor-section">
            <GlassCard title="编辑入库清单">
              <EmptyState
                v-if="!receiptMeta.id"
                title="等待上传截图"
                description="请在左侧区域上传截图，系统将自动开始 OCR 识别。"
              >
                <template #icon>
                  <ReceiptIcon />
                </template>
              </EmptyState>

              <template v-else>
                <div class="receipt-draft-toolbar">
                  <div class="receipt-draft-meta">
                    <span class="badge">草稿 #{{ receiptMeta.id }}</span>
                    <span>{{ formatDateTime(receiptMeta.createdAt) }}</span>
                  </div>

                  <div class="receipt-draft-actions">
                    <Button type="button" variant="secondary" :disabled="isLocked" @click="addItem">添加一行</Button>
                    <Button type="button" variant="secondary" :disabled="isLocked || !hasEditableItems" @click="normalizeItems">
                      清理
                    </Button>
                  </div>
                </div>

                <label class="receipt-note">
                  <span>识别摘要 / 备注</span>
                  <textarea
                    v-model="draft.note"
                    :disabled="isLocked"
                    rows="2"
                    placeholder="模型识别摘要..."
                  ></textarea>
                </label>

                <div class="receipt-lines">
                  <article
                    v-for="(item, index) in draft.items"
                    :key="index"
                    class="receipt-line-card"
                    :class="{ 'is-empty': !item.name.trim(), 'is-locked': isLocked }"
                  >
                    <div class="receipt-line-header">
                      <span class="receipt-line-badge">{{ index + 1 }}</span>
                      <Button
                        type="button"
                        variant="danger"
                        size="small"
                        :disabled="isLocked || draft.items.length === 1"
                        @click="removeItem(index)"
                      >
                        删除
                      </Button>
                    </div>

                    <div class="receipt-line-grid">
                      <label class="receipt-field">
                        <span>商品名称</span>
                        <input v-model="item.name" :disabled="isLocked" />
                      </label>
                      <label class="receipt-field receipt-field-small">
                        <span>数量</span>
                        <input v-model.number="item.quantity" type="number" :disabled="isLocked" />
                      </label>
                      <label class="receipt-field">
                        <span>存储位置</span>
                        <input v-model="item.storageLocation" :disabled="isLocked" />
                      </label>
                      <label class="receipt-field receipt-field-wide">
                        <span>备注</span>
                        <textarea v-model="item.note" :disabled="isLocked" rows="1"></textarea>
                      </label>
                    </div>
                  </article>
                </div>
              </template>
            </GlassCard>
          </section>

          <aside class="receipt-sidebar">
            <GlassCard title="确认入库" class="receipt-confirm-card">
              <div v-if="receiptMeta.id" class="receipt-confirm-panel">
                <div class="receipt-upload-summary">
                  <div class="receipt-summary-item">
                    <span>状态</span>
                    <strong :class="statusBadgeClass">{{ statusLabel }}</strong>
                  </div>
                  <div class="receipt-summary-item">
                    <span>有效商品</span>
                    <strong>{{ validItems.length }} 条</strong>
                  </div>
                  <div class="receipt-summary-item">
                    <span>同步记录</span>
                    <strong>{{ saveStateLabel }}</strong>
                  </div>
                </div>

                <div class="receipt-action-stack">
                  <Button 
                    type="button" 
                    class="btn-full"
                    :disabled="isLocked || confirming || !validItems.length" 
                    @click="confirmDraft"
                  >
                    {{ confirming ? '确认中...' : '确认同步' }}
                  </Button>
                  <Button type="button" variant="secondary" :disabled="!receiptMeta.id || saving" @click="saveDraft(true)">
                    立即保存
                  </Button>
                </div>
              </div>
              <EmptyState v-else title="未就绪" compact description="等待数据接入" />
            </GlassCard>
          </aside>
        </div>
      </main>
    </div>

    <GlassCard :title="`最近导入记录 · ${receiptImports.length} 条`">
      <DataTable
        :columns="importColumns"
        :data="receiptImports"
        row-key="id"
        empty-title="暂无截图导入记录"
        empty-description="上传第一张截图后，这里会显示所有导入草稿。"
      >
        <template #status="{ row }">
          <span :class="['badge', row.status === 'CONFIRMED' ? 'badge-confirmed' : 'badge-pending']">
            {{ row.status === 'CONFIRMED' ? '已确认' : '待确认' }}
          </span>
        </template>

        <template #createdAt="{ row }">
          <span class="time-col">{{ formatDateTime(row.createdAt) }}</span>
        </template>

        <template #confirmedAt="{ row }">
          <span class="time-col">{{ row.confirmedAt ? formatDateTime(row.confirmedAt) : '—' }}</span>
        </template>

        <template #actions="{ row }">
          <Button
            type="button"
            size="small"
            variant="secondary"
            @click="openImport(row.id)"
          >
            {{ row.status === 'CONFIRMED' ? '查看' : '继续编辑' }}
          </Button>
        </template>
      </DataTable>
    </GlassCard>
  </div>
</div>
</template>

<script setup>
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInventoryStore } from '../stores/inventory.store'
import { useUiStore } from '../stores/ui.store'
import { confirmReceiptImport, createReceiptImport, getReceiptImport, getReceiptImports, updateReceiptImport } from '../services/api'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/layout/PageHeader.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import DataTable from '../components/ui/DataTable.vue'
import Button from '../components/ui/Button.vue'
import { CheckIcon, ReceiptIcon } from '../components/icons'

const route = useRoute()
const router = useRouter()
const inventory = useInventoryStore()
const ui = useUiStore()

const fileInput = ref(null)
const receiptImports = ref([])
const uploadMessage = ref('')
const confirmMessage = ref('')
const uploading = ref(false)
const saving = ref(false)
const confirming = ref(false)
const isDragging = ref(false)
const saveState = ref('idle')
const saveTimer = ref(null)
const hydrating = ref(false)

const receiptMeta = reactive({
  id: null,
  originalFilename: '',
  imagePath: '',
  imageUrl: '',
  status: '',
  createdAt: '',
  confirmedAt: '',
  itemCount: 0
})

const draft = reactive({
  note: '',
  items: [createDraftItem()]
})

const importColumns = [
  { key: 'id', label: '编号' },
  { key: 'originalFilename', label: '文件名' },
  { key: 'status', label: '状态' },
          { key: 'itemCount', label: '有效结果' },
  { key: 'createdAt', label: '创建时间' },
  { key: 'confirmedAt', label: '确认时间' },
  { key: 'actions', label: '操作' }
]

function createDraftItem() {
  return {
    name: '',
    quantity: 1,
    storageLocation: '',
    note: ''
  }
}

function clearSaveTimer() {
  if (saveTimer.value) {
    clearTimeout(saveTimer.value)
    saveTimer.value = null
  }
}

function resetMeta() {
  receiptMeta.id = null
  receiptMeta.originalFilename = ''
  receiptMeta.imagePath = ''
  receiptMeta.imageUrl = ''
  receiptMeta.status = ''
  receiptMeta.createdAt = ''
  receiptMeta.confirmedAt = ''
  receiptMeta.itemCount = 0
  saveState.value = 'idle'
}

function resetDraft() {
  draft.note = ''
  draft.items.splice(0, draft.items.length, createDraftItem())
}

function normalizeItem(item) {
  return {
    name: String(item?.name || '').trim(),
    quantity: Number.isFinite(Number(item?.quantity)) && Number(item?.quantity) > 0 ? Number(item.quantity) : 1,
    storageLocation: String(item?.storageLocation || '').trim(),
    note: String(item?.note || '').trim()
  }
}

function applyImport(record) {
  hydrating.value = true
  try {
    receiptMeta.id = record.id ?? null
    receiptMeta.originalFilename = record.originalFilename || ''
    receiptMeta.imagePath = record.imagePath || ''
    receiptMeta.imageUrl = record.imageUrl || ''
    receiptMeta.status = record.status || ''
    receiptMeta.createdAt = record.createdAt || ''
    receiptMeta.confirmedAt = record.confirmedAt || ''
    receiptMeta.itemCount = record.itemCount || 0

    draft.note = record.note || ''
    const items = Array.isArray(record.items) && record.items.length
      ? record.items.map((item) => normalizeItem(item))
      : [createDraftItem()]

    draft.items.splice(0, draft.items.length, ...items)
  } finally {
    hydrating.value = false
  }
}

function buildDraftPayload() {
  return {
    note: draft.note.trim(),
    items: draft.items.map((item) => normalizeItem(item))
  }
}

async function loadImports() {
  try {
    receiptImports.value = await getReceiptImports()
  } catch (error) {
    ui.error(error instanceof Error ? error.message : '加载导入列表失败')
  }
}

async function openImport(importId) {
  await router.replace({
    name: 'ReceiptImports',
    query: { draft: String(importId) }
  })
}

async function refreshCurrentDraft() {
  if (!receiptMeta.id) {
    return
  }

  await loadImport(receiptMeta.id)
}

async function loadImport(importId) {
  if (!importId) {
    resetMeta()
    resetDraft()
    return
  }

  try {
    const record = await getReceiptImport(importId)
    applyImport(record)
    saveState.value = 'idle'
  } catch (error) {
    ui.error(error instanceof Error ? error.message : '加载导入草稿失败')
  }
}

async function persistDraft() {
  if (!receiptMeta.id || hydrating.value) {
    return true
  }

  saving.value = true
  saveState.value = 'saving'

  try {
    const record = await updateReceiptImport(receiptMeta.id, buildDraftPayload())
    applyImport(record)
    saveState.value = 'saved'
    await loadImports()
    return true
  } catch (error) {
    saveState.value = 'dirty'
    ui.error(error instanceof Error ? error.message : '保存草稿失败')
    return false
  } finally {
    saving.value = false
  }
}

function scheduleSave() {
  if (hydrating.value || !receiptMeta.id) {
    return
  }

  clearSaveTimer()
  saveState.value = 'dirty'
  saveTimer.value = setTimeout(() => {
    persistDraft()
  }, 600)
}

async function saveDraft(immediate = false) {
  clearSaveTimer()
  if (!immediate) {
    scheduleSave()
    return true
  }

  return persistDraft()
}

function validateFile(file) {
  if (!file) {
    return '请选择图片文件'
  }

  if (!file.type || !file.type.startsWith('image/')) {
    return '仅支持上传图片文件'
  }

  if (file.size <= 0) {
    return '图片文件为空'
  }

  if (file.size > 5 * 1024 * 1024) {
    return '图片大小不能超过 5MB'
  }

  return ''
}

async function submitUpload(file) {
  const validationMessage = validateFile(file)
  if (validationMessage) {
    uploadMessage.value = validationMessage
    ui.error(validationMessage)
    return
  }

  uploading.value = true
    uploadMessage.value = '正在上传截图并调用本地模型识别...'

  try {
    const record = await createReceiptImport(file)
    applyImport(record)
    saveState.value = 'idle'
    uploadMessage.value = '上传成功，草稿已创建，可以开始编辑。'
    await router.replace({
      name: 'ReceiptImports',
      query: { draft: String(record.id) }
    })
    await loadImports()
    ui.success('截图导入草稿创建成功')
  } catch (error) {
    uploadMessage.value = error instanceof Error ? error.message : '上传失败'
    ui.error(uploadMessage.value)
  } finally {
    uploading.value = false
    isDragging.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

function openPicker() {
  if (uploading.value) {
    return
  }

  fileInput.value?.click()
}

async function handleFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  await submitUpload(file)
}

async function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file) {
    return
  }

  await submitUpload(file)
}

function addItem() {
  draft.items.push(createDraftItem())
  scheduleSave()
}

function removeItem(index) {
  if (draft.items.length === 1) {
    draft.items.splice(0, 1, createDraftItem())
  } else {
    draft.items.splice(index, 1)
  }

  scheduleSave()
}

function normalizeItems() {
  const normalized = draft.items
    .map((item) => normalizeItem(item))
    .filter((item) => item.name)

  draft.items.splice(0, draft.items.length, ...(normalized.length ? normalized : [createDraftItem()]))
  scheduleSave()
}

const validItems = computed(() =>
  draft.items.filter((item) => normalizeItem(item).name)
)

const hasEditableItems = computed(() => draft.items.some((item) => item.name.trim() || item.note.trim() || item.storageLocation.trim()))
const isLocked = computed(() => receiptMeta.status === 'CONFIRMED')
const statusLabel = computed(() => {
  if (!receiptMeta.id) {
    return '未导入'
  }

  return receiptMeta.status === 'CONFIRMED' ? '已确认' : '待确认'
})
const statusBadgeClass = computed(() => (receiptMeta.status === 'CONFIRMED' ? 'badge-confirmed' : 'badge-pending'))
const saveStateLabel = computed(() => {
  if (saving.value) {
    return '保存中'
  }

  if (saveState.value === 'saved') {
    return '已自动保存'
  }

  if (saveState.value === 'dirty') {
    return '未保存'
  }

  return receiptMeta.id ? '已加载' : '等待上传'
})

async function confirmDraft() {
  if (!receiptMeta.id) {
    ui.error('请先上传截图')
    return
  }

  if (!validItems.value.length) {
    ui.error('请至少填写一条有效商品')
    return
  }

  const saved = await saveDraft(true)
  if (!saved) {
    return
  }

  confirming.value = true
  confirmMessage.value = '正在确认入库...'

  try {
    const result = await confirmReceiptImport(receiptMeta.id)
    confirmMessage.value = result.message || '确认成功'
    ui.success(confirmMessage.value)
    await Promise.all([loadImport(receiptMeta.id), loadImports(), inventory.refresh()])
  } catch (error) {
    confirmMessage.value = error instanceof Error ? error.message : '确认入库失败'
    ui.error(confirmMessage.value)
  } finally {
    confirming.value = false
  }
}

watch(
  () => route.query.draft,
  async (draftId) => {
    const value = Array.isArray(draftId) ? draftId[0] : draftId
    if (value) {
      await loadImport(Number(value))
    } else {
      resetMeta()
      resetDraft()
      confirmMessage.value = ''
    }

    await loadImports()
  },
  { immediate: true }
)

watch(
  draft,
  () => {
    if (hydrating.value || !receiptMeta.id || isLocked.value) {
      return
    }

    scheduleSave()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  clearSaveTimer()
})
</script>
