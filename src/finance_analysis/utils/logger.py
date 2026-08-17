import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from finance_analysis.config import LOG_PATH, LOG_LEVEL


def setup_logging() -> None:
    """配置全局日志：控制台 + 文件（轮转）"""

    log_path = Path(LOG_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. 日志格式：时间戳 [级别] 模块名: 消息
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 2. 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 3. 文件输出（轮转）
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,             # 保留最近3个日志文件
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # 4. 一次性应用到根 logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        handlers=[console_handler, file_handler],
    )