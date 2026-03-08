<template>
  <el-container class="app-wrapper">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon :size="24" color="#00d9ff"><Cpu /></el-icon>
        <span>WuwaAI</span>
      </div>
      <el-menu
        :default-active="route.path"
        router
        class="el-menu-vertical"
        background-color="transparent"
        text-color="#a0a5b5"
        active-text-color="#00d9ff"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>实时日志</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <span class="status-indicator" :class="store.connectionStatus"></span>
          状态: {{ store.connectionStatus === 'connected' ? '已连接' : '未连接' }}
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useAutomationStore } from '@/stores/automation'
import { onMounted, onUnmounted } from 'vue'

const route = useRoute()
const store = useAutomationStore()

onMounted(() => {
  store.startPollingStatus()
})

onUnmounted(() => {
  store.stopPollingStatus()
})
</script>

<style lang="scss">
:root {
  --el-color-primary: #00d9ff;
  --el-bg-color: #1a1a2e;
  --el-bg-color-overlay: #16213e;
  --el-text-color-primary: #e0e0e0;
  --el-border-color: #0f3460;
  --el-menu-hover-bg-color: rgba(0, 217, 255, 0.1);
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background-color: var(--el-bg-color);
  color: var(--el-text-color-primary);
}

.app-wrapper {
  height: 100vh;
}

.sidebar {
  background-color: #16213e;
  border-right: 1px solid var(--el-border-color);
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 20px;
    font-weight: bold;
    color: #00d9ff;
    border-bottom: 1px solid var(--el-border-color);
    text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
  }
  .el-menu-vertical {
    border-right: none;
  }
}

.header {
  background-color: rgba(22, 33, 62, 0.8);
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  backdrop-filter: blur(10px);
  .header-content {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #a0a5b5;
  }
  .status-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #f56c6c;
    box-shadow: 0 0 8px #f56c6c;
    &.connected {
      background-color: #67c23a;
      box-shadow: 0 0 8px #67c23a;
    }
  }
}

.main-content {
  padding: 20px;
  background: radial-gradient(circle at top left, #1a1a2e, #0f172a);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
