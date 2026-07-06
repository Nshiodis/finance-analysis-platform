# 读取 data 文件夹下的所有 txt 文件，并打印内容

from pathlib import Path

data_path = Path(__file__).resolve().parent.parent / "data"

for file in data_path.glob("*.txt"):
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"=== {file.name} ===")
    print(text)