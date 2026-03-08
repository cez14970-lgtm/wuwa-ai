"""
AI 执行器模块
将解决方案转为具体操作并执行
"""
import asyncio
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class ActionExecutor:
    """动作执行器"""
    
    def __init__(self, controller):
        self.controller = controller
        logger.info("⚡ ActionExecutor 初始化完成")
    
    async def execute(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行解决方案
        
        Args:
            solution: 包含解决方案的字典
            
        Returns:
            执行结果
        """
        try:
            if not solution.get("need_help"):
                return {
                    "success": True,
                    "message": "无需帮助，继续原有流程",
                    "actions": []
                }
            
            # 检查是否有搜索结果
            strategies = solution.get("strategies", [])
            if not strategies:
                return {
                    "success": False,
                    "message": "没有找到解决方案"
                }
            
            # 从搜索结果中提取步骤
            from ai.reasoner import ProblemAnalyzer
            analyzer = ProblemAnalyzer()
            
            # 取最佳策略
            best_strategy = strategies[0]
            steps = await analyzer.extract_solution_steps(
                best_strategy.get("content", "")
            )
            
            if not steps:
                return {
                    "success": False,
                    "message": "无法从攻略中提取操作步骤"
                }
            
            # 执行步骤
            results = []
            for i, step in enumerate(steps):
                logger.info(f"📍 执行步骤 {i+1}/{len(steps)}: {step.get('description', '')}")
                
                result = await self._execute_step(step)
                results.append({
                    "step": i + 1,
                    "description": step.get("description", ""),
                    "result": result
                })
                
                # 每个步骤后短暂等待
                await asyncio.sleep(1)
            
            # 检查是否成功
            success_count = sum(1 for r in results if r.get("result", {}).get("success"))
            
            return {
                "success": success_count > 0,
                "total_steps": len(steps),
                "completed_steps": success_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ 执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个步骤
        
        Args:
            step: 步骤字典
            
        Returns:
            执行结果
        """
        action = step.get("action", "").lower()
        
        try:
            if action == "click":
                x = step.get("x", 0)
                y = step.get("y", 0)
                await self.controller.click(x, y)
                return {"success": True, "action": "click", "position": (x, y)}
            
            elif action == "input":
                text = step.get("text", "")
                await self.controller.input_text(text)
                return {"success": True, "action": "input", "text": text}
            
            elif action == "wait":
                seconds = step.get("seconds", 1)
                await asyncio.sleep(seconds)
                return {"success": True, "action": "wait", "seconds": seconds}
            
            elif action == "press":
                key = step.get("key", "")
                await self.controller.press_key(key)
                return {"success": True, "action": "press", "key": key}
            
            elif action == "move":
                x = step.get("x", 0)
                y = step.get("y", 0)
                await self.controller.move(x, y)
                return {"success": True, "action": "move", "position": (x, y)}
            
            else:
                logger.warning(f"⚠️ 未知动作类型: {action}")
                return {"success": False, "error": f"未知动作: {action}"}
                
        except Exception as e:
            logger.error(f"❌ 步骤执行失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        执行一系列动作
        
        Args:
            actions: 动作列表
            
        Returns:
            执行结果列表
        """
        results = []
        
        for i, action in enumerate(actions):
            logger.info(f"📍 执行动作 {i+1}/{len(actions)}")
            
            result = await self._execute_step(action)
            results.append(result)
            
            if not result.get("success"):
                logger.warning(f"⚠️ 动作 {i+1} 失败，继续执行")
            
            await asyncio.sleep(0.5)
        
        return results
