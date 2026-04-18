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

<style scoped>
.glass-card {
  /* 复刻规范中的 .glass 类 */
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow), var(--glass-inner-glow);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(30, 64, 175, 0.12), var(--glass-inner-glow);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--color-text);
}

.glass-card.compact {
  padding: 16px;
}
</style>
