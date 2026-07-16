from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd

def get_project_path() -> Path:
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent

def get_data_path() -> Path:
    """获取数据目录"""
    return get_project_path() / "data"

def get_output_path() -> Path:
    """获取输出目录"""
    output_path = get_project_path() / "output"
    output_path.mkdir(exist_ok=True)
    return output_path

def load_csv(
    file_name: str, 
    folder: str = "output",
) -> pd.DataFrame:
    """
    加载CSV文件

    :param file_name: 文件名
    :param folder: 文件所在目录(默认output)
    :return: pandas DataFrame
    """
    file_path = get_project_path() / folder / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"找不到文件：{file_path}")
    return pd.read_csv(file_path)   

def save_csv(
    df: pd.DataFrame, 
    file_name: str, 
    index: bool = True,
)-> None:
    """
    保存CSV文件 到output目录下

    :param df: pandas DataFrame
    :param file_name: 文件名
    :param index: 是否包含索引(默认True)
    """
    output_path = get_output_path()
    df.to_csv(
        output_path / file_name,
        index=index,
    )
    print(f"{file_name} 已保存至: {output_path / file_name}")

def save_plot(
    fig: Figure, 
    file_name: str, 
)-> None:
    """
    保存 matplotlib 图表 到output目录下

    :param fig: matplotlib Figure
    :param file_name: 文件名
    """
    output_path = get_output_path()
    fig.savefig(
        output_path / file_name,
        dpi=300,
        bbox_inches="tight",
    )
    print(f"已保存文件: {output_path / file_name}")
