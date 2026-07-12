import pandas as pd
from pathlib import Path

def main():
    # =========================
    # 路径
    # =========================

    project_path = Path(__file__).resolve().parent.parent

    data_path = project_path / "data"
    output_path = project_path / "output"

    output_path.mkdir(exist_ok=True)

    # =========================
    # 读取数据
    # =========================

    file_path = data_path / "stock_data_cleaned.csv"

    df = pd.read_csv(file_path)

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

    output_file = output_path / "sector_analysis.csv"

    result_sorted.to_csv(
        output_file,
        index=False
    )

    print("\n========== 分析完成 ==========")
    print(f"分析结果已保存至：{output_file}")


if __name__ == "__main__":
    main()