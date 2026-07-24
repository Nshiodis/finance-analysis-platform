import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import utils


def plot_price_indicator(
    df,
    file_name: str,
    price_column="close",
    indicator_column="MA20",
):
    """
    绘制价格与技术指标
    
    参数:
        df: 股票数据DataFrame
        price_column: 价格列，默认close
        indicator_column: 指标列，默认MA20
        file_name: 图片文件名
    """

    plt.figure(figsize=(12, 6))

    plt.plot(
        df.index,
        df[price_column],
        label=price_column
    )

    plt.plot(
        df.index,
        df[indicator_column],
        label=indicator_column
    )

    plt.title(
        f"{price_column} and {indicator_column}"
    )

    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()

    utils.save_plot(plt.gcf(), file_name)

    plt.show()


def plot_return_distribution(
    df,
    file_name: str,
):
    """
    绘制收益率分布直方图
    
    参数:
        df: 股票数据DataFrame
        file_name: 图片文件名
    """
    plt.figure(figsize=(12, 6))

    plt.hist(
        df["return"].dropna(),
        bins=50
    )

    mean_return = df["return"].mean()
    plt.axvline(
        mean_return,
        color="red",
        linestyle="--",
        label=f"Mean: {mean_return:.4f}"
    )

    plt.legend()
    plt.title("Return Distribution")
    plt.xlabel("Return")
    plt.ylabel("Frequency")    
    utils.save_plot(plt.gcf(), file_name)
    plt.show()

def plot_rsi(
    df,
    file_name: str,
):
    """
    绘制RSI指标
    
    参数:
        df: 股票数据DataFrame
        file_name: 图片文件名
    """
    plt.figure(figsize=(12, 6))

    plt.plot(
        df.index,
        df["RSI"],
        label="RSI"
    )

    plt.axhline(
        70,
        linestyle="--",
        label="Overbought(70)"
    )

    plt.axhline(
        30,
        linestyle="--",
        label="Oversold(30)"
    )

    plt.title("RSI Indicator")

    plt.title(
        "RSI Indicator"
    )

    plt.ylim(0,100)

    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()

    utils.save_plot(plt.gcf(), file_name)

    plt.show()


def plot_macd(
    df,
    file_name: str,
):
    """
    绘制MACD指标
    
    参数:
        df: 股票数据DataFrame
        file_name: 图片文件名
    """
    plt.figure(figsize=(12, 6))

    plt.plot(
        df.index,
        df["DIF"],
        label="DIF"
    )

    plt.plot(
        df.index,
        df["DEA"],
        label="DEA"
    )

    colors = [
        "red" if value >= 0 else "green"
        for value in df["MACD"]
    ]
    plt.bar(
        df.index,
        df["MACD"],
        color=colors,
    )

    plt.axhline(
        0,
        linestyle="--"
    )
    plt.title("MACD Indicator")

    red_patch = Patch(
        color="red",
        label="MACD Positive"
    )

    green_patch = Patch(
        color="green",
        label="MACD Negative"
    )

    plt.legend(
        handles=[
            plt.Line2D([], [], label="DIF"),
            plt.Line2D([], [], label="DEA"),
            red_patch,
            green_patch
        ]
    )
    plt.xticks(rotation=45)

    plt.tight_layout()

    utils.save_plot(plt.gcf(), file_name)

    plt.show()


def plot_compare(stock_pool):
    """
    绘制股票池比较收盘价
    
    参数:
        stock_pool: 股票池对象
    """
    plt.figure(figsize=(12, 6))
    for stock in stock_pool.stocks:
        plt.plot(
            stock.df.index,
            stock.df["close"],
            label=stock.file_name.replace(".csv", "")
        )
    plt.title("Close Price Comparison")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    utils.save_plot(plt.gcf(), "compare_close_price")
    plt.show()