import { ref } from 'vue'
import { defineStore } from 'pinia'

let flashId = 0
const timers = new Map()

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const flashMessages = ref([])

  function openSidebar() {
    sidebarOpen.value = true
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function removeFlash(id) {
    flashMessages.value = flashMessages.value.filter((message) => message.id !== id)

    const timer = timers.get(id)
    if (timer) {
      clearTimeout(timer)
      timers.delete(id)
    }
  }

  function pushFlash(type, text, timeout = 4200) {
    const id = ++flashId
    flashMessages.value.push({ id, type, text })

    const timer = setTimeout(() => {
      removeFlash(id)
    }, timeout)

    timers.set(id, timer)
    return id
  }

  function success(text) {
    return pushFlash('success', text)
  }

  function error(text) {
    return pushFlash('error', text)
  }

  function clearFlash() {
    flashMessages.value.forEach((message) => removeFlash(message.id))
    flashMessages.value = []
  }

  return {
    sidebarOpen,
    flashMessages,
    openSidebar,
    closeSidebar,
    toggleSidebar,
    pushFlash,
    success,
    error,
    removeFlash,
    clearFlash
  }
})
