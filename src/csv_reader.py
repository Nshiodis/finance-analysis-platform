from pathlib import Path
import pandas as pd

#1.找到data文件夹
data_path = Path(__file__).resolve().parent.parent / "data"

#2.找到csv文件
file_path = data_path / "test.csv"

df = pd.read_csv(file_path)

print(df.head())
print("数据读取成功")