import pandas as pd
import matplotlib.pyplot as plt
import utils

def main():
    # ==============
    # 读取数据
    # ==============

    df = utils.load_csv("merged_data.csv")

    print("\n前五行数据")
    print(df.head())
    print("\n表信息")
    df.info()

    # ==============
    # 转换日期类型
    # ==============
    df["date"] = pd.to_datetime(df["date"])
    print("\n转换后的数据类型")
    print(df.dtypes)

    # ==============
    # 设置时间索引
    # ==============
    df = df.set_index("date")
    print("\n设置时间索引")
    print(df.head())

    # ==============
    # 排序
    # ==============
    df = df.sort_index()
    print("\n已按索引排序")

    # ==============
    # 时间切片
    # ==============
    print("\n2024年1月的数据")
    print(df.loc["2024-01"])
    print("\n2024年1月3号到6号的数据")
    print(df.loc["2024-01-03":"2024-01-06"])

    # ==============
    # 按时间分组
    # ==============
    monthly_price_mean = df["price"].resample("ME").mean()
    print("\n按月统计平均价格")
    print(monthly_price_mean)
    weekly_price_sum = df["price"].resample("W-MON").sum()
    print("\n按周汇总（每周一为标签，求和）")
    print(weekly_price_sum)

    # ==============
    # 滚动窗口计算
    # ==============
    df["price_ma3"] = df["price"].rolling(window=3).mean()
    print("\n三日移动平均价格")
    print(df[["price","price_ma3"]].head())

    # ==============
    # 保存结果
    # ==============
    utils.save_csv(
        df, 
        "time_series_data.csv", 
        index=True,
    )

    # ==============
    # 画出价格和移动平均线
    # ==============
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df["price"], label="Price")
    plt.plot(df.index, df["price_ma3"], label="MA3")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    utils.save_plot(plt.gcf(), "price_ma3.png")
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()