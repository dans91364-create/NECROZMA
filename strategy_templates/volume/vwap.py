"""VWAP Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class VWAPStrategy(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VWAPStrategy", params)
        self.rules = [{"type": "entry_long", "condition": "price crosses above VWAP"}, {"type": "entry_short", "condition": "price crosses below VWAP"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            vwap = (price * df["volume"]).cumsum() / (df["volume"].cumsum() + EPSILON)
            signals[(price > vwap) & (price.shift(1) <= vwap.shift(1))], signals[(price < vwap) & (price.shift(1) >= vwap.shift(1))] = 1, -1
        return signals
class VWAPBreakout(Strategy):
    def __init__(self, params: Dict):
        super().__init__("VWAPBreakout", params)
        self.std_mult = params.get("std_mult", 2.0)
        self.rules = [{"type": "entry_long", "condition": "price > VWAP + 2*std"}, {"type": "entry_short", "condition": "price < VWAP - 2*std"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "volume" in df.columns:
            vwap = (price * df["volume"]).cumsum() / (df["volume"].cumsum() + EPSILON)
            vwap_std = ((price - vwap) ** 2 * df["volume"]).cumsum() / (df["volume"].cumsum() + EPSILON)
            vwap_std = vwap_std ** 0.5
            signals[price > vwap + self.std_mult * vwap_std], signals[price < vwap - self.std_mult * vwap_std] = 1, -1
        return signals
