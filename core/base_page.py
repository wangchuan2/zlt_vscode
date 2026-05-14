"""基础页面对象"""

import asyncio
import time
from typing import Optional

from core.logger import get_logger
from core.allure_reporter import allure

logger = get_logger("page")


class BasePage:
    """页面对象基类，封装常用操作"""

    def __init__(self, page):
        self.page = page

    async def wait_for(self, milliseconds: int = 1000):
        """等待指定毫秒"""
        await self.page.wait_for_timeout(milliseconds)

    async def find_and_click(self, selectors: list[str], timeout: int = 5000) -> bool:
        """依次尝试多个选择器，找到可见元素并点击"""
        for sel in selectors:
            try:
                loc = self.page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible():
                    await loc.click()
                    logger.info(f"Playwright 点击: {sel}")
                    return True
            except Exception:
                pass
        logger.warning(f"未找到可点击元素: {selectors}")
        return False

    async def screenshot(self, filename: str) -> str:
        """页面截图并返回路径"""
        from config.settings import SCREENSHOT_DIR
        import os
        path = os.path.join(SCREENSHOT_DIR, filename)
        await self.page.screenshot(path=path)
        logger.info(f"页面截图: {path}")
        allure.attach_screenshot(filename, path)
        return path

    async def dump_dom(self, filename: str = "dom.html") -> str:
        """保存当前页面 DOM"""
        from config.settings import SCREENSHOT_DIR
        import os
        path = os.path.join(SCREENSHOT_DIR, filename)
        html = await self.page.content()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"DOM 已保存: {path}")
        allure.attach_text(filename, html[:5000])
        return path

    def list_frames(self):
        """列出所有 frame 信息（同步日志）"""
        async def _do():
            for i, frame in enumerate(self.page.frames):
                try:
                    url = frame.url[:100] if frame.url else "empty"
                    logger.info(f"  Frame {i}: url={url}")
                except Exception as e:
                    logger.warning(f"  Frame {i}: 无法获取URL: {e}")
        asyncio.get_event_loop().create_task(_do())

    async def wait_for_progress(
        self,
        selector: str,
        timeout: int = 60000,
        interval: int = 500,
        on_update=None,
    ) -> dict:
        """轮询监听页面上的进度条，从 0% 到 100%

        Args:
            selector: 进度条元素的 CSS 选择器
                      （如 '.el-progress-bar__inner'、'[role="progressbar"]'）
            timeout:  最大等待时间（毫秒），默认 60 秒
            interval: 轮询间隔（毫秒），默认 500ms
            on_update: 可选回调，每次进度变化时调用，参数 (current, previous)

        Returns:
            {"ok": True, "progress": 100}  — 进度到达 100%
            {"ok": False, "reason": "timeout", "last_progress": x}  — 超时
            {"ok": False, "reason": "not_found"}  — 未找到进度条元素
        """
        import time

        start = time.time()
        last_progress = -1
        logger.info(f"开始监听进度条: {selector}")

        while (time.time() - start) * 1000 < timeout:
            try:
                result = await self.page.evaluate(
                    """(selector) => {
                        const el = document.querySelector(selector);
                        if (!el) return {found: false};

                        // 尝试多种方式提取百分比
                        let pct = null;

                        // 1. style.width (如 "50%")
                        const width = el.style.width;
                        if (width && width.includes('%')) {
                            pct = parseFloat(width);
                        }

                        // 2. aria-valuenow (无障碍属性)
                        if (pct === null) {
                            const val = el.getAttribute('aria-valuenow');
                            if (val) pct = parseFloat(val);
                        }

                        // 3. textContent (如 "50%" 或 "5/10")
                        if (pct === null) {
                            const text = el.textContent.trim();
                            const m = text.match(/(\d+(?:\.\d+)?)%/);
                            if (m) pct = parseFloat(m[1]);
                        }

                        // 4. value/max (原生 progress 元素)
                        if (pct === null && el.value !== undefined && el.max) {
                            pct = (el.value / el.max) * 100;
                        }

                        return {found: true, progress: pct || 0};
                    }""",
                    selector,
                )

                if not result.get("found"):
                    if last_progress < 0:
                        # 首次就没找到，可能是进度条还没出现，继续等待
                        await self.wait_for(interval)
                        continue
                    else:
                        # 之前有进度，现在找不到了，认为已完成
                        logger.info("进度条消失，认为已完成")
                        return {"ok": True, "progress": 100}

                current = result["progress"]

                # 进度变化时日志 + 回调
                if current != last_progress:
                    logger.info(f"进度条进度: {current}%")
                    if on_update:
                        on_update(current, last_progress)
                    last_progress = current

                # 到达 100%
                if current >= 100:
                    logger.info("进度条到达 100%，完成")
                    return {"ok": True, "progress": 100}

            except Exception as e:
                logger.debug(f"进度条读取异常: {e}")

            await self.wait_for(interval)

        logger.warning(f"进度条监听超时，最后进度: {last_progress}%")
        return {"ok": False, "reason": "timeout", "last_progress": last_progress}

    async def wait_for_progress_by_ocr(
        self,
        region: tuple[int, int, int, int],
        timeout: int = 60000,
        interval: int = 2000,
        threshold: float = 100.0,
        on_update=None,
    ) -> dict:
        """通过区域截图 + OCR 识别来监听进度条

        Args:
            region: 截图区域 (left, top, width, height) 的屏幕坐标
            timeout: 最大等待时间（毫秒），默认 60 秒
            interval: 轮询间隔（毫秒），默认 1 秒
            threshold: 判定完成的百分比阈值，默认 100.0
            on_update: 可选回调，每次进度变化时调用，参数 (current, previous)

        Returns:
            {"ok": True, "progress": 100}  — 进度到达阈值
            {"ok": False, "reason": "timeout", "last_progress": x}  — 超时
            {"ok": False, "reason": "ocr_error", "error": str}  — OCR 异常
        """
        import time
        from utils.ocr_helper import recognize_region, extract_percentage

        start = time.time()
        last_progress = -1.0
        logger.info(f"开始 OCR 监听进度条，区域: {region}")

        while (time.time() - start) * 1000 < timeout:
            try:
                # 区域截图并 OCR 识别
                text = recognize_region(region)

                # 提取百分比
                current = extract_percentage(text)

                if current is None:
                    # 没识别到数字，可能是进度条还没出现或已完成消失
                    if last_progress > 0:
                        logger.info("OCR 未识别到进度，认为已完成")
                        return {"ok": True, "progress": last_progress}
                    await self.wait_for(interval)
                    continue

                # 进度变化时日志 + 回调
                if current != last_progress:
                    logger.info(f"OCR 识别进度: {current}%")
                    if on_update:
                        on_update(current, last_progress)
                    last_progress = current

                # 到达阈值
                if current >= threshold:
                    logger.info(f"进度到达 {current}%，完成")
                    return {"ok": True, "progress": current}

            except Exception as e:
                logger.warning(f"OCR 识别异常: {e}")
                return {"ok": False, "reason": "ocr_error", "error": str(e)}

            await self.wait_for(interval)

        logger.warning(f"OCR 进度监听超时，最后进度: {last_progress}%")
        return {"ok": False, "reason": "timeout", "last_progress": last_progress}

    async def set_date_picker(self, placeholder: str, date: str) -> bool:
        """用多种策略定位 Element Plus 日期输入框并设置值

        策略顺序：
          1. Playwright locator（placeholder）— 最稳定
          2. JS 按 placeholder 属性匹配
          3. JS 按 input class（el-range-input）+ 索引匹配

        Args:
            placeholder: input 的 placeholder 属性值（如"起始日期"）
            date: 要设置的日期字符串（如"2026-04-01"）
        """
        # ── 策略 1: Playwright locator ─────────────────────────────────
        try:
            loc = self.page.locator(f'input[placeholder="{placeholder}"]')
            if await loc.count() > 0:
                await loc.fill(date)
                await loc.press("Enter")
                logger.info(f"日期选择器已设置 (Playwright): {date}")
                return True
        except Exception as e:
            logger.debug(f"Playwright 填充失败: {e}")

        # ── 策略 2: JS 注入（兼容已有 placeholder） ──────────────────────
        try:
            result = await self.page.evaluate(
                """({placeholder, date}) => {
                    const inputs = document.querySelectorAll('input');
                    let input = Array.from(inputs).find(
                        el => el.getAttribute('placeholder') === placeholder
                    );

                    // 策略 3: 按 class + 索引兜底（起始日期=0，结束日期=1）
                    if (!input) {
                        const rangeInputs = document.querySelectorAll('.el-range-input');
                        const idx = placeholder.includes('起始') || placeholder.includes('开始')
                            ? 0 : 1;
                        input = rangeInputs[idx] || null;
                    }

                    if (!input) return {ok: false, reason: 'not_found'};

                    // 获取原生 HTMLInputElement.value setter，绕过 Vue proxy
                    const nativeSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    nativeSetter.call(input, date);

                    // 触发 Vue/Element Plus 监听的事件
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

                    return {ok: true};
                }""",
                {"placeholder": placeholder, "date": date},
            )
            if result.get("ok"):
                logger.info(f"日期选择器已设置 (JS): {date}")
                return True
            else:
                logger.warning(f"未找到 placeholder='{placeholder}' 的日期输入框")
                return False
        except Exception as e:
            logger.error(f"设置日期失败: {e}")
            return False
