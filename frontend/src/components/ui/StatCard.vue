<template>
  <section class="stat-card">
    <div class="stat-card-top">
      <div class="stat-card-icon" :class="tone">
        <slot name="icon" />
      </div>
      <span v-if="label" class="stat-card-label">{{ label }}</span>
    </div>
    <div class="stat-card-value">{{ value }}</div>
    <div v-if="description" class="stat-card-description">{{ description }}</div>
  </section>
</template>

<script setup>
defineProps({
  value: {
    type: [String, Number],
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  tone: {
    type: String,
    default: 'default'
  }
})
</script>
