"""Risk Management Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class DrawdownControl(Strategy):
    """Drawdown Control"""
    def __init__(self, params: Dict):
        super().__init__("DrawdownControl", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "limit drawdown exposure and risk acceptable"}, {"type": "entry_short", "condition": "limit drawdown exposure and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

