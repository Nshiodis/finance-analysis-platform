import pandas as pd
from pathlib import Path

def main():
    # =========================
    # 路径
    # =========================
    project_path = Path(__file__).resolve().parent.parent

    data_path = project_path / "data"
    output_path = project_path / "output"

    file_path = data_path / "stock_data_cleaned.csv"
    output_path.mkdir(exist_ok=True)

    # =========================
    # 读取数据
    # =========================
    df = pd.read_csv(file_path)
    print("\n========== 数据预览 ==========")
    print(df.head())

    # =========================
    # 按行业统计平均股价
    # =========================
    price_mean_table = pd.pivot_table(
        df,
        index="sector",
        values="price",
        aggfunc="mean"
    )
    print("\n========== 按行业统计平均股价 ==========")
    print(price_mean_table)

    # =========================
    # 多个统计指标
    # =========================
    sector_summary_table = pd.pivot_table(
        df,
        index="sector",
        values=["price", "volume"],
        aggfunc={
            "price": "mean",
            "volume": "sum"
        }
    )
    print("\n========== 按行业统计平均价格和总交易量 ==========")
    print(sector_summary_table)

    # =========================
    # 填充空值
    # =========================
    price_mean_0_table = pd.pivot_table(
        df,
        index="sector",
        values="price",
        aggfunc="mean",
        fill_value=0
    )
    print("\n========== 按行业统计平均股价（空值填充为0） ==========")
    print(price_mean_0_table)

    # =========================
    # 交叉统计
    # =========================
    pivot_market_table = pd.pivot_table(
        df,
        index="sector",
        columns="market",
        values="price",
        aggfunc="mean"
    )
    print("\n========== 按行业和市场统计平均股价 ==========")
    print(pivot_market_table)

    # =========================
    # 保存结果
    # =========================
    sector_summary_table.to_csv(output_path / "sector_summary.csv")
    pivot_market_table.to_csv(output_path / "pivot_market_table.csv")

    print("\nPivot Market Table 已保存到 output/pivot_market_table.csv")
    print("\nSector Summary 已保存到 output/sector_summary.csv")


if __name__ == "__main__":
    main()