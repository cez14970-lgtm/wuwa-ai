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
        return {"success": "未找到游戏窗口" not in result, "message": result}
    
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
            # 剧情模式：自动点击对话
            await self._auto_dialogue()
        elif scene_type == "battle":
            # 战斗模式：自动战斗
            await self._auto_battle()
        elif scene_type == "loading":
            # 等待加载
            await asyncio.sleep(3)
        # 其他场景暂时跳过
    
    async def _auto_dialogue(self):
        """自动剧情对话"""
        # 这里可以调用ok-script自动点击"继续"按钮
        # 简化版本：等待一段时间让对话自动播放
        await asyncio.sleep(2)
    
    async def _auto_battle(self):
        """自动战斗"""
        # 这里可以添加自动战斗逻辑
        await asyncio.sleep(1)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "running": self.running,
            "paused": self.paused,
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
