import pandas as pd
import finance_analysis.analysis.indicators as indicators
import finance_analysis.analysis.risk as risk
from finance_analysis.repository.stock_repository import StockRepository
import finance_analysis.utils.utils as utils
import matplotlib.pyplot as plt

class StockData:
    """股票数据对象"""

    def __init__(self, file_name: str, folder: str = "data"):
        self.file_name = file_name
        self.symbol = None

        self.df = utils.load_csv(file_name, folder)
        self.raw_columns = self.df.columns.tolist()


    @classmethod
    def from_dataframe(cls, df):
        stock = cls.__new__(cls)

        stock.file_name = None
        stock.df = df
        stock.raw_columns = df.columns.tolist()

        if "symbol" in df.columns:
            stock.symbol = df["symbol"].iloc[0]
        else:
            stock.symbol = None

        return stock

    
    @classmethod
    def from_database(
            cls,
            symbol: str
    ):

        repo = StockRepository(
            utils.get_database_path()
        )

        df = repo.get_stock(symbol)

        if df.empty:
            raise ValueError(
                f"股票 {symbol} 不存在"
            )        

        return cls.from_dataframe(df)
    
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
    
    def tail(self, n: int = 5):
        """查看数据后几行"""
        return self.df.tail(n)
    
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


    def date_index(self):
        """将索引转换为日期时间"""
        return self.to_datetime("date").set_index("date")
# =============================================================================
# 数据保存
# =============================================================================
    def save_plot(self, file_name: str):
        """保存图表"""
        utils.save_plot(plt.gcf(), file_name)
        return self

    def save_csv(self, file_name: str, index: bool = True):
        """保存数据"""
        utils.save_csv(self.df, file_name, index)
        return self

# =============================================================================
# 技术指标
# =============================================================================
    def indicators_info(self):
        """查看新增指标列名"""
        print("新增指标列名:")
        print(
            [
                col for col in self.df.columns
                if col not in self.raw_columns
            ]
        )
    
    def calculate_return(self):
        """计算收益率"""
        return indicators.calculate_return(self.df)

    def calculate_total_return(self):
        """计算总收益率"""
        return indicators.calculate_total_return(self.df)
    
    def calculate_ma(self, window: int = 20):
        """计算移动平均"""
        return indicators.calculate_ma(
            self.df,
            window
        )

    def calculate_rsi(
            self, 
            window: int = 14, 
            method: str = "wilder"
    ) -> pd.DataFrame:
        """计算RSI"""
        return indicators.calculate_rsi(
            self.df,
            window,
            method
        )

    def calculate_macd(self):
        """计算MACD"""
        return indicators.calculate_macd(self.df)

    def calculate_volatility(self):
        """计算年化波动率"""
        return risk.calculate_volatility(
            self.df
        )

    def calculate_max_drawdown(self):
        """计算最大回撤"""
        return risk.calculate_max_drawdown(
            self.df
        )

    def calculate_sharpe_ratio(self):
        """计算夏普比率"""
        return risk.calculate_sharpe_ratio(
            self.df
        )
