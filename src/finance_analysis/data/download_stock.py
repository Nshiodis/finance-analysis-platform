import logging
from pathlib import Path

import akshare as ak

from finance_analysis.config import settings


logger = logging.getLogger(__name__)


def download_stock(
        symbol: str,
        start_date: str,
        end_date: str,
        file_name: str,
) -> None:
    """
    下载股票历史数据

    symbol:
        股票代码，例如 sh600519

    start_date:
        开始日期

    end_date:
        结束日期

    file_name:
        保存文件名
    """
    data_path = Path(settings.data_path)
    data_path.mkdir(parents=True, exist_ok=True)

    stock = ak.stock_zh_a_daily(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date,
    )

    if stock.empty:
        logger.warning("下载失败，没有数据：%s", symbol)
        return

    stock.to_csv(
        data_path / file_name,
        index=False,
    )

    logger.info("下载完成：%s", data_path / file_name)


def download_index(
        symbol: str,
        start_date: str,
        end_date: str,
        file_name: str,
) -> None:
    """
    下载指数历史数据

    symbol:
        指数代码，例如 sh000300

    start_date:
        开始日期

    end_date:
        结束日期

    file_name:
        保存文件名
    """
    data_path = Path(settings.data_path)
    data_path.mkdir(parents=True, exist_ok=True)

    index = ak.stock_zh_index_daily_em(
        symbol,
        start_date=start_date,
        end_date=end_date,
    )

    if index.empty:
        logger.warning("下载失败，没有数据：%s", symbol)
        return

    index.to_csv(
        data_path / file_name,
        index=False,
    )

    logger.info("下载完成：%s", data_path / file_name)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    download_index(
        symbol="sh000300",
        start_date="20200101",
        end_date="20251231",
        file_name="000300.csv"
    )

if __name__ == "__main__":
    main()
