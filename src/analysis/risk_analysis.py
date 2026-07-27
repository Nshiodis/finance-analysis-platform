import pandas as pd


def calculate_volatility(df: pd.DataFrame) -> float:
    """计算年化波动率"""
    daily_volatility = df["return"].std()

    annual_volatility = daily_volatility * (252 ** 0.5)

    return annual_volatility


def calculate_drawdown(df):
    """计算回撤序列"""
    cumulative_return = (1 + df["return"]).cumprod()

    historical_max = cumulative_return.cummax()

    drawdown = (
        cumulative_return - historical_max
    ) / historical_max

    return drawdown


def calculate_max_drawdown(df: pd.DataFrame) -> float:
    """计算最大回撤"""

    drawdown = calculate_drawdown(df)

    return drawdown.min()


def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0
) -> float:
    """
    计算夏普比率

    参数：
        df: 股票数据 DataFrame
        risk_free_rate: 无风险利率，默认值为0

    返回：
        夏普比率
    """
    excess_return = df["return"] - risk_free_rate
    annual_excess_return = excess_return.mean() * 252

    annual_volatility = df["return"].std() * (252 ** 0.5)

    sharpe_ratio = annual_excess_return / annual_volatility

    return sharpe_ratio
