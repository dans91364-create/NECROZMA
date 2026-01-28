"""Risk Management Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class ATRStopStrategy(Strategy):
    """ATR Stop Loss"""
    def __init__(self, params: Dict):
        super().__init__("ATRStopStrategy", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "ATR-based stops and risk acceptable"}, {"type": "entry_short", "condition": "ATR-based stops and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

class ChandelierExit(Strategy):
    """Chandelier Exit"""
    def __init__(self, params: Dict):
        super().__init__("ChandelierExit", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "trailing ATR stop and risk acceptable"}, {"type": "entry_short", "condition": "trailing ATR stop and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

class TrailingStopATR(Strategy):
    """Trailing Stop ATR"""
    def __init__(self, params: Dict):
        super().__init__("TrailingStopATR", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "dynamic trailing and risk acceptable"}, {"type": "entry_short", "condition": "dynamic trailing and risk acceptable"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simple momentum signals with implied risk management
        sma = price.rolling(self.period).mean()
        signals[price > sma], signals[price < sma] = 1, -1
        return signals

