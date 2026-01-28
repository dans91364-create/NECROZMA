"""Smart Money Concepts (SMC)"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class WyckoffMethod(Strategy):
    """Wyckoff Method"""
    def __init__(self, params: Dict):
        super().__init__("WyckoffMethod", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "Wyckoff phases bullish"}, {"type": "entry_short", "condition": "Wyckoff phases bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

class MarketMakerModel(Strategy):
    """Market Maker Model"""
    def __init__(self, params: Dict):
        super().__init__("MarketMakerModel", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "MM manipulation bullish"}, {"type": "entry_short", "condition": "MM manipulation bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

