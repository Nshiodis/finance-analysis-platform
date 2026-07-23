import pandas as pd

def calculate_return(df: pd.DataFrame):
    """计算收益率"""
    df["return"] = df["close"].pct_change()
    return df

def calculate_ma(df: pd.DataFrame, window: int = 20):
    """计算移动平均"""
    df[f"MA{window}"] = (
        df["close"]
        .rolling(window)
        .mean()
    )
    return df

def calculate_rsi(
        df: pd.DataFrame,
        window: int = 14,
        method: str = "wilder"
    ) -> pd.DataFrame:
    """计算RSI"""

    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    if method == "sma":
        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()
    elif method == "ema":
        avg_gain = gain.ewm(
            span=window,
            adjust=False
        ).mean()
        avg_loss = loss.ewm(
            span=window,
            adjust=False
        ).mean()
    elif method == "wilder":
        avg_gain = gain.ewm(
            alpha=1/window,
            adjust=False
        ).mean()
        avg_loss = loss.ewm(
            alpha=1/window,
            adjust=False
        ).mean()
    else:
        raise ValueError(
            "method must be 'sma' or 'ema' or 'wilder'"
        )

    rs = avg_gain / avg_loss.replace(0, 1e-10)

    df["RSI"] = 100 - (100 / (1 + rs))

    return df

def calculate_macd(df: pd.DataFrame):
    """计算MACD"""

    ema12 = df["close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = df["close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["DIF"] = ema12 - ema26

    df["DEA"] = df["DIF"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["MACD"] = df["DIF"] - df["DEA"]
    return df