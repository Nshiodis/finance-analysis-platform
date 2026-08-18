from datetime import date

from finance_analysis.config import DATABASE_PATH
from finance_analysis.exceptions import StockNotFoundError, StockNoDataError
from finance_analysis.models.stock import StockData
from finance_analysis.repository.stock_repository import StockRepository


class StockService:
    """股票业务服务：负责取数、判断、计算指标的编排"""

    def __init__(self, db_path=DATABASE_PATH):
        self.repository = StockRepository(db_path)


    def get_stock_metrics(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
    ) -> dict:
        """获取股票数据"""
        df = self.repository.get_stock(symbol, start, end)

        if df.empty:
            if start is None and end is None:
                raise StockNotFoundError(f"股票 {symbol} 不存在")
            full_df = self.repository.get_stock(symbol)
            if full_df.empty:
                raise StockNotFoundError(f"股票 {symbol} 不存在")
            raise StockNoDataError(f"股票 {symbol} 在指定日期范围内没有数据")

        stock = StockData.from_dataframe(df)

        stock.calculate_return()

        return {
            "symbol": symbol,
            "rows": len(stock.df),
            "latest_close": float(stock.df["close"].iloc[-1]),
            "total_return": float(stock.calculate_total_return()),
            "volatility": float(stock.calculate_volatility()),
            "sharpe": float(stock.calculate_sharpe_ratio()),
            "max_drawdown": float(stock.calculate_max_drawdown())
        }
