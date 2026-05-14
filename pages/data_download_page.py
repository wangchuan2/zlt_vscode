"""数据下载页面"""

import asyncio

from core.base_page import BasePage
from core.logger import get_logger
from core.allure_reporter import allure
from config.coords_data_download import COORDS_DATA

logger = get_logger("data_download")


class DataDownloadPage(BasePage):
    """数据下载页面对象"""

    async def swipe_to_find_data_download(self) -> bool:
        """1. 登录后在侧边栏长按下滑，找到并点击"数据下载"菜单"""
        with allure.step("下滑查找数据下载菜单"):
            from utils.pyautogui_helper import swipe_down, click_screen

            sx, sy = COORDS_DATA["swipe_start"]
            mx, my = COORDS_DATA["swipe_menu"]

            if not swipe_down(
                sx, sy,
                distance=200, duration=0.5, label="侧边栏下滑"
            ):
                return False
            await asyncio.sleep(0.5)

            ok = click_screen(mx, my, "数据下载")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def click_data_type(self) -> bool:
        """3. 点击数据类型"""
        with allure.step("点击数据类型"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS_DATA["data_type_tab"]
            ok = click_screen(x, y, "数据类型")
            if ok:
                await asyncio.sleep(1)
            return ok
        
    async def click_data_download_menu(self) -> bool:
        """2. 点击数据下载"""
        with allure.step("点击数据下载"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS_DATA["data_download_menu"]
            ok = click_screen(x, y, "点击数据下载")
            if ok:
                await asyncio.sleep(1)
            return ok

    async def toggle_shenzhen_snapshots(self) -> bool:
        """4. 点击深圳交易所，取消股票快照和基金快照勾选"""
        with allure.step("深圳交易所取消快照勾选"):
            from utils.pyautogui_helper import click_screen

            # 点击深圳交易所
            x, y = COORDS_DATA["shenzhen_exchange"]
            if not click_screen(x, y, "深圳交易所"):
                return False
            await asyncio.sleep(0.5)

            # 取消股票快照
            x, y = COORDS_DATA["shenzhen_stock_snapshot"]
            if not click_screen(x, y, "深圳股票快照"):
                return False
            await asyncio.sleep(0.3)

            # 取消基金快照
            x, y = COORDS_DATA["shenzhen_fund_snapshot"]
            if not click_screen(x, y, "深圳基金快照"):
                return False
            await asyncio.sleep(0.3)

            return True

    async def toggle_shanghai_snapshots(self) -> bool:
        """5. 点击上海交易所，取消股票快照和基金快照勾选"""
        with allure.step("上海交易所取消快照勾选"):
            from utils.pyautogui_helper import click_screen

            # 点击上海交易所
            x, y = COORDS_DATA["shanghai_exchange"]
            if not click_screen(x, y, "上海交易所"):
                return False
            await asyncio.sleep(0.5)

            # 取消股票快照
            x, y = COORDS_DATA["shanghai_stock_snapshot"]
            if not click_screen(x, y, "上海股票快照"):
                return False
            await asyncio.sleep(0.3)

            # 取消基金快照
            x, y = COORDS_DATA["shanghai_fund_snapshot"]
            if not click_screen(x, y, "上海基金快照"):
                return False
            await asyncio.sleep(0.3)

            return True

    async def click_april_data(self) -> bool:
        """6. 点击4月份数据"""
        with allure.step("点击4月份数据"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS_DATA["april_data"]
            ok = click_screen(x, y, "4月份数据")
            if ok:
                await asyncio.sleep(0.5)
            return ok

    async def click_update_data(self) -> bool:
        """7. 点击更新数据"""
        with allure.step("点击更新数据"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS_DATA["update_data_button"]
            ok = click_screen(x, y, "更新数据")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def download_flow(self) -> bool:
        """完整的数据下载流程"""
        steps = [
            ("1 下滑找菜单", self.swipe_to_find_data_download),
            ("2 点击数据下载", self.click_data_download_menu),
            ("3 点击数据类型", self.click_data_type),
            ("4 深圳交易所取消快照", self.toggle_shenzhen_snapshots),
            ("5 上海交易所取消快照", self.toggle_shanghai_snapshots),
            ("6 点击4月份数据", self.click_april_data),
            ("7 点击更新数据", self.click_update_data),
        ]
        for name, step_fn in steps:
            if not await step_fn():
                logger.error(f"数据下载步骤失败: {name}")
                await self.screenshot(f"fail_download_{name}.png")
                return False

        logger.info("数据下载流程完成")
        await self.screenshot("data_download_done.png")
        await asyncio.sleep(10)
        return True
