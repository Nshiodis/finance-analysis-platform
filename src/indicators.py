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
