"""本地最小类型 stub：akshare（官方无类型标注，只覆盖项目用到的两个函数）。

签名与已安装版本（akshare 1.18.70）的实际定义一致，无 Any。
"""

import pandas as pd


def stock_zh_a_daily(
    symbol: str = "sh603843",
    start_date: str = "19900101",
    end_date: str = "21000118",
    adjust: str = "",
) -> pd.DataFrame: ...


def stock_zh_index_daily_em(
    symbol: str = "csi931151",
    start_date: str = "19900101",
    end_date: str = "20500101",
) -> pd.DataFrame: ...
