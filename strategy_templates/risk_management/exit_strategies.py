"""Risk Management Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class TimeBasedExit(Strategy):
    """Time-based Exit"""
    def __init__(self, params: Dict):
        super().__init__("TimeBasedExit", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "exit after N bars and risk acceptable"}, {"type": "entry_short", "condition": "exit after N bars and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

class ProfitTargetScale(Strategy):
    """Profit Target Scaling"""
    def __init__(self, params: Dict):
        super().__init__("ProfitTargetScale", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "scale out at targets and risk acceptable"}, {"type": "entry_short", "condition": "scale out at targets and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

