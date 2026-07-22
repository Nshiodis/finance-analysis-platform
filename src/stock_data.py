import pandas as pd
import indicators
import utils

class StockData:
    """股票数据对象"""

    def __init__(self, file_name: str, folder: str = "output"):
        self.file_name = file_name
        self.df = utils.load_csv(file_name, folder)
# =============================================================================
# 数据基本信息
# =============================================================================

    def info(self):
        """查看数据基本信息"""
        self.df.info()

    def describe(self):
        """查看数据统计摘要"""
        return self.df.describe()

    def columns(self):
        """查看数据列名"""
        return self.df.columns
    
    def shape(self):
        """查看数据形状"""
        return self.df.shape
    
    def head(self, n: int = 5):
        """查看数据前几行"""
        return self.df.head(n)

    def dtypes(self):
        """查看各列数据类型"""
        return self.df.dtypes
# =============================================================================
# 数据清理
# =============================================================================
    
    def clean(self):
        """清理数据"""
        self.df = self.df.drop_duplicates()
        self.df = self.df.dropna()
        return self
    
# =============================================================================
# 数据转换
# =============================================================================
    def to_datetime(self, column: str):
        """将指定列转换为日期时间"""
        self.df[column] = pd.to_datetime(self.df[column])
        return self
# =============================================================================
# 数据索引
# =============================================================================
    
    def set_index(self, column: str):
        """设置指定列为索引"""
        self.df = self.df.set_index(column)
        return self

    def sort_index(self):
        """按索引排序"""
        self.df = self.df.sort_index()
        return self
    
# =============================================================================
# 数据保存
# =============================================================================
    def save_plot(self, fig, file_name):
        """保存图表"""
        utils.save_plot(fig, file_name)
        return self

    def save_csv(self, file_name: str, index: bool = True):
        """保存数据"""
        utils.save_csv(self.df, file_name, index)
        return self

# =============================================================================
# 技术指标
# =============================================================================
    def calculate_return(self):
        """计算收益率"""
        self.df = indicators.calculate_return(self.df)

    def calculate_ma(self, window: int = 20):
        """计算移动平均"""
        self.df = indicators.calculate_ma(
            self.df,
            window
        )