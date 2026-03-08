"""
游戏控制器模块
使用 ok-script 控制游戏
"""
import asyncio
import os
import base64
from typing import Optional, Tuple
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


class GameController:
    """游戏控制器"""
    
    def __init__(self):
        self.window_handle = None
        self.process_name = os.getenv("GAME_PROCESS_NAME", "WuWa.exe")
        self.window_title = os.getenv("GAME_WINDOW_TITLE", "鸣潮")
        self.width = int(os.getenv("GAME_WIDTH", "1920"))
        self.height = int(os.getenv("GAME_HEIGHT", "1080"))
        
        # 尝试导入ok-script
        self.ok = None
        self._init_ok_script()
        
        logger.info(f"🎮 GameController 初始化, 进程: {self.process_name}")
    
    def _init_ok_script(self):
        """初始化ok-script"""
        try:
            import ok
            self.ok = ok
            logger.info("✅ ok-script 导入成功")
        except ImportError:
            logger.warning("⚠️ ok-script 未安装，将使用备用方案")
    
    async def connect(self) -> str:
        """
        连接游戏窗口
        
        Returns:
            连接状态
        """
        try:
            if self.ok:
                # 使用ok-script连接
                # 这里需要根据ok-script的实际API调整
                windows = self.ok.find_windows(self.window_title)
                if windows:
                    self.window_handle = windows[0]
                    logger.info(f"✅ 已连接到游戏窗口: {self.window_handle}")
                    return f"已连接: {self.window_handle}"
                else:
                    # 没找到窗口，使用模拟模式
                    logger.warning("⚠️ 未找到游戏窗口，启用模拟模式")
                    self.window_handle = "mock"
                    return "未找到游戏窗口，已启用模拟模式用于测试"
            else:
                # 没有ok-script，使用模拟模式
                logger.warning("⚠️ ok-script未安装，启用模拟模式")
                self.window_handle = "mock"
                return "ok-script未安装，已启用模拟模式"
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return f"连接失败: {str(e)}"
    
    async def screenshot(self) -> str:
        """
        截取游戏画面
        
        Returns:
            base64编码的图像
        """
        try:
            # 模拟模式 - 返回测试图片
            if self.window_handle == "mock":
                # 返回一个简单的测试图片（黑色背景+文字）
                from PIL import Image, ImageDraw, ImageFont
                import io
                
                img = Image.new('RGB', (1280, 720), color=(20, 20, 40))
                d = ImageDraw.Draw(img)
                d.text((500, 340), "WuwaAI 模拟模式", fill=(0, 217, 255))
                d.text((450, 380), "游戏未连接 - 这是测试画面", fill=(150, 150, 150))
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                img_bytes = buffer.getvalue()
                return base64.b64encode(img_bytes).decode()
            
            if self.ok and self.window_handle:
                # 使用ok-script截图
                img = self.ok.screenshot(self.window_handle)
                # 转为base64
                import io
                from PIL import Image
                
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG")
                img_bytes = buffer.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode()
                
                return img_base64
            else:
                logger.warning("⚠️ 无法截图: 未连接游戏")
                return ""
                
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return ""
    
    async def click(self, x: int, y: int) -> bool:
        """
        点击指定位置
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            是否成功
        """
        try:
            if self.ok and self.window_handle:
                self.ok.click(self.window_handle, x, y)
                logger.info(f"🖱️ 点击 ({x}, {y})")
                return True
            else:
                logger.warning("⚠️ 无法点击: 未连接游戏")
                return False
        except Exception as e:
            logger.error(f"❌ 点击失败: {e}")
            return False
    
    async def double_click(self, x: int, y: int) -> bool:
        """双击"""
        try:
            if self.ok and self.window_handle:
                self.ok.double_click(self.window_handle, x, y)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 双击失败: {e}")
            return False
    
    async def right_click(self, x: int, y: int) -> bool:
        """右键点击"""
        try:
            if self.ok and self.window_handle:
                self.ok.right_click(self.window_handle, x, y)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 右键失败: {e}")
            return False
    
    async def move(self, x: int, y: int) -> bool:
        """
        移动鼠标
        
        Args:
            x: X坐标
            y: Y坐标
        """
        try:
            if self.ok and self.window_handle:
                self.ok.move_to(self.window_handle, x, y)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 移动失败: {e}")
            return False
    
    async def input_text(self, text: str) -> bool:
        """
        输入文本
        
        Args:
            text: 要输入的文本
        """
        try:
            if self.ok and self.window_handle:
                self.ok.input(self.window_handle, text)
                logger.info(f"⌨️ 输入: {text}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 输入失败: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """
        按键
        
        Args:
            key: 键名 (如 "w", "a", "space", "enter")
        """
        try:
            if self.ok and self.window_handle:
                self.ok.press(self.window_handle, key)
                logger.info(f"⌨️ 按键: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 按键失败: {e}")
            return False
    
    async def drag(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        拖拽
        
        Args:
            x1, y1: 起点
            x2, y2: 终点
        """
        try:
            if self.ok and self.window_handle:
                self.ok.drag(self.window_handle, x1, y1, x2, y2)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 拖拽失败: {e}")
            return False
    
    async def wait(self, seconds: float) -> bool:
        """
        等待
        
        Args:
            seconds: 秒数
        """
        await asyncio.sleep(seconds)
        return True
    
    async def is_foreground(self) -> bool:
        """检查游戏窗口是否在前台"""
        try:
            if self.ok:
                return self.ok.is_foreground(self.window_handle)
            return False
        except:
            return False
    
    async def activate(self) -> bool:
        """激活游戏窗口"""
        try:
            if self.ok:
                self.ok.activate(self.window_handle)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 激活窗口失败: {e}")
            return False
