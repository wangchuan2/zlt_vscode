"""数据下载模块坐标配置

使用说明：
- 坐标为屏幕绝对坐标（pyautogui 坐标系）
- 如果调整了窗口位置或屏幕分辨率，需要重新用 measure_coords.py 测量
- 坐标格式：(x, y)，x 为水平方向（从左到右），y 为垂直方向（从上到下）
"""

COORDS_DATA = {
    # ---------- 下滑找菜单坐标 ----------
    "swipe_start": (818, 541),           # 长按起始坐标：智量通侧边栏区域
    "swipe_menu": (818, 593),            # 下滑后"数据下载"菜单坐标

    # ---------- 数据下载页面 ----------
    "data_download_menu": (666, 691),    # 智量通侧边栏"数据下载"菜单项
    "data_type_tab": (720, 223),             # "数据类型"标签/按钮

    # ---------- 交易所勾选 ----------
    "shenzhen_exchange": (637, 264),         # 深圳交易所
    "shenzhen_stock_snapshot": (677, 328),   # 深圳-股票快照勾选框
    "shenzhen_fund_snapshot": (678, 390),    # 深圳-基金快照勾选框

    "shanghai_exchange": (637, 409),         # 上海交易所
    "shanghai_stock_snapshot": (677, 470),   # 上海-股票快照勾选框
    "shanghai_fund_snapshot": (680, 535),    # 上海-基金快照勾选框

    # ---------- 月份与更新 ----------
    "april_data": (814, 315),                # 4月份数据
    "update_data_button": (1114, 229),        # 更新数据按钮
}
