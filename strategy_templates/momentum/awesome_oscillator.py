"""Additional Momentum Oscillators"""
import pandas as pd
from typing import Dict
from ..base import Strategy

class ErgodicOscillator(Strategy):
    """Ergodic Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("ErgodicOscillator", params)
        self.long_period, self.short_period = params.get("long_period", 32), params.get("short_period", 5)
        self.signal = params.get("signal_period", 5)
        self.rules = [{"type": "entry_long", "condition": "EO crosses above signal"}, {"type": "entry_short", "condition": "EO crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        mom = price.diff()
        eo = mom.ewm(span=self.long_period).mean().ewm(span=self.short_period).mean()
        sig = eo.ewm(span=self.signal).mean()
        signals[(eo > sig) & (eo.shift(1) <= sig.shift(1))], signals[(eo < sig) & (eo.shift(1) >= sig.shift(1))] = 1, -1
        return signals

class PrettyGoodOsc(Strategy):
    """Pretty Good Oscillator"""
    def __init__(self, params: Dict):
        super().__init__("PrettyGoodOsc", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "PGO > 3"}, {"type": "entry_short", "condition": "PGO < -3"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals, price = pd.Series(0, index=df.index), df.get("mid_price", df.get("close", df.get("Close")))
        sma, atr = price.rolling(self.period).mean(), price.diff().abs().rolling(self.period).mean()
        pgo = (price - sma) / (atr + 1e-10)
        signals[pgo > 3], signals[pgo < -3] = 1, -1
        return signals
