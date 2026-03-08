import { defineStore } from 'pinia'
import api from '@/api'
import { ElMessage } from 'element-plus'

export const useAutomationStore = defineStore('automation', {
  state: () => ({
    connectionStatus: 'disconnected',
    automationState: 'idle',
    logs: [],
    pollingInterval: null,
    currentMode: 'story'
  }),
  actions: {
    async connect() {
      try {
        const res = await api.connectGame()
        if (res.data.success) {
          this.connectionStatus = 'connected'
          ElMessage.success('成功连接到游戏！')
          this.addLog('系统', '已成功连接游戏', 'success')
        } else {
          ElMessage.warning(res.data.message || '连接失败')
          this.addLog('系统', res.data.message || '连接失败', 'warning')
        }
      } catch (error) {
        ElMessage.error('连接失败，请检查游戏是否运行')
        this.addLog('系统', '连接游戏失败: ' + error.message, 'error')
      }
    },
    async start(mode) {
      try {
        const res = await api.startAutomation(mode)
        if (res.data.success) {
          this.automationState = 'running'
          this.currentMode = mode
          ElMessage.success(`开始执行: ${mode}`)
          this.addLog('执行', `任务模式 [${mode}] 已启动`, 'info')
        } else {
          ElMessage.warning(res.data.message || '启动失败')
        }
      } catch (error) {
        ElMessage.error('启动失败')
        this.addLog('系统', '启动任务失败', 'error')
      }
    },
    async stop() {
      try {
        const res = await api.stopAutomation()
        if (res.data.success) {
          this.automationState = 'idle'
          ElMessage.warning('任务已停止')
          this.addLog('执行', '用户手动停止了任务', 'warning')
        }
      } catch (error) {
        ElMessage.error('停止失败')
      }
    },
    async fetchStatus() {
      try {
        const res = await api.getAutomationStatus()
        if (res.data.success) {
          const status = res.data.status
          // 先检查连接状态，再检查运行状态
          this.connectionStatus = status.connected ? 'connected' : 'disconnected'
          this.automationState = status.running ? 'running' : 'idle'
        }
      } catch (error) {
        // 忽略轮询错误
      }
    },
    startPollingStatus() {
      if (!this.pollingInterval) {
        this.pollingInterval = setInterval(() => {
          this.fetchStatus()
        }, 3000)
      }
    },
    stopPollingStatus() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },
    addLog(source, message, level = 'info') {
      const now = new Date()
      const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
      this.logs.unshift({ id: Date.now(), time: timeString, source, message, level })
      if (this.logs.length > 200) this.logs.pop()
    }
  }
})
