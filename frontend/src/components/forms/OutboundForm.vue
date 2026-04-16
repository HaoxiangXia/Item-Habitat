<template>
  <GlassCard title="出库信息">
    <form class="form" @submit.prevent="handleSubmit">
      <SelectField
        v-model="form.productId"
        label="选择货物"
        required
        :options="productOptions"
        placeholder="请选择货物"
        option-label-key="label"
        option-value-key="value"
      />

      <div v-if="selectedProduct" class="product-info">
        <div class="info-card">
          <div class="info-row">
            <span class="info-label">货物名称</span>
            <span class="info-value">{{ selectedProduct.name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">当前库存</span>
            <span class="info-value">{{ selectedProduct.quantity }} 件</span>
          </div>
          <div class="info-row">
            <span class="info-label">存储位置</span>
            <span class="info-value">{{ selectedProduct.storageLocation || '-' }}</span>
          </div>
        </div>
      </div>

      <InputField
        v-model="form.quantity"
        type="number"
        label="出库数量"
        min="1"
        :max="selectedProduct?.quantity || 1"
        required
        :hint="selectedProduct ? `当前库存：${selectedProduct.quantity} 件` : '请选择货物后填写数量'"
      />

      <TextareaField v-model="form.note" label="备注" rows="3" placeholder="可选备注信息" />

      <div class="form-actions">
        <Button type="submit" :disabled="!selectedProduct">确认出库</Button>
        <Button variant="secondary" type="button" @click="resetForm">重置</Button>
      </div>
    </form>
  </GlassCard>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { useInventoryStore } from '../../stores/inventory.store'
import { useUiStore } from '../../stores/ui.store'
import GlassCard from '../layout/GlassCard.vue'
import Button from '../ui/Button.vue'
import InputField from '../ui/Input.vue'
import SelectField from '../ui/Select.vue'
import TextareaField from '../ui/Textarea.vue'

const inventory = useInventoryStore()
const ui = useUiStore()

const form = reactive({
  productId: '',
  quantity: 1,
  note: ''
})

const productOptions = computed(() =>
  inventory.productOptions.map((product) => ({
    value: String(product.id),
    label: `${product.name} - 库存 ${product.quantity} 件`
  }))
)

const selectedProduct = computed(() => inventory.getProductById(form.productId))

watch(selectedProduct, (product) => {
  if (product && Number(form.quantity) > product.quantity) {
    form.quantity = product.quantity > 0 ? product.quantity : 1
  }
})

function resetForm() {
  form.productId = ''
  form.quantity = 1
  form.note = ''
}

async function handleSubmit() {
  const result = await inventory.outboundProduct({
    productId: form.productId,
    quantity: form.quantity,
    note: form.note
  })

  if (result.success) {
    ui.success(result.message)
    resetForm()
    return
  }

  ui.error(result.message)
}
</script>
