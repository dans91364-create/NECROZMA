"""Exotic Chart and Order Flow Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class RangeBars(Strategy):
    """Range Bars"""
    def __init__(self, params: Dict):
        super().__init__("RangeBars", params)
        self.threshold = params.get("threshold", 0.5)
        self.rules = [{"type": "entry_long", "condition": "fixed range bars bullish"}, {"type": "entry_short", "condition": "fixed range bars bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price momentum as proxy
        momentum = price.pct_change(5)
        signals[momentum > self.threshold], signals[momentum < -self.threshold] = 1, -1
        return signals

class TickCharts(Strategy):
    """Tick Charts"""
    def __init__(self, params: Dict):
        super().__init__("TickCharts", params)
        self.threshold = params.get("threshold", 0.5)
        self.rules = [{"type": "entry_long", "condition": "tick-based bullish"}, {"type": "entry_short", "condition": "tick-based bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price momentum as proxy
        momentum = price.pct_change(5)
        signals[momentum > self.threshold], signals[momentum < -self.threshold] = 1, -1
        return signals

class VolumeBars(Strategy):
    """Volume Bars"""
    def __init__(self, params: Dict):
        super().__init__("VolumeBars", params)
        self.threshold = params.get("threshold", 0.5)
        self.rules = [{"type": "entry_long", "condition": "volume-based bullish"}, {"type": "entry_short", "condition": "volume-based bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price momentum as proxy
        momentum = price.pct_change(5)
        signals[momentum > self.threshold], signals[momentum < -self.threshold] = 1, -1
        return signals

class DeltaBars(Strategy):
    """Delta Bars"""
    def __init__(self, params: Dict):
        super().__init__("DeltaBars", params)
        self.threshold = params.get("threshold", 0.5)
        self.rules = [{"type": "entry_long", "condition": "delta-based bullish"}, {"type": "entry_short", "condition": "delta-based bearish"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        # Simplified: use price momentum as proxy
        momentum = price.pct_change(5)
        signals[momentum > self.threshold], signals[momentum < -self.threshold] = 1, -1
        return signals

