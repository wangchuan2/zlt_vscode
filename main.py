"""项目入口"""

import asyncio
import sys

from core.allure_reporter import allure
from core.logger import get_logger
from core.test_discoverer import discover_tests
from cases.test_runner import TestRunner

logger = get_logger("main")


async def run_all():
    """自动发现并批量运行所有测试用例"""
    logger.info("=" * 50)
    logger.info("自动化测试开始")
    logger.info("=" * 50)

    # 自动发现 cases/ 目录下所有用例方法
    tests = discover_tests("cases")
    if not tests:
        logger.warning("未发现任何测试用例")
        return True

    # 使用 TestRunner 批量执行，仅失败时统一通知
    runner = TestRunner()
    current_instance = None
    current_class = None

    for display_name, cls, method_name in tests:
        try:
            # 复用同一个类实例
            if current_class is not cls:
                current_instance = cls()
                current_class = cls

            runner.add_from_class(current_instance, method_name)
        except Exception as e:
            logger.error(f"用例 {display_name} 添加异常: {e}")

    # 批量执行，全部跑完后统一通知
    all_passed = await runner.run()

    # 生成报告
    logger.info("\n" + "=" * 50)
    logger.info("生成 Allure 报告...")
    allure.generate_report()
    logger.info("=" * 50)

    return all_passed


if __name__ == "__main__":
    try:
        ok = asyncio.run(run_all())
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        logger.info("用户中断")
        sys.exit(130)
