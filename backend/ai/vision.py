"""
AI 视觉理解模块
使用 VLM 理解游戏画面内容
"""
import base64
import json
from typing import Optional, Dict, Any
from utils.logger import get_logger
from utils.llm import get_llm_client

logger = get_logger(__name__)


class SceneInfo:
    """场景信息"""
    def __init__(self, scene_type: str, description: str, elements: list, status: str):
        self.scene_type = scene_type  # story/battle/explore/puzzle/menu/loading
        self.description = description
        self.elements = elements  # 关键元素列表
        self.status = status  # normal/stuck/need_help
    
    def to_dict(self):
        return {
            "scene_type": self.scene_type,
            "description": self.description,
            "elements": self.elements,
            "status": self.status
        }


class SceneRecognizer:
    """场景识别器 - AI视觉理解"""
    
    # 场景类型提示
    SCENE_PROMPT = """你是一个游戏画面分析专家。请分析以下鸣潮游戏截图。

游戏画面类型可能包括:
- story: 剧情对话
- battle: 战斗
- explore: 探索世界
- puzzle: 机关解谜
- menu: 菜单界面
- loading: 加载中
- unknown: 未知

请分析:
1. 当前是什么类型的场景?
2. 画面中有什么关键元素?(按钮/任务/提示/敌人/道具等)
3. 玩家当前状态如何?

请用JSON格式返回分析结果:
{
    "scene_type": "类型",
    "description": "场景描述",
    "elements": [
        {"type": "元素类型", "content": "内容", "position": "位置(如有)"}
    ],
    "status": "状态(normal/stuck/need_help)"
}

注意: 如果画面中有:
- 密码输入框
- 未完成的机关
- 卡关提示
- 找不到任务目标
请将status设为"need_help"
"""

    def __init__(self, model: str = None):
        self.client = get_llm_client()
        self.model = model or "qwen-vl-max"
        logger.info(f"🎯 SceneRecognizer 初始化完成, 模型: {self.model}")
    
    async def analyze(self, image_base64: str) -> SceneInfo:
        """
        分析游戏截图
        
        Args:
            image_base64: base64编码的截图
            
        Returns:
            SceneInfo对象
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": f"data:image/jpeg;base64,{image_base64}"},
                        {"text": self.SCENE_PROMPT}
                    ]
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            # 解析JSON
            # 尝试提取JSON部分
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            return SceneInfo(
                scene_type=result.get("scene_type", "unknown"),
                description=result.get("description", ""),
                elements=result.get("elements", []),
                status=result.get("status", "normal")
            )
            
        except Exception as e:
            logger.error(f"❌ 场景分析失败: {e}")
            return SceneInfo(
                scene_type="unknown",
                description=f"分析失败: {str(e)}",
                elements=[],
                status="unknown"
            )
    
    async def analyze_text_only(self, description: str) -> SceneInfo:
        """
        仅基于文字描述分析场景（用于OCR结果）
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"{self.SCENE_PROMPT}\n\n注意: 以下不是图片，而是从游戏中识别出的文字:\n{description}"
                }
            ]
            
            response = await self.client.chat.completions.create(
                model="qwen-plus",  # 使用文本模型
                messages=messages,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            return SceneInfo(
                scene_type=result.get("scene_type", "unknown"),
                description=result.get("description", ""),
                elements=result.get("elements", []),
                status=result.get("status", "normal")
            )
            
        except Exception as e:
            logger.error(f"❌ 文本分析失败: {e}")
            return SceneInfo(
                scene_type="unknown",
                description=f"分析失败: {str(e)}",
                elements=[],
                status="unknown"
            )
