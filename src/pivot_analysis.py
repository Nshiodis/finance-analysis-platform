import pandas as pd
import utils

def main():
    # =========================
    # 读取数据
    # =========================
    df = utils.load_csv("stock_data_cleaned.csv", "output")
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
    utils.save_csv(
        sector_summary_table,
        "sector_summary.csv",
        index=True
    )
    utils.save_csv(
        pivot_market_table,
        "pivot_market_table.csv",
        index=True
    )
    
if __name__ == "__main__":
    main()