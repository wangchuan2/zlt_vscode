"""全局配置

环境变量覆盖（Jenkins 部署时使用）：
  ZLT_VS_CODE_PATH    - VS Code 可执行文件路径
  ZLT_DEBUG_PORT      - 调试端口
  ZLT_PHONE           - 登录手机号
  ZLT_PASSWORD        - 登录密码
  ZLT_FEISHU_WEBHOOK  - 飞书机器人 webhook URL
  ZLT_BASE_DIR        - 基础目录（默认脚本所在目录的父目录）
"""

import os


def _env(name: str, default="") -> str:
    """从环境变量读取，支持空字符串作为合法值"""
    return os.environ.get(name, default)


# =============== VS Code 路径 ===============
VS_CODE_PATH = _env("ZLT_VS_CODE_PATH", r"E:\gongjubao\vscode\Microsoft VS Code\Code.exe")
DEBUG_PORT = int(_env("ZLT_DEBUG_PORT", "9222"))

# =============== 窗口位置配置 ===============
WINDOW_POS = {
    "x": 480,
    "y": 170,
    "width": 1420,
    "height": 840,
}

# =============== 路径配置 ===============
BASE_DIR = _env("ZLT_BASE_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")

# =============== 登录信息 ===============
PHONE = _env("ZLT_PHONE", "18162428572")
PASSWORD = _env("ZLT_PASSWORD", "111111")

# =============== Allure 配置 ===============
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure_results")
ALLURE_REPORT_DIR = os.path.join(REPORT_DIR, "allure_report")

# =============== 飞书机器人配置 ===============
# 在飞书群设置 -> 添加自定义机器人 -> 复制 webhook URL
FEISHU_WEBHOOK = _env(
    "ZLT_FEISHU_WEBHOOK",
    "https://open.feishu.cn/open-apis/bot/v2/hook/0bfc3120-9eb9-452e-a2d6-33e8ff07b705",
)

# 自动创建目录
for d in (LOG_DIR, REPORT_DIR, SCREENSHOT_DIR, ALLURE_RESULTS_DIR):
    os.makedirs(d, exist_ok=True)
