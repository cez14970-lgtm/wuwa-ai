"""
WuwaAI 后端主入口
鸣潮智能自动化助手 - v2.0
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pydantic import BaseModel
import uvicorn

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / "backend" / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wuwa_ai import WuwaAI, Config

# 全局AI实例
ai: WuwaAI = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    global ai
    print("🚀 初始化 WuwaAI v2.0...")
    
    # 创建AI实例
    ai = WuwaAI(is_cloud=Config.IS_CLOUD_GAME)
    
    yield
    
    print("👋 关闭 WuwaAI...")


# 创建FastAPI应用
app = FastAPI(
    title="WuwaAI API v2.0",
    description="鸣潮智能自动化助手 API",
    version="2.0.0",
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
    return {"message": "WuwaAI API v2.0", "version": "2.0.0"}


@app.get("/health")
async def health():
    if not ai:
        return {"status": "error", "message": "AI未初始化"}
    
    status = ai.get_status()
    return {"status": "ok", **status}


# ==================== 游戏控制 ====================

class ConnectRequest(BaseModel):
    is_cloud: bool = True


@app.post("/game/connect")
async def connect_game(request: ConnectRequest = None):
    """连接游戏"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        is_cloud = request.is_cloud if request else True
        result = ai.connect()
        
        return {"success": "成功" in result, "message": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/game/screenshot")
async def get_screenshot():
    """获取截图"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        img_base64 = ai.get_screenshot_base64()
        
        if not img_base64:
            return {"success": False, "error": "截图失败"}
        
        return {"success": True, "image": img_base64}
    except Exception as e:
        return {"success": False, "error": str(e)}


class ClickRequest(BaseModel):
    x: int
    y: int


@app.post("/game/click")
async def click_position(request: ClickRequest):
    """点击"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        ai.controller.click(request.x, request.y)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


class KeyRequest(BaseModel):
    key: str


@app.post("/game/key")
async def press_key(request: KeyRequest):
    """按键"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        ai.controller.press_key(request.key)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 任务控制 ====================

class StartRequest(BaseModel):
    task: str = "explore"


@app.post("/task/start")
async def start_task(request: StartRequest):
    """开始任务"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        ai.start_task(request.task)
        
        return {"success": True, "message": f"任务已开始: {request.task}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/task/stop")
async def stop_task():
    """停止任务"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        ai.stop_task()
        
        return {"success": True, "message": "任务已停止"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/task/execute")
async def execute_task():
    """执行一次任务检测"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        ai.execute_once()
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/task/status")
async def get_status():
    """获取任务状态"""
    try:
        if not ai:
            return {"success": False, "error": "AI未初始化"}
        
        return {"success": True, "status": ai.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 自动化循环 ====================

import asyncio

automation_task = None


@app.post("/automation/start")
async def start_automation():
    """开始自动化循环"""
    global automation_task
    
    if not ai:
        return {"success": False, "error": "AI未初始化"}
    
    async def loop():
        while True:
            try:
                ai.execute_once()
                await asyncio.sleep(Config.TASK_INTERVAL)
            except Exception as e:
                print(f"自动化循环错误: {e}")
                break
    
    automation_task = asyncio.create_task(loop())
    
    return {"success": True, "message": "自动化已开始"}


@app.post("/automation/stop")
async def stop_automation():
    """停止自动化循环"""
    global automation_task
    
    if automation_task:
        automation_task.cancel()
        automation_task = None
    
    if ai:
        ai.stop_task()
    
    return {"success": True, "message": "自动化已停止"}


# ==================== 设置 ====================

@app.get("/settings")
async def get_settings():
    """获取设置"""
    return {
        "success": True,
        "settings": {
            "is_cloud_game": Config.IS_CLOUD_GAME,
            "game_process": Config.GAME_PROCESS_NAME,
            "task_interval": Config.TASK_INTERVAL
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
