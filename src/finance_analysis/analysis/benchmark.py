from finance_analysis.models.stock import StockData


class Benchmark:
    """市场基准类"""

    def __init__(self, stock_data: StockData):
        self.stock_data = stock_data


    def calculate_return(self):
        """计算市场基准收益率"""

        return self.stock_data.calculate_return()


    def calculate_total_return(self):
        """计算市场基准总收益率"""

        return self.stock_data.calculate_total_return()
    
