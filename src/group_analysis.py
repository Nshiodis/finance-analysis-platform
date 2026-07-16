import pandas as pd
import utils

def main():
    # =========================
    # 读取数据
    # =========================
    df = utils.load_csv("stock_data_cleaned.csv", "output")
    
    # 日期转换
    df["date"] = pd.to_datetime(df["date"])

    print("\n========== 数据预览 ==========")
    print(df.head())

    # =========================
    # 每个行业平均价格
    # =========================

    print("\n========== 每个行业平均价格 ==========")

    print(
        df.groupby("sector")["price"].mean()
    )

    # =========================
    # 每个行业总成交量
    # =========================

    print("\n========== 每个行业总成交量 ==========")

    print(
        df.groupby("sector")["volume"].sum()
    )

    # =========================
    # 每个行业股票数量
    # =========================

    print("\n========== 每个行业股票数量 ==========")

    print(
        df.groupby("sector")["stock"].nunique()
    )

    # =========================
    # 每个市场平均价格
    # =========================

    print("\n========== 每个市场平均价格 ==========")

    print(
        df.groupby("market")["price"].mean()
    )

    # =========================
    # 行业综合统计
    # =========================

    print("\n========== 行业综合统计 ==========")

    result = (
        df.groupby("sector")
        .agg(
            avg_price=("price", "mean"),
            max_price=("price", "max"),
            min_price=("price", "min"),
            total_volume=("volume", "sum"),
            stock_count=("stock", "nunique")
        )
        .reset_index()
    )

    print(result)

    # =========================
    # 按平均价格排序
    # =========================

    print("\n========== 按平均价格排序 ==========")

    result_sorted = result.sort_values(
        by="avg_price",
        ascending=False
    )

    print(result_sorted)

    # =========================
    # 最终分析结果
    # =========================

    print("\n========== 行业分析报告 ==========")

    print(
        result_sorted[
            [
                "sector",
                "avg_price",
                "max_price",
                "min_price",
                "stock_count",
                "total_volume"
            ]
        ]
    )

    # =========================
    # 保存分析结果
    # =========================

    utils.save_csv(
        result_sorted,
        "sector_analysis.csv",
        index=False,
    )

if __name__ == "__main__":
    main()