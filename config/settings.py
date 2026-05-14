"""全局配置"""

import os


# =============== VS Code 路径 ===============
VS_CODE_PATH = r"E:\gongjubao\vscode\Microsoft VS Code\Code.exe"
DEBUG_PORT = 9222

# =============== 窗口位置配置 ===============
WINDOW_POS = {
    "x": 480,
    "y": 170,
    "width": 1420,
    "height": 840,
}

# =============== 路径配置 ===============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")

# =============== 登录信息 ===============
PHONE = "18162428572"
PASSWORD = "111111"

# =============== Allure 配置 ===============
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure_results")
ALLURE_REPORT_DIR = os.path.join(REPORT_DIR, "allure_report")

# =============== 飞书机器人配置 ===============
# 在飞书群设置 -> 添加自定义机器人 -> 复制 webhook URL
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/0bfc3120-9eb9-452e-a2d6-33e8ff07b705"

# 自动创建目录
for d in (LOG_DIR, REPORT_DIR, SCREENSHOT_DIR, ALLURE_RESULTS_DIR):
    os.makedirs(d, exist_ok=True)
