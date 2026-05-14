"""策略页面"""

import asyncio

from core.base_page import BasePage
from core.logger import get_logger
from core.allure_reporter import allure
from config.coords import COORDS
from utils import faker_tool

logger = get_logger("strategy")


class StrategyPage(BasePage):
    """策略研究页面对象"""

    async def click_strategy_research(self) -> bool:
        """点击策略研究"""
        with allure.step("点击策略研究"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["strategy_research"]
            ok = click_screen(x, y, "策略研究")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def click_create_strategy(self) -> bool:
        """点击创建策略"""
        with allure.step("点击创建策略"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["create_strategy"]
            ok = click_screen(x, y, "创建策略")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def fill_strategy_name(self, prefix: str = "自动化") -> bool:
        """填写策略名称"""
        with allure.step("填写策略名称"):
            from utils.pyautogui_helper import type_screen
            name = faker_tool.strategy_name(prefix=prefix)
            x, y = COORDS["strategy_name"]
            ok = type_screen(x, y, name, "策略名称")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def select_strategy_template(self) -> bool:
        """选择策略模板 -> 交易模板"""
        with allure.step("选择策略模板"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["strategy_template"]
            if not click_screen(x, y, "策略模板"):
                return False
            await asyncio.sleep(1)
            x, y = COORDS["trade_template"]
            if not click_screen(x, y, "交易模板"):
                return False
            await asyncio.sleep(1)
            return True

    async def select_category(self) -> bool:
        """选择分类 -> 通用"""
        with allure.step("选择分类"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["category"]
            if not click_screen(x, y, "分类"):
                return False
            await asyncio.sleep(1)
            x, y = COORDS["category_common"]
            if not click_screen(x, y, "通用"):
                return False
            await asyncio.sleep(1)
            return True

    async def fill_description(self) -> bool:
        """填写策略描述"""
        with allure.step("填写描述"):
            from utils.pyautogui_helper import type_screen
            desc = faker_tool.strategy_description()
            x, y = COORDS["description"]
            ok = type_screen(x, y, desc, "描述")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def confirm_strategy(self) -> bool:
        """点击确定按钮"""
        with allure.step("确认创建策略"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["strategy_confirm"]
            ok = click_screen(x, y, "策略确定")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def click_three_dots(self) -> bool:
        """点击策略卡片右侧的"三个点"更多操作按钮"""
        with allure.step("点击更多操作（三个点）"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["three_dots"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 three_dots 坐标")
                return False
            ok = click_screen(x, y, "三个点")
            if ok:
                await asyncio.sleep(1)
            return ok

    async def first_strategy(self) -> bool:
        """点击第一个策略"""
        with allure.step("点击18162428572第一个策略"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["first_strategy"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 first_strategy 坐标")
                return False
            ok = click_screen(x, y, "第一个策略")
            if ok:
                await asyncio.sleep(1)
            return ok
    
    async def run_backtest_details(self) -> bool:
        """点击策略详情"""
        with allure.step("点击策略详情"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["run_backtest_details"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 run_backtest_details 坐标")
                return False
            ok = click_screen(x, y, "点击策略详情")
            if ok:
                await asyncio.sleep(1)
            return ok
    
    async def open_strategy(self) -> bool:
        """打开策略"""
        with allure.step("点击打开策略"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["open_strategy"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 open_strategy 坐标")
                return False
            ok = click_screen(x, y, "打开策略")
            if ok:
                await asyncio.sleep(1)
            return ok

    async def click_delete(self) -> bool:
        """点击下拉菜单中的删除选项"""
        with allure.step("点击删除"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["click_delete"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 click_delete 坐标")
                return False
            ok = click_screen(x, y, "删除选项")
            if ok:
                await asyncio.sleep(1)
            return ok

    async def confirm_delete(self) -> bool:
        """在删除确认弹窗中点击确定"""
        with allure.step("确认删除"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["confirm_delete"]
            if x == 0 and y == 0:
                logger.warning("坐标未配置，请在 config/coords.py 中设置 confirm_delete 坐标")
                return False
            ok = click_screen(x, y, "确认删除")
            if ok:
                await asyncio.sleep(2)
            return ok

    async def delete_strategy_flow(self) -> bool:
        """完整的删除策略流程：第一个策略 -> 三个点 -> 删除 -> 确认删除"""
        steps = [
            ("点击第一个策略", self.first_strategy),
            ("点击更多操作", self.click_three_dots),
            ("点击删除", self.click_delete),
            ("确认删除", self.confirm_delete),
        ]
        for name, step_fn in steps:
            if not await step_fn():
                logger.error(f"删除步骤失败: {name}")
                await self.screenshot(f"fail_delete_{name}.png")
                return False
        logger.info("策略删除流程完成")
        await self.screenshot("strategy_deleted.png")
        return True

    # ---------- 回测设置 ----------

    async def select_frequency(self) -> bool:
        """点击选择频率下拉框并确认选项"""
        with allure.step("选择频率"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["select_frequency"]
            if not click_screen(x, y, "选择频率"):
                return False
            await asyncio.sleep(1)
            x, y = COORDS["confirm_frequency"]
            if not click_screen(x, y, "确认频率"):
                return False
            await asyncio.sleep(1)
            return True

    async def select_match_frequency(self) -> bool:
        """点击撮合频率下拉框并确认选项"""
        with allure.step("选择撮合频率"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["match_frequency"]
            if not click_screen(x, y, "撮合频率"):
                return False
            await asyncio.sleep(1)
            x, y = COORDS["confirm_match_frequency"]
            if not click_screen(x, y, "确认撮合频率"):
                return False
            await asyncio.sleep(1)
            return True

    async def fill_preload_kline(self, value: str = "5") -> bool:
        """点击预加载K线输入框，清空后输入数值"""
        with allure.step(f"预加载K线: {value}"):
            from utils.pyautogui_helper import clear_and_type_screen
            x, y = COORDS["preload_kline_input"]
            ok = clear_and_type_screen(x, y, value, "预加载K线")
            if ok:
                await asyncio.sleep(0.5)
            return ok

    async def fill_backtest_start_date(self, date: str = "2026-04-01") -> bool:
        """通过日历 UI 交互设置回测开始时间：
        点击开始时间 → 向右切换月份(5次) → 点击1号
        """
        #await asyncio.sleep(300)
        with allure.step(f"回测开始时间: {date}"):
            from utils.pyautogui_helper import click_screen

            # 1. 点击开始时间输入框，打开日历弹窗
            x, y = COORDS["backtest_start_date"]
            click_screen(x, y, "开始时间选择器")
            await asyncio.sleep(0.8)

            # 2. 点击向右箭头 5 次（从 2025-11 前进到 2026-04）
            nx, ny = COORDS["calendar_next_month"]
            for i in range(3):
                click_screen(nx, ny, f"下月箭头 ({i+1}/5)")
                await asyncio.sleep(0.3)

            # 3. 点击 1 号
            d1x, d1y = COORDS["calendar_day_1"]
            click_screen(d1x, d1y, "1号日期")
            await asyncio.sleep(0.5)
            return True

    async def fill_backtest_end_date(self, date: str = "2026-04-10") -> bool:
        """通过日历 UI 交互设置回测结束时间：
        点击结束时间 → 向左切换月份(1次) → 点击10号
        """
        with allure.step(f"回测结束时间: {date}"):
            from utils.pyautogui_helper import click_screen

            # 1. 点击结束时间输入框，打开日历弹窗
            x, y = COORDS["backtest_end_date"]
            click_screen(x, y, "结束时间选择器")
            await asyncio.sleep(0.8)

            # 2. 点击向左箭头 1 次（从 2026-05 回退到 2026-04）
            px, py = COORDS["calendar_prev_month"]
            click_screen(px, py, "上月箭头 (1/1)")
            await asyncio.sleep(0.3)

            # 3. 点击 10 号
            d10x, d10y = COORDS["calendar_day_10"]
            click_screen(d10x, d10y, "10号日期")
            await asyncio.sleep(0.5)
            return True


    async def fill_initial_capital(self, value: str = "1000000") -> bool:
        """点击初始资金输入框，清空后输入金额"""
        with allure.step(f"初始资金: {value}"):
            from utils.pyautogui_helper import clear_and_type_screen
            x, y = COORDS["initial_capital"]
            ok = clear_and_type_screen(x, y, value, "初始资金")
            if ok:
                await asyncio.sleep(0.5)
            return ok

    async def click_run_backtest(self) -> bool:
        """点击运行回测按钮"""
        with allure.step("运行回测"):
            from utils.pyautogui_helper import click_screen
            x, y = COORDS["run_backtest"]
            ok = click_screen(x, y, "运行回测")
            if ok:
                await asyncio.sleep(5)
            return ok

    async def backtest_settings_flow(self) -> bool:
        """回测设置完整流程（创建策略后调用）"""
        steps = [
            ("点击第一个策略", self.first_strategy),
            ("选择频率", self.select_frequency),
            ("选择撮合频率", self.select_match_frequency),
            ("预加载K线", self.fill_preload_kline),
            ("回测开始时间", self.fill_backtest_start_date),
            ("回测结束时间", self.fill_backtest_end_date),
            ("初始资金", self.fill_initial_capital),
            ("运行回测", self.click_run_backtest),
        ]
        for name, step_fn in steps:
            if not await step_fn():
                logger.error(f"回测步骤失败: {name}")
                await self.screenshot(f"fail_backtest_{name}.png")
                return False
        logger.info("回测设置并运行完成")
        await self.screenshot("backtest_running.png")

        # OCR 监听回测进度，替代固定 10 秒等待
        with allure.step("监听回测进度"):
            region = COORDS.get("backtest_progress_region", (0, 0, 0, 0))
            if region[2] > 0 and region[3] > 0:
                result = await self.wait_for_progress_by_ocr(
                    region=region,
                    timeout=300000,      # 最多等 5 分钟
                    interval=2000,       # 每 2 秒截图识别一次
                    on_update=lambda cur, prev: logger.info(f"回测进度: {cur}%"),
                )
                if result["ok"]:
                    logger.info(f"回测进度到达 {result['progress']}%，继续下一步")
                    await self.run_backtest_details()
                    await self.screenshot("backtest_running_details.png")
                else:
                    logger.warning(f"回测进度监听异常: {result}，继续执行")
            else:
                logger.warning("回测进度区域坐标未配置， fallback 等待 10 秒")
                await asyncio.sleep(10)

        return True

    async def create_and_run_backtest_flow(self) -> bool:
        """创建策略并运行回测的完整流程"""
        if not await self.create_strategy_flow():
            return False
        if not await self.backtest_settings_flow():
            return False
        logger.info("创建策略并运行回测流程完成")
        return True

    async def create_strategy_flow(self) -> bool:
        """完整的创建策略流程"""
        steps = [
            ("进入策略研究", self.click_strategy_research),
            ("点击创建策略", self.click_create_strategy),
            ("填写策略名称", self.fill_strategy_name),
            ("选择策略模板", self.select_strategy_template),
            ("选择分类", self.select_category),
            ("填写描述", self.fill_description),
            ("确认创建", self.confirm_strategy),
        ]

        for name, step_fn in steps:
            if not await step_fn():
                logger.error(f"步骤失败: {name}")
                await self.screenshot(f"fail_{name}.png")
                return False

        logger.info("策略创建流程完成")
        await self.screenshot("strategy_created.png")
        return True
    
    async def open_strategy_first(self) -> bool:
        """完整的创建策略流程"""
        steps = [
            ("进入策略研究", self.click_strategy_research),
            ("点击第一个策略", self.first_strategy),
            ("打开策略", self.open_strategy),
        ]
        for name, step_fn in steps:
            if not await step_fn():
                logger.error(f"步骤失败: {name}")
                await self.screenshot(f"fail_{name}.png")
                return False

        logger.info("策略创建流程完成")
        await self.screenshot("strategy_created.png")
        return True
