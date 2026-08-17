import pandas as pd
from matplotlib.figure import Figure

import logging
from finance_analysis.config import PROJECT_ROOT, OUTPUT_PATH

logger = logging.getLogger(__name__)


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
    file_path = PROJECT_ROOT / folder / file_name

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
    output_path = OUTPUT_PATH
    df.to_csv(
        output_path / file_name,
        index=index,
    )
    logger.info("%s 已保存至: %s", file_name, output_path / file_name)

def save_plot(
    fig: Figure, 
    file_name: str, 
)-> None:
    """
    保存 matplotlib 图表 到output目录下

    :param fig: matplotlib Figure
    :param file_name: 文件名
    """
    output_path = OUTPUT_PATH
    fig.savefig(
        output_path / file_name,
        dpi=300,
        bbox_inches="tight",
    )
    logger.info("已保存文件: %s", output_path / file_name)
