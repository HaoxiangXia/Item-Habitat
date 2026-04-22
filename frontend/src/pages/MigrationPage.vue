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
            <SelectField
              v-model="inbound.storageLocation"
              label="存储空间"
              :options="locationOptions"
              option-label-key="name"
              option-value-key="name"
              placeholder="请选择存储空间"
            />
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
            <TextareaField v-model="outbound.note" label="迁徙说明" rows="3" placeholder="可选备注信息" />
            <div class="form-actions">
              <Button type="submit" class="full-width" :disabled="!outbound.productId">确认迁徙</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useInventoryStore } from '../stores/inventory.store'
import { useUiStore } from '../stores/ui.store'
import InputField from '../components/ui/Input.vue'
import SelectField from '../components/ui/Select.vue'
import TextareaField from '../components/ui/Textarea.vue'
import Button from '../components/ui/Button.vue'

const inventory = useInventoryStore()
const ui = useUiStore()

const inbound = reactive({
  name: '',
  quantity: 1,
  storageLocation: '',
  note: ''
})

const outbound = reactive({
  productId: null,
  quantity: 1,
  note: ''
})

const locationOptions = computed(() => inventory.locationOptions)
const productOptions = computed(() => 
  inventory.products.map(p => ({
    label: `${p.name} (${p.storageLocation || '无位置'}) - 余 ${p.quantity}`,
    value: p.id
  }))
)

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
      Object.assign(outbound, { productId: null, quantity: 1, note: '' })
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
  color: var(--color-text);
  margin-bottom: 4px;
}

.card-header-simple p {
  font-size: 14px;
  color: var(--color-text-muted);
}

.card-body-simple {
  padding: 24px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.full-width {
  width: 100%;
}

@media (max-width: 800px) {
  .migration-grid {
    grid-template-columns: 1fr;
  }
}
