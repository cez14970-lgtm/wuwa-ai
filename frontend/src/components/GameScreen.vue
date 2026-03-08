<template>
  <div class="screen-container">
    <div v-if="imgSrc" class="video-feed">
      <img :src="imgSrc" alt="Game Screen" />
      <div class="overlay-scanline"></div>
    </div>
    <div v-else class="placeholder">
      <el-icon class="pulse-icon" :size="48"><Monitor /></el-icon>
      <p>等待连接游戏进程...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAutomationStore } from '@/stores/automation'
import api from '@/api'

const store = useAutomationStore()
const imgSrc = ref(null)
let streamInterval = null

const fetchFrame = async () => {
  if (store.connectionStatus !== 'connected') {
    imgSrc.value = null
    return
  }
  try {
    const res = await api.getScreenshot()
    if (res.data.success && res.data.image) {
      imgSrc.value = 'data:image/jpeg;base64,' + res.data.image
    }
  } catch (error) {
    console.warn("无法获取画面")
  }
}

onMounted(() => {
  streamInterval = setInterval(fetchFrame, 500)
})

onUnmounted(() => {
  clearInterval(streamInterval)
})
</script>

<style lang="scss" scoped>
.screen-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #0b0f19;
  border: 1px solid #0f3460;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  .placeholder {
    color: #4a5568;
    text-align: center;
    .pulse-icon {
      animation: pulse 2s infinite;
      margin-bottom: 10px;
    }
  }
  .video-feed {
    width: 100%;
    height: 100%;
    position: relative;
    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .overlay-scanline {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
      background-size: 100% 4px, 6px 100%;
      pointer-events: none;
    }
  }
}
@keyframes pulse {
  0% { opacity: 0.5; text-shadow: 0 0 0 #00d9ff; }
  50% { opacity: 1; text-shadow: 0 0 10px #00d9ff; color: #00d9ff;}
  100% { opacity: 0.5; text-shadow: 0 0 0 #00d9ff; }
}
</style>
