"""本地最小类型 stub：akshare（官方无类型标注）。"""

import pandas as pd


def stock_zh_a_daily(
    symbol: str,
    start_date: str = "19900101",
    end_date: str = "20500101",
    adjust: str = "",
) -> pd.DataFrame: ...


def stock_zh_index_daily_em(
    symbol: str,
    start_date: str = "20000101",
    end_date: str = "20500101",
) -> pd.DataFrame: ...
