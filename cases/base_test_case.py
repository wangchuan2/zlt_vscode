"""测试用例基类

提供通用能力：
- 浏览器连接/断开管理
- Allure 测试报告
- 飞书结果通知（单条/批量模式）
- 执行耗时统计

使用方式：
    class TestSomething(BaseTestCase):
        async def test_something(self) -> bool:
            self._start_test("测试名称")
            try:
                # ... 测试步骤 ...
                self._set_passed()
                return True
            except Exception as e:
                self._set_failed(str(e))
                return False
            finally:
                await self._teardown()

批量执行方式（推荐）：
    runner = TestRunner()
    runner.add("创建策略", TestStrategyCreate().test_create)
    runner.add("数据下载", TestDataDownload().zztest_download)
    await runner.run()  # 统一发送表格通知
"""

import time

from core.browser_manager import BrowserManager
from core.allure_reporter import allure
from core.logger import get_logger
from utils.feishu_notifier import FeishuNotifier

logger = get_logger("case")


class BaseTestCase:
    """测试用例基类

    批量执行时 TestRunner 会自动设置 batch_mode = True，
    此时每个用例结束不再发送单条通知，由 runner 最后统一发送。
    """

    batch_mode: bool = False  # 类变量：批量模式开关

    def __init__(self):
        self.notifier = FeishuNotifier()
        self.manager: BrowserManager | None = None
        self._start_time: float = 0.0
        self._test_name: str = ""
        self._status: str = ""
        self._error: str = ""

    def _start_test(self, name: str, description: str = "", labels: dict | None = None):
        """记录测试开始时间和名称"""
        self._start_time = time.time()
        self._test_name = name
        self._status = "running"
        self._error = ""
        allure.start_test(name=name, description=description, labels=labels or {})

    def _set_passed(self):
        """标记测试通过"""
        self._status = "passed"
        allure.stop_test("passed")
        logger.info("测试通过！")

    def _set_failed(self, error: str):
        """标记测试失败"""
        self._status = "failed"
        self._error = error
        allure.stop_test("failed", error)
        logger.error(f"测试失败: {error}")

    async def _setup(self):
        """初始化浏览器连接"""
        self.manager = BrowserManager()
        return await self.manager.connect()

    async def _teardown(self):
        """断开浏览器，批量模式时不发通知（由 runner 统一发送）"""
        try:
            if self.manager:
                await self.manager.disconnect()
                self.manager.terminate()
        finally:
            if not BaseTestCase.batch_mode:
                self._notify_result()

    def _notify_result(self):
        """发送飞书通知（在 finally 中调用）"""
        if not self._test_name:
            return

        duration = f"{time.time() - self._start_time:.1f}s"
        self.notifier.send_test_result(
            test_name=self._test_name,
            status=self._status,
            duration=duration,
            error=self._error,
        )

    def get_result(self) -> dict:
        """获取当前用例的执行结果（用于批量收集）"""
        return {
            "name": self._test_name,
            "status": self._status,
            "duration": f"{time.time() - self._start_time:.1f}s",
            "error": self._error,
        }
