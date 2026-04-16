<template>
  <div class="status-indicator">
    <span class="status-dot" :class="status"></span>
    <span class="status-text" :class="status">{{ label }}</span>
  </div>
</template>

<script setup>
defineProps({
  status: {
    type: String,
    default: 'normal',
    validator: (value) => ['normal', 'alarm', 'offline'].includes(value)
  },
  label: {
    type: String,
    required: true
  }
})
</script>
