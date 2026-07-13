import pandas as pd
from pathlib import Path

def main():
    # ==========================
    # 读取数据
    # ==========================
    project_path = Path(__file__).resolve().parent.parent
    
    data_path = project_path / "data"
    
    stock_df = pd.read_csv(data_path / "stock_data_cleaned.csv")
    company_df = pd.read_csv(data_path / "company_info.csv")

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
    output_path = project_path / "output"
    output_path.mkdir(exist_ok=True)

    merged_left_df.to_csv(
        output_path / "merged_data.csv",
        index=False
    )

    print("\n========== 保存成功 ==========")
    print(output_path / "merged_data.csv")

if __name__ == "__main__":
    main()