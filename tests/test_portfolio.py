from finance_analysis.models.stock import StockData
from finance_analysis.models.portfolio import Portfolio
import finance_analysis.visualization.visualization as visualization

def main():

    stock1 = StockData(file_name="000858.csv").to_datetime("date").set_index("date")
    stock2 = StockData(file_name="300750.csv").to_datetime("date").set_index("date")
    stock3 = StockData(file_name="600519.csv").to_datetime("date").set_index("date")

    portfolio = Portfolio(
        {
            stock1: 0.3,
            stock2: 0.4,
            stock3: 0.3
        }
    )

    print(portfolio.portfolio_summary())

    visualization.plot_portfolio_curve(portfolio)

    visualization.plot_portfolio_return_distribution(portfolio)



if __name__ == "__main__":
    main()
