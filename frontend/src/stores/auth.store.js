import { defineStore } from 'pinia'
import * as api from '../services/api'

if (typeof window !== 'undefined') {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false
  }),
  actions: {
    async login(username, password) {
      try {
        const response = await api.login(username, password)
        this.user = response.user
        this.isAuthenticated = true
        return { success: true }
      } catch (error) {
        return { success: false, message: error.message || '登录失败' }
      }
    },
    logout() {
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }
})
