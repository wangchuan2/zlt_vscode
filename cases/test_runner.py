"""测试批量执行器

用法:
    runner = TestRunner()
    runner.add(TestStrategyCreate().test_create_and_run)
    runner.add(TestDataDownload().zztest_download)
    await runner.run()
"""

import time
from typing import Callable, Awaitable

from core.logger import get_logger
from utils.feishu_notifier import FeishuNotifier

logger = get_logger("runner")


class TestRunner:
    """批量测试执行器"""

    def __init__(self):
        self.cases: list[tuple[str, Callable[[], Awaitable[bool]]]] = []
        self.results: list[dict] = []
        self.notifier = FeishuNotifier()

    def add(self, name: str, case_fn: Callable[[], Awaitable[bool]]):
        """添加测试用例"""
        self.cases.append((name, case_fn))

    def add_from_class(self, instance, method_name: str):
        """从测试类实例中添加用例方法（用于自动发现）"""
        name = f"{instance.__class__.__name__}.{method_name}"
        fn = getattr(instance, method_name)
        self.cases.append((name, fn))

    async def run(self) -> bool:
        """执行所有用例，仅失败时统一发送飞书通知"""
        from cases.base_test_case import BaseTestCase

        # 开启批量模式：用例结束不发单条通知
        BaseTestCase.batch_mode = True
        start = time.time()
        self.results = []

        logger.info(f"开始执行 {len(self.cases)} 个测试用例")

        for name, case_fn in self.cases:
            case_start = time.time()
            logger.info(f"执行: {name}")
            try:
                ok = await case_fn()
                status = "passed" if ok else "failed"
                error = "" if ok else "测试断言失败"
            except Exception as e:
                status = "failed"
                error = str(e)
                logger.error(f"用例异常: {name} - {e}")

            duration = f"{time.time() - case_start:.1f}s"
            self.results.append({
                "name": name,
                "status": status,
                "duration": duration,
                "error": error,
            })

        total = time.time() - start
        logger.info(f"全部执行完成，总耗时: {total:.1f}s")

        # 仅当有失败用例时才发送通知
        failed_results = [r for r in self.results if r["status"] == "failed"]
        if failed_results:
            self.notifier.send_batch_result(failed_results)
            logger.info(f"发送失败用例通知，共 {len(failed_results)} 条")
        else:
            logger.info("全部通过，不发送飞书通知")

        return len(failed_results) == 0
