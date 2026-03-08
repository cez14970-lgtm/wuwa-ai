"""
AI 推理决策模块
基于LLM分析场景并制定解决方案
"""
import json
from typing import Dict, Any, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.llm import get_llm_client

logger = get_logger(__name__)


class ProblemAnalyzer:
    """问题分析器 - LLM推理决策"""
    
    ANALYSIS_PROMPT = """你是一个游戏策略专家。玩家正在玩鸣潮游戏，需要你的帮助。

当前场景信息:
{scene_info}

玩家历史上下文:
{history}

请分析:
1. 玩家是否需要帮助?(是否卡关了?)
2. 如果需要帮助，具体问题是什么?
3. 应该采取什么行动?

问题类型可能包括:
- password: 需要输入密码
- puzzle: 机关/谜题
- lost: 找不到任务目标/迷失方向
- dialogue: 需要选择对话选项
- loading: 长时间加载卡住
- battle: 战斗困难
- other: 其他问题

请用JSON格式返回分析结果:
{{
    "need_help": true/false,
    "problem_type": "问题类型(如适用)",
    "problem_description": "问题描述",
    "need_search": true/false,
    "suggested_action": "建议的下一步行动",
    "confidence": 0.0-1.0
}}

如果need_search为true，说明需要联网搜索解决方案。
"""

    def __init__(self):
        self.client = get_llm_client()
        logger.info("🧠 ProblemAnalyzer 初始化完成")
    
    async def analyze(self, scene_info, memory) -> Dict[str, Any]:
        """
        分析场景并给出解决方案
        
        Args:
            scene_info: SceneInfo对象
            memory: Memory对象
            
        Returns:
            解决方案字典
        """
        try:
            # 获取历史上下文
            history = memory.get_recent(5) if memory else []
            history_text = json.dumps(history, ensure_ascii=False, indent=2) if history else "无"
            
            # 构建提示
            prompt = self.ANALYSIS_PROMPT.format(
                scene_info=json.dumps(scene_info.to_dict() if hasattr(scene_info, 'to_dict') else scene_info, 
                                     ensure_ascii=False, indent=2),
                history=history_text
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # 解析JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            logger.info(f"📊 分析结果: need_help={result.get('need_help')}, need_search={result.get('need_search')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 分析失败: {e}")
            return {
                "need_help": False,
                "error": str(e),
                "suggested_action": "继续原有流程"
            }
    
    async def extract_solution_steps(self, solution_text: str) -> list:
        """
        从解决方案文本中提取具体操作步骤
        
        Args:
            solution_text: 解决方案描述
            
        Returns:
            操作步骤列表
        """
        try:
            prompt = f"""从以下游戏攻略中提取具体的操作步骤。

攻略内容:
{solution_text}

请提取步骤，格式要求:
- 每个步骤应该是可以执行的具体动作
- 使用中文描述
- 格式如: "点击位置(100,200)" 或 "输入文本:密码" 或 "等待3秒"

请返回JSON数组:
[
    {{"action": "click", "x": 100, "y": 200, "description": "点击确认按钮"}},
    {{"action": "input", "text": "密码", "description": "输入密码"}},
    {{"action": "wait", "seconds": 3, "description": "等待加载"}}
]
"""
            
            messages = [{"role": "user", "content": prompt}]
            
            response = await self.client.chat.completions.create(
                model="qwen-plus",
                messages=messages,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            
            steps = json.loads(result_text.strip())
            
            return steps
            
        except Exception as e:
            logger.error(f"❌ 步骤提取失败: {e}")
            return []
