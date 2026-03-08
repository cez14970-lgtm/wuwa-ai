"""
游戏控制器模块
使用 Windows API 控制游戏窗口截图和点击
"""
import asyncio
import os
import sys
import base64
import io
from typing import Optional, Tuple
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

logger = get_logger(__name__)


class GameController:
    """游戏控制器 - Windows API 实现"""
    
    # 鸣潮的游戏进程名
    GAME_PROCESS_NAMES = [
        "Client-Win64-Shipping.exe",  # 正式版
        "WuWa.exe",                   # 可能的其他名称
        "Wuthering Waves.exe",       # 可能的其他名称
    ]
    
    # 窗口类名 (Unreal Engine游戏)
    WINDOW_CLASS_NAMES = [
        "UnrealWindow",
        "UnityWndClass",
        "Warcraft III",
    ]
    
    def __init__(self):
        self.window_handle = None
        self.process_name = os.getenv("GAME_PROCESS_NAME", "Client-Win64-Shipping.exe")
        self.window_title = os.getenv("GAME_WINDOW_TITLE", "鸣潮")
        self.width = int(os.getenv("GAME_WIDTH", "1920"))
        self.height = int(os.getenv("GAME_HEIGHT", "1080"))
        
        # Windows API 句柄
        self._hwnd = None
        self._game_running = False
        
        logger.info(f"🎮 GameController 初始化, 目标进程: {self.process_name}")
    
    def _init_windows_api(self):
        """初始化Windows API"""
        try:
            # 尝试导入 pywin32
            import win32gui
            import win32ui
            import win32con
            import win32api
            from PIL import Image
            return True
        except ImportError:
            logger.warning("⚠️ pywin32 未安装，尝试其他方案")
            return False
    
    async def connect(self) -> str:
        """
        连接游戏窗口
        
        Returns:
            连接状态
        """
        try:
            # 尝试使用多种方法连接
            result = await self._connect_windows()
            if result:
                self._game_running = True
                return result
            
            # 如果上面的方法失败，尝试查找进程
            result = await self._find_game_process()
            return result
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return f"连接失败: {str(e)}"
    
    async def _connect_windows(self) -> str:
        """使用Windows API连接"""
        try:
            import win32gui
            import win32con
            
            # 方法1: 按窗口标题查找
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
            
            # 方法2: 按类名查找
            for class_name in self.WINDOW_CLASS_NAMES:
                hwnd = win32gui.FindWindow(class_name, None)
                if hwnd:
                    self._hwnd = hwnd
                    title = win32gui.GetWindowText(hwnd)
                    logger.info(f"✅ 已找到游戏窗口(类名): {title}")
                    return f"已连接: {title}"
            
            return None
            
        except ImportError:
            return "需要安装 pywin32: pip install pywin32"
        except Exception as e:
            logger.error(f"Windows API错误: {e}")
            return None
    
    async def _find_game_process(self) -> str:
        """查找游戏进程"""
        try:
            import psutil
            
            # 遍历进程列表
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    name = proc.info['name']
                    if name in self.GAME_PROCESS_NAMES:
                        logger.info(f"✅ 找到游戏进程: {name} (PID: {proc.pid})")
                        self._game_running = True
                        return f"找到游戏进程: {name} (PID: {proc.pid})"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 如果没找到，尝试常见游戏进程名
            common_names = ["Client-Win64-Shipping", "WuWa", "Wuthering"]
            for name in common_names:
                for proc in psutil.process_iter(['name']):
                    try:
                        if name.lower() in proc.info['name'].lower():
                            logger.info(f"✅ 找到类似进程: {proc.info['name']}")
                            self._game_running = True
                            return f"找到游戏进程: {proc.info['name']}"
                    except:
                        continue
            
            return "未找到游戏进程，请确保游戏已启动"
            
        except ImportError:
            # 尝试用命令行查找
            import subprocess
            try:
                result = subprocess.run(
                    'tasklist | findstr "Client WuWa Wuthering"',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    logger.info(f"✅ 找到进程: {result.stdout}")
                    self._game_running = True
                    return f"找到游戏进程: {result.stdout.strip()}"
            except:
                pass
            
            return "未找到游戏进程，请确保游戏已启动"
    
    async def screenshot(self) -> str:
        """
        截取游戏画面
        
        Returns:
            base64编码的图像
        """
        try:
            # 先尝试Windows API截图
            result = await self._screenshot_windows()
            if result:
                return result
            
            # 如果失败，返回模拟图片提示用户
            return await self._screenshot_fallback()
            
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return await self._screenshot_fallback()
    
    async def _screenshot_windows(self) -> Optional[str]:
        """使用Windows API截图"""
        try:
            import win32gui
            import win32ui
            import win32con
            from PIL import Image
            
            if not self._hwnd:
                # 尝试重新连接
                await self._connect_windows()
                if not self._hwnd:
                    return None
            
            # 获取窗口位置
            left, top, right, bottom = win32gui.GetWindowRect(self._hwnd)
            width = right - left
            height = bottom - top
            
            # 创建设备上下文
            hwndDC = win32gui.GetWindowDC(self._hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # 创建位图
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # 截图
            result = win32gui.BitBlt(
                saveDC.GetSafeHdc(), 0, 0, width, height,
                mfcDC.GetSafeHdc(), 0, 0,
                win32con.SRCCOPY
            )
            
            if result == 0:
                # 截图失败
                return None
            
            # 转为PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # 转为base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode()
            
            # 清理
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self._hwnd, hwndDC)
            
            logger.info(f"✅ 截图成功: {width}x{height}")
            return img_base64
            
        except Exception as e:
            logger.error(f"Windows截图失败: {e}")
            return None
    
    async def _screenshot_fallback(self) -> str:
        """备用截图方案"""
        try:
            from PIL import Image, ImageDraw
            
            # 创建提示图片
            img = Image.new('RGB', (1280, 720), color=(30, 30, 50))
            d = ImageDraw.Draw(img)
            
            d.text((440, 300), "等待连接游戏...", fill=(200, 200, 200))
            d.text((400, 340), f"请确保 '{self.process_name}' 已启动", fill=(150, 150, 150))
            
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=80)
            return base64.b64encode(buffer.getvalue()).decode()
        except:
            return ""
    
    async def click(self, x: int, y: int) -> bool:
        """
        点击指定位置
        
        Args:
            x: X坐标 (相对于窗口)
            y: Y坐标 (相对于窗口)
            
        Returns:
            是否成功
        """
        try:
            import win32gui
            import win32api
            import win32con
            
            if not self._hwnd:
                logger.warning("⚠️ 未连接游戏窗口")
                return False
            
            # 将坐标转为屏幕坐标
            # 先获取窗口当前位置
            win32gui.SetForegroundWindow(self._hwnd)
            await asyncio.sleep(0.1)
            
            # 发送鼠标点击
            win32api.SendMessage(
                self._hwnd,
                win32con.WM_LBUTTONDOWN,
                win32con.MK_LBUTTON,
                (y << 16) | x
            )
            await asyncio.sleep(0.05)
            win32api.SendMessage(
                self._hwnd,
                win32con.WM_LBUTTONUP,
                0,
                (y << 16) | x
            )
            
            logger.info(f"🖱️ 点击 ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 点击失败: {e}")
            return False
    
    async def input_text(self, text: str) -> bool:
        """输入文本"""
        try:
            import win32gui
            import win32api
            
            if not self._hwnd:
                return False
            
            win32gui.SetForegroundWindow(self._hwnd)
            
            # 逐字符输入
            for char in text:
                win32api.SendMessage(self._hwnd, win32con.WM_CHAR, ord(char), 0)
                await asyncio.sleep(0.05)
            
            logger.info(f"⌨️ 输入: {text}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 输入失败: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """按键"""
        try:
            import win32gui
            import win32api
            import win32con
            
            if not self._hwnd:
                return False
            
            # 虚拟键码映射
            key_map = {
                'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
                'space': 0x20, 'enter': 0x0D, 'esc': 0x1B,
                'tab': 0x09, 'shift': 0x10, 'ctrl': 0x11,
            }
            
            vk = key_map.get(key.lower(), 0)
            if vk:
                win32api.SendMessage(self._hwnd, win32con.WM_KEYDOWN, vk, 0)
                await asyncio.sleep(0.05)
                win32api.SendMessage(self._hwnd, win32con.WM_KEYUP, vk, 0)
                logger.info(f"⌨️ 按键: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 按键失败: {e}")
            return False
    
    async def wait(self, seconds: float) -> bool:
        """等待"""
        await asyncio.sleep(seconds)
        return True
    
    async def is_foreground(self) -> bool:
        """检查游戏窗口是否在前台"""
        try:
            import win32gui
            if self._hwnd:
                return win32gui.GetForegroundWindow() == self._hwnd
            return False
        except:
            return False
    
    async def activate(self) -> bool:
        """激活游戏窗口"""
        try:
            import win32gui
            if self._hwnd:
                win32gui.SetForegroundWindow(self._hwnd)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 激活窗口失败: {e}")
            return False
