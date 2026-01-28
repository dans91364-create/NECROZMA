"""Range-based Volatility Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy
class NR4Strategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("NR4Strategy", params)
        self.rules = [{"type": "entry_long", "condition": "NR4 then upside breakout"}, {"type": "entry_short", "condition": "NR4 then downside breakout"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            range_val = df["high"] - df["low"]
            nr4 = range_val == range_val.rolling(4).min()
            price = df.get("close", df.get("mid_price"))
            signals[nr4.shift(1) & (price > price.shift(1))], signals[nr4.shift(1) & (price < price.shift(1))] = 1, -1
        return signals
class NR7Strategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("NR7Strategy", params)
        self.rules = [{"type": "entry_long", "condition": "NR7 then upside breakout"}, {"type": "entry_short", "condition": "NR7 then downside breakout"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            range_val = df["high"] - df["low"]
            nr7 = range_val == range_val.rolling(7).min()
            price = df.get("close", df.get("mid_price"))
            signals[nr7.shift(1) & (price > price.shift(1))], signals[nr7.shift(1) & (price < price.shift(1))] = 1, -1
        return signals
class InsideBarBreakout(Strategy):
    def __init__(self, params: Dict):
        super().__init__("InsideBarBreakout", params)
        self.rules = [{"type": "entry_long", "condition": "inside bar then break high"}, {"type": "entry_short", "condition": "inside bar then break low"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            inside = (df["high"] < df["high"].shift(1)) & (df["low"] > df["low"].shift(1))
            price = df.get("close", df.get("mid_price"))
            signals[inside.shift(1) & (price > df["high"].shift(1))], signals[inside.shift(1) & (price < df["low"].shift(1))] = 1, -1
        return signals
