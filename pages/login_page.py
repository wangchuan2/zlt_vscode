"""登录页面对象"""

import asyncio

from core.base_page import BasePage
from core.logger import get_logger
from core.allure_reporter import allure
from config.coords import COORDS
from config.settings import PHONE, PASSWORD

logger = get_logger("login")


class LoginPage(BasePage):
    """智量通登录页"""

    async def click_zhiliangtong_icon(self) -> bool:
        """点击智量通图标"""
        with allure.step("点击智量通图标"):
            selectors = ['[aria-label="智量通"]', '[title*="智量通"]', 'text=智量通']
            found = await self.find_and_click(selectors)
            if not found:
                # fallback: 尝试第 3~14 个 activitybar 按钮
                for i in range(3, 15):
                    try:
                        btn = self.page.locator(f'.activitybar .action-item:nth-child({i})').first
                        if await btn.count() > 0:
                            await btn.click()
                            await asyncio.sleep(0.8)
                            if await self.page.locator('text=智量通用户管理').count() > 0:
                                logger.info(f"在第 {i} 个位置找到智量通")
                                return True
                    except Exception:
                        pass
                return False
            await asyncio.sleep(1)
            return True

    async def is_logged_in(self) -> bool:
        """检测是否已登录"""
        with allure.step("检测登录状态"):
            await self.wait_for(2000)
            await self.screenshot("login_check.png")
            await self.dump_dom("login_check_dom.html")

            for i, frame in enumerate(self.page.frames):
                try:
                    if await frame.locator("text=昵称").count() > 0:
                        logger.info(f"Frame {i} 检测到已登录状态（存在 昵称）")
                        return True
                    if await frame.get_by_text("个人中心").count() > 0:
                        logger.info(f"Frame {i} 检测到已登录状态（存在 个人中心）")
                        return True
                except Exception as e:
                    logger.debug(f"Frame {i} 检测异常: {e}")

            logger.info("未检测到登录状态")
            return False

    async def login_with_pyautogui(self) -> bool:
        """使用 pyautogui 屏幕坐标登录"""
        with allure.step("账号密码登录"):
            from utils.pyautogui_helper import click_screen, type_screen

            # 点击账号登录标签
            x, y = COORDS["account_tab"]
            if not click_screen(x, y, "账号登录"):
                return False
            await asyncio.sleep(1)

            # 输入手机号
            x, y = COORDS["phone_input"]
            if not type_screen(x, y, PHONE, "手机号"):
                return False
            await asyncio.sleep(0.5)

            # 输入密码
            x, y = COORDS["password_input"]
            if not type_screen(x, y, PASSWORD, "密码"):
                return False
            await asyncio.sleep(0.5)

            # 点击登录按钮
            x, y = COORDS["login_button"]
            if not click_screen(x, y, "登录按钮"):
                return False
            await asyncio.sleep(3)
            return True

    async def ensure_login(self) -> bool:
        """确保已登录（已登录则跳过，未登录则执行登录）"""
        # 子方法已包含 allure 步骤，此处不再额外包裹
        await self.wait_for(3000)
        if not await self.click_zhiliangtong_icon():
            logger.error("点击智量通图标失败")
            return False

        await self.wait_for(3000)
        if await self.is_logged_in():
            logger.info("已登录，跳过登录步骤")
            return True

        if not await self.login_with_pyautogui():
            logger.error("登录失败")
            return False

        return await self.is_logged_in()
