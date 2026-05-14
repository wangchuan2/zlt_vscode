"""测试用例自动发现模块

自动扫描 cases/ 目录下所有以 test_ 开头的 .py 文件，
查找类名以 Test 开头的类，收集其中方法名以 test 开头的所有方法。

约定：
- 文件名以 test_ 开头
- 类名以 Test 开头
- 方法名以 test 开头（不区分大小写）
- 方法签名: async def test_xxx(self) -> bool
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import List, Tuple, Type

from core.logger import get_logger

logger = get_logger("discover")


def _is_test_method(name: str) -> bool:
    """检查方法名是否以 test 开头（不区分大小写）"""
    return name.lower().startswith("test")


def _is_async_method(obj, method_name: str) -> bool:
    """检查方法是否是异步方法"""
    method = getattr(obj, method_name, None)
    if method is None or not callable(method):
        return False
    return inspect.iscoroutinefunction(method)


def discover_tests(cases_dir: str = "cases") -> List[Tuple[str, Type, str]]:
    """
    自动发现测试用例，返回 [(用例显示名, 类, 方法名), ...]

    每个方法独立为一个用例条目。
    """
    base_path = Path(cases_dir).resolve()
    if not base_path.exists():
        logger.error(f"用例目录不存在: {base_path}")
        return []

    # 将 cases 目录加入 Python 路径，确保可以 import
    parent_dir = str(base_path.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    found: List[Tuple[str, Type, str]] = []

    for file_path in sorted(base_path.glob("test_*.py")):
        module_name = f"{base_path.name}.{file_path.stem}"

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logger.warning(f"导入模块失败 {module_name}: {e}")
            continue

        for class_name, cls in inspect.getmembers(module, inspect.isclass):
            # 类名以 Test 开头，且在当前模块中定义（不是从其他模块导入的）
            if not class_name.startswith("Test"):
                continue
            if getattr(cls, "__module__", "") != module_name:
                continue

            # 搜集类中所有以 test 开头的方法
            test_methods = []
            for method_name in dir(cls):
                if _is_test_method(method_name) and _is_async_method(cls, method_name):
                    test_methods.append(method_name)

            if not test_methods:
                logger.debug(f"跳过 {class_name}：没有 test 开头的方法")
                continue

            # 每个方法作为一个独立用例
            for method_name in sorted(test_methods):
                display_name = f"{class_name}.{method_name}"
                found.append((display_name, cls, method_name))
                logger.info(f"✅ 发现用例: {display_name} (来自 {file_path.name})")

    logger.info(f"共发现 {len(found)} 个用例")
    return found


async def run_discovered_tests(cases_dir: str = "cases") -> List[bool]:
    """发现并执行所有测试用例"""
    tests = discover_tests(cases_dir)
    if not tests:
        logger.warning("未发现任何测试用例")
        return []

    results = []
    current_instance = None
    current_class = None

    for display_name, cls, method_name in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"执行用例: {display_name}")
        logger.info(f"{'='*40}")

        try:
            # 复用同一个类实例（同一类的连续方法）
            if current_class is not cls:
                current_instance = cls()
                current_class = cls

            method = getattr(current_instance, method_name)
            result = await method()
            results.append(result)
        except Exception as e:
            logger.error(f"用例 {display_name} 执行异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    return results
