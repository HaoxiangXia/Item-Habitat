<template>
  <div class="login-wrapper">
    <AuroraBackground class="aurora-fixed" />
    
    <div class="login-content">
      <GlassCard class="login-card">
        <div class="login-header">
          <h1 class="brand-title">栖物志</h1>
          <p class="brand-subtitle">给每件物品一个清晰、可追踪的栖息地</p>
        </div>

        <form class="login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label>用户名</label>
            <Input 
              v-model="username" 
              placeholder="输入你的账号" 
              required
              class="glass-input"
            />
          </div>
          
          <div class="form-group">
            <label>密码</label>
            <Input 
              v-model="password" 
              type="password" 
              placeholder="输入你的密码" 
              required 
              class="glass-input"
            />
          </div>

          <transition name="shake">
            <div class="form-error" v-if="error">{{ error }}</div>
          </transition>

          <Button 
            type="submit" 
            class="login-btn-fancy" 
            :loading="loading"
          >
            开启探索
          </Button>

          <div class="login-footer">
            <span class="footer-tag">ITEM HABITAT</span>
            <span class="footer-desc">大学生轻量化物品管理系统</span>
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
.aurora-fixed {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 1;
}

.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-content {
  width: 100%;
  max-width: 440px;
  padding: 24px;
  z-index: 10;
  animation: slide-up 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-card {
  padding: 48px;
  border-radius: 32px;
  backdrop-filter: blur(20px) saturate(180%);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 12px;
  letter-spacing: 0.1em;
  background: linear-gradient(135deg, #fff 0%, #0075de 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.6;
  font-weight: 300;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding-left: 12px;
}

.glass-input :deep(input) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 14px !important;
  color: white !important;
  padding: 12px 16px !important;
  transition: all 0.3s ease;
}

.glass-input :deep(input:focus) {
  border-color: rgba(255, 255, 255, 0.3) !important;
  background: rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.05);
}

.form-error {
  color: #fca5a5;
  font-size: 0.85rem;
  text-align: center;
  background: rgba(239, 68, 68, 0.1);
  padding: 10px;
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.login-btn-fancy {
  height: 52px;
  width: 100%;
  max-width: 240px;
  align-self: center;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 14px;
  background: white;
  color: var(--color-brand, #0075de);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  margin-top: 8px;
}

.login-btn-fancy:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(255, 255, 255, 0.2);
  filter: brightness(1.1);
}

.login-footer {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  opacity: 0.6;
}

.footer-tag {
  font-size: 0.65rem;
  font-weight: 800;
  color: white;
  letter-spacing: 0.2em;
}

.footer-desc {
  color: #94a3b8;
  font-size: 0.75rem;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shake-enter-active {
  animation: shake 0.4s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
