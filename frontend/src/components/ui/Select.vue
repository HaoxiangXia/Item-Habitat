<template>
  <div class="form-group">
    <label v-if="label">{{ label }} <span v-if="required" class="required">*</span></label>
    <select :value="modelValue" :disabled="disabled" @change="$emit('update:modelValue', $event.target.value)">
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="getOptionValue(option)"
        :value="getOptionValue(option)"
      >
        {{ getOptionLabel(option) }}
      </option>
    </select>
    <small v-if="hint">{{ hint }}</small>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  optionLabelKey: {
    type: String,
    default: 'label'
  },
  optionValueKey: {
    type: String,
    default: 'value'
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])

function getOptionLabel(option) {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionLabelKey]
  }

  return option
}

function getOptionValue(option) {
  if (typeof option === 'object' && option !== null) {
    return option[props.optionValueKey]
  }

  return option
}
</script>
