"""
鼠标坐标测量工具
运行后，将鼠标移到 VS Code 的目标元素上，按 Ctrl+C 停止
"""

import time
import sys

try:
    import pyautogui
except ImportError:
    print("请先安装 pyautogui: pip install pyautogui")
    sys.exit(1)


def main():
    print("=" * 50)
    print("鼠标坐标实时测量工具")
    print("=" * 50)
    print("\n使用方法：")
    print("  1. 切换到 VS Code 窗口")
    print("  2. 将鼠标移到目标元素上")
    print("  3. 查看下方输出的坐标")
    print("  4. 填入 config/coords.py 的 COORDS 中")
    print("  5. 按 Ctrl+C 停止\n")
    print("-" * 50)

    try:
        while True:
            x, y = pyautogui.position()
            print(f"\r当前鼠标位置: X = {x:4d}, Y = {y:4d}    ", end="", flush=True)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n\n已停止测量。")
        print(f"最后记录的位置: X = {x}, Y = {y}")


if __name__ == "__main__":
    main()
