<template>
  <div class="aurora-bg">
    <!-- 替换为柔和的蓝石块/烟雾感的环境点缀 -->
    <div class="aurora-band aurora-band-1"></div>
    <div class="aurora-band aurora-band-2"></div>
    <div class="aurora-band aurora-band-3"></div>
  </div>
</template>

<style scoped>
.aurora-band-1 {
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, #cbd5e0 0%, transparent 70%);
  top: -10vw;
  right: -5vw;
  animation: float-slow 30s infinite alternate ease-in-out;
}

.aurora-band-2 {
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
</style>
