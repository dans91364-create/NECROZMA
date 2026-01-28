"""Multi-pair Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class CorrelationTrader(Strategy):
    """Correlation Trading"""
    def __init__(self, params: Dict):
        super().__init__("CorrelationTrader", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "trade correlated pairs bullish signal"}, {"type": "entry_short", "condition": "trade correlated pairs bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class PairDivergence(Strategy):
    """Pair Divergence"""
    def __init__(self, params: Dict):
        super().__init__("PairDivergence", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "divergence between correlated pairs bullish signal"}, {"type": "entry_short", "condition": "divergence between correlated pairs bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

