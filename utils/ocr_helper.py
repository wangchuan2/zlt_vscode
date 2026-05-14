"""OCR 辅助工具：区域截图 + 文本识别"""

import os
import re
import sys
from pathlib import Path
from typing import Optional

from core.logger import get_logger

logger = get_logger("ocr")

# 延迟导入，避免未安装时报错
try:
    import pytesseract
    from PIL import Image
    _has_tesseract = True
except ImportError:
    pytesseract = None
    Image = None
    _has_tesseract = False


# Windows 常见安装路径 + 自定义路径
_WINDOWS_PATHS = [
    r"E:\ocr\tesseract.exe",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def _auto_find_tesseract() -> Optional[str]:
    """自动发现 Tesseract 可执行文件路径"""
    if sys.platform == "win32":
        for path in _WINDOWS_PATHS:
            if os.path.isfile(path):
                return path
    return None


def setup_tesseract(path: Optional[str] = None) -> bool:
    """配置 Tesseract 路径

    Args:
        path: 手动指定 tesseract.exe 路径，None 则自动查找

    Returns:
        是否配置成功
    """
    if not _has_tesseract:
        return False

    if path:
        pytesseract.pytesseract.tesseract_cmd = path
        return True

    found = _auto_find_tesseract()
    if found:
        pytesseract.pytesseract.tesseract_cmd = found
        logger.info(f"自动发现 Tesseract: {found}")
        return True

    return False


def _check():
    if not _has_tesseract:
        raise ImportError(
            "OCR 依赖未安装，请执行: pip install pytesseract Pillow\n"
            "并安装 Tesseract-OCR 引擎: https://github.com/UB-Mannheim/tesseract/wiki"
        )

    # 尝试自动配置路径
    if not setup_tesseract():
        current = getattr(pytesseract.pytesseract, 'tesseract_cmd', 'tesseract')
        if not os.path.isfile(current):
            raise ImportError(
                "Tesseract-OCR 引擎未找到。请执行以下步骤之一:\n"
                "1. 将 Tesseract 加入系统 PATH\n"
                "2. 或在代码中指定路径: setup_tesseract(r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')\n"
                "下载地址: https://github.com/UB-Mannheim/tesseract/wiki"
            )


def recognize_region(
    region: tuple[int, int, int, int],
    lang: str = "eng",
    preprocess: bool = True,
) -> str:
    """截取屏幕指定区域并进行 OCR 识别

    Args:
        region: (left, top, width, height) 截图区域
        lang: Tesseract 语言包，默认 chi_sim+eng（中文简体+英文）
        preprocess: 是否进行图像预处理（灰度化+二值化）以提高识别率

    Returns:
        识别出的文本字符串
    """
    _check()
    import pyautogui
    from datetime import datetime
    from config.settings import SCREENSHOT_DIR
    import os

    # 1. 区域截图
    screenshot = pyautogui.screenshot(region=region)
    logger.debug(f"区域截图: {region}")

    # 保存截图（调试用，每次进度截图）
    ts = datetime.now().strftime("%H%M%S_%f")[:9]
    # raw_path = os.path.join(SCREENSHOT_DIR, f"ocr_raw_{ts}.png")
    # screenshot.save(raw_path)

    # 2. 图像预处理
    processed = screenshot
    if preprocess:
        processed = screenshot.convert("L")
        # 保存预处理后截图
        proc_path = os.path.join(SCREENSHOT_DIR, f"ocr_proc_{ts}.png")
        processed.save(proc_path)

    # 3. OCR 识别
    w, h = processed.size
    if w < 100 or h < 50:
        processed = processed.resize((w * 3, h * 3), Image.LANCZOS)

    # 尝试多种 config 组合
    configs = [
        "--psm 7 -c tessedit_char_whitelist=0123456789%",
        "--psm 7",
        "",
    ]
    text = ""
    for i, cfg in enumerate(configs):
        try:
            text = pytesseract.image_to_string(processed, lang=lang, config=cfg)
            if text.strip():
                break
        except Exception:
            pass

    cleaned = text.strip().replace(" ", "").replace("\n", "")
    logger.info(f"OCR 识别结果: '{cleaned}'")
    return cleaned


def extract_percentage(text: str) -> Optional[float]:
    """从 OCR 文本中提取百分比数字

    支持的格式：
      - "100%" → 100.0
      - "50%"  → 50.0
      - "进度:75" → 75.0
      - "75/100" → 75.0

    Returns:
        提取到的百分比数值，未找到返回 None
    """
    # 匹配 xx% 格式
    m = re.search(r"(\d+(?:\.\d+)?)%", text)
    if m:
        return float(m.group(1))

    # 匹配 进度:75 或 75% 中的数字
    m = re.search(r"(?:进度|完成|progress)?[:\s]*(\d+(?:\.\d+)?)", text, re.I)
    if m:
        val = float(m.group(1))
        if 0 <= val <= 100:
            return val

    # 匹配 x/y 格式（如 75/100）
    m = re.search(r"(\d+)/(\d+)", text)
    if m:
        num, den = int(m.group(1)), int(m.group(2))
        if den > 0:
            return (num / den) * 100

    return None


def is_progress_complete(text: str, threshold: float = 100.0) -> bool:
    """判断 OCR 文本是否表示进度已完成"""
    # 直接匹配 "100%" 或 "完成"
    if re.search(r"100\s*%", text):
        return True
    if "完成" in text or "已完成" in text:
        return True

    # 提取百分比判断
    pct = extract_percentage(text)
    if pct is not None and pct >= threshold:
        return True

    return False
