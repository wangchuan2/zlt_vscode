"""飞书机器人通知工具

使用方法：
1. 在飞书群设置中添加"自定义机器人"，复制 webhook URL
2. 将 webhook URL 填入 config/settings.py 的 FEISHU_WEBHOOK
3. 在测试完成后调用 send_result() 推送结果
"""

import json
import os
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import requests

from core.logger import get_logger
from config.settings import FEISHU_WEBHOOK

logger = get_logger("feishu")


class FeishuNotifier:
    """飞书群机器人通知"""

    def __init__(self, webhook: Optional[str] = None):
        # 优先使用传入的参数，其次环境变量，最后配置文件的默认值
        self.webhook = webhook or os.environ.get("FEISHU_WEBHOOK") or FEISHU_WEBHOOK

    def _send(self, msg: dict) -> bool:
        """发送消息到飞书"""
        if not self.webhook:
            logger.warning("飞书 webhook 未配置，跳过通知")
            return False

        headers = {"Content-Type": "application/json; charset=utf-8"}
        try:
            resp = requests.post(
                self.webhook,
                headers=headers,
                data=json.dumps(msg, ensure_ascii=False).encode("utf-8"),
                timeout=10,
            )
            result = resp.json()
            if result.get("code") == 0:
                logger.info("飞书通知发送成功")
                return True
            else:
                logger.error(f"飞书通知失败: {result}")
                return False
        except Exception as e:
            logger.error(f"飞书通知异常: {e}")
            return False

    def send_text(self, content: str) -> bool:
        """发送纯文本消息"""
        return self._send({
            "msg_type": "text",
            "content": {"text": content},
        })

    def send_markdown(self, title: str, content: str) -> bool:
        """发送 Markdown 格式消息"""
        return self._send({
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": content},
                    }
                ],
            },
        })

    def send_test_result(
        self,
        test_name: str,
        status: str,           # passed / failed
        duration: str = "",
        error: str = "",
    ) -> bool:
        """发送单个测试结果卡片"""
        color = "green" if status == "passed" else "red"
        status_text = "✅ 通过" if status == "passed" else "❌ 失败"

        content = (
            f"**测试名称:** {test_name}\n"
            f"**执行状态:** <font color='{color}'>{status_text}</font>\n"
            f"**执行时间:** {datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        if duration:
            content += f"**耗时:** {duration}\n"
        if error:
            content += f"**错误信息:** {error}\n"

        return self.send_markdown(
            title=f"自动化测试报告: {test_name}",
            content=content,
        )

    def send_batch_result(self, results: list[dict]) -> bool:
        """发送批量测试结果（表格形式）

        Args:
            results: 每个元素是 {"name": str, "status": "passed"/"failed",
                     "duration": str, "error": str}
        """
        if not results:
            return self.send_text("本次无测试用例执行")

        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = total - passed

        # 汇总行
        summary = (
            f"**执行时间:** {time.strftime('%Y-%m-%d %H:%M:%S')}  "
            f"**总计:** {total}  **✅通过:** {passed}  **❌失败:** {failed}\n\n"
        )

        # 表格头
        table = "| 测试用例 | 状态 | 耗时 | 详情 |\n"
        table += "| :--- | :--- | :--- | :--- |\n"

        # 表格行：失败的显示错误详情，成功的显示 "-"
        for r in results:
            name = r.get("name", "未知")
            status = "✅ 通过" if r.get("status") == "passed" else "❌ 失败"
            duration = r.get("duration", "")
            error = r.get("error", "")
            detail = error if error else "-"
            table += f"| {name} | {status} | {duration} | {detail} |\n"

        content = summary + table

        return self.send_markdown(
            title="自动化测试批量执行报告",
            content=content,
        )


def notify(text: str) -> bool:
    """快捷函数：发送纯文本通知"""
    return FeishuNotifier().send_text(text)
