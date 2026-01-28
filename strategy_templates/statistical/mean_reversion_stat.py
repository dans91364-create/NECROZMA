"""Statistical Trading Strategies"""
import pandas as pd
import numpy as np
from typing import Dict
from ..base import Strategy, EPSILON

class MeanReversionOU(Strategy):
    """Ornstein-Uhlenbeck Process"""
    def __init__(self, params: Dict):
        super().__init__("MeanReversionOU", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "OU process buy signal"}, {"type": "entry_short", "condition": "OU process sell signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Statistical measure using rolling window
        mean, std = price.rolling(self.period).mean(), price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -2], signals[zscore > 2] = 1, -1
        return signals

