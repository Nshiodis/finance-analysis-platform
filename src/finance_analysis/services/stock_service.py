from datetime import date

import pandas as pd

from finance_analysis.config import DATABASE_PATH
from finance_analysis.exceptions import StockNotFoundError, StockNoDataError, InvalidDateRangeError
from finance_analysis.models.stock import StockData
from finance_analysis.repository.stock_repository import StockRepository


class StockService:
    """股票业务服务：负责取数、判断、计算指标的编排"""

    def __init__(self, db_path=DATABASE_PATH):
        self.repository = StockRepository(db_path)


    def _get_stock_data(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
    ) -> StockData:
        """获取股票数据"""
        if start is not None and end is not None and start > end:
            raise InvalidDateRangeError("开始日期不能晚于结束日期")
        
        df = self.repository.get_stock(symbol, start, end)

        if df.empty:
            if start is None and end is None:
                raise StockNotFoundError(f"股票 {symbol} 不存在")
            full_df = self.repository.get_stock(symbol)
            if full_df.empty:
                raise StockNotFoundError(f"股票 {symbol} 不存在")
            raise StockNoDataError(f"股票 {symbol} 在指定日期范围内没有数据")

        stock = StockData.from_dataframe(df)

        return stock

    
    def get_stock_metrics(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
    ) -> dict:
        """获取股票数据"""
        stock = self._get_stock_data(symbol, start, end)

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


    def list_stocks(self) -> list[str]:
        """获取所有股票代码"""
        return self.repository.get_all_symbols()


    def get_stock_risk(
        self,
        symbol: str,
        start: date | None = None,
        end: date | None = None,
    ) -> dict:
        """获取股票风险指标"""
        stock = self._get_stock_data(symbol, start, end)

        stock.calculate_return()

        return {
            "symbol": symbol,
            "rows": len(stock.df),
            "total_return": float(stock.calculate_total_return()),
            "volatility": float(stock.calculate_volatility()),
            "sharpe": float(stock.calculate_sharpe_ratio()),
            "max_drawdown": float(stock.calculate_max_drawdown())
        }


    def get_stock_indicators(
        self,
        symbol: str,
        window: int = 20,
        start: date | None = None,
        end: date | None = None,
    ) -> dict:
        """获取股票技术指标序列(MA/RSI/MACD)"""
        stock = self._get_stock_data(symbol, start, end)

        # 三个函数都会往 df 里"加列"：
        stock.calculate_ma(window)      # 加列 MA{window}
        stock.calculate_rsi(window)     # 加列 RSI
        stock.calculate_macd()          # 加列 DIF/DEA/MACD（返回的三元组这里用不到）

        df = stock.df

        # 日期统一转成 "YYYY-MM-DD" 字符串
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # 只挑需要的列，再去掉指标为 NaN 的行（MA 开头空 window-1 行）
        indicator_df = df[["date", f"MA{window}", "RSI", "DIF", "DEA", "MACD"]]
        indicator_df = indicator_df.dropna()

        # 列名转小写：适配在 API 层做，不动底层 indicators.py
        indicator_df = indicator_df.rename(columns={
            f"MA{window}": "ma",
            "RSI": "rsi",
            "DIF": "dif",
            "DEA": "dea",
            "MACD": "macd",
        })

        # 每行变成一个 dict，组成列表
        series = indicator_df.to_dict("records")

        return {
            "symbol": symbol,
            "window": window,
            "rows": len(series),
            "series": series,
        }
