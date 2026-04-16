<template>
  <PageHeader
    title="购物截图导入"
    subtitle="上传收货截图，手动校对后批量转成入库记录"
  >
    <template #icon>
      <ReceiptIcon />
    </template>

    <template #actions>
      <Button variant="secondary" type="button" @click="openPicker">选择截图</Button>
      <router-link class="nav-btn" to="/inbound">返回入库</router-link>
    </template>
  </PageHeader>

  <div class="receipt-import-page">
    <GlassCard title="第 1 步：上传截图">
      <div class="receipt-upload-grid">
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
            <img class="receipt-preview-image" :src="receiptMeta.imageUrl" :alt="receiptMeta.originalFilename" />
            <div class="receipt-dropzone-text">
              <p class="receipt-dropzone-kicker">当前截图</p>
              <h3>{{ receiptMeta.originalFilename }}</h3>
              <p>文件已上传，下面可以直接编辑草稿并确认入库。</p>
            </div>
          </template>

          <template v-else>
            <div class="receipt-dropzone-placeholder">
              <ReceiptIcon />
              <h3>点击或拖拽上传购物截图</h3>
              <p>支持 PNG、JPG、GIF、WEBP，单文件不超过 5MB。</p>
            </div>
          </template>
        </div>

        <div class="receipt-upload-side">
          <div class="receipt-upload-summary">
            <div class="receipt-summary-item">
              <span class="receipt-summary-label">导入状态</span>
              <strong :class="['badge', statusBadgeClass]">{{ statusLabel }}</strong>
            </div>
            <div class="receipt-summary-item">
              <span class="receipt-summary-label">有效条目</span>
              <strong>{{ validItems.length }} 条</strong>
            </div>
            <div class="receipt-summary-item">
              <span class="receipt-summary-label">草稿状态</span>
              <strong>{{ saveStateLabel }}</strong>
            </div>
          </div>

          <p class="receipt-upload-hint">
            这个 MVP 不做自动 OCR，上传后会先生成一个可编辑草稿。你可以把识别到的商品名、数量和位置手动补全，再统一确认入库。
          </p>

          <p v-if="uploadMessage" class="receipt-helper-text">{{ uploadMessage }}</p>
        </div>
      </div>
    </GlassCard>

    <div class="receipt-main-grid">
      <GlassCard title="第 2 步：编辑待整理草稿">
        <EmptyState
          v-if="!receiptMeta.id"
          title="还没有导入草稿"
          description="先上传一张购物截图，系统会自动创建一个可编辑草稿。"
        >
          <template #icon>
            <ReceiptIcon />
          </template>
        </EmptyState>

        <template v-else>
          <div class="receipt-draft-toolbar">
            <div class="receipt-draft-meta">
              <span>草稿编号 #{{ receiptMeta.id }}</span>
              <span>创建于 {{ formatDateTime(receiptMeta.createdAt) }}</span>
              <span v-if="receiptMeta.confirmedAt">确认于 {{ formatDateTime(receiptMeta.confirmedAt) }}</span>
            </div>

            <div class="receipt-draft-actions">
              <Button type="button" variant="secondary" :disabled="isLocked" @click="addItem">添加一行</Button>
              <Button type="button" variant="secondary" :disabled="isLocked || !hasEditableItems" @click="normalizeItems">
                清理空行
              </Button>
            </div>
          </div>

          <div class="receipt-lines">
            <article
              v-for="(item, index) in draft.items"
              :key="index"
              class="receipt-line-card"
              :class="{ 'is-empty': !item.name.trim() }"
            >
              <div class="receipt-line-header">
                <div class="receipt-line-title">
                  <span class="receipt-line-badge">条目 {{ index + 1 }}</span>
                  <span class="receipt-line-subtitle" v-if="item.name.trim()">{{ item.name }}</span>
                  <span class="receipt-line-subtitle is-muted" v-else>等待填写商品信息</span>
                </div>

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
                  <input v-model="item.name" :disabled="isLocked" placeholder="例如：蓝牙耳机" />
                </label>

                <label class="receipt-field receipt-field-small">
                  <span>数量</span>
                  <input
                    v-model.number="item.quantity"
                    :disabled="isLocked"
                    type="number"
                    min="1"
                    step="1"
                  />
                </label>

                <label class="receipt-field">
                  <span>存储位置</span>
                  <input v-model="item.storageLocation" :disabled="isLocked" placeholder="例如：宿舍衣柜左上格" />
                </label>

                <label class="receipt-field receipt-field-wide">
                  <span>备注</span>
                  <textarea v-model="item.note" :disabled="isLocked" rows="2" placeholder="可选备注"></textarea>
                </label>
              </div>
            </article>
          </div>
        </template>
      </GlassCard>

      <GlassCard title="第 3 步：确认入库">
        <EmptyState
          v-if="!receiptMeta.id"
          title="等待草稿生成"
          description="上传截图后，这里会显示确认信息和入库按钮。"
        >
          <template #icon>
            <CheckIcon />
          </template>
        </EmptyState>

        <template v-else>
          <div class="receipt-confirm-panel">
            <div class="receipt-confirm-stats">
              <div class="receipt-confirm-stat">
                <span>文件名</span>
                <strong>{{ receiptMeta.originalFilename }}</strong>
              </div>
              <div class="receipt-confirm-stat">
                <span>草稿条目</span>
                <strong>{{ validItems.length }} 条</strong>
              </div>
              <div class="receipt-confirm-stat">
                <span>状态</span>
                <strong>{{ statusLabel }}</strong>
              </div>
              <div class="receipt-confirm-stat">
                <span>自动保存</span>
                <strong>{{ saveStateLabel }}</strong>
              </div>
            </div>

            <div class="receipt-confirm-note">
              <p>
                确认后，草稿中的每一条有效商品都会写入现有库存表和交易表。此操作会生成正常的入库记录，方便后续检索和历史回溯。
              </p>
            </div>

            <div class="form-actions">
              <Button type="button" :disabled="isLocked || confirming || !validItems.length" @click="confirmDraft">
                {{ confirming ? '确认中...' : '确认入库' }}
              </Button>
              <Button type="button" variant="secondary" :disabled="!receiptMeta.id || saving" @click="saveDraft(true)">
                保存草稿
              </Button>
              <Button type="button" variant="secondary" :disabled="!receiptMeta.id" @click="refreshCurrentDraft">
                重新加载
              </Button>
            </div>

            <p v-if="confirmMessage" class="receipt-helper-text">{{ confirmMessage }}</p>
          </div>
        </template>
      </GlassCard>
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
  { key: 'itemCount', label: '有效条目' },
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
  uploadMessage.value = '正在上传截图并创建导入草稿...'

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
      return
    }

    resetMeta()
    resetDraft()
    confirmMessage.value = ''
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

watch(
  () => route.query.draft,
  async () => {
    await loadImports()
  },
  { immediate: true }
)

loadImports()

onBeforeUnmount(() => {
  clearSaveTimer()
})
</script>
