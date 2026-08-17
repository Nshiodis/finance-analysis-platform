class StockNotFoundError(ValueError):
    """股票不存在"""


class StockNoDataError(ValueError):
    """股票指定区间数据为空"""