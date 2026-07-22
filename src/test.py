from stock_data import StockData


def main():

    stock = StockData(
        "600519.csv",
        folder="data"
    )
    stock.to_datetime("date")
    print(stock.head())

    stock.info()


if __name__ == "__main__":
    main()