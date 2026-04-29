<template>
  <div class="login-container">
    <AuroraBackground class="aurora-fixed" />
    
    <div class="login-card-wrapper">
      <GlassCard class="login-card">
        <div class="login-header">
          <div class="logo">🏘️</div>
          <h1>栖物志</h1>
          <p>给每件物品一个清晰、可追踪的栖息地</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <Input 
              v-model="username" 
              placeholder="输入你的账号" 
              required
              class="custom-input"
            />
          </div>
          
          <div class="form-group">
            <label>密码</label>
            <Input 
              v-model="password" 
              type="password" 
              placeholder="输入你的密码" 
              required 
              class="custom-input"
            />
          </div>

          <div class="form-error" v-if="error">{{ error }}</div>

          <Button 
            type="submit" 
            class="login-btn" 
            :loading="loading"
          >
            开启探索
          </Button>

          <div class="login-footer">
            <span>大学生轻量化物品管理系统</span>
          </div>
        </form>
      </GlassCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.store'
import { useUiStore } from '../stores/ui.store'
import AuroraBackground from '../components/layout/AuroraBackground.vue'
import GlassCard from '../components/layout/GlassCard.vue'
import Input from '../components/ui/Input.vue'
import Button from '../components/ui/Button.vue'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

// 如果已经登录，直接跳转首页
onMounted(() => {
  if (auth.isAuthenticated) {
    router.push('/')
  }
})

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const result = await auth.login(username.value, password.value)
    if (result.success) {
      if (ui.success) {
        ui.success('欢迎回来，' + auth.user.username)
      }
      await router.push('/')
    } else {
      error.value = result.message
      if (ui.error) {
        ui.error(result.message)
      }
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = '服务器连接失败'
    if (ui.error) {
      ui.error('登录出错，请稍后再试')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f172a;
}

.aurora-fixed {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.login-card-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 20px;
  z-index: 10;
}

.login-card {
  padding: 40px;
  border-radius: 24px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 12px;
}

.login-header h1 {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.login-header p {
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #e2e8f0;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 4px;
}

.form-error {
  color: #f87171;
  font-size: 0.85rem;
  text-align: center;
  background: rgba(248, 113, 113, 0.1);
  padding: 8px;
  border-radius: 8px;
}

.login-btn {
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 10px;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  color: #64748b;
  font-size: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 24px;
}
</style>
