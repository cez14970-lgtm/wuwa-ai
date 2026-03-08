"""
记忆模块
记录历史交互，避免重复尝试失败的方案
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


class Memory:
    """游戏记忆模块"""
    
    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.history: List[Dict[str, Any]] = []
        self.failed_solutions: Dict[str, int] = {}  # 方案 -> 失败次数
        
        # 存储路径
        self.storage_path = Path(__file__).parent.parent.parent / "data" / "memory.json"
        self._ensure_storage_path()
        self._load()
        
        logger.info(f"🧠 Memory 初始化完成, 已加载 {len(self.history)} 条历史记录")
    
    def _ensure_storage_path(self):
        """确保存储目录存在"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """加载历史记录"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.failed_solutions = data.get('failed_solutions', {})
                    logger.info(f"已加载 {len(self.history)} 条历史记录")
        except Exception as e:
            logger.warning(f"加载历史记录失败: {e}")
    
    def _save(self):
        """保存历史记录"""
        try:
            data = {
                'history': self.history[-self.max_items:],  # 只保留最近的
                'failed_solutions': self.failed_solutions
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def record(self, solution: Dict[str, Any], result: Dict[str, Any]):
        """
        记录一次交互
        
        Args:
            solution: 解决方案
            result: 执行结果
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "solution": solution,
            "result": result,
            "success": result.get("success", False)
        }
        
        self.history.append(entry)
        
        # 如果失败，记录失败的方案
        if not result.get("success"):
            problem = solution.get("problem_description", "")
            if problem:
                self.failed_solutions[problem] = self.failed_solutions.get(problem, 0) + 1
        
        # 限制历史长度并保存
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items:]
        self._save()
        
        logger.info(f"📝 已记录: success={result.get('success')}")
    
    def get_recent(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        获取最近的历史记录
        
        Args:
            count: 获取数量
            
        Returns:
            历史记录列表
        """
        return self.history[-count:] if self.history else []
    
    def get_failed_solutions(self, problem: str) -> int:
        """
        获取某个问题失败的次数
        
        Args:
            problem: 问题描述
            
        Returns:
            失败次数
        """
        return self.failed_solutions.get(problem, 0)
    
    def should_try_again(self, problem: str, max_attempts: int = 3) -> bool:
        """
        判断是否应该再次尝试
        
        Args:
            problem: 问题描述
            max_attempts: 最大尝试次数
            
        Returns:
            是否应该尝试
        """
        return self.get_failed_solutions(problem) < max_attempts
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取记忆摘要
        
        Returns:
            摘要信息
        """
        total = len(self.history)
        success = sum(1 for h in self.history if h.get("success"))
        
        return {
            "total_interactions": total,
            "success_count": success,
            "fail_count": total - success,
            "success_rate": f"{(success/total*100):.1f}%" if total > 0 else "N/A",
            "failed_problems": len(self.failed_solutions)
        }
    
    def clear(self):
        """清空历史记录"""
        self.history = []
        self.failed_solutions = {}
        self._save()
        logger.info("🧠 历史记录已清空")
