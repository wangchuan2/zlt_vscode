"""Jenkins 环境专用配置

使用方法:
    1. Jenkins Pipeline 中通过 withCredentials 注入环境变量
    2. 本配置自动从环境变量读取敏感信息
    3. 所有输出目录基于 Jenkins WORKSPACE

环境变量:
    WORKSPACE           - Jenkins 工作目录（自动设置）
    ZLT_PHONE           - 登录手机号（Jenkins Credentials）
    ZLT_PASSWORD        - 登录密码（Jenkins Credentials）
    ZLT_FEISHU_WEBHOOK  - 飞书 Webhook（Jenkins Credentials）
    ZLT_VS_CODE_PATH    - VS Code 路径（可选，默认自动查找）
"""

import os


# 从 Jenkins 环境变量获取工作目录
WORKSPACE = os.environ.get("WORKSPACE", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============== VS Code 路径（Jenkins 节点上可能不同）===============
# 按优先级查找 VS Code
_VSCODE_CANDIDATES = [
    os.environ.get("ZLT_VS_CODE_PATH"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    r"C:\Program Files\Microsoft VS Code\Code.exe",
    r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
]

VS_CODE_PATH = None
for p in _VSCODE_CANDIDATES:
    if p and os.path.isfile(p):
        VS_CODE_PATH = p
        break

if not VS_CODE_PATH:
    VS_CODE_PATH = r"C:\Program Files\Microsoft VS Code\Code.exe"

DEBUG_PORT = int(os.environ.get("ZLT_DEBUG_PORT", "9222"))

# =============== 窗口位置配置 ===============
# Jenkins 环境下保持固定窗口位置，便于坐标匹配
WINDOW_POS = {
    "x": 480,
    "y": 170,
    "width": 1420,
    "height": 840,
}

# =============== 路径配置（全部放在 Jenkins WORKSPACE 下）===============
BASE_DIR = WORKSPACE
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")

# =============== 登录信息（从 Jenkins Credentials 注入）===============
PHONE = os.environ.get("ZLT_PHONE", "")
PASSWORD = os.environ.get("ZLT_PASSWORD", "")

if not PHONE or not PASSWORD:
    import warnings
    warnings.warn("ZLT_PHONE 或 ZLT_PASSWORD 环境变量未设置，登录可能失败")

# =============== Allure 配置 ===============
ALLURE_RESULTS_DIR = os.path.join(REPORT_DIR, "allure_results")
ALLURE_REPORT_DIR = os.path.join(REPORT_DIR, "allure_report")

# =============== 飞书机器人配置 ===============
FEISHU_WEBHOOK = os.environ.get("ZLT_FEISHU_WEBHOOK", "")

if not FEISHU_WEBHOOK:
    import warnings
    warnings.warn("ZLT_FEISHU_WEBHOOK 环境变量未设置，飞书通知将不可用")

# 自动创建目录
for d in (LOG_DIR, REPORT_DIR, SCREENSHOT_DIR, ALLURE_RESULTS_DIR):
    os.makedirs(d, exist_ok=True)
