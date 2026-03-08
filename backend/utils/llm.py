"""
LLM 客户端
统一管理各种LLM API调用
"""
import os
import httpx
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """LLM客户端"""
    
    def __init__(self):
        # 优先使用阿里百炼
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("DASHSCOPE_BASE_URL") or os.getenv("LLM_BASE_URL", 
            "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = os.getenv("DASHSCOPE_MODEL") or os.getenv("LLM_MODEL_NAME", "qwen-plus")
        
        # 兼容 OpenAI 格式
        self.is_openai_compatible = "dashscope" in self.base_url or "openai" in self.base_url
        
        self.client = httpx.AsyncClient(
            timeout=120.0,
            limits=httpx.Limits(max_connections=10)
        )
        
        logger.info(f"🤖 LLMClient 初始化, 模型: {self.model}")
    
    async def chat(self, messages: list, **kwargs) -> dict:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            响应字典
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 根据不同的API调整请求格式
        if "dashscope" in self.base_url:
            # 阿里百炼格式
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        else:
            # OpenAI兼容格式
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"LLM API错误: {response.status_code} - {response.text}")
                raise Exception(f"API错误: {response.status_code}")
                
        except Exception as e:
            logger.error(f"LLM请求失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局客户端实例
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


async def close_llm_client():
    """关闭LLM客户端"""
    global _client
    if _client:
        await _client.close()
        _client = None
