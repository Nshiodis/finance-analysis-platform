from finance_analysis.data.stock_pool  import StockPool
from finance_analysis.data.stock_data import StockData
import finance_analysis.visualization.visualization as visualization
import pandas as pd


def main():
    pool = StockPool(
        [
            "600519.csv",
            "300750.csv",
            "000858.csv",
        ]
    )


    # 股票风险比较
    risk_df = pd.DataFrame(pool.compare_risk())

    print(risk_df)


    # 排序
    risk_df = (
        risk_df.sort_values("sharpe",ascending=False)
    )

    print(risk_df)


    # 风险收益图
    visualization.plot_risk_return(risk_df)


    # 单股票回撤图
    stock: StockData = pool.stocks[0]
    stock.to_datetime("date").set_index("date")
    visualization.plot_drawdown(stock)

if __name__ == "__main__":
    main()