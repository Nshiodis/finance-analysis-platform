import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

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
    # 数据统计
    # =========================

    print("\n========== 描述性统计 ==========")
    print(df.describe())

    print("\n========== 基本统计 ==========")

    print(f"平均价格：{df['price'].mean():.2f}")
    print(f"最高价格：{df['price'].max():.2f}")
    print(f"最低价格：{df['price'].min():.2f}")
    print(f"成交总量：{df['volume'].sum():,}")

    # =========================
    # 分类统计
    # =========================

    print("\n========== 行业股票数量 ==========")
    print(df["sector"].value_counts())

    print("\n========== 市场股票数量 ==========")
    print(df["market"].value_counts())

    # =========================
    # 每日平均价格（折线图）
    # =========================

    daily_price = df.groupby("date")["price"].mean()

    plt.figure(figsize=(10, 6))

    plt.plot(
        daily_price.index,
        daily_price.values,
        marker="o"
    )

    plt.title("Average Stock Price by Date")
    plt.xlabel("Date")
    plt.ylabel("Average Price")

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        output_path / "daily_average_price.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    # =========================
    # 各行业平均价格（柱状图）
    # =========================

    sector_price = df.groupby("sector")["price"].mean()

    plt.figure(figsize=(8, 6))

    plt.bar(
        sector_price.index,
        sector_price.values
    )

    plt.title("Average Price by Sector")
    plt.xlabel("Sector")
    plt.ylabel("Average Price")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        output_path / "sector_average_price.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    # =========================
    # 股票价格分布（直方图）
    # =========================

    plt.figure(figsize=(8, 6))

    plt.hist(
        df["price"],
        bins=10,
        edgecolor="black"
    )

    plt.title("Price Distribution")
    plt.xlabel("Price")
    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.savefig(
        output_path / "price_distribution.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    # =========================
    # 价格 VS 成交量（散点图）
    # =========================

    plt.figure(figsize=(8, 6))

    plt.scatter(
        df["price"],
        df["volume"]
    )

    plt.title("Price vs Volume")
    plt.xlabel("Price")
    plt.ylabel("Volume")

    plt.tight_layout()

    plt.savefig(
        output_path / "price_vs_volume.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    # =========================
    # 行业平均成交量（柱状图）
    # =========================

    sector_volume = df.groupby("sector")["volume"].mean()

    plt.figure(figsize=(8, 6))

    plt.bar(
        sector_volume.index,
        sector_volume.values
    )

    plt.title("Average Volume by Sector")
    plt.xlabel("Sector")
    plt.ylabel("Average Volume")

    plt.xticks(rotation=20)

    plt.tight_layout()

    plt.savefig(
        output_path / "sector_average_volume.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    print("\n========== 可视化完成 ==========")
    print(f"图片已保存到：{output_path}")


if __name__ == "__main__":
    main()