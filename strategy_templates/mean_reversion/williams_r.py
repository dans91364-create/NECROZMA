"""Williams %R Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class WilliamsR(Strategy):
    """Williams %R Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("WilliamsR", params)
        self.period = params.get("period", 14)
        self.oversold = params.get("oversold", -80)
        self.overbought = params.get("overbought", -20)
        self.rules = [{"type": "entry_long", "condition": "%R crosses above -80"},
                     {"type": "entry_short", "condition": "%R crosses below -20"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high = df["high"]
            low = df["low"]
            close = df.get("close", df.get("mid_price"))
            highest_high = high.rolling(self.period).max()
            lowest_low = low.rolling(self.period).min()
            williams_r = -100 * (highest_high - close) / ((highest_high - lowest_low) + EPSILON)
            signals[(williams_r > self.oversold) & (williams_r.shift(1) <= self.oversold)] = 1
            signals[(williams_r < self.overbought) & (williams_r.shift(1) >= self.overbought)] = -1
        return signals
