<template>
  <header class="page-header">
    <div class="page-header-left">
      <div class="page-header-icon">
        <slot name="icon" />
      </div>
      <div>
        <h1>{{ title }}</h1>
        <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
      </div>
    </div>

    <div v-if="$slots.actions" class="page-header-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>
