"""Rate of Change Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class ROCStrategy(Strategy):
    """Rate of Change Momentum"""
    def __init__(self, params: Dict):
        super().__init__("ROCStrategy", params)
        self.period = params.get("period", 12)
        self.threshold = params.get("threshold", 5)
        self.rules = [{"type": "entry_long", "condition": "ROC crosses above threshold"},
                     {"type": "entry_short", "condition": "ROC crosses below -threshold"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        roc = 100 * price.pct_change(self.period)
        signals[(roc > self.threshold) & (roc.shift(1) <= self.threshold)] = 1
        signals[(roc < -self.threshold) & (roc.shift(1) >= -self.threshold)] = -1
        return signals
