from stock_pool import StockPool
import visualization


def main():
    pool = StockPool(
        ["600519.csv", "300750.csv"],
        folder="data"
    )
    pool.set_index("date")
    
    pool.calculate_returns()

    result = pool.sort_by_total_return()

    print(result)

    visualization.plot_compare(pool)


if __name__ == "__main__":
    main()
