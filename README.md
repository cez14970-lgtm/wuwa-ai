# 🤖 WuwaAI - 鸣潮智能自动化助手

基于 AI 的鸣潮游戏自动化工具，能够智能分析游戏场景、自动搜索攻略、自动执行操作，真正实现"托管"过剧情。

## ✨ 特性

- 🎯 **AI 视觉理解** - VLM 模型理解游戏画面内容
- 🧠 **智能决策** - LLM 分析场景并制定解决方案
- 🔍 **联网搜索** - 自动搜索攻略，解决卡关问题
- 💾 **记忆模块** - 记住失败的方案，避免重复尝试
- 🔄 **多种模式** - 剧情模式 / 战斗模式 / 探索模式

## 📊 对比传统自动化

| 功能 | ok-ww (传统) | WuwaAI (AI增强) |
|------|-------------|-----------------|
| 图像识别 | ✅ | ✅ |
| 理解画面含义 | ❌ | ✅ |
| 联网搜答案 | ❌ | ✅ |
| 复杂机关解谜 | ❌ | ✅ |
| 自动过剧情 | 部分 | ✅ |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────┐
│              Web 控制台                  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│              FastAPI 后端                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ 场景识别 │ │ 问题分析 │ │ 步骤规划 │   │
│  │ (VLM)   │ │ (LLM)   │ │ (LLM)   │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            ok-script 引擎               │
│  截图 / 点击 / 输入 / 按键                │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- Windows 10/11
- 阿里云百炼 API Key（用于 LLM）

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/cez14970-lgtm/wuwa-ai.git
cd wuwa-ai

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend\requirements.txt

# 配置环境变量
copy backend\.env.example backend\.env
# 编辑 .env 填入 API Key
```

### 3. 配置 .env

```env
# 阿里百炼 API (必需)
DASHSCOPE_API_KEY=your_api_key
DASHSCOPE_MODEL=qwen-plus

# 游戏配置
GAME_PROCESS_NAME=WuWa.exe
GAME_WINDOW_TITLE=鸣潮
```

获取阿里百炼 API Key: https://bailian.aliyun.com/

### 4. 运行

```bash
# 启动后端
python backend\main.py

# 访问 http://localhost:8000/docs 查看 API 文档
```

## 📱 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/game/connect` | POST | 连接游戏 |
| `/game/screenshot` | POST | 截图 |
| `/game/click` | POST | 点击 |
| `/ai/analyze` | POST | AI 分析场景 |
| `/ai/execute` | POST | 执行解决方案 |
| `/automation/start` | POST | 开始自动化 |
| `/automation/stop` | POST | 停止自动化 |
| `/automation/status` | GET | 获取状态 |

## 📁 项目结构

```
wuwa-ai/
├── backend/
│   ├── main.py           # FastAPI 主入口
│   ├── automation.py     # 自动化主循环
│   ├── ai/
│   │   ├── vision.py     # VLM 视觉理解
│   │   ├── reasoner.py   # LLM 推理决策
│   │   ├── searcher.py   # 联网搜索
│   │   └── executor.py   # 执行器
│   ├── game/
│   │   ├── controller.py # 游戏控制
│   │   └── memory.py     # 记忆模块
│   └── utils/
│       ├── logger.py     # 日志
│       └── llm.py        # LLM 客户端
├── frontend/             # 前端 (开发中)
├── configs/
│   └── game_config.json
├── scripts/
│   └── setup.sh
└── README.md
```

## ⚠️ 注意事项

1. **风险提示**: 使用第三方自动化工具可能违反游戏用户协议，请自行评估风险
2. **仅供学习**: 本项目仅供学习交流，请勿用于商业用途
3. **适度使用**: 建议适度使用，保护游戏体验

## 🔧 开发

```bash
# 安装 ok-script (可选)
pip install ok-script

# 开发模式运行
python backend\main.py
```

## 📋 待实现

- [ ] 前端 Web 控制台
- [ ] 实时游戏画面预览
- [ ] 更多自动化模式
- [ ] 语音交互
- [ ] 移动端支持

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

---

Made with ❤️ for 鸣潮玩家
