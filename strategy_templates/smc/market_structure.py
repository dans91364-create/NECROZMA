"""Smart Money Concepts (SMC)"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class BreakOfStructure(Strategy):
    """Break of Structure (BOS)"""
    def __init__(self, params: Dict):
        super().__init__("BreakOfStructure", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "structure breaks bullish"}, {"type": "entry_short", "condition": "structure breaks bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

class ChangeOfCharacter(Strategy):
    """Change of Character (CHoCH)"""
    def __init__(self, params: Dict):
        super().__init__("ChangeOfCharacter", params)
        self.lookback = params.get("lookback", 20)
        self.rules = [{"type": "entry_long", "condition": "character changes bullish"}, {"type": "entry_short", "condition": "character changes bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        if "high" in df.columns:
            # Simplified SMC: use swing highs/lows as structure
            swing_high, swing_low = df["high"].rolling(self.lookback).max(), df["low"].rolling(self.lookback).min()
            # Buy on break above, sell on break below
            signals[(price > swing_high.shift(1))], signals[(price < swing_low.shift(1))] = 1, -1
        return signals

