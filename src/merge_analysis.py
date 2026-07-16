import pandas as pd
import utils

def main():
    # ==========================
    # 读取数据
    # ==========================
    stock_df = utils.load_csv("stock_data_cleaned.csv", "output")
    company_df = utils.load_csv("company_info.csv", "data")

    print("\n========== 股票数据预览 ==========")
    print(stock_df.head())
    print()
    stock_df.info()
    print("\n========== 公司信息数据预览 ==========")
    print(company_df.head())

    # ==========================
    # 数据合并（只保留在两个表中都有的）
    # ==========================
    merged_inner_df = pd.merge(
        stock_df,
        company_df,
        on="sector",
        how="inner"
    )
    print("\n========== inner合并后的数据预览 ==========")
    print(merged_inner_df.head())

    # ==========================
    # 数据合并（保留左表的所有记录）
    # ==========================
    merged_left_df = pd.merge(
        stock_df,
        company_df,
        on="sector",
        how="left"
    )
    print("\n========== left合并后的数据预览 ==========")
    print(merged_left_df.head())
    print()
    merged_left_df.info()

    # ==========================
    # 数据合并（保留所有记录）
    # ==========================
    merged_outer_df = pd.merge(
        stock_df,
        company_df,
        on="sector",
        how="outer"
    )
    print("\n========== outer合并后的数据预览 ==========")
    print(merged_outer_df.head())

    # =========================
    # 保存合并后的数据
    # =========================
    utils.save_csv(
        merged_left_df,
        "merged_data.csv",
        index=False,
    )

if __name__ == "__main__":
    main()