<template>
  <el-card class="settings-card" shadow="never">
    <template #header>
      <div class="card-header"><el-icon><Setting /></el-icon> 系统配置</div>
    </template>
    <el-form :model="settings" label-width="120px" class="tech-form">
      <el-divider content-position="left">API 接口配置</el-divider>
      <el-form-item label="LLM API Key">
        <el-input v-model="settings.apiKey" placeholder="输入LLM API Key" show-password />
      </el-form-item>
      <el-form-item label="模型选择">
        <el-select v-model="settings.model" placeholder="选择模型">
          <el-option label="qwen-plus" value="qwen-plus" />
          <el-option label="qwen-max" value="qwen-max" />
        </el-select>
      </el-form-item>

      <el-divider content-position="left">游戏配置</el-divider>
      <el-form-item label="游戏进程名">
        <el-input v-model="settings.processName" placeholder="如 WuWa.exe" />
      </el-form-item>
      <el-form-item label="窗口标题">
        <el-input v-model="settings.windowTitle" placeholder="如 鸣潮" />
      </el-form-item>

      <el-divider content-position="left">自动化参数</el-divider>
      <el-form-item label="截图间隔(秒)">
        <el-input-number v-model="settings.screenshotInterval" :min="1" :max="10" />
      </el-form-item>
      <el-form-item label="最大重试">
        <el-input-number v-model="settings.maxRetries" :min="1" :max="10" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="saveConfig" :loading="loading" class="glow-btn">保存配置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const settings = ref({
  apiKey: '',
  model: 'qwen-plus',
  processName: 'WuWa.exe',
  windowTitle: '鸣潮',
  screenshotInterval: 2,
  maxRetries: 3
})

const saveConfig = async () => {
  loading.value = true
  try {
    await api.saveSettings(settings.value)
    ElMessage.success('配置已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.getSettings()
    if (res.data.settings) {
      settings.value = { ...settings.value, ...res.data.settings }
    }
  } catch (e) {}
})
</script>

<style lang="scss" scoped>
.settings-card {
  background: rgba(22, 33, 62, 0.6);
  border: 1px solid var(--el-border-color);
  max-width: 800px;
  .card-header {
    color: #00d9ff;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .tech-form {
    :deep(.el-divider__text) {
      background-color: transparent;
      color: #00d9ff;
    }
  }
  .glow-btn {
    box-shadow: 0 0 10px rgba(0, 217, 255, 0.4);
    &:hover {
      box-shadow: 0 0 20px rgba(0, 217, 255, 0.8);
    }
  }
}
</style>
