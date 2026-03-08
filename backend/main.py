"""
WuwaAI 后端主入口
鸣潮智能自动化助手 - AI增强版
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / "backend" / ".env")

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from automation import WuwaAIAutomation, get_automation
from utils.logger import get_logger

logger = get_logger(__name__)

# 全局自动化实例
automation: WuwaAIAutomation = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global automation
    logger.info("🚀 初始化 WuwaAI...")
    
    try:
        automation = await get_automation()
        logger.info("✅ WuwaAI 初始化完成")
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
    
    yield
    
    logger.info("👋 关闭 WuwaAI...")
    if automation:
        await automation.stop()


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


# ==================== 根路由 ====================

@app.get("/")
async def root():
    return {
        "message": "WuwaAI API Running", 
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "automation": automation.get_status() if automation else None
    }


# ==================== 游戏控制 ====================

class ConnectRequest(BaseModel):
    process_name: str = "WuWa.exe"
    window_title: str = "鸣潮"


@app.post("/game/connect")
async def connect_game(request: ConnectRequest = None):
    """连接游戏窗口"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        if request:
            os.environ["GAME_PROCESS_NAME"] = request.process_name
            os.environ["GAME_WINDOW_TITLE"] = request.window_title
        
        result = await automation.connect_game()
        return result
    except Exception as e:
        logger.error(f"连接游戏失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/game/screenshot")
async def get_screenshot():
    """截取游戏画面"""
    try:
        if not automation or not automation.controller:
            return {"success": False, "error": "未连接游戏"}
        
        screenshot = await automation.controller.screenshot()
        return {"success": True, "image": screenshot[:1000] + "..." if len(screenshot) > 1000 else screenshot}
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return {"success": False, "error": str(e)}


class ClickRequest(BaseModel):
    x: int
    y: int


@app.post("/game/click")
async def click_position(request: ClickRequest):
    """点击指定位置"""
    try:
        if not automation or not automation.controller:
            return {"success": False, "error": "未连接游戏"}
        
        await automation.controller.click(request.x, request.y)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


class InputRequest(BaseModel):
    text: str


@app.post("/game/input")
async def input_text(request: InputRequest):
    """输入文本"""
    try:
        if not automation or not automation.controller:
            return {"success": False, "error": "未连接游戏"}
        
        await automation.controller.input_text(request.text)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== AI 分析 ====================

@app.post("/ai/analyze")
async def analyze_scene():
    """AI分析当前场景"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        screenshot = await automation.controller.screenshot()
        if not screenshot:
            return {"success": False, "error": "截图失败"}
        
        scene_info = await automation.recognizer.analyze(screenshot)
        solution = await automation.analyzer.analyze(scene_info, automation.memory)
        
        return {
            "success": True,
            "scene": scene_info.to_dict() if hasattr(scene_info, 'to_dict') else scene_info,
            "solution": solution
        }
    except Exception as e:
        logger.error(f"分析失败: {e}")
        return {"success": False, "error": str(e)}


@app.post("/ai/execute")
async def execute_solution():
    """执行AI生成的解决方案"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        screenshot = await automation.controller.screenshot()
        scene_info = await automation.recognizer.analyze(screenshot)
        solution = await automation.analyzer.analyze(scene_info, automation.memory)
        
        if not solution.get("need_help"):
            return {"success": True, "message": "无需帮助，按原有流程执行"}
        
        # 搜索解决方案
        if solution.get("need_search"):
            strategies = await automation.searcher.search(solution["problem_description"])
            solution["strategies"] = strategies
        
        # 执行
        result = await automation.executor.execute(solution)
        
        # 记录到记忆
        automation.memory.record(solution, result)
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"执行失败: {e}")
        return {"success": False, "error": str(e)}


# ==================== 自动化控制 ====================

class StartRequest(BaseModel):
    mode: str = "story"


@app.post("/automation/start")
async def start_automation(request: StartRequest = None):
    """开始自动化"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        mode = request.mode if request else "story"
        await automation.start(mode)
        return {"success": True, "message": f"自动化已开始 (模式: {mode})"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/automation/stop")
async def stop_automation():
    """停止自动化"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        await automation.stop()
        return {"success": True, "message": "自动化已停止"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/automation/pause")
async def pause_automation():
    """暂停自动化"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        await automation.pause()
        return {"success": True, "message": "自动化已暂停"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/automation/resume")
async def resume_automation():
    """恢复自动化"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        await automation.resume()
        return {"success": True, "message": "自动化已恢复"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/automation/status")
async def get_status():
    """获取自动化状态"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        return {"success": True, "status": automation.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 设置 ====================

class SettingsRequest(BaseModel):
    screenshot_interval: int = 2
    max_retries: int = 3
    action_delay: int = 1


@app.get("/settings")
async def get_settings():
    """获取设置"""
    if not automation:
        return {"success": False, "error": "自动化未初始化"}
    
    return {"success": True, "settings": automation.config}


@app.post("/settings")
async def update_settings(request: SettingsRequest):
    """更新设置"""
    try:
        if not automation:
            return {"success": False, "error": "自动化未初始化"}
        
        automation.config["screenshot_interval"] = request.screenshot_interval
        automation.config["max_retries"] = request.max_retries
        automation.config["action_delay"] = request.action_delay
        
        return {"success": True, "message": "设置已更新", "settings": automation.config}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
