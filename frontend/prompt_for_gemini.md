# 🎨 WuwaAI 前端设计 Prompt

你是一个专业的Vue3前端开发者。请基于以下项目需求，设计并实现一个**鸣潮游戏自动化助手**的Web控制台界面。

## 项目背景

WuwaAI 是一个基于AI的鸣潮游戏自动化工具，后端使用FastAPI，前端需要创建一个现代化的Web控制台来：
- 实时显示游戏画面
- 控制自动化流程
- 查看日志和状态

## 技术栈要求

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI组件库**: 不限制，可以使用 Element Plus / Naive UI / TailwindCSS
- **状态管理**: Pinia
- **样式**: SCSS 或 TailwindCSS

## 页面结构

### 1. 首页/仪表盘 (Dashboard)
- 顶部: 项目Logo + 连接状态指示
- 左侧: 游戏画面实时预览 (16:9比例)
- 右侧: 控制面板
  - 连接/断开游戏按钮
  - 开始/停止自动化按钮
  - 模式选择 (剧情模式/战斗模式/探索模式)
- 底部: 状态栏 (当前场景/AI状态/运行时间)

### 2. 实时日志页面
- 可滚动的日志窗口
- 日志级别过滤 (info/warning/error)
- 时间戳显示
- 一键清空按钮

### 3. 设置页面
- API配置 (LLM API Key, 模型选择)
- 游戏窗口配置 (分辨率, 进程名)
- 自动化选项 (是否自动搜索, 重试次数等)
- 导出/导入配置

## UI设计要求

### 配色方案
- 主色调: 科技感深色系 (#1a1a2e, #16213e)
- 强调色: 青色/蓝色 (#00d9ff, #0f3460)
- 状态色: 绿色(运行中) / 红色(错误) / 黄色(警告)

### 布局
- 侧边栏导航
- 响应式设计 (支持平板)
- 游戏画面区域带边框和阴影

### 交互
- 按钮hover效果
- 加载状态动画
- Toast通知提示

## 页面路由

```
/           -> Dashboard (首页)
/logs       -> 日志页面
/settings   -> 设置页面
```

## 组件设计

### 1. GameScreen.vue
- 显示游戏截图
- 支持点击坐标显示
- 截图刷新按钮

### 2. ControlPanel.vue
- 大型圆形开始/停止按钮
- 模式切换开关
- 状态指示灯

### 3. LogViewer.vue
- 虚拟列表 (大量日志不卡顿)
- 颜色编码 (不同级别不同颜色)
- 自动滚动开关

### 4. SettingsForm.vue
- 分组配置项
- 输入验证
- 保存确认

## API对接

前端需要调用以下后端接口 (后端运行在 http://localhost:8000):

```javascript
// 游戏控制
POST /game/connect      // 连接游戏
POST /game/screenshot   // 获取截图
POST /game/click        // 点击 (x, y)
POST /game/input        // 输入文字

// AI分析
POST /ai/analyze        // 分析场景
POST /ai/execute        // 执行解决方案

// 控制
POST /start             // 开始自动化
POST /stop              // 停止自动化
GET  /status            // 获取状态

// 设置
GET  /settings          // 获取设置
POST /settings          // 更新设置
```

## 输出要求

1. 创建完整的Vue3项目结构
2. 实现上述所有页面和组件
3. 添加必要的路由和状态管理
4. 样式要美观现代，有科技感
5. 代码要模块化，易于维护

请生成完整的代码！
