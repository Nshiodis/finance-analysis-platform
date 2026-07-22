from pathlib import Path
import akshare as ak

def download_stock(
        symbol: str,
        start_date: str,
        end_date: str,
        file_name: str,
):
    """
    下载股票历史数据

    symbol:
        股票代码，例如 sh600519

    start_date:
        开始日期

    end_date:
        结束日期

    file_name:
        保存文件名
    """
    project_path = Path(__file__).resolve().parent.parent

    data_path = project_path / "data"

    data_path.mkdir(exist_ok=True)

    stock = ak.stock_zh_a_daily(
        symbol=symbol, 
        start_date=start_date, 
        end_date=end_date,
    )

    if stock.empty:
        print("下载失败，没有数据")
        return


    stock.to_csv(
        data_path / file_name,
        index=False,
    )

    print("下载完成")


def main():

    download_stock(
        symbol="sh600519",
        start_date="20200101",
        end_date="20251231",
        file_name="600519.csv"
    )


if __name__ == "__main__":
    main()