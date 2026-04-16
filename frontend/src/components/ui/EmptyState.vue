<template>
  <div class="empty-state">
    <div v-if="$slots.icon" class="empty-state-icon">
      <slot name="icon" />
    </div>
    <p class="empty-state-title">{{ title }}</p>
    <p v-if="description" class="empty-state-description">{{ description }}</p>
    <div v-if="$slots.action" class="empty-state-action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>
