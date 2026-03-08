"""
WuwaAI - 鸣潮智能自动化
真正可用的版本 - 基于ok-ww架构设计

版本: 2.0.0
"""
import os
import sys
import asyncio
import time
import base64
import io
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / "backend" / ".env")


# ==================== 配置 ====================

class Config:
    """配置"""
    # 游戏配置
    GAME_PROCESS_NAME = os.getenv("GAME_PROCESS_NAME", "Client-Win64-Shipping.exe")
    GAME_WINDOW_TITLE = os.getenv("GAME_WINDOW_TITLE", "鸣潮")
    
    # 云游戏配置
    IS_CLOUD_GAME = True  # 用户使用云游戏
    
    # 截图配置
    SCREENSHOT_QUALITY = 80
    
    # 任务配置
    TASK_INTERVAL = 0.5  # 任务检测间隔(秒)
    CLICK_INTERVAL = 0.2  # 点击间隔(秒)


# ==================== 基础类 ====================

class Box:
    """检测到的区域"""
    def __init__(self, x: int, y: int, width: int, height: int, confidence: float = 1.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.confidence = confidence
    
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def click_point(self) -> Tuple[int, int]:
        """返回点击中心点"""
        cx, cy = self.center()
        # 添加随机偏移避免检测
        import random
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        return (cx + offset_x, cy + offset_y)
    
    def __repr__(self):
        return f"Box(x={self.x}, y={self.y}, w={self.width}, h={self.height}, conf={self.confidence:.2f})"


class GameScene(Enum):
    """游戏场景"""
    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    LOADING = "loading"
    OPEN_WORLD = "open_world"  # 开放世界
    COMBAT = "combat"          # 战斗
    DIALOG = "dialog"          # 对话
    MENU = "menu"              # 菜单
    BLACK = "black"            # 黑屏


# ==================== 截图模块 ====================

class Screenshot:
    """截图模块 - 支持云游戏和本地游戏"""
    
    def __init__(self, is_cloud: bool = True):
        self.is_cloud = is_cloud
        self._last_screenshot = None
    
    def capture(self) -> Optional[Any]:
        """截取屏幕"""
        try:
            from PIL import Image, ImageGrab
            
            if self.is_cloud:
                # 云游戏：截取整个屏幕
                img = ImageGrab.grab()
            else:
                # 本地游戏：截取游戏窗口
                import win32gui
                import win32ui
                import win32con
                
                # 查找窗口
                hwnd = win32gui.FindWindow(None, Config.GAME_WINDOW_TITLE)
                if not hwnd:
                    return None
                
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                hwndDC = win32gui.GetWindowDC(hwnd)
                mfcDC = win32ui.CreateDCFromHandle(hwndDC)
                saveDC = mfcDC.CreateCompatibleDC()
                
                saveBitMap = win32ui.CreateBitmap()
                saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
                saveDC.SelectObject(saveBitMap)
                
                import ctypes
                ctypes.windll.user32.BitBlt(saveDC.GetSafeHdc(), 0, 0, width, height,
                                           mfcDC.GetSafeHdc(), 0, 0, 0x00CC0020)
                
                bmpinfo = saveBitMap.GetInfo()
                bmpstr = saveBitMap.GetBitmapBits(True)
                img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), 
                                      bmpstr, 'raw', 'BGRX', 0, 1)
                
                win32gui.DeleteObject(saveBitMap.GetHandle())
                saveDC.DeleteDC()
                mfcDC.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwndDC)
            
            self._last_screenshot = img
            return img
            
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def to_base64(self, img=None) -> str:
        """转为base64"""
        if img is None:
            img = self._last_screenshot
        if img is None:
            return ""
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=Config.SCREENSHOT_QUALITY)
        return base64.b64encode(buffer.getvalue()).decode()
    
    def save(self, path: str, img=None):
        """保存图片"""
        if img is None:
            img = self._last_screenshot
        if img:
            img.save(path)


# ==================== 元素检测模块 ====================

class ElementDetector:
    """元素检测 - 模板匹配 + OCR + 颜色"""
    
    def __init__(self, screenshot: Screenshot):
        self.screenshot = screenshot
        self._template_cache = {}
    
    def find_template(self, template_name: str, threshold: float = 0.8) -> Optional[Box]:
        """模板匹配查找元素"""
        import cv2
        import numpy as np
        
        # 截图
        screenshot_img = self.screenshot.capture()
        if screenshot_img is None:
            return None
        
        # 转为灰度图
        screenshot_gray = cv2.cvtColor(np.array(screenshot_img), cv2.COLOR_RGB2GRAY)
        
        # 加载模板（需要提前准备模板图片）
        template = self._load_template(template_name)
        if template is None:
            return None
        
        template_gray = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2GRAY)
        
        # 模板匹配
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            return Box(max_loc[0], max_loc[1], 
                      template.width, template.height, max_val)
        return None
    
    def find_all_template(self, template_name: str, threshold: float = 0.8) -> List[Box]:
        """查找所有匹配的元素"""
        import cv2
        import numpy as np
        
        screenshot_img = self.screenshot.capture()
        if screenshot_img is None:
            return []
        
        screenshot_gray = cv2.cvtColor(np.array(screenshot_img), cv2.COLOR_RGB2GRAY)
        template = self._load_template(template_name)
        if template is None:
            return []
        
        template_gray = cv2.cvtColor(np.array(template), cv2.COLOR_RGB2GRAY)
        
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        locations = np.where(result >= threshold)
        boxes = []
        
        h, w = template_gray.shape
        for pt in zip(*locations[::-1]):
            boxes.append(Box(pt[0], pt[1], w, h, result[pt[1], pt[0]]))
        
        return boxes
    
    def detect_color_region(self, x1: int, y1: int, x2: int, y2: int, 
                           color_range: dict) -> float:
        """检测颜色区域占比"""
        import cv2
        import numpy as np
        
        screenshot_img = self.screenshot.capture()
        if screenshot_img is None:
            return 0.0
        
        # 裁剪区域
        img_array = np.array(screenshot_img)
        region = img_array[y1:y2, x1:x2]
        
        # 检查每个通道的颜色范围
        h, w, c = region.shape
        mask = np.ones((h, w), dtype=bool)
        
        for i, channel in enumerate(['r', 'g', 'b']):
            if channel in color_range:
                min_val, max_val = color_range[channel]
                channel_data = region[:, :, i]
                mask &= (channel_data >= min_val) & (channel_data <= max_val)
        
        return np.sum(mask) / (h * w)
    
    def ocr_read(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """OCR文字识别"""
        try:
            import easyocr
            
            screenshot_img = self.screenshot.capture()
            if screenshot_img is None:
                return ""
            
            # 裁剪区域
            region = screenshot_img.crop((x1, y1, x2, y2))
            
            # OCR
            reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            results = reader.readtext(np.array(region))
            
            # 合并文字
            text = " ".join([result[1] for result in results])
            return text
            
        except Exception as e:
            print(f"OCR失败: {e}")
            return ""
    
    def detect_scene(self) -> GameScene:
        """检测当前场景"""
        # 通过颜色检测判断场景
        
        # 1. 检测黑屏
        black_ratio = self.detect_color_region(0, 0, 1920, 1080, 
                                               {'r': (0, 30), 'g': (0, 30), 'b': (0, 30)})
        if black_ratio > 0.9:
            return GameScene.BLACK
        
        # 2. 检测对话框（屏幕底部中央的白色区域）
        dialog_ratio = self.detect_color_region(400, 800, 1520, 1000,
                                                 {'r': (200, 255), 'g': (200, 255), 'b': (200, 255)})
        if dialog_ratio > 0.3:
            return GameScene.DIALOG
        
        # 3. 检测开放世界（天空的蓝色）
        sky_ratio = self.detect_color_region(0, 0, 1920, 400,
                                              {'r': (100, 180), 'g': (150, 220), 'b': (200, 255)})
        if sky_ratio > 0.3:
            return GameScene.OPEN_WORLD
        
        return GameScene.UNKNOWN
    
    def _load_template(self, name: str):
        """加载模板图片"""
        if name in self._template_cache:
            return self._template_cache[name]
        
        # 模板路径
        template_dir = project_root / "templates"
        template_path = template_dir / f"{name}.png"
        
        if not template_path.exists():
            print(f"模板不存在: {template_path}")
            return None
        
        from PIL import Image
        template = Image.open(template_path)
        self._template_cache[name] = template
        return template


# ==================== 操作模块 ====================

class Controller:
    """操作模块 - 点击、按键"""
    
    def __init__(self, is_cloud: bool = True):
        self.is_cloud = is_cloud
    
    def click(self, x: int, y: int):
        """点击"""
        try:
            import pyautogui
            pyautogui.click(x, y)
            print(f"点击: ({x}, {y})")
        except Exception as e:
            print(f"点击失败: {e}")
    
    def click_box(self, box: Box):
        """点击区域"""
        cx, cy = box.click_point()
        self.click(cx, cy)
    
    def right_click(self, x: int, y: int):
        """右键点击"""
        try:
            import pyautogui
            pyautogui.click(x, y, button='right')
        except:
            pass
    
    def press_key(self, key: str):
        """按键"""
        try:
            import pyautogui
            pyautogui.press(key)
            print(f"按键: {key}")
        except Exception as e:
            print(f"按键失败: {e}")
    
    def hold_key(self, key: str, duration: float):
        """按住按键"""
        try:
            import pyautogui
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
        except:
            pass
    
    def type_text(self, text: str):
        """输入文本"""
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.05)
        except:
            pass


# ==================== 任务模块 ====================

class BaseTask:
    """任务基类"""
    
    def __init__(self, detector: ElementDetector, controller: Controller):
        self.detector = detector
        self.controller = controller
        self.running = False
    
    def run(self):
        """执行任务 - 子类实现"""
        raise NotImplementedError
    
    def start(self):
        """开始任务"""
        self.running = True
        print(f"任务开始: {self.__class__.__name__}")
    
    def stop(self):
        """停止任务"""
        self.running = False
        print(f"任务停止: {self.__class__.__name__}")


class SkipDialogTask(BaseTask):
    """跳过对话任务"""
    
    def run(self):
        """执行跳过对话"""
        scene = self.detector.detect_scene()
        
        if scene == GameScene.DIALOG:
            # 检测到对话框
            
            # 方法1: 按空格跳过
            self.controller.press_key('space')
            time.sleep(0.3)
            
            # 方法2: 检测跳过按钮
            skip_btn = self.detector.find_template('skip_dialog', threshold=0.7)
            if skip_btn:
                self.controller.click_box(skip_btn)
                time.sleep(0.3)
            
            # 方法3: 点击屏幕右下角（通常是对话继续按钮）
            self.controller.click(1800, 900)
            
            return True
        
        return False


class AutoExploreTask(BaseTask):
    """自动探索任务"""
    
    def run(self):
        """执行自动探索"""
        scene = self.detector.detect_scene()
        
        if scene == GameScene.OPEN_WORLD:
            # 开放世界：自动移动
            
            # 按住W前进
            self.controller.hold_key('w', 1.0)
            time.sleep(0.5)
            
            # 随机跳跃
            import random
            if random.random() > 0.7:
                self.controller.press_key('space')
                time.sleep(0.3)
            
            # 检测互动键
            f_key = self.detector.find_template('interact_f', threshold=0.7)
            if f_key:
                self.controller.press_key('f')
                time.sleep(0.5)
            
            return True
        
        return False


class AutoCombatTask(BaseTask):
    """自动战斗任务"""
    
    def run(self):
        """执行自动战斗"""
        scene = self.detector.detect_scene()
        
        if scene == GameScene.COMBAT:
            # 战斗：自动攻击
            
            # 普通攻击
            self.controller.click(960, 540)
            time.sleep(0.2)
            
            # 技能
            self.controller.press_key('q')
            time.sleep(0.3)
            self.controller.press_key('e')
            time.sleep(0.3)
            self.controller.press_key('r')
            time.sleep(0.3)
            
            # 闪避
            self.controller.press_key('shift')
            time.sleep(0.2)
            
            return True
        
        return False


# ==================== 主控制器 ====================

class WuwaAI:
    """WuwaAI 主控制器"""
    
    def __init__(self, is_cloud: bool = True):
        self.is_cloud = is_cloud
        
        # 初始化各模块
        self.screenshot = Screenshot(is_cloud)
        self.detector = ElementDetector(self.screenshot)
        self.controller = Controller(is_cloud)
        
        # 任务
        self.tasks = {
            'skip_dialog': SkipDialogTask(self.detector, self.controller),
            'explore': AutoExploreTask(self.detector, self.controller),
            'combat': AutoCombatTask(self.detector, self.controller),
        }
        
        self.running = False
        self.current_task = None
    
    def connect(self) -> str:
        """连接游戏"""
        # 测试截图
        img = self.screenshot.capture()
        if img:
            return f"连接成功! 截图大小: {img.size}"
        return "连接失败: 无法截取屏幕"
    
    def get_screenshot_base64(self) -> str:
        """获取截图base64"""
        return self.screenshot.to_base64()
    
    def start_task(self, task_name: str):
        """开始任务"""
        if task_name in self.tasks:
            self.current_task = task_name
            self.tasks[task_name].start()
            self.running = True
    
    def stop_task(self):
        """停止任务"""
        if self.current_task:
            self.tasks[self.current_task].stop()
        self.running = False
        self.current_task = None
    
    def execute_once(self):
        """执行一次任务检测和执行"""
        if not self.running or not self.current_task:
            return
        
        task = self.tasks.get(self.current_task)
        if task:
            task.run()
    
    def get_status(self) -> dict:
        """获取状态"""
        return {
            "running": self.running,
            "current_task": self.current_task,
            "scene": self.detector.detect_scene().value
        }


# ==================== 测试 ====================

if __name__ == "__main__":
    # 测试
    ai = WuwaAI(is_cloud=True)
    
    print("连接游戏...")
    result = ai.connect()
    print(result)
    
    print("\n获取截图...")
    img_base64 = ai.get_screenshot_base64()
    print(f"截图长度: {len(img_base64)}")
    
    print("\n检测场景...")
    scene = ai.detector.detect_scene()
    print(f"当前场景: {scene.value}")
    
    print("\n开始自动探索...")
    ai.start_task('explore')
    
    # 运行一段时间
    for i in range(10):
        ai.execute_once()
        time.sleep(1)
    
    ai.stop_task()
    print("测试完成")
