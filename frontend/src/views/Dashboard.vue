<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="tech-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><VideoCamera /></el-icon> 实时画面监视
            </div>
          </template>
          <GameScreen />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="tech-card" shadow="never">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon> 控制面板
            </div>
          </template>
          <ControlPanel />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import GameScreen from '@/components/GameScreen.vue'
import ControlPanel from '@/components/ControlPanel.vue'
</script>

<style lang="scss" scoped>
.tech-card {
  background: rgba(22, 33, 62, 0.6);
  border: 1px solid var(--el-border-color);
  box-shadow: inset 0 0 20px rgba(0, 217, 255, 0.05);
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #00d9ff;
    font-weight: bold;
    letter-spacing: 1px;
  }
}
</style>
