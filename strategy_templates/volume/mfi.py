"""Money Flow Index Volume Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class MFIVolume(Strategy):
    def __init__(self, params: Dict):
        super().__init__("MFIVolume", params)
        self.period, self.oversold, self.overbought = params.get("period", 14), params.get("oversold", 20), params.get("overbought", 80)
        self.rules = [{"type": "entry_long", "condition": "MFI < 20"}, {"type": "entry_short", "condition": "MFI > 80"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            tp = (df["high"] + df["low"] + df.get("close", df.get("mid_price"))) / 3
            mf = tp * df["volume"]
            pmf = mf.where(tp > tp.shift(1), 0).rolling(self.period).sum()
            nmf = mf.where(tp < tp.shift(1), 0).rolling(self.period).sum()
            mfi = 100 - 100 / (1 + pmf / (nmf + EPSILON))
            signals[mfi < self.oversold], signals[mfi > self.overbought] = 1, -1
        return signals
