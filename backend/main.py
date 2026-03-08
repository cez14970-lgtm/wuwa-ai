"""
WuwaAI 后端主入口
鸣潮智能自动化助手 - AI增强版
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
load_dotenv(project_root / "backend" / ".env")

from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ai.vision import SceneRecognizer
from ai.reasoner import ProblemAnalyzer
from ai.searcher import StrategySearcher
from ai.executor import ActionExecutor
from game.controller import GameController
from game.memory import Memory
from utils.logger import get_logger

logger = get_logger(__name__)

# 全局状态
app_state = {
    "recognizer": None,
    "analyzer": None,
    "searcher": None,
    "executor": None,
    "controller": None,
    "memory": None,
    "running": False,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 初始化 WuwaAI...")
    
    try:
        # 初始化各模块
        app_state["memory"] = Memory()
        app_state["controller"] = GameController()
        app_state["recognizer"] = SceneRecognizer()
        app_state["analyzer"] = ProblemAnalyzer()
        app_state["searcher"] = StrategySearcher()
        app_state["executor"] = ActionExecutor(app_state["controller"])
        
        logger.info("✅ 所有模块初始化完成")
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
    
    yield
    
    logger.info("👋 关闭 WuwaAI...")


# 创建FastAPI应用
app = FastAPI(
    title="WuwaAI API",
    description="鸣潮智能自动化助手 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "WuwaAI API Running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok", "modules": list(app_state.keys())}


# ==================== 游戏控制 ====================

@app.post("/game/connect")
async def connect_game():
    """连接游戏窗口"""
    try:
        controller = app_state["controller"]
        result = await controller.connect()
        return {"success": True, "message": result}
    except Exception as e:
        logger.error(f"连接游戏失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/game/screenshot")
async def get_screenshot():
    """截取游戏画面"""
    try:
        controller = app_state["controller"]
        screenshot = await controller.screenshot()
        return {"success": True, "image": screenshot}
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/game/click")
async def click_position(x: int, y: int):
    """点击指定位置"""
    try:
        controller = app_state["controller"]
        await controller.click(x, y)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/game/input")
async def input_text(text: str):
    """输入文本"""
    try:
        controller = app_state["controller"]
        await controller.input_text(text)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== AI 分析 ====================

@app.post("/ai/analyze")
async def analyze_scene():
    """AI分析当前场景"""
    try:
        controller = app_state["controller"]
        recognizer = app_state["recognizer"]
        analyzer = app_state["analyzer"]
        
        # 1. 截取画面
        screenshot = await controller.screenshot()
        
        # 2. AI视觉理解
        scene_info = await recognizer.analyze(screenshot)
        
        # 3. 判断是否需要帮助
        solution = await analyzer.analyze(scene_info, app_state["memory"])
        
        return {
            "success": True,
            "scene": scene_info,
            "solution": solution
        }
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/ai/execute")
async def execute_solution():
    """执行AI生成的解决方案"""
    try:
        executor = app_state["executor"]
        analyzer = app_state["analyzer"]
        controller = app_state["controller"]
        
        # 获取最新分析结果
        screenshot = await controller.screenshot()
        scene_info = await app_state["recognizer"].analyze(screenshot)
        solution = await analyzer.analyze(scene_info, app_state["memory"])
        
        if not solution.get("need_help"):
            return {"success": True, "message": "无需帮助，按原有流程执行"}
        
        # 搜索解决方案
        if solution.get("need_search"):
            searcher = app_state["searcher"]
            strategies = await searcher.search(solution["problem"])
            solution["strategies"] = strategies
        
        # 执行
        result = await executor.execute(solution)
        
        # 记录到记忆
        app_state["memory"].record(solution, result)
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"执行失败: {e}")
        return {"success": False, "error": str(e)}


# ==================== 控制 ====================

@app.post("/start")
async def start_automation():
    """开始自动化"""
    app_state["running"] = True
    return {"success": True, "message": "自动化已开始"}


@app.post("/stop")
async def stop_automation():
    """停止自动化"""
    app_state["running"] = False
    return {"success": True, "message": "自动化已停止"}


@app.get("/status")
async def get_status():
    """获取当前状态"""
    return {
        "running": app_state["running"],
        "memory": app_state["memory"].get_summary() if app_state["memory"] else None
    }


# ==================== 设置 ====================

@app.post("/settings")
async def update_settings(settings: dict):
    """更新设置"""
    # TODO: 保存设置到配置文件
    return {"success": True, "message": "设置已更新"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
