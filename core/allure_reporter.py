"""简易 Allure 报告生成器（不依赖 pytest）"""

import json
import os
import time
import uuid
import shutil
from datetime import datetime
from typing import Optional

from config.settings import ALLURE_RESULTS_DIR, ALLURE_REPORT_DIR
from core.logger import get_logger

logger = get_logger("allure")


def _mime_to_ext(mime: str) -> str:
    mapping = {
        "text/plain": "txt",
        "image/png": "png",
        "image/jpeg": "jpg",
        "application/json": "json",
        "text/html": "html",
    }
    return mapping.get(mime, "bin")


class AllureReporter:
    """手动生成 Allure 结果的报告器"""

    def __init__(self, results_dir: str = ALLURE_RESULTS_DIR):
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self._current_test: Optional[str] = None
        self._current_start: Optional[float] = None
        self._steps: list = []
        self._step_stack: list = []
        self._test_attachments: list = []
        self._labels: dict = {}
        self._description: str = ""

    def start_test(self, name: str, description: str = "", labels: Optional[dict] = None):
        """开始记录一个测试用例"""
        self._current_test = name
        self._current_start = time.time()
        self._steps = []
        self._step_stack = []
        self._test_attachments = []
        self._labels = labels or {}
        self._description = description
        logger.info(f"▶ 开始测试: {name}")

    def stop_test(self, status: str = "passed", status_details: Optional[str] = None):
        """结束当前测试用例并写入结果"""
        if not self._current_test or self._current_start is None:
            return

        duration = time.time() - self._current_start
        uuid_str = str(uuid.uuid4())

        result = {
            "uuid": uuid_str,
            "name": self._current_test,
            "status": status,
            "start": int(self._current_start * 1000),
            "stop": int(time.time() * 1000),
        }

        if self._description:
            result["description"] = self._description

        if status_details and status != "passed":
            result["statusDetails"] = {"message": status_details}

        if self._steps:
            result["steps"] = self._steps

        if self._test_attachments:
            result["attachments"] = self._test_attachments

        labels = [{"name": k, "value": v} for k, v in self._labels.items()]
        labels.append({"name": "suite", "value": "自动化测试"})
        result["labels"] = labels

        result_file = os.path.join(self.results_dir, f"{uuid_str}-result.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        status_emoji = {"passed": "✅", "failed": "❌", "broken": "⚠️", "skipped": "⏭️"}
        logger.info(f"{status_emoji.get(status, '?')} 测试结束 [{status}]: {self._current_test} ({duration:.1f}s)")

        self._current_test = None
        self._current_start = None

    def step(self, name: str):
        """记录一个步骤（上下文管理器）"""
        return _StepContext(self, name)

    def _add_step(self, step_data: dict):
        """添加步骤到列表，支持附件"""
        if self._step_stack:
            parent = self._step_stack[-1]
            parent.setdefault("steps", []).append(step_data)
        else:
            self._steps.append(step_data)

    def _attach(self, name: str, mime: str, data: bytes) -> dict:
        """写入附件文件并返回附件声明对象"""
        ext = _mime_to_ext(mime)
        attach_uuid = str(uuid.uuid4())
        attach_file = os.path.join(self.results_dir, f"{attach_uuid}-attachment.{ext}")
        with open(attach_file, "wb") as f:
            f.write(data)
        return {"name": name, "source": f"{attach_uuid}-attachment.{ext}", "type": mime}

    def attach_text(self, name: str, text: str):
        """添加文本附件"""
        declaration = self._attach(name, "text/plain", text.encode("utf-8"))
        self._test_attachments.append(declaration)
        logger.debug(f"附件(文本): {name}")

    def attach_screenshot(self, name: str, image_path: str):
        """添加截图附件"""
        if not os.path.exists(image_path):
            logger.warning(f"截图文件不存在: {image_path}")
            return
        with open(image_path, "rb") as f:
            declaration = self._attach(name, "image/png", f.read())
        self._test_attachments.append(declaration)
        logger.debug(f"附件(截图): {name}")

    def generate_report(self, output_dir: str = ALLURE_REPORT_DIR):
        """生成 Allure HTML 报告（需安装 allure-commandline）"""
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
            os.makedirs(output_dir, exist_ok=True)
            import subprocess
            subprocess.run(
                ["allure", "generate", self.results_dir, "-o", output_dir, "--clean"],
                check=True,
                capture_output=True,
            )
            logger.info(f"📊 Allure 报告已生成: {output_dir}/index.html")
            return True
        except FileNotFoundError:
            logger.warning("⚠️ 未找到 allure 命令行工具，报告未生成")
            logger.info(f"   可手动运行: allure generate {self.results_dir} -o {output_dir} --clean")
            return False
        except Exception as e:
            logger.error(f"❌ 生成报告失败: {e}")
            return False


class _StepContext:
    def __init__(self, reporter: AllureReporter, name: str):
        self.reporter = reporter
        self.name = name
        self.start: Optional[float] = None
        self.step_data: Optional[dict] = None

    def __enter__(self):
        self.start = time.time()
        self.step_data = {"name": self.name, "status": "passed"}
        self.reporter._step_stack.append(self.step_data)
        logger.info(f"  → 步骤: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stop = time.time()
        self.step_data["status"] = "passed" if exc_type is None else "failed"
        self.step_data["start"] = int(self.start * 1000)
        self.step_data["stop"] = int(stop * 1000)
        self.reporter._step_stack.pop()
        self.reporter._add_step(self.step_data)
        if exc_type is not None:
            logger.error(f"  ✗ 步骤失败: {self.name} - {exc_val}")
        return False

    def attach_text(self, name: str, text: str):
        """在步骤内添加文本附件"""
        declaration = self.reporter._attach(name, "text/plain", text.encode("utf-8"))
        self.step_data.setdefault("attachments", []).append(declaration)

    def attach_screenshot(self, name: str, image_path: str):
        """在步骤内添加截图附件"""
        if not os.path.exists(image_path):
            return
        with open(image_path, "rb") as f:
            declaration = self.reporter._attach(name, "image/png", f.read())
        self.step_data.setdefault("attachments", []).append(declaration)


# 全局单例
allure = AllureReporter()
