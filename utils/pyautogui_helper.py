"""pyautogui 屏幕操作封装"""

import time

from core.logger import get_logger
from core.allure_reporter import allure

logger = get_logger("pyautogui")

# 延迟导入 pyautogui，避免未安装时报错
try:
    import pyautogui
    _has_pyautogui = True
except ImportError:
    pyautogui = None
    _has_pyautogui = False

try:
    import pyperclip
    _has_pyperclip = True
except ImportError:
    pyperclip = None
    _has_pyperclip = False


def _check():
    if not _has_pyautogui:
        raise ImportError("请先安装 pyautogui: pip install pyautogui")


def click_screen(x: int, y: int, label: str = "") -> bool:
    """在屏幕绝对坐标点击"""
    _check()
    if x <= 0 or y <= 0:
        logger.warning(f"点击坐标无效: ({x}, {y})")
        return False
    try:
        pyautogui.click(x, y)
        msg = f"已点击 [{label}] 屏幕坐标 ({x}, {y})"
        logger.info(msg)
        return True
    except Exception as e:
        logger.error(f"点击 [{label}] 失败: {e}")
        return False


def type_screen(x: int, y: int, text: str, label: str = "") -> bool:
    """在屏幕绝对坐标点击并输入（使用剪贴板粘贴）"""
    _check()
    if x <= 0 or y <= 0:
        logger.warning(f"输入坐标无效: ({x}, {y})")
        return False
    if not _has_pyperclip:
        logger.warning("pyperclip 未安装，将尝试直接输入")
        try:
            pyautogui.click(x, y)
            time.sleep(0.3)
            pyautogui.typewrite(text, interval=0.01)
            return True
        except Exception as e:
            logger.error(f"在 [{label}] 输入失败: {e}")
            return False

    try:
        pyautogui.click(x, y)
        time.sleep(0.3)
        original = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('v')
        pyautogui.keyUp('v')
        pyautogui.keyUp('ctrl')
        time.sleep(0.1)
        pyperclip.copy(original)
        logger.info(f"已在 [{label}] 输入: {text}")
        return True
    except Exception as e:
        logger.error(f"在 [{label}] 输入失败: {e}")
        return False


def clear_and_type_screen(x: int, y: int, text: str, label: str = "") -> bool:
    """先清空输入框（Ctrl+A 全选后输入），再输入新内容"""
    _check()
    if x <= 0 or y <= 0:
        logger.warning(f"输入坐标无效: ({x}, {y})")
        return False
    try:
        pyautogui.click(x, y)
        time.sleep(0.3)
        # 全选原有内容
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('a')
        pyautogui.keyUp('a')
        pyautogui.keyUp('ctrl')
        time.sleep(0.1)
        # 直接输入新内容（覆盖选中内容）
        pyautogui.typewrite(text, interval=0.01)
        time.sleep(0.1)
        logger.info(f"已在 [{label}] 清空并输入: {text}")
        return True
    except Exception as e:
        logger.error(f"在 [{label}] 清空输入失败: {e}")
        return False


def swipe_down(start_x: int, start_y: int, distance: int = 200, duration: float = 0.5, label: str = "") -> bool:
    """长按下滑：在指定坐标按下，向下滑动指定距离后松开

    Args:
        start_x: 起始位置 x 坐标
        start_y: 起始位置 y 坐标
        distance: 向下滑动的距离（像素）
        duration: 滑动耗时（秒）
        label: 操作描述（用于日志）
    """
    _check()
    if start_x <= 0 or start_y <= 0:
        logger.warning(f"滑动起始坐标无效: ({start_x}, {start_y})")
        return False
    try:
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(start_x, start_y + distance, duration=duration)
        pyautogui.mouseUp()
        logger.info(f"已长按下滑 [{label}] 从 ({start_x}, {start_y}) 滑动 {distance}px")
        return True
    except Exception as e:
        logger.error(f"长按下滑 [{label}] 失败: {e}")
        return False


def take_screenshot(filename: str = "screenshot.png") -> str:
    """全屏截图"""
    _check()
    from config.settings import SCREENSHOT_DIR
    import os
    path = os.path.join(SCREENSHOT_DIR, filename)
    try:
        pyautogui.screenshot(path)
        logger.info(f"全屏截图: {path}")
        allure.attach_screenshot(filename, path)
        return path
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return ""
