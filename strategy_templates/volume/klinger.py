"""Klinger Oscillator Strategies"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class KlingerOscillator(Strategy):
    def __init__(self, params: Dict):
        super().__init__("KlingerOscillator", params)
        self.fast, self.slow = params.get("fast", 34), params.get("slow", 55)
        self.rules = [{"type": "entry_long", "condition": "Klinger crosses above zero"}, {"type": "entry_short", "condition": "Klinger crosses below zero"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            hlc = (df["high"] + df["low"] + df.get("close", df.get("mid_price"))) / 3
            dm = df["high"] - df["low"]
            cm = dm.where(hlc > hlc.shift(1), -dm)
            vf = df["volume"] * cm.abs() / (dm + EPSILON) * cm.apply(lambda x: 1 if x > 0 else -1)
            kvo = vf.ewm(span=self.fast).mean() - vf.ewm(span=self.slow).mean()
            signals[(kvo > 0) & (kvo.shift(1) <= 0)], signals[(kvo < 0) & (kvo.shift(1) >= 0)] = 1, -1
        return signals
class KlingerSignal(Strategy):
    def __init__(self, params: Dict):
        super().__init__("KlingerSignal", params)
        self.fast, self.slow, self.signal = params.get("fast", 34), params.get("slow", 55), params.get("signal", 13)
        self.rules = [{"type": "entry_long", "condition": "Klinger crosses above signal"}, {"type": "entry_short", "condition": "Klinger crosses below signal"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            hlc = (df["high"] + df["low"] + df.get("close", df.get("mid_price"))) / 3
            dm = df["high"] - df["low"]
            cm = dm.where(hlc > hlc.shift(1), -dm)
            vf = df["volume"] * cm.abs() / (dm + EPSILON) * cm.apply(lambda x: 1 if x > 0 else -1)
            kvo = vf.ewm(span=self.fast).mean() - vf.ewm(span=self.slow).mean()
            sig = kvo.ewm(span=self.signal).mean()
            signals[(kvo > sig) & (kvo.shift(1) <= sig.shift(1))], signals[(kvo < sig) & (kvo.shift(1) >= sig.shift(1))] = 1, -1
        return signals
