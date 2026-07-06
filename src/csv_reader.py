# 读取 data 文件夹下的 CSV 文件并显示基本信息和统计数据

from pathlib import Path
import pandas as pd

# 找到 data 文件夹
data_path = Path(__file__).resolve().parent.parent / "data"

# 循环读取 CSV 文件
for file in data_path.glob("*.csv"):
    print(f"=== 读取文件: {file.name} ===")
    
    # 读取数据
    df = pd.read_csv(file)
    
    print("=== 前五行数据 ===")
    print(df.head())

    print("\n=== 数据基本信息 ===")
    df.info()

    print("\n=== 数值统计 ===")
    print(df.describe())

