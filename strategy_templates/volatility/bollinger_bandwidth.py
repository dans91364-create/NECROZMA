"""Bollinger Bandwidth Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class BollingerBandwidth(Strategy):
    def __init__(self, params: Dict):
        super().__init__("BollingerBandwidth", params)
        self.period, self.std_dev, self.threshold = params.get("period", 20), params.get("std_dev", 2.0), params.get("threshold", 0.05)
        self.rules = [{"type": "entry_long", "condition": "bandwidth expanding"}, {"type": "entry_short", "condition": "bandwidth contracting then reversing"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        sma, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        bandwidth = (2 * self.std_dev * std) / (sma + EPSILON)
        signals[(bandwidth > bandwidth.shift(1)) & (bandwidth.shift(1) < self.threshold)], signals[(bandwidth < bandwidth.shift(1)) & (bandwidth.shift(1) < self.threshold)] = 1, -1
        return signals
