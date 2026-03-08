"""
AI 联网搜索模块
搜索鸣潮游戏攻略
"""
import os
import json
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class StrategySearcher:
    """攻略搜索器"""
    
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.search_results = []
        logger.info(f"🔍 StrategySearcher 初始化, Tavily: {'已配置' if self.tavily_key else '未配置'}")
    
    async def search(self, problem: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        搜索游戏攻略
        
        Args:
            problem: 问题描述
            max_results: 最大结果数
            
        Returns:
            攻略列表
        """
        try:
            # 构建搜索查询
            query = f"鸣潮 {problem} 攻略"
            
            if self.tavily_key:
                results = await self._search_tavily(query, max_results)
            else:
                results = await self._search_fallback(query, max_results)
            
            self.search_results = results
            logger.info(f"� найдено {len(results)} 条攻略")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 搜索失败: {e}")
            return []
    
    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """使用Tavily搜索"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.tavily_key,
                        "query": query,
                        "max_results": max_results,
                        "include_answer": True,
                        "include_raw_content": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get("results", []):
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "content": item.get("content", "")[:500],
                            "score": item.get("score", 0)
                        })
                    
                    return results
                else:
                    logger.warning(f"Tavily返回错误: {response.status_code}")
                    return await self._search_fallback(query, max_results)
                    
        except Exception as e:
            logger.error(f"Tavily搜索失败: {e}")
            return await self._search_fallback(query, max_results)
    
    async def _search_fallback(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """备用搜索方案 - 使用模拟结果或简单搜索"""
        # 这里可以添加其他搜索方案的逻辑
        # 比如使用百度搜索API等
        
        # 返回一些通用的游戏攻略网站
        return [
            {
                "title": "鸣潮 官方攻略",
                "url": "https://wiki.biligame.com/wuwa/",
                "content": "鸣潮维基百科 contains comprehensive game guides",
                "source": "bilibili-wiki"
            },
            {
                "title": "鸣潮 攻略 - TapTap",
                "url": "https://www.taptap.com/app/267761/topic",
                "content": "TapTap community guides",
                "source": "taptap"
            }
        ]
    
    def get_best_strategy(self) -> str:
        """获取最佳策略"""
        if not self.search_results:
            return ""
        
        # 按分数排序
        sorted_results = sorted(self.search_results, key=lambda x: x.get("score", 0), reverse=True)
        
        # 合并内容
        best = sorted_results[0]
        return f"{best.get('title', '')}\n{best.get('content', '')}\n来源: {best.get('url', '')}"
