from finance_analysis.analysis.evaluation import PerformanceEvaluator
from finance_analysis.models.portfolio import Portfolio
from finance_analysis.analysis.benchmark import Benchmark
from finance_analysis.models.stock import StockData
from finance_analysis.visualization.visualization import plot_performance_curve


def main():
    benchmark = Benchmark(StockData("000300.csv").date_index())

    stock1 = StockData(file_name="000858.csv").date_index()
    stock2 = StockData(file_name="300750.csv").date_index()
    stock3 = StockData(file_name="600519.csv").date_index()

    portfolio = Portfolio(
        {
            stock1: 0.3,
            stock2: 0.4,
            stock3: 0.3
        }
    )

    evaluator = PerformanceEvaluator(
        portfolio,
        benchmark
    )

    print(evaluator.summary())

    plot_performance_curve(portfolio, benchmark)


if __name__ == "__main__":
    main()
