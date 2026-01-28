"""Multi-pair Trading Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class CarryTrade(Strategy):
    """Carry Trade"""
    def __init__(self, params: Dict):
        super().__init__("CarryTrade", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "interest rate differential bullish signal"}, {"type": "entry_short", "condition": "interest rate differential bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

class TriangularArbitrage(Strategy):
    """Triangular Arbitrage"""
    def __init__(self, params: Dict):
        super().__init__("TriangularArbitrage", params)
        self.period = params.get("period", 20)
        self.rules = [{"type": "entry_long", "condition": "three-way currency arbitrage bullish signal"}, {"type": "entry_short", "condition": "three-way currency arbitrage bearish signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Single-pair proxy: use momentum as correlation/strength proxy
        momentum = price.pct_change(self.period)
        signals[momentum > momentum.rolling(self.period).mean()], signals[momentum < momentum.rolling(self.period).mean()] = 1, -1
        return signals

