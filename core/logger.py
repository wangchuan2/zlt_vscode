"""日志模块"""

import logging
import os
from datetime import datetime

from config.settings import LOG_DIR


def get_logger(name: str = "automation") -> logging.Logger:
    """获取配置好的日志记录器"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件输出 — 按天合并到同一个文件
    log_file = os.path.join(LOG_DIR, f"{datetime.now():%Y%m%d}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
