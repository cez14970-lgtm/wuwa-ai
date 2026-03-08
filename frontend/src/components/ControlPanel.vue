<template>
  <div class="control-panel">
    <div class="connection-section">
      <el-button 
        class="cyber-btn"
        :type="store.connectionStatus === 'connected' ? 'success' : 'primary'"
        @click="store.connect"
        :disabled="store.connectionStatus === 'connected'"
      >
        <el-icon class="el-icon--left"><Link /></el-icon>
        {{ store.connectionStatus === 'connected' ? '已连接' : '连接游戏' }}
      </el-button>
    </div>
    <el-divider />
    <div class="execution-section">
      <div class="label">任务模式选择:</div>
      <el-select v-model="selectedMode" placeholder="选择自动化模式" class="w-full mb-3" :disabled="store.automationState === 'running'">
        <el-option label="剧情模式" value="story" />
        <el-option label="战斗模式" value="battle" />
        <el-option label="探索模式" value="explore" />
      </el-select>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          class="start-btn glow" 
          @click="handleStart"
          :disabled="store.connectionStatus !== 'connected' || store.automationState === 'running'"
        >
          <el-icon><VideoPlay /></el-icon> 开始执行
        </el-button>
        <el-button 
          type="danger" 
          class="stop-btn glow" 
          @click="store.stop"
          :disabled="store.automationState === 'idle'"
        >
          <el-icon><VideoPause /></el-icon> 停止
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAutomationStore } from '@/stores/automation'

const store = useAutomationStore()
const selectedMode = ref('story')

const handleStart = () => {
  store.start(selectedMode.value)
}
</script>

<style lang="scss" scoped>
.control-panel {
  .mb-3 { margin-bottom: 15px; }
  .w-full { width: 100%; }
  .label {
    color: #a0a5b5;
    margin-bottom: 8px;
    font-size: 14px;
  }
  .cyber-btn {
    width: 100%;
    background-color: transparent;
    border: 1px solid #00d9ff;
    color: #00d9ff;
    &:hover:not(:disabled) {
      background-color: rgba(0, 217, 255, 0.1);
    }
    &.el-button--success {
      border-color: #67c23a;
      color: #67c23a;
    }
  }
  .action-buttons {
    display: flex;
    gap: 10px;
    .start-btn { flex: 2; }
    .stop-btn { flex: 1; }
    .glow:not(:disabled) {
      box-shadow: 0 0 10px currentcolor;
    }
  }
}
</style>
