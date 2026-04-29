<template>
  <div class="page-container">
    <div class="migration-grid">
      <!-- 栖息卡片 -->
      <div class="migration-card-wrapper">
        <div class="card-header-simple">
          <h2>栖息</h2>
          <p>将新物品登记入库</p>
        </div>
        <div class="card-body-simple">
          <form class="form" @submit.prevent="handleInbound">
            <InputField v-model="inbound.name" label="物品名称" required placeholder="请输入物品名称" />
            <InputField v-model="inbound.quantity" type="number" label="数量" min="1" required />
            <div class="location-select-row">
              <SelectField
                v-model="inbound.storageLocation"
                label="栖息至"
                :options="locationOptions"
                option-label-key="name"
                option-value-key="name"
                placeholder="请选择存储空间"
                class="flex-1"
              />
              <button type="button" class="add-btn-small" title="添加新空间" @click="showAddModal = true">+</button>
            </div>
            <TextareaField v-model="inbound.note" label="备注" rows="3" placeholder="可选备注信息" />
            <div class="form-actions">
              <Button type="submit" class="full-width">确认栖息</Button>
            </div>
          </form>
        </div>
      </div>

      <!-- 迁徙卡片 -->
      <div class="migration-card-wrapper">
        <div class="card-header-simple">
          <h2>迁徙</h2>
          <p>物品出库或位置变动</p>
        </div>
        <div class="card-body-simple">
          <form class="form" @submit.prevent="handleOutbound">
            <SelectField
              v-model="outbound.productId"
              label="选择物品"
              required
              :options="productOptions"
              placeholder="请选择物品"
              option-label-key="label"
              option-value-key="value"
            />
            <InputField v-model="outbound.quantity" type="number" label="迁徙数量" min="1" required />
            <div class="location-select-row">
              <SelectField
                v-model="outbound.targetLocation"
                label="迁徙至"
                :options="migrationTargetOptions"
                option-label-key="name"
                option-value-key="name"
                placeholder="请选择目的地"
                class="flex-1"
              />
              <button type="button" class="add-btn-small" title="添加新空间" @click="showAddModal = true">+</button>
            </div>
            <TextareaField v-model="outbound.note" label="迁徙说明" rows="3" placeholder="可选备注信息" />
            <div class="form-actions">
              <Button type="submit" class="full-width" :disabled="!outbound.productId">确认迁徙</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加新空间弹窗 -->
  <Modal :open="showAddModal" title="添加新空间" @close="showAddModal = false">
    <div class="add-space-form">
      <div class="form-group">
        <label>空间名称</label>
        <InputField v-model="newSpace.name" placeholder="例如：我的书桌" />
      </div>
      <div class="form-group">
        <label>上传实拍照</label>
        <div class="upload-placeholder">
          <div class="upload-icon">📸</div>
          <p>点击或拖拽照片至此</p>
        </div>
      </div>
      <div class="form-group">
        <label>手写备注</label>
        <TextareaField v-model="newSpace.note" placeholder="写下对这个空间的记忆..." />
      </div>
      <div class="form-actions-modal">
        <Button variant="secondary" @click="showAddModal = false">取消</Button>
        <Button @click="handleAddSpace">确认添加</Button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { useUiStore } from '../stores/ui.store'
import InputField from '../components/ui/Input.vue'
import SelectField from '../components/ui/Select.vue'
import TextareaField from '../components/ui/Textarea.vue'
import Button from '../components/ui/Button.vue'
import Modal from '../components/ui/Modal.vue'

const inventory = useInventoryStore()
const ui = useUiStore()

const showAddModal = ref(false)
const newSpace = reactive({
  name: '',
  note: ''
})

const inbound = reactive({
  name: '',
  quantity: 1,
  storageLocation: '',
  note: ''
})

const outbound = reactive({
  productId: null,
  quantity: 1,
  targetLocation: '出库',
  note: ''
})

const locationOptions = computed(() => inventory.locationOptions)
const migrationTargetOptions = computed(() => [
  { name: '出库' },
  ...inventory.locationOptions
])

const productOptions = computed(() => 
  inventory.products.map(p => ({
    label: `${p.name} (${p.storageLocation || '无位置'}) - 余 ${p.quantity}`,
    value: p.id
  }))
)

const handleAddSpace = () => {
  console.log('添加新空间:', newSpace)
  showAddModal.value = false
  ui.showFlash('空间已添加（演示）', 'success')
  Object.assign(newSpace, { name: '', note: '' })
}

const handleInbound = async () => {
  try {
    const res = await inventory.inboundProduct(inbound)
    if (res.success) {
      ui.showFlash(res.message, 'success')
      Object.assign(inbound, { name: '', quantity: 1, storageLocation: '', note: '' })
    } else {
      ui.showFlash(res.message, 'error')
    }
  } catch (err) {
    ui.showFlash('栖息失败', 'error')
  }
}

const handleOutbound = async () => {
  try {
    const res = await inventory.outboundProduct(outbound)
    if (res.success) {
      ui.showFlash(res.message, 'success')
      Object.assign(outbound, { productId: null, quantity: 1, targetLocation: '出库', note: '' })
    } else {
      ui.showFlash(res.message, 'error')
    }
  } catch (err) {
    ui.showFlash('迁徙失败', 'error')
  }
}
</script>

<style scoped>
.migration-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.migration-card-wrapper {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header-simple {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #fcfdfe;
}

.card-header-simple h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.card-header-simple p {
  font-size: 14px;
  color: #64748b;
}

.card-body-simple {
  padding: 24px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.location-select-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.flex-1 {
  flex: 1;
}

.add-btn-small {
  width: 42px;
  height: 42px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 2px;
}

.add-btn-small:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.add-space-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #475569;
  font-size: 0.95rem;
}

.upload-placeholder {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-placeholder:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.upload-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.form-actions-modal {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.full-width {
  width: 100%;
}

@media (max-width: 800px) {
  .migration-grid {
    grid-template-columns: 1fr;
  }
}
</style>
