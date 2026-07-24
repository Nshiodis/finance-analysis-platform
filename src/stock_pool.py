from stock_data import StockData


class StockPool:
    """股票池"""

    def __init__(self, files, folder="data"):
        self.stocks = []

        for file in files:
            stock = StockData(
                file_name=file,
                folder=folder
            )
            self.stocks.append(stock)


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
            df = stock.df
            total_return = float(
                (df["return"] + 1).prod() - 1
            )
            result.append({
                "stock": stock.file_name,
                "total_return": total_return
            })
        return result


    def sort_by_total_return(self) -> list:
        """按总收益排序"""
        result = self.get_summary()
        result.sort(key=lambda x: x["total_return"], reverse=True)
        return result