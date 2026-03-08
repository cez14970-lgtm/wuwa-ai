"""
游戏控制器模块
支持本地游戏和云游戏的截图和控制
"""
import asyncio
import os
import sys
import base64
import io
from typing import Optional
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)


class GameController:
    """游戏控制器 - 支持本地和云游戏"""
    
    def __init__(self):
        self.window_handle = None
        self._hwnd = None
        self.process_name = os.getenv("GAME_PROCESS_NAME", "Client-Win64-Shipping.exe")
        self.window_title = os.getenv("GAME_WINDOW_TITLE", "鸣潮")
        self.width = int(os.getenv("GAME_WIDTH", "1920"))
        self.height = int(os.getenv("GAME_HEIGHT", "1080"))
        
        # 游戏状态
        self._game_running = False
        self._is_cloud_game = False  # 是否是云游戏
        
        logger.info(f"🎮 GameController 初始化")
    
    async def connect(self) -> str:
        """连接游戏"""
        try:
            # 首先尝试本地Windows API
            result = await self._connect_local()
            if result and "未找到" not in result:
                self._game_running = True
                return result
            
            # 如果本地没找到，尝试云游戏模式
            self._is_cloud_game = True
            self._game_running = True
            logger.info("☁️ 检测到云游戏模式")
            return "云游戏模式已启用"
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            # 即使出错也启用模拟模式
            self._game_running = True
            return f"连接失败，启用演示模式: {str(e)}"
    
    async def _connect_local(self) -> Optional[str]:
        """连接本地游戏"""
        try:
            import win32gui
            
            # 按标题查找窗口
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and ("鸣潮" in title or "Wuthering" in title or "WuWa" in title):
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                self._hwnd = windows[0]
                title = win32gui.GetWindowText(self._hwnd)
                logger.info(f"✅ 已找到游戏窗口: {title}")
                return f"已连接: {title}"
            
            return None
            
        except ImportError:
            logger.warning("pywin32未安装")
            return None
        except Exception as e:
            logger.error(f"连接本地游戏失败: {e}")
            return None
    
    async def screenshot(self) -> str:
        """
        截取游戏画面
        
        Returns:
            base64编码的图像
        """
        try:
            # 云游戏模式 - 使用屏幕截图
            if self._is_cloud_game:
                return await self._screenshot_screen()
            
            # 本地游戏 - 尝试窗口截图
            result = await self._screenshot_window()
            if result:
                return result
            
            # 失败则用屏幕截图
            return await self._screenshot_screen()
            
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return await self._screenshot_demo()
    
    async def _screenshot_window(self) -> Optional[str]:
        """窗口截图"""
        try:
            import win32gui
            import win32ui
            import win32con
            from PIL import Image
            
            if not self._hwnd:
                return None
            
            # 获取窗口位置
            left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                return None
            
            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(self._hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # 截图
            import ctypes
            result = ctypes.windll.user32.BitBlt(
                saveDC.GetSafeHdc(), 0, 0, width, height,
                mfcDC.GetSafeHdc(), 0, 0, 0x00CC0020  # SRCCOPY
            )
            
            if result == 0:
                return None
            
            # 转为PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            
            # 转为base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # 清理
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, hwndDC)
            
            logger.info(f"✅ 窗口截图成功: {width}x{height}")
            return img_base64
            
        except Exception as e:
            logger.error(f"窗口截图失败: {e}")
            return None
    
    async def _screenshot_screen(self) -> str:
        """屏幕截图（支持云游戏）"""
        try:
            from PIL import Image, ImageGrab
            
            # 截取整个屏幕
            img = ImageGrab.grab()
            
            # 转为base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"✅ 屏幕截图成功: {img.size}")
            return img_base64
            
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return await self._screenshot_demo()
    
    async def _screenshot_demo(self) -> str:
        """演示模式图片"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建演示图片
            img = Image.new('RGB', (1280, 720), color=(20, 25, 40))
            d = ImageDraw.Draw(img)
            
            # 绘制游戏界面模拟
            # 顶部任务栏
            d.rectangle([0, 0, 1280, 60], fill=(30, 35, 50))
            d.text((20, 20), "☁️ WuwaAI 云游戏模式", fill=(0, 217, 255))
            
            # 中间主体
            d.rectangle([100, 100, 1180, 620], fill=(40, 45, 60))
            d.text((500, 350), "等待游戏画面...", fill=(150, 150, 150))
            d.text((450, 380), "请确保云游戏已开启", fill=(100, 100, 100))
            
            # 底部操作栏
            d.rectangle([0, 660, 1280, 720], fill=(30, 35, 50))
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            return base64.b64encode(buffer.getvalue()).decode()
            
        except Exception as e:
            logger.error(f"演示图片生成失败: {e}")
            return ""
    
    async def click(self, x: int, y: int) -> bool:
        """点击"""
        try:
            if self._is_cloud_game:
                # 云游戏：用pyautogui点击屏幕
                return await self._click_screen(x, y)
            else:
                # 本地游戏：用Windows API点击窗口
                return await self._click_window(x, y)
        except Exception as e:
            logger.error(f"❌ 点击失败: {e}")
            return False
    
    async def _click_screen(self, x: int, y: int) -> bool:
        """屏幕点击"""
        try:
            import pyautogui
            pyautogui.click(x, y)
            logger.info(f"🖱️ 屏幕点击 ({x}, {y})")
            return True
        except ImportError:
            # 备用：用Windows API
            return await self._click_window(x, y)
    
    async def _click_window(self, x: int, y: int) -> bool:
        """窗口点击"""
        try:
            import win32gui
            import win32api
            import win32con
            
            if not self._hwnd:
                return False
            
            # 设置前台窗口
            win32gui.SetForegroundWindow(self._hwnd)
            await asyncio.sleep(0.1)
            
            # 发送点击消息
            lparam = (y << 16) | x
            win32api.SendMessage(self._hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            await asyncio.sleep(0.05)
            win32api.SendMessage(self._hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            
            logger.info(f"🖱️ 窗口点击 ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"窗口点击失败: {e}")
            return False
    
    async def input_text(self, text: str) -> bool:
        """输入文本"""
        try:
            if self._is_cloud_game:
                import pyautogui
                pyautogui.typewrite(text, interval=0.05)
            else:
                import win32gui
                import win32api
                import win32con
                
                if self._hwnd:
                    win32gui.SetForegroundWindow(self._hwnd)
                    for char in text:
                        win32api.SendMessage(self._hwnd, win32con.WM_CHAR, ord(char), 0)
            
            logger.info(f"⌨️ 输入: {text}")
            return True
        except Exception as e:
            logger.error(f"❌ 输入失败: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """按键"""
        try:
            if self._is_cloud_game:
                import pyautogui
                key_map = {'w': 'w', 'a': 'a', 's': 's', 'd': 'd', 
                          'space': 'space', 'enter': 'enter', 'esc': 'esc'}
                pyautogui.press(key_map.get(key, key))
            else:
                import win32gui
                import win32api
                import win32con
                
                vk_map = {'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
                         'space': 0x20, 'enter': 0x0D, 'esc': 0x1B,
                         'tab': 0x09}
                
                vk = vk_map.get(key.lower(), 0)
                if vk and self._hwnd:
                    win32gui.SetForegroundWindow(self._hwnd)
                    win32api.SendMessage(self._hwnd, win32con.WM_KEYDOWN, vk, 0)
                    await asyncio.sleep(0.05)
                    win32api.SendMessage(self._hwnd, win32con.WM_KEYUP, vk, 0)
            
            logger.info(f"⌨️ 按键: {key}")
            return True
        except Exception as e:
            logger.error(f"❌ 按键失败: {e}")
            return False
    
    async def wait(self, seconds: float) -> bool:
        """等待"""
        await asyncio.sleep(seconds)
        return True
    
    async def is_foreground(self) -> bool:
        """检查游戏是否在前台"""
        try:
            import win32gui
            if self._hwnd:
                return win32gui.GetForegroundWindow() == self._hwnd
            return True  # 云游戏假定在前台
        except:
            return True
    
    async def activate(self) -> bool:
        """激活游戏窗口"""
        try:
            import win32gui
            if self._hwnd:
                win32gui.SetForegroundWindow(self._hwnd)
                return True
            return False
        except:
            return False
