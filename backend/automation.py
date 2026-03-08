"""
WuwaAI 自动化主循环
负责协调各个模块，实现全自动过剧情
"""
import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime

from ai.vision import SceneRecognizer
from ai.reasoner import ProblemAnalyzer
from ai.searcher import StrategySearcher
from ai.executor import ActionExecutor
from game.controller import GameController
from game.memory import Memory
from utils.logger import get_logger

logger = get_logger(__name__)


class WuwaAIAutomation:
    """自动化主控制器"""
    
    def __init__(self):
        self.controller: Optional[GameController] = None
        self.recognizer: Optional[SceneRecognizer] = None
        self.analyzer: Optional[ProblemAnalyzer] = None
        self.searcher: Optional[StrategySearcher] = None
        self.executor: Optional[ActionExecutor] = None
        self.memory: Optional[Memory] = None
        
        self.running = False
        self.paused = False
        self.connected = False  # 游戏是否已连接
        self.current_mode = "story"  # story/battle/explore
        
        # 配置
        self.config = {
            "screenshot_interval": 2,  # 截图间隔(秒)
            "max_retries": 3,          # 最大重试次数
            "action_delay": 1,         # 动作间隔(秒)
        }
    
    async def initialize(self):
        """初始化所有模块"""
        logger.info("🚀 初始化 WuwaAI 自动化引擎...")
        
        self.memory = Memory()
        self.controller = GameController()
        self.recognizer = SceneRecognizer()
        self.analyzer = ProblemAnalyzer()
        self.searcher = StrategySearcher()
        self.executor = ActionExecutor(self.controller)
        
        logger.info("✅ 初始化完成")
        return True
    
    async def connect_game(self) -> Dict[str, Any]:
        """连接游戏"""
        if not self.controller:
            return {"success": False, "error": "未初始化"}
        
        result = await self.controller.connect()
        connected = "未找到" not in result and "失败" not in result
        self.connected = connected
        
        return {"success": connected, "message": result}
    
    async def start(self, mode: str = "story"):
        """开始自动化"""
        if self.running:
            logger.warning("⚠️ 自动化已在运行中")
            return
        
        self.running = True
        self.current_mode = mode
        logger.info(f"▶️ 开始自动化 (模式: {mode})")
        
        # 启动主循环
        asyncio.create_task(self._main_loop())
    
    async def stop(self):
        """停止自动化"""
        self.running = False
        logger.info("⏹️ 自动化已停止")
    
    async def pause(self):
        """暂停自动化"""
        self.paused = True
        logger.info("⏸️ 自动化已暂停")
    
    async def resume(self):
        """恢复自动化"""
        self.paused = False
        logger.info("▶️ 自动化已恢复")
    
    async def _main_loop(self):
        """主自动化循环"""
        logger.info("🔄 主循环启动")
        
        consecutive_errors = 0
        max_errors = 5
        
        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(1)
                    continue
                
                # 1. 截图
                screenshot = await self.controller.screenshot()
                if not screenshot:
                    logger.warning("⚠️ 截图失败")
                    await asyncio.sleep(2)
                    continue
                
                # 2. AI视觉理解
                scene_info = await self.recognizer.analyze(screenshot)
                logger.info(f"🎯 场景: {scene_info.scene_type}, 状态: {scene_info.status}")
                
                # 3. 判断是否需要帮助
                solution = await self.analyzer.analyze(scene_info, self.memory)
                
                if solution.get("need_help"):
                    logger.warning(f"🆘 需要帮助: {solution.get('problem_description')}")
                    
                    # 4. 如果需要搜索
                    if solution.get("need_search"):
                        strategies = await self.searcher.search(
                            solution.get("problem_description", "")
                        )
                        solution["strategies"] = strategies
                    
                    # 5. 执行解决方案
                    result = await self.executor.execute(solution)
                    
                    # 6. 记录到记忆
                    self.memory.record(solution, result)
                    
                    if result.get("success"):
                        logger.info("✅ 问题已解决")
                    else:
                        logger.warning("❌ 解决方案失败，将重试")
                
                # 正常场景处理（原有逻辑）
                await self._handle_normal_scene(scene_info)
                
                consecutive_errors = 0
                
                # 等待下一次循环
                await asyncio.sleep(self.config["screenshot_interval"])
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ 主循环错误 ({consecutive_errors}/{max_errors}): {e}")
                
                if consecutive_errors >= max_errors:
                    logger.error("❌ 错误次数过多，停止自动化")
                    self.running = False
                    break
                
                await asyncio.sleep(2)
        
        logger.info("🔄 主循环结束")
    
    async def _handle_normal_scene(self, scene_info):
        """处理正常场景"""
        # 根据场景类型执行相应操作
        scene_type = scene_info.scene_type
        
        if scene_type == "story":
            await self._auto_story()
        elif scene_type == "battle":
            await self._auto_battle()
        elif scene_type == "explore":
            await self._auto_explore()
        elif scene_type == "loading":
            await asyncio.sleep(3)
        else:
            # 未知场景，尝试自动操作
            await self._auto_explore()
    
    async def _auto_story(self):
        """自动剧情模式"""
        logger.info("📖 执行自动剧情...")
        
        # 1. 查找"继续"按钮并点击 (屏幕中间下方)
        # 2. 等待对话播放
        # 3. 重复
        
        # 模拟点击"继续"按钮位置 (1920x1080分辨率)
        await self.controller.click(960, 900)  # 屏幕底部中央
        await asyncio.sleep(1)
        
        # 模拟按空格跳过对话
        await self.controller.press_key('space')
        await asyncio.sleep(2)
        
        logger.info("✅ 剧情操作完成")
    
    async def _auto_battle(self):
        """自动战斗模式"""
        logger.info("⚔️ 执行自动战斗...")
        
        # 战斗基本操作循环
        # 1. 普通攻击 (鼠标左键)
        await self.controller.click(960, 540)  # 点击屏幕中间
        await asyncio.sleep(0.3)
        
        # 2. 释放技能 (Q/E/R键)
        await self.controller.press_key('q')  # 技能1
        await asyncio.sleep(0.5)
        
        await self.controller.press_key('e')  # 技能2
        await asyncio.sleep(0.5)
        
        await self.controller.press_key('r')  # 大招
        await asyncio.sleep(0.5)
        
        # 3. 闪避 (Shift)
        await self.controller.press_key('shift')
        await asyncio.sleep(0.3)
        
        # 4. 跳跃 (Space) 躲避技能
        await self.controller.press_key('space')
        
        await asyncio.sleep(1)
        logger.info("✅ 战斗操作完成")
    
    async def _auto_explore(self):
        """自动探索模式"""
        logger.info("🗺️ 执行自动探索...")
        
        # 1. 自动移动 (按住W)
        # 2. 跳跃翻越障碍 (Space)
        # 3. 互动 (E)
        # 4. 收集物品
        
        # 模拟按下W键前进
        import time
        start = time.time()
        while time.time() - start < 2:  # 前进2秒
            await self.controller.press_key('w')
            await asyncio.sleep(0.1)
        
        # 尝试互动
        await self.controller.press_key('e')
        await asyncio.sleep(0.5)
        
        # 跳跃
        await self.controller.press_key('space')
        await asyncio.sleep(0.5)
        
        logger.info("✅ 探索操作完成")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "running": self.running,
            "paused": self.paused,
            "connected": self.connected,
            "mode": self.current_mode,
            "memory": self.memory.get_summary() if self.memory else None
        }


# 全局实例
automation: Optional[WuwaAIAutomation] = None


async def get_automation() -> WuwaAIAutomation:
    """获取自动化实例"""
    global automation
    if automation is None:
        automation = WuwaAIAutomation()
        await automation.initialize()
    return automation
