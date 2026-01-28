"""Smart Money Concepts (SMC)"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class PremiumDiscount(Strategy):
    """Premium/Discount Zones"""
    def __init__(self, params: Dict):
        super().__init__("PremiumDiscount", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "value zones bullish"}, {"type": "entry_short", "condition": "value zones bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

class OptimalTradeEntry(Strategy):
    """Optimal Trade Entry (OTE)"""
    def __init__(self, params: Dict):
        super().__init__("OptimalTradeEntry", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "optimal entries bullish"}, {"type": "entry_short", "condition": "optimal entries bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

