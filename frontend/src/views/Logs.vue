<template>
  <el-card class="logs-card" shadow="never">
    <template #header>
      <div class="log-header">
        <div class="title"><el-icon><Document /></el-icon> 运行日志</div>
        <el-radio-group v-model="filterLevel" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="info">信息</el-radio-button>
          <el-radio-button label="warning">警告</el-radio-button>
          <el-radio-button label="error">错误</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <div class="log-container">
      <LogItem v-for="log in filteredLogs" :key="log.id" :log="log" />
      <el-empty v-if="filteredLogs.length === 0" description="暂无日志信息" :image-size="60" />
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAutomationStore } from '@/stores/automation'
import LogItem from '@/components/LogItem.vue'

const store = useAutomationStore()
const filterLevel = ref('all')

const filteredLogs = computed(() => {
  if (filterLevel.value === 'all') return store.logs
  return store.logs.filter(log => log.level === filterLevel.value)
})
</script>

<style lang="scss" scoped>
.logs-card {
  background: rgba(22, 33, 62, 0.6);
  border: 1px solid var(--el-border-color);
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  :deep(.el-card__body) {
    flex: 1;
    overflow: hidden;
    padding: 10px;
  }
  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .title {
      color: #00d9ff;
      font-weight: bold;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  .log-container {
    height: 100%;
    overflow-y: auto;
    font-family: 'Courier New', Courier, monospace;
    &::-webkit-scrollbar { width: 6px; }
    &::-webkit-scrollbar-thumb { background: #0f3460; border-radius: 3px; }
  }
}
</style>
