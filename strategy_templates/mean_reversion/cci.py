"""CCI Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON

class CCIStrategy(Strategy):
    """Commodity Channel Index Strategy"""
    def __init__(self, params: Dict):
        super().__init__("CCIStrategy", params)
        self.period = params.get("period", 20)
        self.oversold = params.get("oversold", -100)
        self.overbought = params.get("overbought", 100)
        self.rules = [{"type": "entry_long", "condition": "CCI crosses above -100"},
                     {"type": "entry_short", "condition": "CCI crosses below 100"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            price = df.get("close", df.get("mid_price"))
            tp = (df["high"] + df["low"] + price) / 3
            sma = tp.rolling(self.period).mean()
            mad = (tp - sma).abs().rolling(self.period).mean()
            cci = (tp - sma) / (0.015 * mad + EPSILON)
            signals[(cci > self.oversold) & (cci.shift(1) <= self.oversold)] = 1
            signals[(cci < self.overbought) & (cci.shift(1) >= self.overbought)] = -1
        return signals

class CCIDivergence(Strategy):
    """CCI Divergence Strategy"""
    def __init__(self, params: Dict):
        super().__init__("CCIDivergence", params)
        self.period = params.get("period", 20)
        self.lookback = params.get("lookback", 5)
        self.rules = [{"type": "entry_long", "condition": "bullish CCI divergence"},
                     {"type": "entry_short", "condition": "bearish CCI divergence"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "low" in df.columns:
            price = df.get("close", df.get("mid_price"))
            tp = (df["high"] + df["low"] + price) / 3
            sma = tp.rolling(self.period).mean()
            mad = (tp - sma).abs().rolling(self.period).mean()
            cci = (tp - sma) / (0.015 * mad + EPSILON)
            price_low = price.rolling(self.lookback).min()
            cci_low = cci.rolling(self.lookback).min()
            signals[(price == price_low) & (cci > cci.shift(self.lookback))] = 1
            signals[(price == price.rolling(self.lookback).max()) & (cci < cci.shift(self.lookback))] = -1
        return signals
