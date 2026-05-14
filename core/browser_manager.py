"""浏览器/VS Code 管理器"""

import asyncio
import subprocess
import sys
from typing import Optional, Tuple

import requests

from playwright.async_api import async_playwright

from config.settings import VS_CODE_PATH, DEBUG_PORT
from core.logger import get_logger
from utils.window_utils import find_vscode_window, set_window_pos

logger = get_logger("browser")


def _kill_port_occupiers(port: int):
    """查找并终止占用指定端口的进程（仅限 Windows）"""
    if sys.platform != "win32":
        return
    try:
        # 先用 netstat 查找 PID
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", f":{port}"],
            capture_output=True,
            text=True,
            shell=True,
        )
        lines = result.stdout.strip().splitlines()
        pids = set()
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit():
                    pids.add(pid)

        for pid in pids:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", pid],
                    capture_output=True,
                    check=False,
                )
                logger.info(f"已终止占用端口 {port} 的进程 PID={pid}")
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"清理端口占用失败: {e}")


class BrowserManager:
    """管理 VS Code 启动、CDP 连接、Playwright 生命周期"""

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._playwright = None
        self._browser = None
        self._page = None

    async def start_vscode(self) -> subprocess.Popen:
        """启动 VS Code 调试模式"""
        # 先清理可能占用端口的残留进程
        _kill_port_occupiers(DEBUG_PORT)
        await asyncio.sleep(1)

        logger.info(f"正在启动 VS Code (调试端口 {DEBUG_PORT})...")
        self._proc = subprocess.Popen(
            [
                VS_CODE_PATH,
                f"--remote-debugging-port={DEBUG_PORT}",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--user-data-dir=C:\\temp\\vscode_debug_profile",
                "--new-window",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
            shell=False,
        )
        logger.info(f"VS Code 进程 PID: {self._proc.pid}")

        # 等待调试端口就绪
        logger.info("等待调试端口就绪...")
        for i in range(30):
            try:
                resp = requests.get(f"http://localhost:{DEBUG_PORT}/json/list", timeout=2)
                if resp.status_code == 200:
                    logger.info(f"调试端口就绪，当前 {len(resp.json())} 个页面")
                    # 设置窗口位置
                    hwnd = find_vscode_window()
                    if hwnd:
                        from config.settings import WINDOW_POS
                        pos = WINDOW_POS
                        if set_window_pos(hwnd, pos["x"], pos["y"], pos["width"], pos["height"]):
                            logger.info(f"窗口已固定到 ({pos['x']}, {pos['y']}) 大小 {pos['width']}x{pos['height']}")
                        else:
                            logger.warning("设置窗口位置失败")
                    else:
                        logger.warning("未找到 VS Code 窗口")
                    return self._proc
            except requests.exceptions.ConnectionError:
                logger.debug(f"  第 {i+1}/30 秒...")
            except Exception as e:
                logger.debug(f"  连接异常: {e}")
            await asyncio.sleep(1)

        self._proc.terminate()
        raise TimeoutError("调试端口 30 秒内未就绪")

    def is_vscode_running(self) -> bool:
        """检查 VS Code 调试端口是否已就绪"""
        try:
            resp = requests.get(f"http://localhost:{DEBUG_PORT}/json/list", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    async def connect(self) -> Tuple:
        """通过 CDP 连接 VS Code，返回 (playwright, browser, page)"""
        if not self.is_vscode_running():
            await self.start_vscode()

        logger.info(f"正在连接 CDP (端口 {DEBUG_PORT})...")
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")

        context = self._browser.contexts[0] if self._browser.contexts else None
        if not context:
            raise RuntimeError("无法获取 browser context")

        page = None
        for _ in range(20):
            for ctx_page in context.pages:
                try:
                    if "Visual Studio Code" in await ctx_page.title() or "vscode-app" in ctx_page.url:
                        await ctx_page.evaluate("1+1")
                        page = ctx_page
                        logger.info("已连接 VS Code 主页面")
                        break
                except Exception:
                    pass
            if page:
                break
            await asyncio.sleep(0.5)

        if not page:
            raise RuntimeError("无法获取有效页面")

        self._page = page
        return self._playwright, self._browser, self._page

    async def disconnect(self):
        """断开连接并清理资源"""
        if self._browser:
            try:
                await self._browser.disconnect()
            except Exception:
                pass
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        self._page = None

    def terminate(self):
        """终止 VS Code 进程"""
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=5)
            except Exception:
                self._proc.kill()
            self._proc = None

    @property
    def page(self):
        return self._page

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        self.terminate()
