"""Ultimate Oscillator Strategy"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class UltimateOscillator(Strategy):
    """Ultimate Oscillator - Multi-timeframe momentum"""
    def __init__(self, params: Dict):
        super().__init__("UltimateOscillator", params)
        self.period1 = params.get("period1", 7)
        self.period2 = params.get("period2", 14)
        self.period3 = params.get("period3", 28)
        self.oversold = params.get("oversold", 30)
        self.overbought = params.get("overbought", 70)
        self.rules = [{"type": "entry_long", "condition": "UO crosses above 30"},
                     {"type": "entry_short", "condition": "UO crosses below 70"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            high, low = df["high"], df["low"]
            close = df.get("close", df.get("mid_price"))
            bp = close - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
            tr = pd.concat([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))], axis=1).max(axis=1)
            avg1 = bp.rolling(self.period1).sum() / (tr.rolling(self.period1).sum() + EPSILON)
            avg2 = bp.rolling(self.period2).sum() / (tr.rolling(self.period2).sum() + EPSILON)
            avg3 = bp.rolling(self.period3).sum() / (tr.rolling(self.period3).sum() + EPSILON)
            uo = 100 * (4*avg1 + 2*avg2 + avg3) / 7
            signals[(uo > self.oversold) & (uo.shift(1) <= self.oversold)] = 1
            signals[(uo < self.overbought) & (uo.shift(1) >= self.overbought)] = -1
        return signals
