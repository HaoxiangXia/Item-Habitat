<template>
  <div class="aurora-container">
    <div class="aurora-blob blob-1"></div>
    <div class="aurora-blob blob-2"></div>
    <div class="aurora-blob blob-3"></div>
    <div class="aurora-blob blob-4"></div>
    <div class="aurora-blob blob-5"></div>
  </div>
</template>

<script setup>
/**
 * Slate-Blue Diffuse Glass (石板蓝弥散玻璃) 核心动态背景组件
 * 复刻视觉规范：
 * 4-5 个巨大的圆形 div，通过 radial-gradient 渐变
 * 颜色在 rgba(147, 197, 253, 0.4) 到 rgba(219, 234, 254, 0.5) 演变
 * filter: blur(120px) 营造弥散光感
 */
</script>

<style scoped>
.aurora-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -10;
  overflow: hidden;
  background-color: #e2e8f0; /* 背景底色：中深浅灰 */
}

.aurora-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.5;
  will-change: transform;
}

/* 巨大的圆形渐变 div */
.blob-1 {
  width: 900px;
  height: 900px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.4) 0%, transparent 70%);
  top: -20%;
  left: -10%;
  animation: float 45s infinite alternate ease-in-out;
}

.blob-2 {
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(219, 234, 254, 0.5) 0%, transparent 70%);
  bottom: -15%;
  right: -5%;
  animation: float 50s infinite alternate-reverse ease-in-out;
}

.blob-3 {
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.4) 0%, transparent 70%);
  top: 15%;
  right: 10%;
  animation: float 40s infinite alternate ease-in-out;
  animation-delay: -10s;
}

/* 补充更多弥散层级 */
.blob-4 {
  width: 650px;
  height: 650px;
  background: radial-gradient(circle, rgba(219, 234, 254, 0.5) 0%, transparent 70%);
  bottom: 10%;
  left: 5%;
  animation: float 55s infinite alternate-reverse ease-in-out;
  animation-delay: -15s;
}

.blob-5 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.4) 0%, transparent 70%);
  top: 35%;
  left: 35%;
  animation: float 60s infinite alternate ease-in-out;
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg) scale(1);
  }
  50% {
    transform: translate(8%, 15%) rotate(10deg) scale(1.1);
  }
  100% {
    transform: translate(-5%, 8%) rotate(-5deg) scale(0.95);
  }
}
</style>

  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, #a0aec0 0%, transparent 60%);
  bottom: -15vw;
  left: -10vw;
  opacity: 0.3;
  animation: float-slow 40s infinite alternate-reverse ease-in-out;
}

.aurora-band-3 {
  width: 30vw;
  height: 30vw;
  background: radial-gradient(circle, #edf2f7 0%, transparent 80%);
  top: 30vh;
  left: 20vw;
  opacity: 0.5;
}

@keyframes float-slow {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(5%, 5%) scale(1.1); }
}
