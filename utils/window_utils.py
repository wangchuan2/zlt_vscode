"""Windows 窗口操作工具"""

import sys
import time

from core.logger import get_logger

logger = get_logger("window")

# 尝试导入 ctypes
try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None


def find_vscode_window() -> int:
    """通过窗口标题和类名查找 VS Code 主窗口，返回 hwnd"""
    if ctypes is None:
        return 0

    found_hwnd = ctypes.c_void_p(0)

    def enum_callback(hwnd, extra):
        nonlocal found_hwnd
        if found_hwnd.value:
            return True
        if not ctypes.windll.user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
        if "Chrome_WidgetWin" not in buf.value:
            return True
        title_buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(hwnd, title_buf, 512)
        if "Visual Studio Code" in title_buf.value:
            found_hwnd.value = hwnd
            return False
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
    return found_hwnd.value or 0


def set_window_pos(hwnd: int, x: int, y: int, width: int, height: int) -> bool:
    """使用 Windows API 设置窗口位置和大小"""
    if ctypes is None:
        logger.warning("ctypes 不可用，无法设置窗口位置")
        return False

    if ctypes.windll.user32.IsWindow(ctypes.c_void_p(hwnd)) == 0:
        logger.warning(f"hwnd={hwnd} 不是有效窗口")
        return False

    SW_SHOWNORMAL = 1
    ctypes.windll.user32.ShowWindow(ctypes.c_void_p(hwnd), ctypes.c_int(SW_SHOWNORMAL))

    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    flags = SWP_NOZORDER | SWP_SHOWWINDOW

    result = ctypes.windll.user32.SetWindowPos(
        ctypes.c_void_p(hwnd),
        ctypes.c_void_p(0),
        ctypes.c_int(x),
        ctypes.c_int(y),
        ctypes.c_int(width),
        ctypes.c_int(height),
        ctypes.c_uint(flags),
    )
    if result == 0:
        err = ctypes.windll.kernel32.GetLastError()
        logger.warning(f"SetWindowPos 失败，hwnd={hwnd}, GetLastError={err}")
        return False
    return True
