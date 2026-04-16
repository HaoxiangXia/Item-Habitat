<template>
  <section class="glass-card" :class="{ compact }">
    <div v-if="$slots.header || title" class="card-header">
      <slot name="header">
        <span class="card-title">{{ title }}</span>
      </slot>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  compact: {
    type: Boolean,
    default: false
  }
})
</script>
