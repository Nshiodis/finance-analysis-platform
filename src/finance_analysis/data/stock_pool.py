from finance_analysis.data.stock_data import StockData


class StockPool:
    """股票池"""

    def __init__(self, files, folder="data"):

        self.stocks: list[StockData] = []

        for file in files:
            stock = StockData(
                file_name=file,
                folder=folder
            )
            self.stocks.append(stock)


    @classmethod
    def from_stocks(
            cls,
            stocks: list[StockData]
    ):
        """根据 StockData 对象列表创建股票池"""

        pool = cls.__new__(cls)

        pool.stocks = stocks

        return pool   


    @classmethod
    def from_database(
            cls,
            symbols: list[str]
    ):
        """从数据库创建股票池"""

        stocks = []

        for symbol in symbols:

            stock = StockData.from_database(
                symbol
            )

            stocks.append(stock)

        return cls.from_stocks(stocks)

    
    def set_index(self, index_col="date") -> None:
        """设置股票池的索引"""
        for stock in self.stocks:
            stock.to_datetime(index_col)
            stock.set_index(index_col)
            stock.sort_index()


    def calculate_returns(self) -> None:
        """计算股票池的收益率"""
        for stock in self.stocks:
            stock.calculate_return()


    def get_summary(self) -> list:
        """比较收益"""
        result = []
        for stock in self.stocks:
            result.append({
                "stock": stock.file_name,
                "total_return": stock.calculate_total_return()
            })
        return result


    def sort_by_total_return(self) -> list:
        """按总收益排序"""
        result = self.get_summary()
        result.sort(key=lambda x: x["total_return"], reverse=True)
        return result


    def compare_risk(self):
        """比较风险"""
        result = []

        for stock in self.stocks:

            if "return" not in stock.df.columns:
                stock.calculate_return()

            risk_info = {
                "stock": stock.file_name or stock.symbol,
                "total_return": stock.calculate_total_return(),
                "volatility": stock.calculate_volatility(),
                "max_drawdown": stock.calculate_max_drawdown(),
                "sharpe": stock.calculate_sharpe_ratio()
                }
            result.append(risk_info)

        return result

