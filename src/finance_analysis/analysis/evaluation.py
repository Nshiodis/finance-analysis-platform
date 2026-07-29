from finance_analysis.analysis.benchmark import Benchmark
from finance_analysis.analysis.portfolio import Portfolio


class PerformanceEvaluator:
    """性能评估器"""

    def __init__(self, portfolio: Portfolio, benchmark: Benchmark):
        self.portfolio = portfolio
        self.benchmark = benchmark


    def get_returns(self):
        """获取收益序列"""

        portfolio_return = (
            self.portfolio.calculate_return()
            )

        benchmark_return = (
            self.benchmark.calculate_return()
            )

        return (
            portfolio_return,
            benchmark_return
            )


    def calculate_excess_return(self):
        """计算超额收益率"""

        portfolio_return, benchmark_return = self.get_returns()

        excess_return = (
            portfolio_return - benchmark_return
            )

        return excess_return


    def summary(self):
        """返回性能评估摘要"""

        return {

            "portfolio_total_return":
                float(
                    self.portfolio.calculate_total_return()
                    ),
            "benchmark_total_return":
                float(
                    self.benchmark.calculate_total_return()
                    ),

            "excess_total_return":
                float(
                    self.portfolio.calculate_total_return()
                    -
                    self.benchmark.calculate_total_return()
                )

        }
