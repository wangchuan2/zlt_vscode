import subprocess
import time
import requests
import asyncio
import sys

try:
    import pyautogui
except ImportError:
    print("请先安装 pyautogui: pip install pyautogui")
    sys.exit(1)

try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None

from playwright.async_api import async_playwright

from common import faker_tool

VS_CODE_PATH = r"E:\gongjubao\vscode\Microsoft VS Code\Code.exe"
DEBUG_PORT = 9222


# ==========================================
# 窗口位置配置（固定 VS Code 窗口位置）\
# ==========================================
WINDOW_POS = {
    "x": 480,    # (1920 - 960) / 2
    "y": 170,    # (1080 - 540) / 2
    "width": 1080,
    "height": 840,
}


# ==========================================
# 坐标配置区（用 measure_coords.py 测量填入）
# ==========================================
# 必须是屏幕绝对坐标（pyautogui 坐标系）
# ==========================================
COORDS = {
    "account_tab": (655, 297),    # ← "账号登录"标签屏幕坐标
    "phone_input": (604, 362),    # ← 手机号输入框屏幕坐标
    "password_input": (584, 413), # ← 密码输入框屏幕坐标
    "login_button": (635, 455),   # ← "登录/注册"按钮屏幕坐标
    "strategy_research": (568, 696),  # ← "策略研究"按钮屏幕坐标
    "create_strategy": (1136, 301),   # ← 创建策略按钮
    "strategy_name": (1033, 405),          # ← 策略名称输入框（请测量后填入）
    "strategy_template": (1045, 454),      # ← 策略模版按钮（请测量后填入）
    "trade_template": (1054, 497),         # ← 交易模版选项（请测量后填入）
    "category": (1056, 488),               # ← 分类按钮（请测量后填入）
    "category_common": (1049, 504),        # ← 通用选项（请测量后填入）
    "description": (1033, 535),            # ← 描述输入框（请测量后填入）
    "strategy_confirm": (1385, 682),            # ← 策略确定
}


# def clear_vscode_window_state():
#     """删除 VS Code 保存的窗口位置状态，恢复默认位置"""
#     import os
#     state_file = r"C:\temp\vscode_debug_profile\globalStorage\state.vscdb"
#     if os.path.exists(state_file):
#         try:
#             os.remove(state_file)
#             print("✅ 已清除窗口位置记忆")
#         except Exception as e:
#             print(f"⚠️ 清除窗口状态失败: {e}")


def find_vscode_window() -> int:
    """通过窗口标题和类名查找 VS Code 主窗口"""
    if ctypes is None:
        return 0

    found_hwnd = ctypes.c_void_p(0)

    def enum_callback(hwnd, extra):
        nonlocal found_hwnd
        if found_hwnd.value:
            return True
        if not ctypes.windll.user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
        if "Chrome_WidgetWin" not in buf.value:
            return True
        title_buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.GetWindowTextW(hwnd, title_buf, 512)
        if "Visual Studio Code" in title_buf.value:
            found_hwnd.value = hwnd
            return False
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)
    return found_hwnd.value or 0


def set_window_pos(hwnd: int, x: int, y: int, width: int, height: int):
    """使用 Windows API 设置窗口位置和大小"""
    if ctypes is None:
        return False

    if ctypes.windll.user32.IsWindow(ctypes.c_void_p(hwnd)) == 0:
        print(f"⚠️ hwnd={hwnd} 不是有效窗口")
        return False

    SW_SHOWNORMAL = 1
    ctypes.windll.user32.ShowWindow(ctypes.c_void_p(hwnd), ctypes.c_int(SW_SHOWNORMAL))

    SWP_NOZORDER = 0x0004
    SWP_SHOWWINDOW = 0x0040
    flags = SWP_NOZORDER | SWP_SHOWWINDOW

    result = ctypes.windll.user32.SetWindowPos(
        ctypes.c_void_p(hwnd),
        ctypes.c_void_p(0),
        ctypes.c_int(x),
        ctypes.c_int(y),
        ctypes.c_int(width),
        ctypes.c_int(height),
        ctypes.c_uint(flags),
    )
    if result == 0:
        err = ctypes.windll.kernel32.GetLastError()
        print(f"⚠️ SetWindowPos 失败，hwnd={hwnd}, GetLastError={err}")
    return result != 0


def start_vscode_with_debug():
    """启动 VS Code 并开启远程调试端口"""
    #clear_vscode_window_state()
    print(f"正在启动 VS Code (调试端口 {DEBUG_PORT})...")
    proc = subprocess.Popen(
        [
            VS_CODE_PATH,
            f"--remote-debugging-port={DEBUG_PORT}",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--user-data-dir=C:\\temp\\vscode_debug_profile",
            "--new-window",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        shell=False,
    )
    print(f"VS Code 进程 PID: {proc.pid}")
    print("等待调试端口就绪...")
    for i in range(30):
        try:
            resp = requests.get(f"http://localhost:{DEBUG_PORT}/json/list", timeout=2)
            if resp.status_code == 200:
                print(f"✅ 调试端口就绪，当前 {len(resp.json())} 个页面")
                # 设置固定窗口位置
                hwnd = find_vscode_window()
                if hwnd:
                    pos = WINDOW_POS
                    if set_window_pos(hwnd, pos["x"], pos["y"], pos["width"], pos["height"]):
                        print(f"✅ 窗口已固定到 ({pos['x']}, {pos['y']}) 大小 {pos['width']}x{pos['height']}")
                    else:
                        print("⚠️ 设置窗口位置失败")
                else:
                    print("⚠️ 未找到 VS Code 窗口")
                return proc
        except requests.exceptions.ConnectionError:
            print(f"  第 {i+1}/30 秒...")
        time.sleep(1)
    proc.terminate()
    raise TimeoutError("调试端口未就绪")


async def connect_to_vscode():
    """通过 CDP 连接 VS Code"""
    print(f"\n正在连接 CDP (端口 {DEBUG_PORT})...")
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")
    context = browser.contexts[0] if browser.contexts else None
    if not context:
        raise RuntimeError("无法获取 context")

    page = None
    for _ in range(20):
        for ctx_page in context.pages:
            try:
                if "Visual Studio Code" in await ctx_page.title() or "vscode-app" in ctx_page.url:
                    await ctx_page.evaluate("1+1")
                    page = ctx_page
                    print("✅ 已连接 VS Code 主页面")
                    break
            except Exception:
                pass
        if page:
            break
        await asyncio.sleep(0.5)

    if not page:
        raise RuntimeError("无法获取有效页面")
    return p, browser, page


def click_screen(x, y, label=""):
    """使用 pyautogui 在屏幕绝对坐标点击（同步操作）"""
    if x <= 0 or y <= 0:
        return False
    try:
        pyautogui.click(x, y)
        if label:
            print(f"✅ 已点击 [{label}] 屏幕坐标 ({x}, {y})")
        return True
    except Exception as e:
        if label:
            print(f"⚠️ 点击 [{label}] 失败: {e}")
        return False


def type_screen(x, y, text, label=""):
    """使用 pyautogui 在屏幕绝对坐标点击并输入（同步操作）"""
    if x <= 0 or y <= 0:
        return False
    try:
        import pyperclip
        pyautogui.click(x, y)
        time.sleep(0.3)
        # 先备份剪贴板
        original = pyperclip.paste()
        # 复制文本到剪贴板
        pyperclip.copy(text)
        time.sleep(0.1)
        # Ctrl+V 粘贴
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('v')
        pyautogui.keyUp('v')
        pyautogui.keyUp('ctrl')
        time.sleep(0.1)
        # 恢复剪贴板
        pyperclip.copy(original)
        if label:
            print(f"✅ 已在 [{label}] 输入: {text}")
        return True
    except Exception as e:
        if label:
            print(f"⚠️ 在 [{label}] 输入失败: {e}")
        return False


async def perform_login(page):
    """执行登录操作"""
    print("\n等待页面稳定...")
    await page.wait_for_timeout(5000)

    # 保存 DOM
    try:
        html = await page.content()
        with open("vscode_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📄 DOM 已保存")
    except Exception as e:
        print(f"⚠️ DOM 保存失败: {e}")

    # ========== 步骤1: 点击"智量通"图标（Playwright 选择器）==========
    print("\n--- 步骤1: 点击智量通图标 ---")
    found = False
    for sel in ['[aria-label="智量通"]', '[title*="智量通"]', 'text=智量通']:
        try:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                print(f"✅ 已点击智量通 ({sel})")
                found = True
                break
        except Exception:
            pass

    if not found:
        for i in range(3, 15):
            try:
                btn = page.locator(f'.activitybar .action-item:nth-child({i})').first
                if await btn.count() > 0:
                    await btn.click()
                    await asyncio.sleep(0.8)
                    if await page.locator('text=智量通用户管理').count() > 0:
                        print(f"✅ 在第 {i} 个位置找到智量通")
                        found = True
                        break
            except Exception:
                pass

    if not found:
        print("❌ 步骤1 失败")
        return False

    # 等待面板加载，同时让 VS Code 获得焦点
    await page.wait_for_timeout(3000)

    # ========== 检测是否已登录 ==========
    print("\n--- 检测登录状态 ---")

    #方法3：截图 + 打印HTML内容
    await page.screenshot(path="login_check.png")
    print("📸 登录检查截图已保存到 login_check.png")

    # html = await page.content()
    # print("=== page.content() 前 3000 字符 ===")
    # print(html[:3000])
    # print("=== page.content() 结束 ===")

    # 先枚举所有 frame，找到正确的定位方式
    print("\n--- 枚举所有 frame ---")
    for i, frame in enumerate(page.frames):
        try:
            url = frame.url[:100] if frame.url else "empty"
            print(f"  Frame {i}: url={url}")
        except Exception as e:
            print(f"  Frame {i}: 无法获取URL: {e}")

    already_logged_in = False
    try:
        # 逐个 frame 搜索"昵称"
        for i, frame in enumerate(page.frames):
            try:
                if await frame.locator("text=昵称").count() > 0:
                    already_logged_in = True
                    print(f"✅ Frame {i} 检测到已登录状态（存在 昵称）")
                    break
                elif await frame.get_by_text("个人中心").count() > 0:
                    already_logged_in = True
                    print(f"✅ Frame {i} 检测到已登录状态（存在 个人中心）")
                    break
            except Exception as e:
                print(f"  Frame {i} 检测异常: {e}")
        if not already_logged_in:
            print("❌ 所有 frame 均未检测到登录状态")
    except Exception as e:
        print(f"⚠️ 整体检测异常: {e}")

    if already_logged_in:
        print("⏭️ 已登录，跳过步骤2-5")
    else:
        # ========== 步骤2-5: 使用 pyautogui 屏幕绝对坐标操作 ==========
        print("\n--- 步骤2: 点击账号登录标签（屏幕坐标）---")
        x, y = COORDS["account_tab"]
        if not click_screen(x, y, "账号登录"):
            print("❌ 步骤2 失败")
            return False
        time.sleep(1)

        print("\n--- 步骤3: 输入手机号（屏幕坐标）---")
        x, y = COORDS["phone_input"]
        if not type_screen(x, y, "18162428572", "手机号"):
            print("❌ 步骤3 失败")
            return False
        time.sleep(0.5)

        print("\n--- 步骤4: 输入密码（屏幕坐标）---")
        x, y = COORDS["password_input"]
        if not type_screen(x, y, "111111", "密码"):
            print("❌ 步骤4 失败")
            return False
        time.sleep(0.5)

        print("\n--- 步骤5: 点击登录按钮（屏幕坐标）---")
        x, y = COORDS["login_button"]
        if not click_screen(x, y, "登录按钮"):
            print("❌ 步骤5 失败")
            return False
        time.sleep(3)

        
    print("\n--- 步骤6: 点击策略研究（屏幕坐标）---")
    x, y = COORDS["strategy_research"]
    if not click_screen(x, y, "策略研究"):
        print("❌ 步骤6 失败")
        return False
    time.sleep(2)
    print("\n--- 步骤7: 点击创建策略（屏幕坐标）---")
    x, y = COORDS["create_strategy"]
    if not click_screen(x, y, "创建策略"):
        print("❌ 步骤7 失败")
        return False
    time.sleep(2)
    print("\n--- 步骤8: 输入策略名称（屏幕坐标）---")
    x, y = COORDS["strategy_name"]
    if not type_screen(x, y, faker_tool.strategy_name(prefix="自动化"), "策略名称"):
        print("❌ 步骤8 失败")
        return False
    time.sleep(200)

    # ========== 步骤9: 选择策略模版 ----------
    print("\n--- 步骤9: 选择策略模版 → 交易模版（屏幕坐标）---")
    # x, y = COORDS["strategy_template"]
    # if not click_screen(x, y, "策略模版"):
    #     print("❌ 步骤9-1 失败")
    #     return False
    # time.sleep(1)
    # x, y = COORDS["trade_template"]
    # if not click_screen(x, y, "交易模版"):
    #     print("❌ 步骤9-2 失败")
    #     return False
    # time.sleep(1)

    # # ========== 步骤10: 选择分类 ----------
    # print("\n--- 步骤10: 选择分类 → 通用（屏幕坐标）---")
    # x, y = COORDS["category"]
    # if not click_screen(x, y, "分类"):
    #     print("❌ 步骤10-1 失败")
    #     return False
    # time.sleep(1)
    # x, y = COORDS["category_common"]
    # if not click_screen(x, y, "通用"):
    #     print("❌ 步骤10-2 失败")
    #     return False
    # time.sleep(1)

    # # ========== 步骤11: 输入描述 ----------
    # print("\n--- 步骤11: 输入描述（屏幕坐标）---")
    # x, y = COORDS["description"]
    # desc = faker_tool.strategy_description()
    # if not type_screen(x, y, desc, "描述"):
    #     print("❌ 步骤11 失败")
    #     return False
    # time.sleep(2)
    # # ========== 步骤11: 输入描述 ----------
    # print("\n--- 步骤12: 策略确定（屏幕坐标）---")
    # x, y = COORDS["strategy_confirm"]
    # if not click_screen(x, y, "策略确定"):
    #     print("❌ 步骤12 失败")
    #     return False
    # time.sleep(2)

    print("\n🎉 流程完成！")
    # 用 pyautogui 截图（截取整个屏幕）
    try:
        pyautogui.screenshot("login_result.png")
        print("📸 屏幕截图已保存到 login_result.png")
    except Exception as e:
        print(f"⚠️ 截图失败: {e}")
    return True


async def main():
    proc = None
    playwright = None
    browser = None

    try:
        resp = requests.get(f"http://localhost:{DEBUG_PORT}/json/list", timeout=2)
        vscode_running = resp.status_code == 200
    except Exception:
        vscode_running = False

    if not vscode_running:
        proc = start_vscode_with_debug()

    try:
        playwright, browser, page = await connect_to_vscode()
        await perform_login(page)
        print("\n保持运行 10 秒...")
        await asyncio.sleep(100)
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser:
            try:
                await browser.disconnect()
            except Exception:
                pass
        if playwright:
            try:
                await playwright.stop()
            except Exception:
                pass
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
