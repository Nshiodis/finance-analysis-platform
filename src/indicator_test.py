from stock_data import StockData
import visualization


def main():

    stock = StockData(
        "600519.csv",
        folder="data"
    )

    (
        stock
        .to_datetime("date")
        .set_index("date")
        .sort_index()
    )

    stock.calculate_return()

    stock.calculate_ma(20)
    stock.calculate_ma(60)

    stock.calculate_rsi()
    stock.calculate_macd()

    print(stock.tail())

    stock.indicators_info()


    visualization.plot_price_indicator(
        stock.df,
        "600519",
        price_column="close",
        indicator_column="MA20"
    )

    visualization.plot_return_distribution(
        stock.df,
        "600519_return_distribution"
    )

    visualization.plot_rsi(
        stock.df,
        "600519_rsi"
    )

    visualization.plot_macd(
        stock.df,
        "600519_macd"
    )



if __name__ == "__main__":
    main()