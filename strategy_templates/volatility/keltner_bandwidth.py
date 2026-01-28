"""Keltner and Donchian Width"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class KeltnerBandwidth(Strategy):
    def __init__(self, params: Dict):
        super().__init__("KeltnerBandwidth", params)
        self.period, self.mult = params.get("period", 20), params.get("multiplier", 2.0)
        self.rules = [{"type": "entry_long", "condition": "Keltner width expanding"}, {"type": "entry_short", "condition": "width contracting"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            tr = (df["high"] - df["low"]).rolling(self.period).mean()
            width = 2 * self.mult * tr
            signals[(width > width.shift(1))], signals[(width < width.shift(1))] = 1, -1
        return signals
class DonchianWidth(Strategy):
    def __init__(self, params: Dict):
        super().__init__("DonchianWidth", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "Donchian width expanding"}, {"type": "entry_short", "condition": "width narrow then breakout"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns:
            width = df["high"].rolling(self.period).max() - df["low"].rolling(self.period).min()
            signals[(width > width.shift(1))], signals[(width < width.rolling(5).mean())] = 1, -1
        return signals
