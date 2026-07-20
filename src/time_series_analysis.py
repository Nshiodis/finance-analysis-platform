import matplotlib.pyplot as plt
from stock_data import StockData

def main():
    # ==============
    # 读取数据
    # ==============

    stock = StockData("merged_data.csv")

    print("\n前五行数据")
    print(stock.head())
    print("\n表信息")
    stock.info()

    # ==============
    # 转换日期类型
    # ==============
    stock.to_datetime("date")
    print("\n转换后的数据类型")
    print(stock.dtypes())

    # ==============
    # 设置时间索引
    # ==============
    stock.set_index("date")
    print("\n设置时间索引")
    print(stock.head())

    # ==============
    # 排序
    # ==============
    stock.sort_index()
    print("\n已按索引排序")

    # ==============
    # 时间切片
    # ==============
    print("\n2024年1月的数据")
    print(stock.df.loc["2024-01"])
    print("\n2024年1月3号到6号的数据")
    print(stock.df.loc["2024-01-03":"2024-01-06"])

    # ==============
    # 按时间分组
    # ==============
    monthly_price_mean = stock.df["price"].resample("ME").mean()
    print("\n按月统计平均价格")
    print(monthly_price_mean)
    weekly_price_sum = stock.df["price"].resample("W-MON").sum()
    print("\n按周汇总（每周一为标签，求和）")
    print(weekly_price_sum)

    # ==============
    # 滚动窗口计算
    # ==============
    stock.df["price_ma3"] = stock.df["price"].rolling(window=3).mean()
    print("\n三日移动平均价格")
    print(stock.df[["price","price_ma3"]].head())

    # ==============
    # 保存结果
    # ==============
    stock.save_csv(
        "time_series_data.csv", 
        index=True,
    )

    # ==============
    # 画出价格和移动平均线
    # ==============
    plt.figure(figsize=(10, 6))
    plt.plot(stock.df.index, stock.df["price"], label="Price")
    plt.plot(stock.df.index, stock.df["price_ma3"], label="MA3")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    stock.save_plot(plt.gcf(), "price_ma3.png")
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()