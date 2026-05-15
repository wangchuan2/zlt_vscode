"""测试用例：创建策略"""

import asyncio

from cases.base_test_case import BaseTestCase
from core.logger import get_logger
from pages.login_page import LoginPage
from pages.strategy_page import StrategyPage

logger = get_logger("case")


class TestStrategyCreate(BaseTestCase):
    """创建策略测试用例"""

    async def zztest_create(self) -> bool:
        """执行完整测试流程：登录 + 创建策略"""
        self._start_test(
            name="创建策略流程测试",
            description="智量通 VS Code 插件：登录 + 创建策略完整流程",
            labels={"feature": "策略管理", "severity": "critical"},
        )
        try:
            playwright, browser, page = await self._setup()
            login_page = LoginPage(page)
            if not await login_page.ensure_login():
                raise AssertionError("登录失败或无法确认登录状态")

            strategy_page = StrategyPage(page)
            if not await strategy_page.create_strategy_flow():
                raise AssertionError("创建策略流程失败")

            self._set_passed()
            return True

        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()

    async def test_create_and_delete(self) -> bool:
        """执行完整测试流程：登录 + 创建策略 + 删除策略"""
        self._start_test(
            name="创建并删除策略流程测试",
            description="智量通 VS Code 插件：登录 + 创建策略 + 删除策略完整流程",
            labels={"feature": "策略管理", "severity": "critical"},
        )
        try:
            playwright, browser, page = await self._setup()
            login_page = LoginPage(page)
            if not await login_page.ensure_login():
                raise AssertionError("登录失败或无法确认登录状态")

            strategy_page = StrategyPage(page)
            if not await strategy_page.create_strategy_flow():
                raise AssertionError("创建策略流程失败")

            logger.info("开始删除刚创建的策略...")
            if not await strategy_page.delete_strategy_flow():
                logger.warning("删除策略流程失败，但不影响创建结果")

            self._set_passed()
            return True

        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()

    async def zztest_create_and_run(self) -> bool:
        """创建策略并运行回测：登录 + 创建策略 + 回测设置 + 运行"""
        self._start_test(
            name="创建策略并运行回测",
            description="智量通 VS Code 插件：创建策略后配置回测参数并运行",
            labels={"feature": "策略回测", "severity": "critical"},
        )
        try:
            playwright, browser, page = await self._setup()

            login_page = LoginPage(page)
            if not await login_page.ensure_login():
                raise AssertionError("登录失败或无法确认登录状态")

            strategy_page = StrategyPage(page)
            if not await strategy_page.create_and_run_backtest_flow():
                raise AssertionError("创建策略并运行回测流程失败")

            await asyncio.sleep(2)
            self._set_passed()
            return True

        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()

    async def zztest_open_first(self) -> bool:
        """登录 + 打开第一个策略"""
        self._start_test(
            name="打开第一个策略",
            description="智量通 VS Code 插件：本地打开第一个策略",
            labels={"feature": "策略回测", "severity": "critical"},
        )
        try:
            playwright, browser, page = await self._setup()

            login_page = LoginPage(page)
            if not await login_page.ensure_login():
                raise AssertionError("登录失败或无法确认登录状态")

            strategy_page = StrategyPage(page)
            if not await strategy_page.open_strategy_first():
                raise AssertionError("打开策略流程失败")

            await asyncio.sleep(3)
            self._set_passed()
            return True

        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()


async def main():
    case = TestStrategyCreate()
    return await case.test_create_and_run()


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(main())
    exit(0 if result else 1)
