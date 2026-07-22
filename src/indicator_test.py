from stock_data import StockData
import matplotlib.pyplot as plt


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

    print(stock.head(30))

    plt.figure(figsize=(12,6))

    plt.plot(
        stock.df.index,
        stock.df["close"],
        label="close"
    )

    plt.plot(
        stock.df.index,
        stock.df["MA20"],
        label="MA20"
    )

    plt.plot(
        stock.df.index,
        stock.df["MA60"],
        label="MA60"
    )

    plt.title("贵州茅台600519", fontproperties="SimHei")
    plt.xlabel("Date")
    plt.ylabel("Price")

    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()

    stock.save_plot(plt.gcf(), "600519.png")

    plt.show()

    mean_return = stock.df["return"].mean()
    plt.figure(figsize=(12,6))

    plt.hist(
        stock.df["return"].dropna(),
        bins=50
    )

    plt.axvline(
        mean_return,
        color="red",
        linestyle="--",
        label=f"Mean: {mean_return:.4f}"
    )

    plt.legend()
    plt.title("600519 Daily Return Distribution")
    plt.xlabel("Return")
    plt.ylabel("Frequency")
    stock.save_plot(plt.gcf(), "600519_return_distribution.png")
    plt.show()


    

if __name__ == "__main__":
    main()