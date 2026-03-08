import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export default {
  connectGame: () => api.post('/game/connect'),
  getScreenshot: () => api.post('/game/screenshot'),
  
  startAutomation: (mode) => api.post('/automation/start', { mode }),
  stopAutomation: () => api.post('/automation/stop'),
  pauseAutomation: () => api.post('/automation/pause'),
  resumeAutomation: () => api.post('/automation/resume'),
  getAutomationStatus: () => api.get('/automation/status'),
  
  analyzeScene: () => api.post('/ai/analyze'),
  executeSolution: () => api.post('/ai/execute'),
  
  getSettings: () => api.get('/settings'),
  saveSettings: (data) => api.post('/settings', data)
}
