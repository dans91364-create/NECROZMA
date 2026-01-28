"""Z-Score Mean Reversion Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class ZScoreReversion(Strategy):
    """Z-Score Mean Reversion"""
    def __init__(self, params: Dict):
        super().__init__("ZScoreReversion", params)
        self.period = params.get("period", 20)
        self.threshold = params.get("threshold", 2.0)
        self.rules = [{"type": "entry_long", "condition": "z-score < -2"},
                     {"type": "entry_short", "condition": "z-score > 2"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        mean = price.rolling(self.period).mean()
        std = price.rolling(self.period).std()
        zscore = (price - mean) / (std + EPSILON)
        signals[zscore < -self.threshold] = 1
        signals[zscore > self.threshold] = -1
        return signals

class PercentRank(Strategy):
    """Percentile Rank Mean Reversion"""
    def __init__(self, params: Dict):
        super().__init__("PercentRank", params)
        self.period = params.get("period", 100)
        self.low_pct = params.get("low_pct", 10)
        self.high_pct = params.get("high_pct", 90)
        self.rules = [{"type": "entry_long", "condition": "rank < 10th percentile"},
                     {"type": "entry_short", "condition": "rank > 90th percentile"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        pct_rank = price.rolling(self.period).apply(
            lambda x: (x < x.iloc[-1]).sum() / len(x) * 100 if len(x) > 0 else 50, raw=False)
        signals[pct_rank < self.low_pct] = 1
        signals[pct_rank > self.high_pct] = -1
        return signals
