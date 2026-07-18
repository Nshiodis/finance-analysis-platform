import pandas as pd
import utils

class StockData:
    """股票数据对象"""

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.df = utils.load_csv(file_name)

    def info(self):
        """查看数据基本信息"""
        self.df.info()

    def head(self, n: int = 5):
        """查看数据前几行"""
        return self.df.head(n)

    def dtypes(self):
        """查看各列数据类型"""
        print(self.df.dtypes)
    
    def to_datetime(self, column: str):
        """将指定列转换为日期时间"""
        self.df[column] = pd.to_datetime(self.df[column])

    def set_index(self, column: str):
        """设置指定列为索引"""
        self.df = self.df.set_index(column)

    def sort_index(self):
        """按索引排序"""
        self.df = self.df.sort_index()

    def save_csv(self, file_name: str, index: bool = True):
        """保存数据"""
        utils.save_csv(self.df, file_name, index)
    
    def save_plot(self, fig, file_name):
        """保存图表"""
        utils.save_plot(fig, file_name)
