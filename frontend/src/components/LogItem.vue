<template>
  <div class="log-item" :class="log.level">
    <span class="time">[{{ log.time }}]</span>
    <span class="source">[{{ log.source }}]</span>
    <span class="message">{{ log.message }}</span>
  </div>
</template>

<script setup>
defineProps({
  log: { type: Object, required: true }
})
</script>

<style lang="scss" scoped>
.log-item {
  padding: 4px 8px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 10px;
  &:hover { background-color: rgba(255, 255, 255, 0.05); }
  .time { color: #606266; min-width: 85px; }
  .source { color: #b1b3b8; min-width: 60px; }
  .message { flex: 1; word-break: break-all; }
  &.info .message { color: #00d9ff; }
  &.success .message { color: #67c23a; }
  &.warning .message { color: #e6a23c; }
  &.error .message { color: #f56c6c; font-weight: bold; }
}
</style>
