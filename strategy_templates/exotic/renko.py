"""Exotic Chart and Order Flow Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class RenkoStrategy(Strategy):
    """Renko Charts"""
    def __init__(self, params: Dict):
        super().__init__("RenkoStrategy", params)
        self.threshold = params.get("threshold", 0.5)
        self.rules = [{"type": "entry_long", "condition": "brick-based charting bullish"}, {"type": "entry_short", "condition": "brick-based charting bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price momentum as proxy
        momentum = price.pct_change(5)
        signals[momentum > self.threshold], signals[momentum < -self.threshold] = 1, -1
        return signals

