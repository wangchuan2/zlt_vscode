# 智量通 VS Code 插件自动化测试框架文档

## 1. 项目概述

本框架用于对 **VS Code 中的"智量通"插件**进行端到端的 UI 自动化测试。目标产品是一个集成在 VS Code 中的量化交易平台，测试覆盖登录、策略创建、回测执行、数据下载等核心业务流程。

## 2. 技术架构

| 层次 | 技术方案 | 说明 |
|------|---------|------|
| **浏览器连接** | Playwright + CDP | 通过 Chrome DevTools Protocol 连接 VS Code 的调试端口 |
| **UI 操作** | pyautogui + 屏幕坐标 | VS Code 插件 UI 难以用 CSS 选择器定位，采用绝对坐标点击 |
| **DOM 操作** | Playwright Locator | 辅助性 DOM 查找（登录状态检测、截图等） |
| **测试框架** | 自研（无 pytest 依赖） | 自定义测试基类、发现器、执行器、报告器 |
| **测试报告** | Allure（自研生成器） | 不依赖 pytest-allure，手动生成 Allure JSON 结果 |
| **通知** | 飞书机器人 Webhook | 失败时自动推送结果到飞书群 |
| **OCR** | Tesseract + pytesseract | 识别屏幕进度条等动态元素 |

## 3. 目录结构

```
zlt_vscode/
├── main.py                      # 项目入口：自动发现 + 批量执行 + 生成报告
│
├── core/                        # 框架核心
│   ├── browser_manager.py       # VS Code 启动、CDP 连接、Playwright 生命周期
│   ├── base_page.py             # 页面对象基类（截图、DOM、进度监听、日期设置）
│   ├── base_test_case.py        # 测试用例基类（浏览器管理、Allure、飞书通知）
│   ├── test_discoverer.py       # 自动发现 cases/ 目录下的测试用例
│   ├── test_runner.py           # 批量测试执行器（统一收集结果、仅失败时通知）
│   ├── allure_reporter.py       # 自研 Allure 报告生成器（JSON 结果 + HTML 报告）
│   └── logger.py                # 日志模块（控制台 + 按天文件）
│
├── pages/                       # 页面对象（PO 模式）
│   ├── login_page.py            # 登录页面（点击智量通图标、账号密码登录、状态检测）
│   ├── strategy_page.py         # 策略研究页面（创建策略、回测设置、删除策略）
│   └── data_download_page.py    # 数据下载页面（交易所勾选、月份选择、更新数据）
│
├── cases/                       # 测试用例
│   ├── base_test_case.py        # 用例基类（同 core/base_test_case.py）
│   ├── test_strategy_create.py  # 策略创建/删除/回测测试
│   ├── test_data_download.py    # 数据下载流程测试
│   └── test_runner.py           # 批量执行器
│
├── config/                      # 配置
│   ├── settings.py              # 全局配置（VS Code 路径、登录信息、飞书 Webhook、目录）
│   ├── coords.py                # 策略模块屏幕坐标配置
│   └── coords_data_download.py  # 数据下载模块屏幕坐标配置
│
├── utils/                       # 工具库
│   ├── pyautogui_helper.py      # 屏幕点击、输入、滑动、截图
│   ├── ocr_helper.py            # 区域截图 + OCR 识别 + 百分比提取
│   ├── feishu_notifier.py       # 飞书机器人通知（单条/批量/表格）
│   ├── faker_utils.py           # 假数据生成（策略名称、描述、股票代码等）
│   └── window_utils.py          # Windows API 窗口查找与定位
│
├── requirements.txt             # Python 依赖
└── measure_coords.py            # 坐标测量辅助脚本
```

## 4. 核心设计

### 4.1 浏览器管理（BrowserManager）

- **启动 VS Code**：以调试模式启动（`--remote-debugging-port=9222`），自动清理端口占用进程
- **CDP 连接**：使用 Playwright 的 `connect_over_cdp()` 连接到 VS Code
- **窗口定位**：启动后通过 Windows API 将窗口固定到指定位置和大小
- **生命周期**：支持 async context manager (`async with`)

```python
from core.browser_manager import BrowserManager

async with BrowserManager() as bm:
    page = bm.page
    # 执行测试...
```

### 4.2 页面对象基类（BasePage）

封装了测试中最常用的操作：

| 方法 | 功能 |
|------|------|
| `wait_for(ms)` | 等待指定毫秒 |
| `find_and_click(selectors)` | 依次尝试多个 CSS 选择器，找到可见元素并点击 |
| `screenshot(filename)` | 页面截图并附加到 Allure 报告 |
| `dump_dom(filename)` | 保存当前页面 HTML |
| `wait_for_progress(selector)` | 轮询监听页面进度条（支持 style.width/aria-valuenow/textContent/value） |
| `wait_for_progress_by_ocr(region)` | 通过区域截图 + OCR 识别监听进度 |
| `set_date_picker(placeholder, date)` | 设置 Element Plus 日期选择器（多种策略兼容） |

### 4.3 测试用例基类（BaseTestCase）

所有测试用例的父类，提供标准生命周期：

```python
class TestSomething(BaseTestCase):
    async def test_something(self) -> bool:
        self._start_test("测试名称", description="...", labels={...})
        try:
            playwright, browser, page = await self._setup()
            # ... 测试步骤 ...
            self._set_passed()
            return True
        except Exception as e:
            self._set_failed(str(e))
            return False
        finally:
            await self._teardown()
```

**批量模式**：当通过 `TestRunner` 执行时，`batch_mode=True`，用例结束不发单条通知，由 runner 最后统一发送表格通知（仅失败时）。

### 4.4 测试自动发现（discover_tests）

扫描 `cases/` 目录，按以下约定收集用例：
- 文件名以 `test_` 开头
- 类名以 `Test` 开头
- 方法名以 `test` 开头（不区分大小写）
- 方法签名：`async def test_xxx(self) -> bool`

### 4.5 批量执行器（TestRunner）

```python
runner = TestRunner()
runner.add("创建策略", TestStrategyCreate().test_create)
runner.add("数据下载", TestDataDownload().zztest_download)
all_passed = await runner.run()  # 统一发送失败通知
```

### 4.6 自研 Allure 报告器（AllureReporter）

不依赖 pytest，手动管理测试生命周期：

```python
from core.allure_reporter import allure

allure.start_test(name="测试名", description="...", labels={...})
with allure.step("步骤名"):
    # 执行操作...
allure.stop_test("passed")  # 或 "failed", error_msg
allure.generate_report()     # 生成 HTML 报告
```

支持：测试步骤嵌套、文本附件、截图附件。

### 4.7 飞书通知（FeishuNotifier）

- **单条通知**：每个用例执行完发送结果卡片
- **批量通知**：表格形式汇总所有用例（仅失败时发送）
- **格式**：Markdown 卡片，包含状态、耗时、错误详情

### 4.8 OCR 进度监听（OCRHelper）

用于识别屏幕上无 DOM 结构的进度条：

```python
from utils.ocr_helper import recognize_region, extract_percentage

text = recognize_region((x, y, width, height))  # 区域截图 + OCR
pct = extract_percentage(text)                    # 提取百分比
```

支持灰度化、二值化预处理，多种 Tesseract config 自动回退。

## 5. 配置说明

### 5.1 全局配置（config/settings.py）

| 配置项 | 说明 |
|--------|------|
| `VS_CODE_PATH` | VS Code 可执行文件路径 |
| `DEBUG_PORT` | 远程调试端口（默认 9222） |
| `WINDOW_POS` | 窗口位置和大小 |
| `PHONE` / `PASSWORD` | 智量通登录账号 |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook URL |
| `LOG_DIR` / `REPORT_DIR` / `SCREENSHOT_DIR` | 输出目录 |

### 5.2 坐标配置

所有 pyautogui 操作依赖屏幕绝对坐标，基于 VS Code 窗口固定在 `(480, 170)`、大小 `1420x840`。

**测量坐标**：使用 `measure_coords.py` 脚本，点击屏幕任意位置获取坐标。

坐标分模块管理：
- `config/coords.py` -- 策略模块坐标
- `config/coords_data_download.py` -- 数据下载模块坐标

## 6. 测试用例示例

### 6.1 策略创建 + 回测（test_strategy_create.py）

```python
class TestStrategyCreate(BaseTestCase):
    async def test_create(self) -> bool:
        """登录 -> 创建策略"""
        self._start_test(...)
        playwright, browser, page = await self._setup()

        login_page = LoginPage(page)
        await login_page.ensure_login()

        strategy_page = StrategyPage(page)
        await strategy_page.create_strategy_flow()  # 7 步流程

        self._set_passed()
        await self._teardown()
```

**StrategyPage 完整流程**：

| 流程 | 步骤 |
|------|------|
| `create_strategy_flow()` | 策略研究 -> 创建策略 -> 填名称 -> 选模板 -> 选分类 -> 填描述 -> 确认 |
| `delete_strategy_flow()` | 第一个策略 -> 三个点 -> 删除 -> 确认删除 |
| `backtest_settings_flow()` | 选频率 -> 撮合频率 -> 预加载K线 -> 开始日期 -> 结束日期 -> 初始资金 -> 运行回测 -> OCR监听进度 |
| `create_and_run_backtest_flow()` | 创建 + 回测 |

### 6.2 数据下载（test_data_download.py）

```python
class TestDataDownload(BaseTestCase):
    async def zztest_download(self) -> bool:
        """登录 -> 数据下载：下滑找菜单 -> 点数据下载 -> 选数据类型 -> 取消快照 -> 选月份 -> 更新"""
```

## 7. 运行方式

### 7.1 批量执行（推荐）

```bash
python main.py
```

流程：自动发现用例 -> 复用类实例执行 -> 仅失败时飞书通知 -> 生成 Allure 报告

### 7.2 单用例执行

```bash
python cases/test_strategy_create.py
python cases/test_data_download.py
```

## 8. 扩展指南

### 8.1 添加新页面

1. 在 `pages/` 新建页面对象，继承 `BasePage`
2. 封装页面操作（优先 Playwright locator，不行则用 pyautogui 坐标）
3. 在 `config/` 添加坐标配置（如需要）

### 8.2 添加新用例

1. 在 `cases/` 新建 `test_xxx.py`
2. 继承 `BaseTestCase`
3. 实现 `async def test_xxx(self) -> bool` 方法
4. 遵循 `_start_test` -> `_setup` -> 业务步骤 -> `_set_passed/_set_failed` -> `_teardown` 模式

### 8.3 注意事项

- **坐标敏感**：VS Code 窗口位置/大小变化会导致坐标失效，需重新测量
- **异步方法**：所有页面对象和用例方法均为 `async`
- **返回 bool**：用例方法必须返回 `True`/`False` 表示结果
- **方法命名**：以 `test` 开头才会被自动发现；以 `zztest` 开头表示暂时禁用（发现器会跳过，但可手动调用）
