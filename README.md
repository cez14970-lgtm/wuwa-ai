# WuwaAI - 鸣潮智能自动化助手

## 项目概述

基于ok-ww开源项目，增强AI能力，实现真正智能托管过剧情。

### 核心升级点

| 现有ok-ww | WuwaAI增强版 |
|-----------|-------------|
| 图像识别+模板匹配 | + AI视觉理解(VLM) |
| 固定流程 | + 动态决策 |
| 无法联网 | + 实时攻略搜索 |
| 遇到问题卡住 | + 自动搜索解法 |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                            │
│  (Web控制台 - 可视化配置/监控/日志)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       AI决策层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 场景识别    │  │ 问题分析    │  │ 步骤规划    │          │
│  │ (VLM)       │  │ (LLM)       │  │ (LLM)       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       工具层                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ 联网搜索    │  │ OCR识别     │  │ 执行控制    │          │
│  │ (Tavily)    │  │ (EasyOCR)   │  │ (ok-script)│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       游戏交互层                             │
│  (点击/按键/移动 - Windows API模拟)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```
wuwa-ai/
├── backend/                    # 后端服务
│   ├── main.py                 # FastAPI主入口
│   ├── ai/
│   │   ├── vision.py           # VLM视觉理解
│   │   ├── reasoner.py        # LLM推理决策
│   │   ├── searcher.py        # 联网搜索
│   │   └── executor.py         # 步骤执行器
│   ├── game/
│   │   ├── controller.py      # 游戏控制
│   │   ├── ocr.py             # OCR识别
│   │   └── memory.py          # 记忆模块
│   └── utils/
│       ├── config.py           # 配置管理
│       └── logger.py           # 日志
│
├── frontend/                   # 前端Web界面
│   ├── src/
│   │   ├── App.vue            # 主应用
│   │   ├── views/
│   │   │   ├── Dashboard.vue  # 控制面板
│   │   │   ├── Logs.vue       # 日志查看
│   │   │   └── Settings.vue   # 设置
│   │   └── components/
│   │       ├── GameScreen.vue # 游戏画面
│   │       └── ControlPanel.vue
│   └── package.json
│
├── scripts/                    # 脚本
│   ├── setup.sh               # 一键安装
│   └── run.sh                 # 启动
│
├── configs/                   # 配置
│   ├── .env.example           # 环境变量模板
│   └── game_config.json       # 游戏配置
│
└── README.md
```

---

## 依赖环境

### Python环境
- Python 3.11+
- Windows 10/11 (需要GUI自动化)

### Python依赖
```
fastapi==0.109.0
uvicorn==0.27.0
ok-script @ git+https://github.com/ok-oldking/ok-script.git
qwen-vl-utils @ git+https://github.com/QwenLM/qwen-vl-utils.git
transformers>=4.36.0
torch>=2.0.0
torchvision>=0.15.0
pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
python-dotenv>=1.0.0
httpx>=0.26.0
aiohttp>=3.9.0
```

### API密钥 (可选)
- 阿里云百炼 (Qwen模型): https://bailian.aliyun.com/
- Tavily搜索: https://tavily.com/

---

## 核心模块设计

### 1. 场景识别模块 (vision.py)

```python
class SceneRecognizer:
    """AI视觉理解 - 理解游戏画面内容"""
    
    def __init__(self, model="qwen-vl-max"):
        self.model = model
    
    async def analyze(self, screenshot) -> SceneInfo:
        """
        输入: 游戏截图
        输出: 场景信息
        """
        # 1. 调用VLM理解画面
        # 2. 识别: 剧情/战斗/探索/机关/菜单/ loading
        # 3. 提取关键元素位置
        # 4. 判断当前状态
```

### 2. 问题分析模块 (reasoner.py)

```python
class ProblemAnalyzer:
    """LLM推理 - 分析当前问题并规划解决方案"""
    
    async def analyze(self, scene_info, history) -> Solution:
        """
        输入: 场景信息 + 历史上下文
        输出: 解决方案
        """
        # 1. 判断是否需要帮助
        # 2. 分析问题类型
        # 3. 决定下一步行动
```

### 3. 联网搜索模块 (searcher.py)

```python
class StrategySearcher:
    """联网搜索 - 查找攻略"""
    
    async def search(self, query) -> List[Strategy]:
        """
        输入: 问题描述
        输出: 搜索到的攻略列表
        """
        # 1. 搜索鸣潮攻略
        # 2. 提取关键步骤
        # 3. 返回结构化结果
```

### 4. 执行控制模块 (executor.py)

```python
class ActionExecutor:
    """步骤执行 - 把解决方案转为操作"""
    
    def __init__(self, controller):
        self.controller = controller
    
    async def execute(self, solution):
        """
        输入: LLM生成的解决方案
        输出: 执行结果
        """
        # 1. 解析步骤
        # 2. 依次执行
        # 3. 验证结果
```

---

## 核心流程

```
开始
  │
  ▼
┌─────────────────┐
│  截取游戏画面   │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  AI视觉理解     │──是──→ 识别为剧情/战斗/探索/机关
│  (这是什么？)   │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  需要帮助？     │
│  (密码/谜题/卡关)
└─────────────────┘
  │
  ├── 否 ──→ 按原有流程执行
  │
  ▼ 是
┌─────────────────┐
│  联网搜索攻略   │
│  (怎么办？)     │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  LLM提取步骤   │
│  (一步步怎么做) │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  执行操作序列   │
│  (点击/输入/等) │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│  验证结果       │
│  (成功了？)     │
└─────────────────┘
  │
  ├── 否 ──→ 记录失败，尝试下一个方案
  │
  ▼ 是
┌─────────────────┐
│  继续原有流程   │
└─────────────────┘
  │
  ▼
循环
```

---

## 遇到具体问题的处理

### 1. 密码输入
```
识别 → "这是密码输入框" → 搜索"鸣潮 xxx 密码" → 提取密码 → 输入 → 确认
```

### 2. 机关解谜
```
识别 → "这是音符机关" → 搜索"鸣潮 音符机关 攻略" → 提取步骤 → 按顺序执行
```

### 3. 任务指引
```
识别 → "找不到任务目标" → 搜索"鸣潮 xxx 任务 位置" → 获取坐标 → 自动寻路
```

---

## 配置说明

### 环境变量 (.env)

```bash
# LLM配置 (推荐阿里百炼)
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# 搜索配置 (可选)
TAVILY_API_KEY=your_tavily_key

# 游戏配置
GAME_PROCESS_NAME=WuWa.exe
GAME_WINDOW_TITLE=鸣潮
```

---

## 部署步骤

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/wuwa-ai.git
cd wuwa-ai
```

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt

# 安装ok-script
pip install ok-script
```

### 3. 配置
```bash
cp configs/.env.example configs/.env
# 编辑 .env 填入API密钥
```

### 4. 启动
```bash
# 启动后端
cd backend
python main.py

# 启动前端 (另一个终端)
cd frontend
npm install
npm run dev
```

### 5. 使用
- 浏览器打开 http://localhost:5173
- 连接游戏窗口
- 开始自动化

---

## 待实现功能优先级

### P0 - 核心功能
- [x] 项目架构设计
- [ ] 基础游戏控制 (点击/移动)
- [ ] 场景截图
- [ ] VLM场景识别
- [ ] LLM决策
- [ ] 联网搜索
- [ ] 步骤执行

### P1 - 重要功能
- [ ] 记忆模块 (记住之前尝试)
- [ ] 错误重试机制
- [ ] 日志记录
- [ ] Web控制台

### P2 - 增强功能
- [ ] 语音交互
- [ ] 多语言支持
- [ ] 自定义工作流

---

## 注意事项

1. **风险提示**: 使用第三方自动化工具可能违反游戏用户协议，请自行评估风险
2. **仅供学习**: 本项目仅供学习交流，请勿用于商业用途
3. **适度使用**: 建议适度使用，保护游戏体验

---

## 参考资源

- ok-script框架: https://github.com/ok-oldking/ok-script
- ok-ww原项目: https://github.com/ok-oldking/ok-wuthering-waves
- Qwen-VL: https://github.com/QwenLM/qwen-vl
- 阿里云百炼: https://bailian.aliyun.com/
