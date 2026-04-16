<template>
  <GlassCard title="入库信息">
    <form class="form" @submit.prevent="handleSubmit">
      <InputField
        v-model="form.name"
        label="货物名称"
        required
        placeholder="请输入货物名称"
      />

      <InputField
        v-model="form.quantity"
        type="number"
        label="数量"
        min="1"
        required
        hint="不填默认为 1"
      />

      <div class="form-group">
        <label>存储位置</label>
        <div class="select-with-add">
          <SelectField
            v-model="form.storageLocation"
            :options="locationOptions"
            option-label-key="name"
            option-value-key="name"
            placeholder="请选择存储位置"
          />
          <Button type="button" variant="secondary" class="add-location-button" @click="showLocationDialog = true">
            <PlusIcon />
            添加
          </Button>
        </div>
      </div>

      <TextareaField
        v-model="form.note"
        label="备注"
        rows="3"
        placeholder="可选备注信息"
      />

      <div class="form-actions">
        <Button type="submit">确认入库</Button>
        <Button variant="secondary" type="button" @click="resetForm">重置</Button>
      </div>
    </form>
  </GlassCard>

  <Modal :open="showLocationDialog" title="添加存储位置" @close="showLocationDialog = false">
    <div class="form-group">
      <label>位置名称</label>
      <InputField
        v-model="newLocationName"
        placeholder="例如：A区-01-03"
        @keyup.enter="saveLocation"
      />
    </div>

    <div class="form-actions">
      <Button type="button" @click="saveLocation">保存</Button>
      <Button variant="secondary" type="button" @click="showLocationDialog = false">取消</Button>
    </div>
  </Modal>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useInventoryStore } from '../../stores/inventory.store'
import { useUiStore } from '../../stores/ui.store'
import GlassCard from '../layout/GlassCard.vue'
import Button from '../ui/Button.vue'
import InputField from '../ui/Input.vue'
import Modal from '../ui/Modal.vue'
import SelectField from '../ui/Select.vue'
import TextareaField from '../ui/Textarea.vue'
import { PlusIcon } from '../icons'

const inventory = useInventoryStore()
const ui = useUiStore()

const form = reactive({
  name: '',
  quantity: 1,
  storageLocation: '',
  note: ''
})

const showLocationDialog = ref(false)
const newLocationName = ref('')

const locationOptions = computed(() => inventory.locationOptions)

watch(
  [locationOptions, () => inventory.lastInboundLocation],
  () => {
    const availableValues = new Set(locationOptions.value.map((location) => location.name))
    if (!form.storageLocation || !availableValues.has(form.storageLocation)) {
      form.storageLocation = inventory.lastInboundLocation || locationOptions.value[0]?.name || ''
    }
  },
  { immediate: true }
)

function resetForm() {
  form.name = ''
  form.quantity = 1
  form.storageLocation = inventory.lastInboundLocation || locationOptions.value[0]?.name || ''
  form.note = ''
}

async function handleSubmit() {
  const result = await inventory.inboundProduct(form)

  if (result.success) {
    ui.success(result.message)
    resetForm()
    return
  }

  ui.error(result.message)
}

async function saveLocation() {
  const result = await inventory.addStorageLocation(newLocationName.value)

  if (!result.success) {
    ui.error(result.message)
    return
  }

  form.storageLocation = result.location
  newLocationName.value = ''
  showLocationDialog.value = false
  ui.success(result.message)
}

resetForm()
</script>
