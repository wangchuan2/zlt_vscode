"""坐标配置

说明：
- 以下坐标为屏幕绝对坐标（pyautogui 坐标系），基于 VS Code 窗口固定在 480,170 位置、分辨率 1080x840
- 如果调整了窗口位置或屏幕分辨率，需要重新用 measure_coords.py 测量
- 坐标格式：(x, y)，x 为水平方向（从左到右），y 为垂直方向（从上到下）
"""

COORDS = {
    # ---------- 登录相关 ----------
    "account_tab": (655, 297),       # 登录弹窗中"账号登录"标签页位置
    "phone_input": (604, 362),       # 手机号输入框位置
    "password_input": (584, 413),    # 密码输入框位置
    "login_button": (635, 455),      # "登录/注册"按钮位置

    # ---------- 策略研究入口 ----------
    "strategy_research": (568, 696), # 智量通侧边栏"策略研究"菜单项位置

    # ---------- 创建策略弹窗 ----------
    "create_strategy": (1136, 301),  # "创建策略"按钮位置（策略研究页面右上角）

    # ---------- 策略表单字段 ----------
    "strategy_name": (1216, 406),    # 策略名称输入框位置
    "strategy_template": (1224, 451),# "策略模板"下拉框位置（点击展开选项）
    "trade_template": (1257, 497),   # 下拉选项中"交易模板"项位置
    "category": (1219, 488),         # "分类"下拉框位置（点击展开选项）
    "category_common": (1049, 504),  # 下拉选项中"通用"分类项位置
    "description": (1222, 539),      # 策略描述文本输入框位置

    # ---------- 表单提交 ----------
    "strategy_confirm": (1589, 675), # "确定"按钮位置（创建策略弹窗右下角）

    "first_strategy": (899, 328),  # 策略列表中第一个策略卡片/行的位置（点击后进入策略详情或选中该行）

    # ---------- 策略列表操作（请用 measure_coords.py 测量后填入正确坐标）----------
    "three_dots": (1865, 383),           # TODO: 策略卡片/行右侧的"三个点"更多操作按钮位置
    "click_delete": (1806, 447),       # TODO: 点击删除按钮位置
    "confirm_delete": (1544, 666),          # 删除确认弹窗中"确定"按钮位置
    "open_strategy": (1680, 385),          # 打开策略

    # ---------- 回测设置 ----------
    "select_frequency": (1732, 382),             # "选择频率"下拉框位置
    "confirm_frequency": (974, 364),            # 频率下拉选项中确认项位置（如"15分钟"）
    "match_frequency": (979, 476),              # "撮合频率"下拉框位置
    "confirm_match_frequency": (1338, 477),      # 撮合频率下拉选项中确认项位置
    "preload_kline_input": (1042, 426),          # "预加载K线"输入框位置
    "backtest_start_date": (961, 459),          # "回测周期-开始时间"输入框位置
    "backtest_end_date": (1168, 458),            # "回测周期-结束时间"输入框位置
    "initial_capital": (1566, 463),              # "初始资金"输入框位置
    "run_backtest": (1865, 920),                 # "运行回测"按钮位置
    "run_backtest_details": (1151, 310),         # "详情"按钮位置

    # ---------- 日历面板交互（请用 measure_coords.py 测量后填入） ----------
    "calendar_prev_month": (1112, 506),   # 日历面板"向左"（上月）箭头按钮
    "calendar_next_month": (1128, 508),   # 日历面板"向右"（下月）箭头按钮
    "calendar_day_1": (1016, 601),        # 日历面板中"1"号日期单元格
    "calendar_day_10": (1306,637 ),       # 日历面板中"10"号日期单元格

    # ---------- 回测进度条 OCR 区域（请用 measure_coords.py 测量后填入） ----------
    #"backtest_progress_region": (left, top, right - left, bottom - top)
    #第一次测量位置左上角 left top  第二次测量位置右下角 right=x bottom=y
    "backtest_progress_region": (1081, 299, 41, 22),  # (left, top, width, height) 回测进度文字区域
    
}
