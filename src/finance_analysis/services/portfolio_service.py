import numpy as np
from pathlib import Path

from finance_analysis.analysis.benchmark import Benchmark
from finance_analysis.analysis.evaluation import PerformanceEvaluator
from finance_analysis.config import DATABASE_PATH
from finance_analysis.exceptions import InvalidPortfolioError, PortfolioNotFoundError
from finance_analysis.models.portfolio import Portfolio
from finance_analysis.models.stock import StockData
from finance_analysis.repository.portfolio_repository import PortfolioRepository


class PortfolioService:
    """组合业务服务：校验 → 组装 → 算绩效"""

    def __init__(self, db_path: str | Path = DATABASE_PATH):
        self.repository = PortfolioRepository(db_path)


    def create_portfolio(self, weights: dict[str, float]) -> dict[str, int | dict[str, float]]:
        """创建组合：先校验，再入库"""
        if not weights:
            raise InvalidPortfolioError("投资组合不能为空")
        if any(w < 0 for w in weights.values()):
            raise InvalidPortfolioError("权重不能小于 0")
        if not np.isclose(sum(weights.values()), 1):
            raise InvalidPortfolioError("权重和必须为 1")

        portfolio_id = self.repository.create_portfolio(weights)
        return {"id": portfolio_id, "weights": weights}


    def get_portfolio_performance(self, portfolio_id: int) -> dict[str, int | float]:
        """查询组合绩效"""
        record = self.repository.get_portfolio(portfolio_id)
        if record is None:
            raise PortfolioNotFoundError(f"组合 {portfolio_id} 不存在")

        weights = record["weights"]

        # 组装 Portfolio：每只股票按日期索引对齐（纪律！）
        stocks: dict[StockData, float] = {}
        for symbol, weight in weights.items():
            stock = StockData.from_database(symbol)   # Day21 现成方法，从库里取数
            stock.date_index()                        # 关键：按日期建索引，别按行号对齐
            stocks[stock] = weight

        portfolio = Portfolio(stocks)                          # Day18 模型
        benchmark = Benchmark(StockData("000300.csv").date_index())   # Day19 写法
        evaluator = PerformanceEvaluator(portfolio, benchmark) # Day19 模型
        summary = evaluator.summary()

        return {
            "id": portfolio_id,
            "portfolio_total_return": float(summary["portfolio_total_return"]),
            "annualized_return": float(portfolio.calculate_annual_return()),
            "volatility": float(portfolio.calculate_annual_volatility()),
            "sharpe": float(portfolio.calculate_sharpe()),
            "benchmark_total_return": float(summary["benchmark_total_return"]),
            "excess_total_return": float(summary["excess_total_return"]),
        }
