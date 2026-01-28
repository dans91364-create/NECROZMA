"""DeMarker Indicator Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class DeMarker(Strategy):
    """DeMarker Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("DeMarker", params)
        self.period = params.get("period", 14)
        self.oversold = params.get("oversold", 0.3)
        self.overbought = params.get("overbought", 0.7)
        self.rules = [{"type": "entry_long", "condition": "DeMarker < 0.3"},
                     {"type": "entry_short", "condition": "DeMarker > 0.7"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            de_max = (high - high.shift(1)).where(high > high.shift(1), 0)
            de_min = (low.shift(1) - low).where(low < low.shift(1), 0)
            demarker = de_max.rolling(self.period).mean() / (
                de_max.rolling(self.period).mean() + de_min.rolling(self.period).mean() + EPSILON)
            signals[demarker < self.oversold] = 1
            signals[demarker > self.overbought] = -1
        return signals
