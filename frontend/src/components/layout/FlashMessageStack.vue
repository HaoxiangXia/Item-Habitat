<template>
  <div v-if="messages.length" class="flash-messages">
    <TransitionGroup name="flash-list" tag="div">
      <div
        v-for="message in messages"
        :key="message.id"
        class="flash-message"
        :class="`flash-${message.type}`"
      >
        <span>{{ message.text }}</span>
        <button type="button" class="flash-close" @click="store.removeFlash(message.id)">
          <XIcon />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUiStore } from '../../stores/ui.store'
import { XIcon } from '../icons'

const store = useUiStore()
const messages = computed(() => store.flashMessages)
</script>
