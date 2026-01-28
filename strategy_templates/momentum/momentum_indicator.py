"""Momentum Indicators"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class MomentumIndicator(Strategy):
    """Classic Momentum Indicator"""
    def __init__(self, params: Dict):
        super().__init__("MomentumIndicator", params)
        self.period = params.get("period", 10)
        self.threshold = params.get("threshold", 100)
        self.rules = [{"type": "entry_long", "condition": "momentum > 100"},
                     {"type": "entry_short", "condition": "momentum < 100"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        momentum = 100 * price / price.shift(self.period)
        signals[(momentum > self.threshold) & (momentum.shift(1) <= self.threshold)] = 1
        signals[(momentum < self.threshold) & (momentum.shift(1) >= self.threshold)] = -1
        return signals

class ChandeForecast(Strategy):
    """Chande Forecast Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("ChandeForecast", params)
        self.period = params.get("period", 14)
        self.threshold = params.get("threshold", 5)
        self.rules = [{"type": "entry_long", "condition": "CFO > threshold"},
                     {"type": "entry_short", "condition": "CFO < -threshold"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        sma = price.rolling(self.period).mean()
        cfo = 100 * (price - sma) / price
        signals[cfo > self.threshold] = 1
        signals[cfo < -self.threshold] = -1
        return signals

class PriceMomentumOsc(Strategy):
    """Price Momentum Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("PriceMomentumOsc", params)
        self.period1 = params.get("period1", 35)
        self.period2 = params.get("period2", 20)
        self.signal_period = params.get("signal_period", 10)
        self.rules = [{"type": "entry_long", "condition": "PMO crosses above signal"},
                     {"type": "entry_short", "condition": "PMO crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        roc = price.pct_change(1)
        pmo = roc.ewm(span=self.period1).mean().ewm(span=self.period2).mean()
        signal = pmo.ewm(span=self.signal_period).mean()
        signals[(pmo > signal) & (pmo.shift(1) <= signal.shift(1))] = 1
        signals[(pmo < signal) & (pmo.shift(1) >= signal.shift(1))] = -1
        return signals

class RelativeMomentum(Strategy):
    """Relative Momentum Index"""
    def __init__(self, params: Dict):
        super().__init__("RelativeMomentum", params)
        self.period = params.get("period", 14)
        self.momentum_period = params.get("momentum_period", 5)
        self.oversold = params.get("oversold", 40)
        self.overbought = params.get("overbought", 60)
        self.rules = [{"type": "entry_long", "condition": "RMI < 40"},
                     {"type": "entry_short", "condition": "RMI > 60"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        price = df.get("mid_price", df.get("close", df.get("Close")))
        momentum = price.diff(self.momentum_period)
        up = momentum.where(momentum > 0, 0).rolling(self.period).mean()
        down = -momentum.where(momentum < 0, 0).rolling(self.period).mean()
        rmi = 100 * up / (up + down + 1e-10)
        signals[rmi < self.oversold] = 1
        signals[rmi > self.overbought] = -1
        return signals
