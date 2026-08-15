import numpy as np
import pandas as pd
from finance_analysis.analysis.risk import calculate_sharpe_ratio
from finance_analysis.models.stock import StockData

class Portfolio:
    """
    投资组合类
    """

    def __init__(self, stocks: dict[StockData, float]):
        """
        Args:
            stocks:
                {
                    StockData对象: 权重
                }
        """
        weight_sum = sum(stocks.values())

        if not stocks:
            raise ValueError("投资组合不能为空")

        if not np.isclose(weight_sum,1):
            raise ValueError("权重和必须为1")

        for weight in stocks.values():

            if weight < 0:
                raise ValueError("权重不能小于0")
            
        self.stocks = stocks

            # 缓存组合收益率
        self._returns = None


    def calculate_return(self) -> pd.Series:
        """
        计算投资组合的收益率
        """
        if self._returns is not None:
            return self._returns
        
        portfolio_return = None

        for stock, weight in self.stocks.items():

            weighted_return = stock.calculate_return() * weight  

            if portfolio_return is None:
                portfolio_return = weighted_return
            else:
                portfolio_return += weighted_return

        self._returns = portfolio_return
        
        return self._returns


    def calculate_total_return(self) -> float:
        """
        计算投资组合的总收益率
        """
        returns = self.calculate_return()
        portfolio_total_return = (
            (1 + returns)
            .cumprod()
            .iloc[-1]
            - 1
        )
        return portfolio_total_return


    def calculate_annual_return(self) -> float:
        """
        计算年化收益率
        """

        total_return = self.calculate_total_return()

        days = len(
            self.calculate_return()
        )

        annual_return = (
            (1 + total_return)
            **
            (252 / days)
            - 1
        )

        return annual_return


    def calculate_daily_volatility(self) -> float:
        """
        计算每日波动率
        """

        returns = self.calculate_return()

        return returns.std()

    
    def calculate_annual_volatility(self) -> float:
        """
        计算年化波动率
        """

        daily_volatility = (
            self.calculate_daily_volatility()
        )

        return (
            daily_volatility
            *
            np.sqrt(252)
        )


    def calculate_sharpe(self, risk_free_rate: float = 0.015) -> float:
        """
        计算夏普比率
        Args:
            risk_free_rate: 年化无风险利率, 默认值为0.015
        """

        returns = self.calculate_return()

        df = returns.to_frame(
            name="return"
        )

        return calculate_sharpe_ratio(
            df,
            risk_free_rate
        )


    def portfolio_summary(self) -> pd.DataFrame:
        """
        计算投资组合的摘要信息
        """
        summary = {
            "total_return": self.calculate_total_return(),
            "annual_return": self.calculate_annual_return(),
            "daily_volatility": self.calculate_daily_volatility(),
            "annual_volatility": self.calculate_annual_volatility(),
            "sharpe": self.calculate_sharpe(),
        }

        return pd.DataFrame(summary, index=["portfolio"])
